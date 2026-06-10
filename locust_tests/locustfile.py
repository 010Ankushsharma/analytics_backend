"""Load tests for analytics endpoints using Locust."""
from locust import HttpUser, task, between, tag


class AnalyticsUser(HttpUser):
    """Simulates a user hitting analytics endpoints."""
    
    wait_time = between(0.5, 2.0)

    @tag("simple")
    @task(3)
    def total_orders(self):
        """Test total orders endpoint."""
        self.client.get("/analytics/total-orders", name="/analytics/total-orders")

    @tag("simple")
    @task(3)
    def total_revenue(self):
        """Test total revenue endpoint."""
        self.client.get("/analytics/total-revenue", name="/analytics/total-revenue")

    @tag("simple")
    @task(2)
    def total_refunds(self):
        """Test total refunds endpoint."""
        self.client.get("/analytics/total-refunds", name="/analytics/total-refunds")

    @tag("simple")
    @task(2)
    def net_revenue(self):
        """Test net revenue endpoint."""
        self.client.get("/analytics/net-revenue", name="/analytics/net-revenue")

    @tag("simple")
    @task(2)
    def average_order_value(self):
        """Test average order value endpoint."""
        self.client.get("/analytics/average-order-value", name="/analytics/average-order-value")

    @tag("complex")
    @task(1)
    def repeat_customer_revenue(self):
        """Test repeat customer revenue (heavier query)."""
        self.client.get(
            "/analytics/repeat-customer-revenue",
            name="/analytics/repeat-customer-revenue",
        )

    @tag("complex")
    @task(2)
    def revenue_trends_daily(self):
        """Test daily revenue trends."""
        self.client.get(
            "/analytics/revenue-trends?period=daily",
            name="/analytics/revenue-trends[daily]",
        )

    @tag("complex")
    @task(1)
    def revenue_trends_weekly(self):
        """Test weekly revenue trends."""
        self.client.get(
            "/analytics/revenue-trends?period=weekly",
            name="/analytics/revenue-trends[weekly]",
        )

    @tag("complex")
    @task(1)
    def revenue_trends_monthly(self):
        """Test monthly revenue trends."""
        self.client.get(
            "/analytics/revenue-trends?period=monthly",
            name="/analytics/revenue-trends[monthly]",
        )

    @tag("complex")
    @task(2)
    def top_customers(self):
        """Test top customers endpoint."""
        self.client.get("/analytics/top-customers", name="/analytics/top-customers")

    @task(1)
    def health_check(self):
        """Health check (lightweight baseline)."""
        self.client.get("/health", name="/health")


class MockDataUser(HttpUser):
    """Simulates users fetching paginated mock data."""
    
    wait_time = between(1.0, 3.0)

    @task(2)
    def get_customers_page(self):
        self.client.get("/customers?limit=100&offset=0", name="/customers[page]")

    @task(3)
    def get_orders_page(self):
        self.client.get("/orders?limit=100&offset=0", name="/orders[page]")

    @task(1)
    def get_refunds_page(self):
        self.client.get("/refunds?limit=100&offset=0", name="/refunds[page]")