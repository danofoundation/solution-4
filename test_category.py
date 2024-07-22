import pytest
from flask import Flask, jsonify, request, abort
from flask.testing import FlaskClient
from application.routes.category_routes import app
from application.connect import firestore_db
from application.services.category_services import create_category, get_category, get_all_categories, get_category_by_name, update_category_by_name, delete_category_by_name
from unittest.mock import MagicMock, patch
from application.models.category_model import Category
from unittest.mock import patch

db = firestore_db.collection('categories')
@pytest.fixture
def client() -> FlaskClient:
    """Set up the Flask test client and test configuration."""
    app.config['TESTING'] = True
    app.config['DEBUG'] = False
    app.config['ENV'] = 'testing'
    return app.test_client()
    
def test_create_category_success(client: FlaskClient):
    """Test successful creation of a category."""
    response = client.post('/categories', 
                           json={
                               "category_name": "Test-Category",
                               "category_description": "Test-Description"
                           })
    assert response.status_code == 201
    
def test_create_category_missing_fields(client: FlaskClient):
    """Test missing required fields."""
    response = client.post('/categories', 
                           json={'category_name': 'Test-Category'})
    assert response.status_code == 500
    assert "Category description is required." in response.get_data(as_text=True)
    
def test_create_category_invalid_content_type(client: FlaskClient):
    """Test invalid content type."""
    response = client.post('/categories', 
                           data={'category_name': 'Test-Category', 
                                 'category_description': 'Test Description'},
                           content_type='application/x-www-form-urlencoded')
    assert response.status_code == 500
                  
def test_get_all_categories_success(client: FlaskClient, mocker):
    """Test successful retrieval of all categories."""
    response = client.get('/categories')
    assert response.status_code == 200
    
def test_update_category_success(client: FlaskClient):
    category_name = "Test-Category"
    updates = {
        "category_name": "Test-Category",
        "category_description": "Test-Description-UPDATE FROM TEST"
    }

    # Perform the update
    response = client.put(f'/categories/{category_name}', json=updates)
    
    # Verify the update
    assert response.status_code == 200
    
def test_update_non_existent_category(client: FlaskClient):
    """Test updating a non-existent category."""
    updates = {
        "category_description": "Some Description"
    }
    response = client.put('/categories/Non-Existent-Category', json=updates)
    assert response.status_code == 404
    assert response.get_json()['message'] == 'Category not found'
    
def test_update_category_invalid_data(client: FlaskClient):
    # Create the category
    client.post('/categories', json={
        'category_name': 'Test-Category',
        'category_description': 'Initial Description'
    })

    # Attempt to update with invalid data
    response = client.put('/categories/Test-Category', json={
        'category_description': ''  # Invalid empty description
    })

    assert response.status_code == 400
    

    
def test_update_category_partial_update(client: FlaskClient):
    # Create the category
    client.post('/categories', json={
        'category_name': 'Test-Category',
        'category_description': 'Initial Description'
    })

    # Partial update
    response = client.put('/categories/Test-Category', json={
        'category_description': 'Partially Updated Description'
    })

    assert response.status_code == 200
    response_data = response.get_json()
    assert response_data['category_name'] == 'Test-Category'
    assert response_data['category_description'] == 'Partially Updated Description'

    
def test_delete_category_not_found(client: FlaskClient):
    """Test deletion of a category that does not exist."""
    # Mock the delete_category_by_name function to simulate category not found
    with patch('application.services.category_services.delete_category_by_name') as mock_delete_category:
        mock_delete_category.side_effect = ValueError("Category not found")
        response = client.delete('/categories/Non-Existent-Category')
        
        # Check that the response status code is 404 Not Found
        assert response.status_code == 404
        
        # Check the response data
        response_data = response.get_json()
        assert response_data['message'] == 'Category not found'
             
def test_delete_category_success(client: FlaskClient):
    """Test successful deletion of a category by name."""
    
    # Mock the create_category function to simulate adding a category
    with patch('application.services.category_services.create_category') as mock_create_category:
        mock_create_category.return_value = True
        client.post('/categories', json={
            'category_name': 'Test-Category',
            'category_description': 'Test-Description'
        })
    
    # Mock the delete_category_by_name function to simulate successful deletion
    with patch('application.services.category_services.delete_category_by_name') as mock_delete_category:
        mock_delete_category.return_value = True
        
        # Make the DELETE request to delete the category
        response = client.delete('/categories/Test-Category')
        
        # Check that the response status code is 200 OK
        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
        
        # Check the response data
        response_data = response.get_json()
        assert response_data['message'] == 'Category deleted successfully', \
            f"Expected message 'Category deleted successfully', but got {response_data['message']}"
   
