"""Data ingestion service - fetches from mock APIs and stores in PostgreSQL."""
import httpx
import asyncio
import time
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import get_settings
from app.db.database import SessionLocal
from app.repositories.customer_repository import CustomerRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.refund_repository import RefundRepository

settings = get_settings()


class IngestionService:
    """Asynchronous data ingestion with retry, batching, and deduplication."""

    def __init__(self):
        self.base_url = settings.api_base_url
        self.batch_size = settings.batch_size
        self.progress = {}

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
    )
    async def _fetch_page(
        self, client: httpx.AsyncClient, endpoint: str, limit: int, offset: int
    ) -> dict:
        """Fetch a single page with retry logic."""
        response = await client.get(
            f"{self.base_url}/{endpoint}",
            params={"limit": limit, "offset": offset},
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()

    async def _ingest_entity(self, endpoint: str, repo_class, db_session):
        """Ingest all records for a single entity type."""
        repo = repo_class(db_session)
        current_max_id = repo.get_max_id()

        async with httpx.AsyncClient() as client:
            first_page = await self._fetch_page(client, endpoint, 1, 0)
            total = first_page["total"]

            self.progress[endpoint] = {
                "total": total,
                "ingested": 0,
                "status": "in_progress",
            }

            print(f"[{endpoint}] Starting ingestion: {total} records")

            offset = current_max_id
            batch = []

            while offset < total:
                page_data = await self._fetch_page(
                    client, endpoint, self.batch_size, offset
                )
                records = page_data["data"]

                if not records:
                    break

                new_records = [r for r in records if r.get("id", 0) > current_max_id]
                batch.extend(new_records)

                if len(batch) >= self.batch_size:
                    repo.bulk_insert(batch[:self.batch_size])
                    batch = batch[self.batch_size:]
                    self.progress[endpoint]["ingested"] = offset + self.batch_size
                    print(f"  [{endpoint}] Ingested {offset + self.batch_size}/{total}")

                offset += self.batch_size

            if batch:
                repo.bulk_insert(batch)

            self.progress[endpoint]["ingested"] = total
            self.progress[endpoint]["status"] = "completed"
            print(f"[{endpoint}] Ingestion complete: {total} records")

    async def run(self):
        """Run full ingestion pipeline."""
        start_time = time.time()
        db = SessionLocal()

        try:
            await self._ingest_entity("customers", CustomerRepository, db)
            await self._ingest_entity("orders", OrderRepository, db)
            await self._ingest_entity("refunds", RefundRepository, db)

            elapsed = time.time() - start_time
            print(f"\nIngestion completed in {elapsed:.2f} seconds")
            print(f"Progress: {self.progress}")
        finally:
            db.close()


def main():
    """Entry point for ingestion."""
    service = IngestionService()
    asyncio.run(service.run())


if __name__ == "__main__":
    main()