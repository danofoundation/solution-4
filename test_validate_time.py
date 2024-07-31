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

#  Valid Time Strings
def test_valid_time_strings():
    assert validate_time_format("00:00:00") == True, "Valid Time Test Case 1 Failed"
    assert validate_time_format("01:01:01") == True, "Valid Time Test Case 2 Failed"
    assert validate_time_format("12:30:45") == True, "Valid Time Test Case 3 Failed"
    assert validate_time_format("23:59:59") == True, "Valid Time Test Case 4 Failed"
    assert validate_time_format("11:59:59") == True, "Valid Time Test Case 5 Failed"
    print("All valid time test cases passed!")

#  Invalid Time Strings (Format Issues)
def test_invalid_time_format_issues():
    assert validate_time_format("24:00:00") == False, "Invalid Format Test Case 1 Failed"  # Invalid hour
    assert validate_time_format("12:60:00") == False, "Invalid Format Test Case 2 Failed"  # Invalid minute
    assert validate_time_format("12:30:60") == False, "Invalid Format Test Case 3 Failed"  # Invalid second
    assert validate_time_format("12:30") == False, "Invalid Format Test Case 4 Failed"     # Missing seconds
    assert validate_time_format("12:30:45:00") == False, "Invalid Format Test Case 5 Failed"  # Extra digits
    print("All invalid time format issue test cases passed!")


#Invalid Time Strings (Extra Characters or Spaces)
def test_invalid_time_extra_characters_spaces():
    assert validate_time_format(" 12:30:45 ") == False, "Extra Spaces Test Case 1 Failed"  # Extra spaces
    assert validate_time_format("12:30:45abc") == False, "Extra Characters Test Case 2 Failed"  # Extra characters
    assert validate_time_format("12:30:45,") == False, "Extra Characters Test Case 3 Failed"  # Extra punctuation
    print("All invalid time extra characters or spaces test cases passed!")


#Empty Strings and Non-Time Strings
def test_empty_and_non_time_strings():
    assert validate_time_format("") == False, "Empty String Test Case 1 Failed"  # Empty string
    assert validate_time_format("abc:def:ghi") == False, "Non-Numeric Test Case 2 Failed"  # Non-numeric input
    assert validate_time_format("123456") == False, "Incorrect Format Test Case 3 Failed"  # Incorrect format
    assert validate_time_format("12:30:45:67") == False, "Too Many Digits Test Case 4 Failed"  # Extra digits
    print("All empty and non-time string test cases passed!")
