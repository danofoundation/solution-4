# tests/test_score.py
import pytest
from flask import Flask, jsonify, request
from flask.testing import FlaskClient
from unittest.mock import patch
import os
from datetime import datetime, timezone
from application.routes.score_routes import app

from application.utils.connect import firestore_db
from firebase_admin import credentials, firestore
import unittest
import urllib
from datetime import datetime, timezone
answers_ref = firestore_db.collection('answers')

answers_ref = firestore_db.collection('answers')

@pytest.fixture
def client() -> FlaskClient:
    """Set up the Flask test client and test configuration."""
    app.config['TESTING'] = True
    app.config['DEBUG'] = False
    app.config['ENV'] = 'testing'
    return app.test_client()
    

def test_get_score_success(client: FlaskClient):
    user_id = 11
    question_id = 11
   
    response = client.get(f'/{user_id}/{question_id}/score')

     # Debugging Information
    print(f"Response Status Code: {response.status_code}")
    print(f"Response JSON: {response.json}")

    assert response.status_code == 200
     
def test_get_score_invalid_user_id(client: FlaskClient):
    invalid_user_id = 1111
    invalid_question_id = 1

    # Make GET request with invalid user_id and question_id
    response = client.get(f'/{invalid_user_id}/{invalid_question_id}/score')

    # Verify the response
    assert response.status_code == 404
    assert response.json == {'message': 'Answer not found'}
    
def test_get_score_invalid_question_id(client: FlaskClient):
    invalid_user_id = 11
    invalid_question_id = 1111

    # Make GET request with invalid user_id and question_id
    response = client.get(f'/{invalid_user_id}/{invalid_question_id}/score')

    # Verify the response
    assert response.status_code == 404
    assert response.json == {'message': 'Answer not found'}

def test_update_score_success(client: FlaskClient):
    updated_score_data = {
        "answer_text": "test answer",
        "created_at": "2024-07-24T13:45:13.959262+00:00",
        "updated_at": "2024-07-24T13:45:13.959270+00:00",
        "score": {
            "user_id": 10,
            "question_id": 10,
            "score": 10,
            "created_at": "2024-07-24T13:45:13.959272+00:00",
            "updated_at": "2024-07-24T13:45:13.959273+00:00"
        },
        "user_id": 10,
        "question_id": 10
    }
    
    # Make the PUT request to the endpoint
    response = client.put('/10/10/score', json=updated_score_data)
    
    # Assert the response status code
    assert response.status_code == 200
    
    # Assert the response JSON data
    assert response.json == {"message": "Score updated successfully"}
    
def test_update_score_invalid_user(client: FlaskClient):
    updated_score_data = {
        "answer_text": "test answer",
        "created_at": "2024-07-24T13:45:13.959262+00:00",
        "updated_at": "2024-07-24T13:45:13.959270+00:00",
        "score": {
            "user_id": 10,
            "question_id": 10,
            "score": 10,
            "created_at": "2024-07-24T13:45:13.959272+00:00",
            "updated_at": "2024-07-24T13:45:13.959273+00:00"
        },
        "user_id": 10,
        "question_id": 10
    }
    
    # Make the PUT request to the endpoint
    response = client.put('/100/10/score', json=updated_score_data)
    
    # Assert the response status code
    assert response.status_code == 400
    
    # Assert the response JSON data
    assert response.json == {"message": "Answer not found"}
    
def test_update_score_invalid_question(client: FlaskClient):
    updated_score_data = {
        "answer_text": "test answer",
        "created_at": "2024-07-24T13:45:13.959262+00:00",
        "updated_at": "2024-07-24T13:45:13.959270+00:00",
        "score": {
            "user_id": 10,
            "question_id": 100,
            "score": 10,
            "created_at": "2024-07-24T13:45:13.959272+00:00",
            "updated_at": "2024-07-24T13:45:13.959273+00:00"
        },
        "user_id": 10,
        "question_id": 100
    }
    
    # Make the PUT request to the endpoint
    response = client.put('/10/100/score', json=updated_score_data)
    
    # Assert the response status code
    assert response.status_code == 400
    
    # Assert the response JSON data
    assert response.json == {"message": "Answer not found"}