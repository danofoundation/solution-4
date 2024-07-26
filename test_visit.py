import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from application.utils.connect import firestore_db
import pytest
from flask import Flask, jsonify, request
from flask.testing import FlaskClient
from unittest.mock import patch
import os
from datetime import datetime, timezone
from application.services import VisitService
from application.routes.visit_routes import app
visits_ref = firestore_db.collection('visits')
@pytest.fixture
def client() -> FlaskClient:
    """Set up the Flask test client and test configuration."""
    app.config['TESTING'] = True
    app.config['DEBUG'] = False
    app.config['ENV'] = 'testing'
    return app.test_client()
def test_submit_visit_success(client: FlaskClient):
    payload = {
        "user_id": "user123",
        "visit_id": "visit456",
        "visit_count": 5,
        "visit_duration": "00:15:30",
        "responses": {
            "q1": {
                "question_id": "q1",
                "category": "c1",
                "score": 75
            },
            "q2": {
                "question_id": "q2",
                "category": "c2",
                "score": 85
            }
        },
        "additional_comment": "Great experience"
    }

    # Send POST request
    response = client.post('/submit_visit', json=payload)

    # Assert the response status code and data
    assert response.status_code == 201
    assert response.json == {"status": "success"}

def test_submit_visit_missing_field(client: FlaskClient):
    payload = {
        "user_id": 1,
        "visit_id": "v123",
        "visit_duration": "01:30:00",
        "responses": {"q1": "answer1"}
    }
    response = client.post('/submit_visit', json=payload)
    assert response.status_code == 400
    
def test_submit_visit_invalid_data_type(client: FlaskClient):
    payload = {
        "user_id": "one",  # Should be an integer
        "visit_id": "v123",
        "visit_count": 10,
        "visit_duration": "01:30:00",
        "responses": {"q1": "answer1"}
    }
    response = client.post('/submit_visit', json=payload)
    assert response.status_code == 400
    
def test_get_visits_success(client: FlaskClient):
    user_id = 1
    response = client.get(f'/{user_id}/visits')
    assert response.status_code == 200
    
def test_get_visits_invalid_user_id(client: FlaskClient):
    user_id = 999  
    response = client.get(f'/{user_id}/visits')
    assert response.status_code == 200
    assert response.json == []

def test_get_visits_empty_user_id(client: FlaskClient):
    response = client.get('///visits') 
    assert response.status_code == 404
    
def test_get_visits_non_numeric_user_id(client: FlaskClient):
    non_numeric_user_id = 'absac123'
    
    response = client.get(f'/{non_numeric_user_id}/visits')
    
    assert response.status_code == 200
   
def test_delete_visit_invalid_visit_id(client: FlaskClient):
    user_id = 1
    invalid_visit_id = 'invalid'
    
    response = client.delete(f'/visits/{invalid_visit_id}')
    assert response.status_code == 404  
    assert "error" in response.json
    
def test_delete_visit_invalid_user_id(client: FlaskClient):
    invalid_user_id = 'invalid'
    visit_id = 'v123'
    
    response = client.delete(f'/{invalid_user_id}/visits')
    assert response.status_code == 404  
    assert "error" in response.json
    
def test_delete_visit_success(client: FlaskClient):
    user_id = 1
    visit_id = '1'  
    response = client.get(f'/{user_id}/visits')
    assert response.status_code == 200
    
