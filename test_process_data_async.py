import pytest
import aiohttp
from aioresponses import aioresponses
from unittest.mock import patch, AsyncMock
from application.tasks.questionnaire_tasks import process_data_async, fetch_with_retries, send_to_chatbot
import json

@pytest.mark.asyncio
async def test_process_data_async_success():
    user_id = 'user123'
    visit_id = 'visit456'
    url = f"http://127.0.0.1:5000/{user_id}/visits/{visit_id}"
    visit_data = {"key": "value"}
    processed_data = {"processed_key": "processed_value"}

    with aioresponses() as m:
        # Mock the response for the URL with a status of 200 and JSON body
        m.get(url, status=200, body=json.dumps(visit_data))

        # Patch the process_data function and send_to_chatbot function
        with patch('application.tasks.questionnaire_tasks.process_data', return_value=processed_data) as mock_process_data:
            with patch('application.tasks.questionnaire_tasks.send_to_chatbot', new_callable=AsyncMock) as mock_send_to_chatbot:
                await process_data_async(user_id, visit_id)

                # Check if process_data was called with the correct data
                mock_process_data.assert_called_once_with(visit_data)

                # Check if send_to_chatbot was called with the processed data
                mock_send_to_chatbot.assert_called_once_with(processed_data)


@pytest.mark.asyncio
async def test_process_data_async_success_no_error():
    user_id = 'user123'
    visit_id = 'visit456'
    url = f"http://127.0.0.1:5000/{user_id}/visits/{visit_id}"
    visit_data = {"key": "value"}
    processed_data = {"processed_key": "processed_value"}

    with aioresponses() as m:
        m.get(url, status=200, body=json.dumps(visit_data))  # Mock successful fetch

        with patch('application.tasks.questionnaire_tasks.process_data', return_value=processed_data):
            with patch('application.tasks.questionnaire_tasks.send_to_chatbot', new_callable=AsyncMock) as mock_send_to_chatbot:
                with patch('application.tasks.questionnaire_tasks.app.logger.error') as mock_logger_error:
                    await process_data_async(user_id, visit_id)

                    # Ensure no error is logged
                    mock_logger_error.assert_not_called()


@pytest.mark.asyncio
async def test_process_data_async_fetch_failure():
    user_id = 'user123'
    visit_id = 'visit456'
    url = f"http://127.0.0.1:5000/{user_id}/visits/{visit_id}"

    with aioresponses() as m:
        # Simulate a failure response (e.g., status code 500)
        m.get(url, status=500)

        with patch('application.tasks.questionnaire_tasks.process_data') as mock_process_data:
            with patch('application.tasks.questionnaire_tasks.send_to_chatbot', new_callable=AsyncMock) as mock_send_to_chatbot:
                # Patch the logger to check the messages
                with patch('application.tasks.questionnaire_tasks.app.logger.error') as mock_logger_error:
                    await process_data_async(user_id, visit_id)
                    
                    # Assert that the final failure message was logged
                    expected_failure_message = (
                        'Processing failed: Failed to fetch data from http://127.0.0.1:5000/user123/visits/visit456 after 5 retries'
                    )
                    assert any(
                        call[0][0] == expected_failure_message
                        for call in mock_logger_error.call_args_list
                    ), f"Expected final failure message was not logged. Actual calls: {mock_logger_error.call_args_list}"


@pytest.mark.asyncio
async def test_process_data_async_process_data_failure():
    user_id = 'user123'
    visit_id = 'visit456'
    url = f"http://127.0.0.1:5000/{user_id}/visits/{visit_id}"
    visit_data = {"key": "value"}

    with aioresponses() as m:
        m.get(url, status=200, body=json.dumps(visit_data))  # Mock successful fetch

        with patch('application.tasks.questionnaire_tasks.process_data', side_effect=Exception("Processing error")) as mock_process_data:
            with patch('application.tasks.questionnaire_tasks.send_to_chatbot', new_callable=AsyncMock) as mock_send_to_chatbot:
                with patch('application.tasks.questionnaire_tasks.app.logger.error') as mock_logger_error:
                    await process_data_async(user_id, visit_id)
                    
                    # Ensure the exception is logged properly
                    mock_logger_error.assert_called_once_with('Processing failed: Processing error')
                    
                    
                    
@pytest.mark.asyncio
async def test_process_data_async_send_to_chatbot_failure():
    user_id = 'user123'
    visit_id = 'visit456'
    url = f"http://127.0.0.1:5000/{user_id}/visits/{visit_id}"
    visit_data = {"key": "value"}
    processed_data = {"processed_key": "processed_value"}

    with aioresponses() as m:
        m.get(url, status=200, body=json.dumps(visit_data))  # Mock successful fetch

        with patch('application.tasks.questionnaire_tasks.process_data', return_value=processed_data):
            with patch('application.tasks.questionnaire_tasks.send_to_chatbot', side_effect=Exception("Sending error")) as mock_send_to_chatbot:
                with patch('application.tasks.questionnaire_tasks.app.logger.error') as mock_logger_error:
                    await process_data_async(user_id, visit_id)
                    
                    # Ensure the exception is logged properly
                    mock_logger_error.assert_called_once_with('Processing failed: Sending error')                    
                    
                    
@pytest.mark.asyncio
async def test_process_data_async_logging_errors():
    user_id = 'user123'
    visit_id = 'visit456'
    url = f"http://127.0.0.1:5000/{user_id}/visits/{visit_id}"

    with aioresponses() as m:
        # Simulate multiple error types to test logging
        m.get(url, status=500)
        
        with patch('application.tasks.questionnaire_tasks.process_data') as mock_process_data:
            with patch('application.tasks.questionnaire_tasks.send_to_chatbot', new_callable=AsyncMock) as mock_send_to_chatbot:
                with patch('application.tasks.questionnaire_tasks.app.logger.error') as mock_logger_error:
                    await process_data_async(user_id, visit_id)
                    
                    # Check for error messages related to the fetch retries and final failure
                    assert any(
                        "HTTP error on attempt" in call[0][0] or
                        "Connection err0000or on attempt" in call[0][0] or
                        "Failed to fetch data from" in call[0][0]
                        for call in mock_logger_error.call_args_list
                    ), f"Expected error messages were not logged. Actual calls: {mock_logger_error.call_args_list}"


