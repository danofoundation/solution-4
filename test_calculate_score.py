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
#!SECTION - calculate_total_scores tests
# Calculate score success
def test_calculate_total_scores():
    responses = valid_data["responses"]
    total_scores = calculate_total_scores(responses)
    assert total_scores == {"A": 17, "B": 5}

# Multiple Responses, Single Category
def test_calculate_total_scores_single_category():
    responses = {
        '1': {'category': 'A', 'score': 10},
        '2': {'category': 'A', 'score': 20},
        '3': {'category': 'A', 'score': 30}
    }
    expected = {'A': 60}
    result = calculate_total_scores(responses)
    assert result == expected

# Multiple Responses, Multiple Categories
def test_calculate_total_scores_multiple_categories():
    responses = {
        '1': {'category': 'A', 'score': 10},
        '2': {'category': 'B', 'score': 20},
        '3': {'category': 'A', 'score': 30},
        '4': {'category': 'B', 'score': 10}
    }
    expected = {'A': 40, 'B': 30}
    result = calculate_total_scores(responses)
    assert result == expected

# Edge Case: Empty Responses
def test_calculate_total_scores_empty():
    responses = {}
    expected = {}
    result = calculate_total_scores(responses)
    assert result == expected

# Edge Case: Single Response
def test_calculate_total_scores_single_response():
    responses = {
        '1': {'category': 'A', 'score': 15}
    }
    expected = {'A': 15}
    result = calculate_total_scores(responses)
    assert result == expected

# Edge Case: Responses with Zero Scores
def test_calculate_total_scores_zero_scores():
    responses = {
        '1': {'category': 'A', 'score': 0},
        '2': {'category': 'B', 'score': 0}
    }
    expected = {'A': 0, 'B': 0}
    result = calculate_total_scores(responses)
    assert result == expected

# Edge Case: Negative Scores
def test_calculate_total_scores_negative_scores():
    responses = {
        '1': {'category': 'A', 'score': -5},
        '2': {'category': 'A', 'score': -10},
        '3': {'category': 'B', 'score': 5}
    }
    expected = {'A': -15, 'B': 5}
    result = calculate_total_scores(responses)
    assert result == expected

# Test case for non-integer scores
def test_calculate_total_scores_non_integer_scores():
    responses = {
        '1': {'category': 'A', 'score': 10.5},
        '2': {'category': 'A', 'score': '20.3'},  # String that can be converted to float
        '3': {'category': 'B', 'score': 5}
    }
    expected = {'A': 30, 'B': 5}
    result = calculate_total_scores(responses)
    assert result == expected

# Test case for mixed data types
def test_calculate_total_scores_mixed_data_types():
    responses = {
        '1': {'category': 'A', 'score': 'high'},  # Non-numeric string
        '2': {'category': 'A', 'score': 20},
        '3': {'category': 'B', 'score': 15.5},  # Float
        '4': {'category': 'B', 'score': '10'}  # String that can be converted to integer
    }
    expected = {'A': 20, 'B': 25}
    result = calculate_total_scores(responses)
    assert result == expected

# Test case for edge case with empty responses
def test_calculate_total_scores_empty_responses():
    responses = {}
    expected = {}
    result = calculate_total_scores(responses)
    assert result == expected


# Edge Case: Missing Keys
def test_calculate_total_scores_missing_keys():
    responses = {
        '1': {'score': 10},  # Missing 'category'
        '2': {'category': 'A', 'score': 20}
    }
    expected = {'A': 20}
    result = calculate_total_scores(responses)
    assert result == expected

# Large Numbers
def test_calculate_total_scores_large_numbers():
    responses = {
        '1': {'category': 'A', 'score': 1_000_000},
        '2': {'category': 'A', 'score': 2_000_000},
        '3': {'category': 'B', 'score': 3_000_000}
    }
    expected = {'A': 3_000_000, 'B': 3_000_000}
    result = calculate_total_scores(responses)
    assert result == expected

