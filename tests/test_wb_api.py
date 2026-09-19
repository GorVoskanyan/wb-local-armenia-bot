import pytest
from services.wb_api import WildberriesAPIClient


@pytest.mark.asyncio
async def test_validate_api_key_mock():
    client = WildberriesAPIClient(api_key="mock_test_key")
    is_valid = await client.validate_api_key()
    assert is_valid is True


@pytest.mark.asyncio
async def test_fetch_seller_cards_mock():
    client = WildberriesAPIClient(api_key="mock_test_key")
    cards = await client.fetch_seller_cards()
    assert isinstance(cards, list)
    assert len(cards) > 0
    assert "nmID" in cards[0]
    assert "title" in cards[0]


@pytest.mark.asyncio
async def test_fetch_seller_stocks_mock():
    client = WildberriesAPIClient(api_key="mock_test_key")
    stocks = await client.fetch_seller_stocks()
    assert isinstance(stocks, list)
    assert len(stocks) > 0
    assert "sku" in stocks[0]
    assert "amount" in stocks[0]


@pytest.mark.asyncio
async def test_fetch_armenian_warehouses_mock():
    client = WildberriesAPIClient(api_key="mock_test_key")
    warehouses = await client.fetch_armenian_warehouses()
    assert isinstance(warehouses, list)
    assert len(warehouses) > 0
    assert "yerevan" in warehouses[0]["name"].lower() or "armenia" in warehouses[0]["name"].lower()
