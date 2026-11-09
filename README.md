# usda-food-search-protocol

This repository holds unit tests for the **USDA FoodData Central API – Food Search** atomic protocol (`GET /foods/search`). The protocol provides programmatic access to food search records, descriptions, `fdcId` identifiers, and available nutrient data from the USDA Agricultural Research Service.

## Contract

| | Type | Description |
|---|---|---|
| **Input** | `str` | Food search query string (e.g., `"cheddar cheese"`, `"apple"`) |
| **Output** | `JSON object` | Contains matching food records list (`foods`), total hit counts, and nutrient information |

```python
params = {"api_key": API_KEY, "query": "cheddar cheese", "pageSize": 1}
response = requests.get("[https://api.nal.usda.gov/fdc/v1/foods/search](https://api.nal.usda.gov/fdc/v1/foods/search)", params=params)
data = response.json()

## Wire diagram
The USDA FoodData Central API search protocol acts as the initial data-fetching layer for retrieving nutritional profiles and food descriptions.
![Workflow wire diagram](docs/wire_diagram.png)

[![tests](https://github.com/RCarrera-695/final-project/actions/workflows/tests.yml/badge.svg)](https://github.com/RCarrera-695/final-project/actions/workflows/tests.yml)