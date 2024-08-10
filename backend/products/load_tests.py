from locust import HttpUser, task, between


class DRFUser(HttpUser):
    wait_time = between(1, 5)

    @task(1)
    def get_products(self):
        self.client.get("/api/products/")
