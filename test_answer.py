# tests/test_app.py
import pytest
from flask import Flask, jsonify, request
from flask.testing import FlaskClient
from unittest.mock import patch
import os
from datetime import datetime, timezone
from application.routes.answer_routes import app
from application.services.answer_services import save_answer, get_answer_by_user_id_and_question_id, update_answer, get_all_answers_for_user, delete_answer
from application.utils.connect import firestore_db
from firebase_admin import credentials, firestore

answers_ref = firestore_db.collection('answers')


@pytest.fixture
def client() -> FlaskClient:
    """Set up the Flask test client and test configuration."""
    app.config['TESTING'] = True
    app.config['DEBUG'] = False
    app.config['ENV'] = 'testing'
    return app.test_client()
    
def test_create_answer_success(client: FlaskClient):
    """Test successful creation of an answer with Firestore."""
    user_id = 10
    question_id = 12
    answer_text = "answer test"
    current_time = datetime.now(timezone.utc).isoformat()
    
    score_data = {
        "created_at": "2024-07-23T12:00:00Z",
        "question_id": question_id,
        "score": 95,
        "updated_at": "2024-07-23T12:00:00Z",
        "user_id": user_id
    }
    
    response = client.post(f'/{user_id}/{question_id}/answer', json={
        'answer_text': answer_text,
        'created_at': current_time,
        'question_id': question_id,
        'score': score_data,
        'updated_at': current_time,
        'user_id': user_id
    })

    assert response.status_code == 201
    assert response.json == {'message': 'Answer saved successfully', 'answer_id': f"{user_id}_{question_id}"}

def test_create_answer_missing_score(client: FlaskClient):
    user_id = 10
    question_id = 12
    answer_text = "answer test"
    current_time = datetime.now(timezone.utc).isoformat()

    # Prepare the data with missing 'score' field
    response = client.post(f'/{user_id}/{question_id}/answer', json={
        'answer_text': answer_text,
        'created_at': current_time,
        'updated_at': current_time,
        'question_id': question_id,
        'user_id': user_id
    })

    # Verify the response
    assert response.status_code == 400
    assert response.json == {"message": "Invalid input data"}

def test_get_answer_success(client: FlaskClient):
    """Test successful retrieval of an answer from Firestore."""
    user_id = 10
    question_id = 12
    answer_text = "answer test"
    current_time = datetime.now(timezone.utc).isoformat()
    
    # Set up Firestore with a test answer
    score_data = {
        "created_at": "2024-07-23T12:00:00Z",
        "question_id": question_id,
        "score": 95,
        "updated_at": "2024-07-23T12:00:00Z",
        "user_id": user_id
    }
    
    answer_data = {
        'user_id': user_id,
        'question_id': question_id,
        'answer_text': answer_text,
        'score': score_data,
        'created_at': current_time,
        'updated_at': current_time
    }
    
    # Insert the test answer into Firestore
    answer_id = f"{user_id}_{question_id}"
    answers_ref.document(answer_id).set(answer_data)

    # Make GET request to retrieve the answer
    response = client.get(f'/{user_id}/{question_id}/answer')

    assert response.status_code == 200
    assert response.json == answer_data
     
def test_get_all_answers_for_user_success(client: FlaskClient):
    user_id = 10
    question_ids = [12, 13]
    current_time = datetime.now(timezone.utc).isoformat()

    # Insert test data into Firestore
    for question_id in question_ids:
        answer_text = f"answer for question {question_id}"
        score_data = {
            "created_at": "2024-07-23T12:00:00Z",
            "question_id": question_id,
            "score": 95,
            "updated_at": "2024-07-23T12:00:00Z",
            "user_id": user_id
        }
        answer_data = {
            'user_id': user_id,
            'question_id': question_id,
            'answer_text': answer_text,
            'score': score_data,
            'created_at': current_time,
            'updated_at': current_time
        }
        answer_id = f"{user_id}_{question_id}"
        answers_ref.document(answer_id).set(answer_data)

    # Make GET request to retrieve all answers for the user
    response = client.get(f'/{user_id}/answers')

    # Verify the response
    assert response.status_code == 200
    response_data = response.json
  
def test_get_answer_invalid_id(client: FlaskClient):
    invalid_user_id = 1111
    invalid_question_id = 1111

    # Make GET request with invalid user_id and question_id
    response = client.get(f'/{invalid_user_id}/{invalid_question_id}/answer')

    # Verify the response
    assert response.status_code == 404
    assert response.json == {'message': 'Answer not found'}
  
def test_get_all_answers_for_user_no_answers(client: FlaskClient):
    user_id = 999  # Assuming this user_id does not have any answers

    # Make GET request to retrieve all answers for the user
    response = client.get(f'/{user_id}/answers')

    # Verify the response
    assert response.status_code == 404
    assert response.json == {'message': 'No answers found for this user'}

def test_get_single_answer_not_found(client: FlaskClient):
    user_id = 999  # Assuming this user_id does not exist
    question_id = 999  # Assuming this question_id does not exist

    # Make GET request to retrieve the answer
    response = client.get(f'/{user_id}/{question_id}/answer')

    # Verify the response
    assert response.status_code == 404
    assert response.json == {'message': 'Answer not found'}     
     
