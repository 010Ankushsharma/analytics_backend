"""Dataset generator using Faker with fixed seed for reproducibility."""
import os
import csv
import random
from datetime import datetime, timedelta
from faker import Faker

# Configuration
SEED = 42
NUM_CUSTOMERS = 100_000
NUM_ORDERS = 1_000_000
NUM_REFUNDS = 200_000
DATA_DIR = os.environ.get("DATA_DIR", "./data")

# Initialize with fixed seed
fake = Faker()
Faker.seed(SEED)
random.seed(SEED)


def generate_customers():
    """Generate 100,000 customer records."""
    print(f"Generating {NUM_CUSTOMERS} customers...")
    filepath = os.path.join(DATA_DIR, "customers.csv")
    
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "email", "created_at"])
        writer.writeheader()
        
        for i in range(1, NUM_CUSTOMERS + 1):
            writer.writerow({
                "id": i,
                "name": fake.name(),
                "email": f"customer_{i}@{fake.domain_name()}",
                "created_at": fake.date_time_between(
                    start_date="-3y", end_date="now"
                ).isoformat(),
            })
            
            if i % 10000 == 0:
                print(f"  Customers: {i}/{NUM_CUSTOMERS}")
    
    print(f"  Saved to {filepath}")


def generate_orders():
    """Generate 1,000,000 order records."""
    print(f"Generating {NUM_ORDERS} orders...")
    filepath = os.path.join(DATA_DIR, "orders.csv")
    statuses = ["completed", "completed", "completed", "pending", "cancelled"]
    
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["id", "customer_id", "amount", "status", "created_at"]
        )
        writer.writeheader()
        
        for i in range(1, NUM_ORDERS + 1):
            writer.writerow({
                "id": i,
                "customer_id": random.randint(1, NUM_CUSTOMERS),
                "amount": round(random.uniform(5.0, 500.0), 2),
                "status": random.choice(statuses),
                "created_at": fake.date_time_between(
                    start_date="-2y", end_date="now"
                ).isoformat(),
            })
            
            if i % 100000 == 0:
                print(f"  Orders: {i}/{NUM_ORDERS}")
    
    print(f"  Saved to {filepath}")


def generate_refunds():
    """Generate 200,000 refund records."""
    print(f"Generating {NUM_REFUNDS} refunds...")
    filepath = os.path.join(DATA_DIR, "refunds.csv")
    
    # Select random order IDs for refunds
    refund_order_ids = random.sample(range(1, NUM_ORDERS + 1), NUM_REFUNDS)
    
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["id", "order_id", "refund_amount", "created_at"]
        )
        writer.writeheader()
        
        for i in range(1, NUM_REFUNDS + 1):
            writer.writerow({
                "id": i,
                "order_id": refund_order_ids[i - 1],
                "refund_amount": round(random.uniform(5.0, 200.0), 2),
                "created_at": fake.date_time_between(
                    start_date="-1y", end_date="now"
                ).isoformat(),
            })
            
            if i % 50000 == 0:
                print(f"  Refunds: {i}/{NUM_REFUNDS}")
    
    print(f"  Saved to {filepath}")


def main():
    """Generate all datasets."""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    print("=" * 60)
    print("DATA GENERATION - Fixed Seed:", SEED)
    print("=" * 60)
    
    generate_customers()
    generate_orders()
    generate_refunds()
    
    print("\n" + "=" * 60)
    print("GENERATION COMPLETE")
    print(f"  Customers: {NUM_CUSTOMERS:,}")
    print(f"  Orders:    {NUM_ORDERS:,}")
    print(f"  Refunds:   {NUM_REFUNDS:,}")
    print(f"  Location:  {DATA_DIR}/")
    print("=" * 60)


if __name__ == "__main__":
    main()