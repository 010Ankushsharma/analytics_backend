"""Integration tests for API endpoints."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


@pytest.fixture
def client():
    """Create test client."""
    from app.main import app
    return TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "version" in data


class TestMockDataEndpoints:
    """Test mock data API endpoints."""

    @patch("app.api.routes.mock_data._load_csv")
    def test_get_customers_pagination(self, mock_load, client):
        import pandas as pd
        mock_df = pd.DataFrame({
            "id": range(1, 101),
            "name": [f"Customer {i}" for i in range(1, 101)],
            "email": [f"c{i}@test.com" for i in range(1, 101)],
            "created_at": ["2026-01-01T00:00:00"] * 100,
        })
        mock_load.return_value = mock_df

        response = client.get("/customers?limit=10&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 100
        assert data["limit"] == 10
        assert len(data["data"]) == 10
        assert data["has_more"] is True

    @patch("app.api.routes.mock_data._load_csv")
    def test_get_orders_sorting(self, mock_load, client):
        import pandas as pd
        mock_df = pd.DataFrame({
            "id": [3, 1, 2],
            "customer_id": [1, 2, 3],
            "amount": [100.0, 50.0, 75.0],
            "status": ["completed", "completed", "pending"],
            "created_at": ["2026-01-03", "2026-01-01", "2026-01-02"],
        })
        mock_load.return_value = mock_df

        response = client.get("/orders?sort_by=amount&order=desc&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["data"][0]["amount"] == 100.0


class TestAnalyticsEndpoints:
    """Test analytics API endpoints."""

    @patch("app.api.deps.get_analytics_service")
    def test_total_orders(self, mock_service_dep, client):
        from app.schemas.schemas import AnalyticsMetric
        from datetime import datetime

        mock_service = MagicMock()
        mock_service.get_total_orders.return_value = AnalyticsMetric(
            metric="total_orders", value=1000000, cached=True
        )
        mock_service_dep.return_value = mock_service

        response = client.get("/analytics/total-orders")
        assert response.status_code == 200
        data = response.json()
        assert data["metric"] == "total_orders"
        assert data["value"] == 1000000

    @patch("app.api.deps.get_analytics_service")
    def test_total_revenue(self, mock_service_dep, client):
        from app.schemas.schemas import AnalyticsMetric

        mock_service = MagicMock()
        mock_service.get_total_revenue.return_value = AnalyticsMetric(
            metric="total_revenue", value=49987234.56, cached=False
        )
        mock_service_dep.return_value = mock_service

        response = client.get("/analytics/total-revenue")
        assert response.status_code == 200
        data = response.json()
        assert data["metric"] == "total_revenue"

    @patch("app.api.deps.get_analytics_service")
    def test_revenue_trends_with_period(self, mock_service_dep, client):
        from app.schemas.schemas import RevenueTrendResponse, RevenueTrendItem

        mock_service = MagicMock()
        mock_service.get_revenue_trends.return_value = RevenueTrendResponse(
            period_type="monthly",
            data=[RevenueTrendItem(period="2026-01", revenue=5000000, order_count=100000)],
            cached=True,
        )
        mock_service_dep.return_value = mock_service

        response = client.get("/analytics/revenue-trends?period=monthly")
        assert response.status_code == 200
        data = response.json()
        assert data["period_type"] == "monthly"