def test_update_answer_invalid_data(client: FlaskClient):
    user_id = 11
    question_id = 4

    # Insert the initial answer into Firestore
    initial_answer_data = {
        'user_id': user_id,
        'question_id': question_id,
        'answer_text': "initial answer",
        'score': {
            'created_at': "2024-07-23T12:00:00Z",
            'question_id': question_id,
            'score': 95,
            'updated_at': "2024-07-23T12:00:00Z",
            'user_id': user_id
        },
        'created_at': "2024-07-23T12:00:00Z",
        'updated_at': "2024-07-23T12:00:00Z"
    }
    answer_id = f"{user_id}_{question_id}"
    answers_ref.document(answer_id).set(initial_answer_data)

    # Make PUT request with missing fields
    response = client.put(f'/{user_id}/{question_id}/answer', json={
        'answer_text': "updated answer text",
        # Missing 'created_at', 'score', and 'updated_at'
    })

    # Verify the response
    assert response.status_code == 400
    assert response.json == {'message': 'Missing required fields'}

def test_update_answer_success(client: FlaskClient):
    """Test successful update of an answer in Firestore."""
    user_id = 11
    question_id = 5

    # Existing answer data
    existing_data = {
        "answer_text": "initial answer text",
        "created_at": "2024-07-23T09:13:58.447540+00:00",
        "question_id": question_id,
        "score": {
            "created_at": "2024-07-23T12:00:00Z",
            "question_id": question_id,
            "score": 95,
            "updated_at": "2024-07-23T12:00:00Z",
            "user_id": user_id
        },
        "updated_at": "2024-07-23T09:13:58.447559+00:00",
        "user_id": user_id
    }

    # Insert the initial answer data into Firestore
    answer_id = f"{user_id}_{question_id}"
    answers_ref.document(answer_id).set(existing_data)

    # Updated answer data
    updated_data = {
        "answer_text": "updated answer text",
        "created_at": existing_data["created_at"],  # Preserve existing created_at
        "updated_at": datetime.now(timezone.utc).isoformat(),  # current time for the update
        "score": existing_data["score"]  # assuming score doesn't change
    }

    # Perform the update
    response = client.put(f'/{user_id}/{question_id}/answer', json=updated_data)

    # Debugging Information
    print(f"Response Status Code: {response.status_code}")
    print(f"Response JSON: {response.json}")

    # Verify the update response
    assert response.status_code == 200
    assert response.json == {'message': 'Answer updated successfully'}

    # Verify the updated data in Firestore
    doc_ref = answers_ref.document(answer_id)
    doc = doc_ref.get()

    assert doc.exists
    answer_data = doc.to_dict()

    # Define the expected updated answer data
    expected_answer_data = {
        'user_id': user_id,
        'question_id': question_id,
        'answer_text': updated_data['answer_text'],
        'score': updated_data['score'],
        'created_at': updated_data['created_at'],  # unchanged
        'updated_at': updated_data['updated_at']
    }

    assert answer_data == expected_answer_data
    
def test_delete_answer_success(client: FlaskClient):
    """Test successful deletion of an answer from Firestore."""
    user_id = 10
    question_id = 12

    # Initial answer data
    answer_data = {
        "answer_text": "test answer text",
        "created_at": "2024-07-23T09:13:58.447540+00:00",
        "question_id": question_id,
        "score": {
            "created_at": "2024-07-23T12:00:00Z",
            "question_id": question_id,
            "score": 95,
            "updated_at": "2024-07-23T12:00:00Z",
            "user_id": user_id
        },
        "updated_at": "2024-07-23T09:13:58.447559+00:00",
        "user_id": user_id
    }

    # Document ID
    answer_id = f"{user_id}_{question_id}"

    # Insert the answer into Firestore
    answers_ref.document(answer_id).set(answer_data)

    # Perform the delete operation
    response = client.delete(f'/{user_id}/{question_id}/answer')
    
    # Verify the delete response
    assert response.status_code == 200
    assert response.json == {'message': 'Answer deleted successfully'}
    
def test_delete_answer_not_found(client: FlaskClient):
    """Test deletion attempt for a non-existing answer."""
    user_id = 10
    question_id = 5

    # Perform delete
    response = client.delete(f'/{user_id}/{question_id}/answer')

    # Verify response
    assert response.status_code == 404
    assert response.json == {'message': 'Answer not found'}

def test_delete_answer_invalid_user_id(client: FlaskClient):
    user_id = 999
    question_id = 5
    
    response = client.delete(f'/{user_id}/{question_id}/answer')

    # Verify response
    assert response.status_code == 404
    assert response.json == {'message': 'Answer not found'}

def test_delete_answer_invalid_question_id(client: FlaskClient):
    user_id = 11
    question_id = 999
    
    response = client.delete(f'/{user_id}/{question_id}/answer')

    # Verify response
    assert response.status_code == 404
    assert response.json == {'message': 'Answer not found'}

def test_delete_answer_incorrect_format(client: FlaskClient):
    """Test deletion with incorrect format for IDs."""
    user_id = "11"
    question_id = 6

    response = client.delete(f'/user_id/{question_id}/answer')

    assert response.status_code == 405

