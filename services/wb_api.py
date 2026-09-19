import logging
from typing import List, Dict, Any, Optional
import httpx
from core.config import settings

logger = logging.getLogger(__name__)


class WildberriesAPIClient:
    """Async HTTP client to interface with Wildberries Seller API."""

    CONTENT_API_URL = "https://content-api.wildberries.ru/content/v2/get/cards/list"
    STOCKS_API_URL = "https://marketplace-api.wildberries.ru/api/v3/stocks"
    WAREHOUSES_API_URL = "https://marketplace-api.wildberries.ru/api/v3/warehouses"

    # Known Armenian WB Warehouse names/keywords (e.g., Yerevan / Armenia warehouses)
    ARMENIAN_WAREHOUSE_KEYWORDS = ["yerevan", "armenia", "երևան", "ереван", "армения"]

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }

    async def validate_api_key(self) -> bool:
        """Validate if the provided WB API key works."""
        if settings.mock_wb_api and self.api_key.startswith("mock_"):
            return True

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.WAREHOUSES_API_URL, headers=self.headers)
                return response.status_code in (200, 201)
        except Exception as e:
            logger.error(f"Error validating WB API key: {e}")
            return False

    async def fetch_seller_cards(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Fetch seller product cards from WB Content API."""
        if settings.mock_wb_api or self.api_key.startswith("mock_"):
            return self._get_mock_cards()

        payload = {
            "settings": {
                "cursor": {"limit": limit},
                "filter": {"withPhoto": -1}
            }
        }
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(self.CONTENT_API_URL, headers=self.headers, json=payload)
                response.raise_for_status()
                data = response.json()
                cards = data.get("cards", [])
                return cards
        except Exception as e:
            logger.error(f"Error fetching seller cards from WB API: {e}")
            return []

    async def fetch_seller_stocks(self, warehouse_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Fetch stock availability from WB Marketplace API."""
        if settings.mock_wb_api or self.api_key.startswith("mock_"):
            return self._get_mock_stocks()

        params = {}
        if warehouse_id:
            params["warehouseId"] = warehouse_id

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(self.STOCKS_API_URL, headers=self.headers, json=params)
                response.raise_for_status()
                data = response.json()
                return data.get("stocks", [])
        except Exception as e:
            logger.error(f"Error fetching stocks from WB API: {e}")
            return []

    async def fetch_armenian_warehouses(self) -> List[Dict[str, Any]]:
        """Fetch seller warehouses located in Armenia."""
        if settings.mock_wb_api or self.api_key.startswith("mock_"):
            return [{"id": 1001, "name": "Yerevan Warehouse Armenia"}]

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.WAREHOUSES_API_URL, headers=self.headers)
                response.raise_for_status()
                warehouses = response.json()
                armenian_whs = [
                    wh for wh in warehouses
                    if any(kw in wh.get("name", "").lower() for kw in self.ARMENIAN_WAREHOUSE_KEYWORDS)
                ]
                return armenian_whs
        except Exception as e:
            logger.error(f"Error fetching warehouses from WB API: {e}")
            return []

    def _get_mock_cards(self) -> List[Dict[str, Any]]:
        return [
            {
                "nmID": 100001,
                "title": "Armenian Coffee Blend (Traditional Yerevan Roast)",
                "vendorCode": "ARM-COFFEE-01",
                "category": "Food & Beverages",
                "photos": [{"big": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=500"}],
                "sizes": [
                    {
                        "price": 5000,
                        "discountedPrice": 3500,
                        "skus": ["10000101"]
                    }
                ]
            },
            {
                "nmID": 100002,
                "title": "Handcrafted Armenian Ceramic Tea Mug",
                "vendorCode": "ARM-MUG-02",
                "category": "Home & Kitchen",
                "photos": [{"big": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=500"}],
                "sizes": [
                    {
                        "price": 8000,
                        "discountedPrice": 4800,
                        "skus": ["10000201"]
                    }
                ]
            },
            {
                "nmID": 100003,
                "title": "Organic Armenian Dried Fruit Assortment 500g",
                "vendorCode": "ARM-FRUIT-03",
                "category": "Food & Beverages",
                "photos": [{"big": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=500"}],
                "sizes": [
                    {
                        "price": 6500,
                        "discountedPrice": 4200,
                        "skus": ["10000301"]
                    }
                ]
            }
        ]

    def _get_mock_stocks(self) -> List[Dict[str, Any]]:
        return [
            {"sku": "10000101", "amount": 25, "warehouseId": 1001},
            {"sku": "10000201", "amount": 10, "warehouseId": 1001},
            {"sku": "10000301", "amount": 40, "warehouseId": 1001},
        ]
