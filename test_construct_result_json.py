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

# Test data
valid_data = {
    "user_id": "user123",
    "visit_count": 2,
    "visit_duration": "01:30:00",
    "responses": {
        "q1": {"category": "A", "score": 10},
        "q2": {"category": "B", "score": 5},
        "q3": {"category": "A", "score": 7}
    }
}

invalid_data = {
    "user_id": "user123",
    "visit_count": 0,  # Invalid visit count
    "visit_duration": "90:00",  # Invalid time format
    "responses": {
        "q1": {"category": "A", "score": 10},
        "q2": {"category": "B", "score": 5},
        "q3": {"category": "A", "score": -7}  # Invalid score
    }
}

# Invalid user_id Type
def test_construct_result_json_invalid_user_id_type():
    data = {
        "user_id": 12345,  # Invalid type
        "visit_count": 10,
        "visit_duration": "00:30:00",
        "responses": {
            '1': {'category': 'J', 'score': 5}
        }
    }
    expected = {
        "user_id": 12345,
        "visit_count": 10,
        "visit_duration": "00:30:00",
        "categories": {'J': 5}
    }
    result = construct_result_json(data)
    assert result == expected

# Invalid visit_count Type
def test_construct_result_json_invalid_visit_count_type():
    data = {
        "user_id": "user505",
        "visit_count": "ten",  # Invalid type
        "visit_duration": "00:45:00",
        "responses": {
            '1': {'category': 'K', 'score': 15}
        }
    }
    expected = {
        "user_id": "user505",
        "visit_count": "ten",
        "visit_duration": "00:45:00",
        "categories": {'K': 15}
    }
    result = construct_result_json(data)
    assert result == expected


# Invalid visit_duration Format
def test_construct_result_json_invalid_visit_duration_format():
    data = {
        "user_id": "user606",
        "visit_count": 4,
        "visit_duration": "1:60:60",  # Invalid time format
        "responses": {
            '1': {'category': 'L', 'score': 20}
        }
    }
    expected = {
        "user_id": "user606",
        "visit_count": 4,
        "visit_duration": "1:60:60",
        "categories": {'L': 20}
    }
    result = construct_result_json(data)
    assert result == expected

# Invalid responses structure
def test_construct_result_json_invalid_responses_structure():
    data = {
        "user_id": "user123",
        "visit_count": 5,
        "visit_duration": "01:30:00",
        "responses": {
            '1': {'category': 'A', 'score': 'high'},  # Invalid score
            '2': {'category': 'B', 'score': -10},    # Valid score but negative
            '3': {'score': 15},                      # Missing 'category'
            '4': {'category': 'A', 'score': 20}      # Valid entry
        }
    }
    
    expected = {
        "user_id": "user123",
        "visit_count": 5,
        "visit_duration": "01:30:00",
        "categories": {'A': 20, 'B': -10}  # 'A' gets 20, 'B' gets -10; '3' is ignored due to missing 'category'
    }
    
    result = construct_result_json(data)
    
    # Print or log the results for debugging
    print("Expected:", expected)
    print("Result:", result)
    
    assert result == expected

# Missing 'responses' field
def test_construct_result_json_missing_responses_field():
    data = {
        "user_id": "user808",
        "visit_count": 6,
        "visit_duration": "01:15:00"
        # Missing 'responses' field
    }
    expected = {
        "user_id": "user808",
        "visit_count": 6,
        "visit_duration": "01:15:00",
        "categories": {}  # Empty categories
    }
    result = construct_result_json(data)
    assert result == expected
    
# Empty user id
def test_construct_result_json_empty_user_id():
    data = {
        "user_id": "",
        "visit_count": 7,
        "visit_duration": "01:00:00",
        "responses": {
            '1': {'category': 'O', 'score': 25}
        }
    }
    expected = {
        "user_id": "",
        "visit_count": 7,
        "visit_duration": "01:00:00",
        "categories": {'O': 25}
    }
    result = construct_result_json(data)
    assert result == expected
    
# Negative visit count
def test_construct_result_json_negative_visit_count():
    data = {
        "user_id": "user909",
        "visit_count": -5,  # Invalid value
        "visit_duration": "01:30:00",
        "responses": {
            '1': {'category': 'P', 'score': 30}
        }
    }
    expected = {
        "user_id": "user909",
        "visit_count": -5,
        "visit_duration": "01:30:00",
        "categories": {'P': 30}
    }
    result = construct_result_json(data)
    assert result == expected
    


