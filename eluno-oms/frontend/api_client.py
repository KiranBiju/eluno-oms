z"""HTTP client for Eluno OMS FastAPI backend."""

import frontend.bootstrap  # noqa: F401
import os

import httpx

API_BASE = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
TIMEOUT = 30.0


class APIClient:
    def __init__(self, base_url: str = API_BASE):
        self.base_url = base_url.rstrip("/")

    def _get(self, path: str, params: dict | None = None):
        with httpx.Client(timeout=TIMEOUT) as client:
            r = client.get(f"{self.base_url}{path}", params=params)
            r.raise_for_status()
            return r.json()

    def _post(self, path: str, json: dict | None = None):
        with httpx.Client(timeout=TIMEOUT) as client:
            r = client.post(f"{self.base_url}{path}", json=json)
            r.raise_for_status()
            return r.json()

    def _put(self, path: str, json: dict):
        with httpx.Client(timeout=TIMEOUT) as client:
            r = client.put(f"{self.base_url}{path}", json=json)
            r.raise_for_status()
            return r.json()

    def _patch(self, path: str, json: dict):
        with httpx.Client(timeout=TIMEOUT) as client:
            r = client.patch(f"{self.base_url}{path}", json=json)
            r.raise_for_status()
            return r.json()

    def _delete(self, path: str):
        with httpx.Client(timeout=TIMEOUT) as client:
            r = client.delete(f"{self.base_url}{path}")
            r.raise_for_status()

    def health(self) -> dict:
        return self._get("/health")

    # Orders
    def get_orders(self, **filters) -> list:
        return self._get("/orders/", params={k: v for k, v in filters.items() if v})

    def get_order(self, order_id: int) -> dict:
        return self._get(f"/orders/{order_id}")

    def create_order(self, data: dict) -> dict:
        return self._post("/orders/", json=data)

    def update_order_status(self, order_id: int, new_status: str, reason: str = "") -> dict:
        return self._patch(f"/orders/{order_id}/status", json={"new_status": new_status, "reason": reason})

    def get_order_stats(self) -> dict:
        return self._get("/orders/stats")

    def get_order_history(self, order_id: int) -> list:
        return self._get(f"/orders/{order_id}/history")

    # Inventory
    def get_inventory(self) -> list:
        return self._get("/inventory/")

    def get_inventory_summary(self) -> dict:
        return self._get("/inventory/summary")

    def create_inventory(self, data: dict) -> dict:
        return self._post("/inventory/", json=data)

    def update_inventory(self, item_id: int, data: dict) -> dict:
        return self._put(f"/inventory/{item_id}", json=data)

    def delete_inventory(self, item_id: int):
        self._delete(f"/inventory/{item_id}")

    def check_availability(self, data: dict) -> dict:
        return self._post("/inventory/availability", json=data)

    # Predictions
    def get_predictions(self) -> list:
        return self._get("/predictions/")

    def run_predictions(self) -> dict:
        return self._post("/predictions/run")

    # Alerts
    def get_alerts(self) -> list:
        return self._get("/alerts/")

    # Copilot
    def ask_copilot(self, question: str) -> dict:
        return self._post("/copilot/chat", json={"question": question})


api = APIClient()
