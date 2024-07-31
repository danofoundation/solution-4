import pytest
import aiohttp
import asyncio
from aioresponses import aioresponses
from application.tasks.questionnaire_tasks import fetch_with_retries  
from unittest.mock import patch, ANY
@pytest.mark.asyncio
async def test_fetch_with_retries_success():
    url = 'http://test.com'
    mock_response = {'key': 'value'}
    
    with aioresponses() as m:
        m.get(url, payload=mock_response, status=200)
        async with aiohttp.ClientSession() as session:
            response = await fetch_with_retries(url, session)
            assert response == mock_response

@pytest.mark.asyncio
async def test_fetch_with_retries_http_error():
    url = 'http://test.com'
    
    with aioresponses() as m:
        m.get(url, status=500)  # Mocking HTTP 500 error
        async with aiohttp.ClientSession() as session:
            with pytest.raises(Exception, match='Failed to fetch data from'):
                await fetch_with_retries(url, session)
                
                
@pytest.mark.asyncio
async def test_fetch_with_retries_connection_error():
    url = 'http://test.com'
    
    with patch('aiohttp.ClientSession.get', side_effect=aiohttp.ClientConnectionError):
        async with aiohttp.ClientSession() as session:
            with pytest.raises(Exception, match='Failed to fetch data from'):
                await fetch_with_retries(url, session)
                

@pytest.mark.asyncio
async def test_fetch_with_retries_timeout_error():
    url = 'http://test.com'
    
    with patch('aiohttp.ClientSession.get', side_effect=asyncio.TimeoutError):
        async with aiohttp.ClientSession() as session:
            with pytest.raises(Exception, match='Failed to fetch data from'):
                await fetch_with_retries(url, session)

@pytest.mark.asyncio
async def test_fetch_with_retries_timeout():
    url = 'http://test.com'

    async def delayed_response(*args, **kwargs):
        await asyncio.sleep(2)  # Simulate delay causing a timeout
        return aiohttp.ClientResponse()

    with aioresponses() as m:
        m.get(url, callback=delayed_response)
        with patch('asyncio.sleep') as mock_sleep:
            async with aiohttp.ClientSession() as session:
                with pytest.raises(Exception, match='Failed to fetch data from'):
                    await fetch_with_retries(url, session, max_retries=1, timeout=1)



@pytest.mark.asyncio
async def test_fetch_with_retries_exponential_backoff():
    url = 'http://test.com'
    attempt_delay = 1
    max_attempts = 3
    expected_delays = [attempt_delay * 2**i for i in range(max_attempts)]
    
    with aioresponses() as m:
        m.get(url, status=500)  # Always fail
        with patch('asyncio.sleep') as mock_sleep:
            async with aiohttp.ClientSession() as session:
                with pytest.raises(Exception, match='Failed to fetch data from'):
                    await fetch_with_retries(url, session, max_retries=max_attempts)
            
            # Check if the sleep was called with the correct delays
            calls = mock_sleep.call_args_list
            actual_delays = [call[0][0] for call in calls]
            
            for i, expected_delay in enumerate(expected_delays):
                # Allow a margin of error to account for the added randomness
                assert abs(actual_delays[i] - expected_delay) < 2  # Increased margin of error




@pytest.mark.asyncio
async def test_fetch_with_retries_invalid_url():
    url = 'http://invalid-url'
    
    with aioresponses() as m:
        m.get(url, status=404)  # Mocking HTTP 404 error
        async with aiohttp.ClientSession() as session:
            with pytest.raises(Exception, match='Failed to fetch data from'):
                await fetch_with_retries(url, session)
                
                
@pytest.mark.asyncio
async def test_fetch_with_retries_success_first_attempt():
    url = 'http://test.com'
    
    with aioresponses() as m:
        m.get(url, status=200, body='{"key": "value"}')  # Success on the first attempt
        async with aiohttp.ClientSession() as session:
            result = await fetch_with_retries(url, session)
            assert result == {"key": "value"}  # Check that the expected result is returned
            
        
@pytest.mark.asyncio
async def test_fetch_with_retries_all_failures():
    url = 'http://test.com'
    max_attempts = 3

    with aioresponses() as m:
        m.get(url, status=500)  # Always fail
        async with aiohttp.ClientSession() as session:
            with pytest.raises(Exception, match='Failed to fetch data from'):
                await fetch_with_retries(url, session, max_retries=max_attempts)
                
