"""
Protocol: USDA FoodData Central API – Food Search (GET /foods/search)
Citable Source: USDA Agricultural Research Service. FoodData Central API Guide. OpenAPI specification version 1.0.1.
Input -> Output Contract: Food search query (string) -> JSON object containing matching food records, food descriptions, fdcId, and available nutrient information.
Package Versions: requests==2.32.3, pytest==8.2.2
"""

import os
import pytest
import requests

BASE_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"
# Retrieve API key securely from environment variables (populated by GitHub Actions secrets)
API_KEY = os.getenv("MY_KEY", "fallback_test_key")


@pytest.fixture(scope="session")
def api_session():
    """Share a single requests session across all tests to minimize overhead."""
    session = requests.Session()
    yield session
    session.close()


def test_food_search_ordinary_query(api_session):
    params = {"api_key": API_KEY, "query": "cheddar cheese", "pageSize": 1}
    response = api_session.get(BASE_URL, params=params)
    assert response.status_code == 200
    data = response.json()
    assert "foods" in data
    assert "totalHits" in data
    assert isinstance(data["foods"], list)
    assert len(data["foods"]) >= 1
    item = data["foods"][0]
    assert isinstance(item["fdcId"], int)
    assert isinstance(item["description"], str)
    assert len(item["description"]) > 0


def test_food_search_with_data_type_filter(api_session):
    params = {"api_key": API_KEY, "query": "milk", "dataType": ["Foundation"], "pageSize": 5}
    response = api_session.get(BASE_URL, params=params)
    assert response.status_code == 200
    data = response.json()
    assert "foods" in data
    for item in data["foods"]:
        assert item.get("dataType") == "Foundation"


def test_food_search_sorting(api_session):
    params = {
        "api_key": API_KEY,
        "query": "apple",
        "sortBy": "description.keyword",
        "sortOrder": "asc",
        "pageSize": 5,
    }
    response = api_session.get(BASE_URL, params=params)
    assert response.status_code == 200
    data = response.json()
    assert "foods" in data
    descriptions = [item.get("description", "") for item in data["foods"]]
    assert descriptions == sorted(descriptions)


def test_food_search_pagination(api_session):
    params = {"api_key": API_KEY, "query": "apple", "pageSize": 2, "pageNumber": 1}
    response = api_session.get(BASE_URL, params=params)
    assert response.status_code == 200
    data = response.json()
    assert "foods" in data
    assert len(data["foods"]) <= 2
    assert any(k in data for k in ("currentPage", "totalPages", "totalHits"))


def test_food_search_nutrient_info_presence(api_session):
    params = {"api_key": API_KEY, "query": "banana", "pageSize": 1}
    response = api_session.get(BASE_URL, params=params)
    assert response.status_code == 200
    data = response.json()
    assert "foods" in data
    assert len(data["foods"]) >= 1
    item = data["foods"][0]
    assert "foodNutrients" in item
    assert isinstance(item["foodNutrients"], list)
    if len(item["foodNutrients"]) > 0:
        nutrient = item["foodNutrients"][0]
        assert "nutrientName" in nutrient or "value" in nutrient


def test_food_search_empty_result(api_session):
    params = {"api_key": API_KEY, "query": "xyznonexistentfood99999"}
    response = api_session.get(BASE_URL, params=params)
    assert response.status_code == 200
    data = response.json()
    assert data.get("foods") == []
    assert data.get("totalHits") == 0


@pytest.mark.parametrize(
    "params,expected_statuses",
    [
        ({"api_key": "INVALID_KEY_TEST", "query": "banana"}, {401, 403}),
    ],
    ids=["invalid_api_key"],
)
def test_food_search_invalid_api_key(api_session, params, expected_statuses):
    response = api_session.get(BASE_URL, params=params)
    assert response.status_code in expected_statuses


@pytest.mark.parametrize(
    "params,expected_status",
    [
        ({"api_key": API_KEY}, 200),
    ],
    ids=["missing_query_parameter"],
)
def test_food_search_missing_query_parameter(api_session, params, expected_status):
    response = api_session.get(BASE_URL, params=params)
    assert response.status_code == expected_status

def test_deliberate_failure_for_ci(api_session):
    params = {"api_key": API_KEY, "query": "cheddar cheese", "pageSize": 1}
    response = api_session.get(BASE_URL, params=params)
    data = response.json()
    # Deliberately wrong assertion to trigger CI failure check (999999 is impossible)
    assert data.get("totalHits") == 60863