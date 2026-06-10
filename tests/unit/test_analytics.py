"""Unit tests for analytics service."""
import pytest
from unittest.mock import MagicMock, patch
from app.services.analytics_service import AnalyticsService
from app.schemas.schemas import AnalyticsMetric


class TestAnalyticsService:
    """Unit tests for AnalyticsService."""

    def setup_method(self):
        """Setup test fixtures."""
        self.mock_db = MagicMock()
        self.mock_cache = MagicMock()
        self.service = AnalyticsService(db=self.mock_db, cache=self.mock_cache)

    def test_get_total_orders_from_cache(self):
        """Test that cached value is returned when available."""
        self.mock_cache.get.return_value = 1000000
        result = self.service.get_total_orders()
        assert result.metric == "total_orders"
        assert result.value == 1000000.0
        assert result.cached is True

    def test_get_total_orders_cache_miss(self):
        """Test that DB is queried on cache miss."""
        self.mock_cache.get.return_value = None
        
        with patch.object(self.service.order_repo, 'count', return_value=500000):
            result = self.service.get_total_orders()
            assert result.metric == "total_orders"
            assert result.value == 500000.0
            assert result.cached is False
            self.mock_cache.set.assert_called_once()

    def test_get_total_revenue_from_cache(self):
        """Test total revenue from cache."""
        self.mock_cache.get.return_value = 49987234.56
        result = self.service.get_total_revenue()
        assert result.metric == "total_revenue"
        assert result.value == 49987234.56
        assert result.cached is True

    def test_get_net_revenue(self):
        """Test net revenue calculation."""
        # Mock cache to return revenue and refunds
        self.mock_cache.get.side_effect = [25000000.0, 5000000.0]
        result = self.service.get_net_revenue()
        assert result.metric == "net_revenue"
        assert result.value == 20000000.0

    def test_get_average_order_value(self):
        """Test average order value."""
        self.mock_cache.get.return_value = 49.99
        result = self.service.get_average_order_value()
        assert result.metric == "average_order_value"
        assert result.value == 49.99

    def test_get_top_customers_from_cache(self):
        """Test top customers from cache."""
        cached_data = [
            {"customer_id": 1, "name": "John", "email": "john@test.com", "total_spend": 5000.0, "order_count": 50},
            {"customer_id": 2, "name": "Jane", "email": "jane@test.com", "total_spend": 4500.0, "order_count": 45},
        ]
        self.mock_cache.get.return_value = cached_data
        result = self.service.get_top_customers()
        assert result.metric == "top_customers"
        assert len(result.data) == 2
        assert result.cached is True

    def test_get_revenue_trends_daily(self):
        """Test daily revenue trends from cache."""
        cached_data = [
            {"period": "2026-01-01", "revenue": 50000.0, "order_count": 1000},
            {"period": "2026-01-02", "revenue": 55000.0, "order_count": 1100},
        ]
        self.mock_cache.get.return_value = cached_data
        result = self.service.get_revenue_trends("daily")
        assert result.period_type == "daily"
        assert len(result.data) == 2
        assert result.cached is True


class TestAnalyticsMetricSchema:
    """Test Pydantic schema validation."""

    def test_valid_metric(self):
        metric = AnalyticsMetric(metric="test", value=100.5, cached=True)
        assert metric.metric == "test"
        assert metric.value == 100.5

    def test_metric_serialization(self):
        metric = AnalyticsMetric(metric="total_orders", value=1000000, cached=False)
        data = metric.model_dump()
        assert "metric" in data
        assert "value" in data
        assert "computed_at" in data