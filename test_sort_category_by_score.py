import pytest
from unittest.mock import patch
from application.tasks.questionnaire_processor import (
    calculate_total_scores,
    construct_result_json,
    validate_time_format,
    validate_data,
    sort_categories_by_score,
    process_data
)


# Basic score
def test_sort_categories_integer_scores():
    result_json = {
        "user_id": "user123",
        "visit_count": 5,
        "visit_duration": "01:30:00",
        "categories": {
            "A": 10,
            "B": 50,
            "C": 30
        }
    }
    expected = {
        "user_id": "user123",
        "visit_count": 5,
        "visit_duration": "01:30:00",
        "categories": {
            "B": 50,
            "C": 30,
            "A": 10
        }
    }
    result = sort_categories_by_score(result_json)
    assert result == expected

# Float score
def test_sort_categories_float_scores():
    result_json = {
        "user_id": "user125",
        "visit_count": 8,
        "visit_duration": "02:30:00",
        "categories": {
            "A": 10.5,
            "B": 5.75,
            "C": 15.25
        }
    }
    expected = {
        "user_id": "user125",
        "visit_count": 8,
        "visit_duration": "02:30:00",
        "categories": {
            "A": 10.5,
            "C": 15.25,
            "B": 5.75
        }
    }
    result = sort_categories_by_score(result_json)
    assert result == expected

# Mixed Integer and Float Scores
def test_sort_categories_mixed_scores():
    result_json = {
        "user_id": "user126",
        "visit_count": 9,
        "visit_duration": "03:00:00",
        "categories": {
            "A": 120,     # Integer
            "B": 50.5,    # Float
            "C": 100,     # Integer
            "D": 75.75    # Float
        }
    }
    expected = {
        "user_id": "user126",
        "visit_count": 9,
        "visit_duration": "03:00:00",
        "categories": {
            "A": 120,
            "D": 75.75,
            "C": 100,
            "B": 50.5
        }
    }
    result = sort_categories_by_score(result_json)
    assert result == expected

#Empty Categories
def test_sort_categories_empty_categories():
    result_json = {
        "user_id": "user128",
        "visit_count": 11,
        "visit_duration": "05:00:00",
        "categories": {}
    }
    expected = {
        "user_id": "user128",
        "visit_count": 11,
        "visit_duration": "05:00:00",
        "categories": {}
    }
    result = sort_categories_by_score(result_json)
    assert result == expected


#Single Category
def test_sort_categories_single_category():
    result_json = {
        "user_id": "user129",
        "visit_count": 12,
        "visit_duration": "06:00:00",
        "categories": {
            "A": 90
        }
    }
    expected = {
        "user_id": "user129",
        "visit_count": 12,
        "visit_duration": "06:00:00",
        "categories": {
            "A": 90
        }
    }
    result = sort_categories_by_score(result_json)
    assert result == expected

# All Positive Integer
def test_sort_categories_all_positive_integers():
    result_json = {
        "user_id": "user132",
        "visit_count": 5,
        "visit_duration": "01:00:00",
        "categories": {
            "A": 10,
            "B": 50,
            "C": 30
        }
    }
    expected = {
        "user_id": "user132",
        "visit_count": 5,
        "visit_duration": "01:00:00",
        "categories": {
            "B": 50,
            "C": 30,
            "A": 10
        }
    }
    result = sort_categories_by_score(result_json)
    assert result == expected

# Large Number
def test_sort_categories_large_scores():
    result_json = {
        "user_id": "user137",
        "visit_count": 11,
        "visit_duration": "06:00:00",
        "categories": {
            "A": 10000,
            "B": 5000,
            "C": 15000
        }
    }
    expected = {
        "user_id": "user137",
        "visit_count": 11,
        "visit_duration": "06:00:00",
        "categories": {
            "C": 15000,
            "A": 10000,
            "B": 5000
        }
    }
    result = sort_categories_by_score(result_json)
    assert result == expected

# All Same Score
def test_sort_categories_all_scores_same():
    result_json = {
        "user_id": "user138",
        "visit_count": 12,
        "visit_duration": "02:00:00",
        "categories": {
            "A": 50,
            "B": 50,
            "C": 50,
            "D": 50
        }
    }
    # Since all scores are the same, the original order should be preserved.
    expected = {
        "user_id": "user138",
        "visit_count": 12,
        "visit_duration": "02:00:00",
        "categories": {
            "A": 50,
            "B": 50,
            "C": 50,
            "D": 50
        }
    }
    result = sort_categories_by_score(result_json)
    assert result == expected
