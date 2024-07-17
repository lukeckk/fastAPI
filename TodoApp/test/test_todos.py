from ..routers.todos import get_db, get_current_user
from fastapi import status
from .utils import *

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_read_all_authenticated(test_todo):
    response = client.get("/")
    #compare the status code
    assert response.status_code == status.HTTP_200_OK
    #compare the returned data in json format
    assert response.json() == [{'title': "Learn to code", 'description': "Need to learn everyday", 'priority': 5, 'complete': False, 'owner_id': 1, 'id' : 1}]


def test_read_one_authenticated(test_todo):
    response = client.get("/todo/1")
    # compare the status code
    assert response.status_code == status.HTTP_200_OK
    # compare the returned data in json format
    assert response.json() == {'title': "Learn to code", 'description': "Need to learn everyday", 'priority': 5, 'complete': False,
         'owner_id': 1, 'id': 1}

# test if user enters to-do id that does not exist
def test_read_one_authenticated_not_found():
    response = client.get("/todo/999")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo not found.'}

# test create to do
def test_create_todo(test_todo):
    request_data={
        'title': 'New Todo!',
        'description': 'new description',
        'priority': 5,
        'complete': False
    }

    response = client.post('/todo/', json=request_data)
    assert response.status_code == 201

# test update to do
def test_update_todo(test_todo):
    request_data={
        'title': 'Updated title',
        'description': 'Updated description',
        'priority': 5,
        'complete': False
    }

    response = client.put('/todo/1', json=request_data)
    assert response.status_code == 204
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model.title == 'Updated title'

# test update to do not found
def test_update_todo_not_found(test_todo):
    request_data={
        'title': 'Updated title',
        'description': 'Updated description',
        'priority': 5,
        'complete': False
    }
    # pass in an id that doesnt exist
    response = client.put('/todo/999', json=request_data)
    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo not found'}

# Test delete
def test_delete_todo(test_todo):
    response = client.delete('/todo/1')
    assert response.status_code == 204
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None

# Test delete to do not found
def test_delete_todo_not_found(test_todo):
    response = client.delete('/todo/999')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo not found'}
