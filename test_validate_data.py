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

#Valid Data
def test_validate_data_valid():
    data = {
        "user_id": "user123",
        "visit_count": 5,
        "visit_duration": "01:30:00",
        "categories": {
            "A": 10,
            "B": 5
        }
    }
    expected = {"status": "success", "messages": ["Data is valid."]}
    assert validate_data(data) == expected


# Missing user_id
def test_validate_data_missing_user_id():
    data = {
        "visit_count": 5,
        "visit_duration": "01:30:00",
        "categories": {
            "A": 10,
            "B": 5
        }
    }
    expected = {"status": "error", "messages": ["Missing or invalid 'user_id'."]}
    assert validate_data(data) == expected

#Invalid user_id Type
def test_validate_data_invalid_user_id_type():
    data = {
        "user_id": 12345,  # Invalid type
        "visit_count": 5,
        "visit_duration": "01:30:00",
        "categories": {
            "A": 10,
            "B": 5
        }
    }
    expected = {"status": "error", "messages": ["Missing or invalid 'user_id'."]}
    assert validate_data(data) == expected

#Missing visit_count
def test_validate_data_missing_visit_count():
    data = {
        "user_id": "user123",
        "visit_duration": "01:30:00",
        "categories": {
            "A": 10,
            "B": 5
        }
    }
    expected = {"status": "error", "messages": ["Missing or invalid 'visit_count'. Must be a positive integer."]}
    assert validate_data(data) == expected

#Invalid visit_count Type
def test_validate_data_invalid_visit_count_type():
    data = {
        "user_id": "user123",
        "visit_count": "five",  # Invalid type
        "visit_duration": "01:30:00",
        "categories": {
            "A": 10,
            "B": 5
        }
    }
    expected = {"status": "error", "messages": ["Missing or invalid 'visit_count'. Must be a positive integer."]}
    assert validate_data(data) == expected

#Invalid visit_count Value
def test_validate_data_invalid_visit_count_value():
    data = {
        "user_id": "user123",
        "visit_count": -5,  # Invalid value
        "visit_duration": "01:30:00",
        "categories": {
            "A": 10,
            "B": 5
        }
    }
    expected = {"status": "error", "messages": ["Missing or invalid 'visit_count'. Must be a positive integer."]}
    assert validate_data(data) == expected

#Invalid visit_duration Format
def test_validate_data_invalid_visit_duration_format():
    data = {
        "user_id": "user123",
        "visit_count": 5,
        "visit_duration": "1:30",  # Invalid format
        "categories": {
            "A": 10,
            "B": 5
        }
    }
    expected = {"status": "error", "messages": ["Invalid 'visit_duration'. Must be in HH:MM:SS format."]}
    assert validate_data(data) == expected

#Missing categories
def test_validate_data_missing_categories():
    data = {
        "user_id": "user123",
        "visit_count": 5,
        "visit_duration": "01:30:00"
    }
    expected = {"status": "error", "messages": ["Missing or invalid 'categories'. Must be a dictionary."]}
    assert validate_data(data) == expected

#Invalid categories Type
def test_validate_data_invalid_categories_type():
    data = {
        "user_id": "user123",
        "visit_count": 5,
        "visit_duration": "01:30:00",
        "categories": ["A", "B"]  # Invalid type
    }
    expected = {"status": "error", "messages": ["Missing or invalid 'categories'. Must be a dictionary."]}
    assert validate_data(data) == expected


#Invalid categories Values
def test_validate_data_invalid_categories_values():
    data = {
        "user_id": "user123",
        "visit_count": 5,
        "visit_duration": "01:30:00",
        "categories": {
            "A": -10,  # Invalid score (negative)
            "B": "five"  # Invalid score (not an integer)
        }
    }
    expected = {"status": "error", "messages": [
        "Invalid score for category 'A'. Must be a non-negative integer.",
        "Invalid score for category 'B'. Must be a non-negative integer."
    ]}
    assert validate_data(data) == expected

#Multiple Errors
def test_validate_data_multiple_errors():
    data = {
        "user_id": 12345,  # Invalid type
        "visit_count": "five",  # Invalid type
        "visit_duration": "1:30",  # Invalid format
        "categories": ["A", "B"]  # Invalid type
    }
    expected = {"status": "error", "messages": [
        "Missing or invalid 'user_id'.",
        "Missing or invalid 'visit_count'. Must be a positive integer.",
        "Invalid 'visit_duration'. Must be in HH:MM:SS format.",
        "Missing or invalid 'categories'. Must be a dictionary."
    ]}
    assert validate_data(data) == expected
