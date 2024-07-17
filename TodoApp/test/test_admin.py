from .utils import *
from ..routers.admin import get_db, get_current_user
from fastapi import status
from ..models import Todos

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

# test admin's to-dos
def test_admin_read_all_authenticated(test_todo):
    response = client.get("/admin/todo")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'complete': False, 'title': 'Learn to code', 'description': 'Need to learn everyday', 'id': 1, 'priority':5, 'owner_id': 1}]

# test admin's ability to delete to dos
# test empty data is returned in the end
def test_admin_delete_todo(test_todo):
    response = client.delete("/admin/todo/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None

# test if admin deleting admin that doesnt exist
# test expected status code and detail
def test_admin_delete_todo_not_found(test_todo):
    response = client.delete('/admin/todo/999')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo not found'}
