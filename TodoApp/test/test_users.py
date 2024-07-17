from .utils import *
from ..routers.users import get_current_user,get_db
from fastapi import status

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

# test the get_user method
def test_return_user(test_user):
    response = client.get("/user")
    assert response.status_code == status.HTTP_200_OK
    # checking separately below because cant compare hashedpassword
    assert response.json()['username'] == "test"
    assert response.json()['email'] == "test@gmail.com"
    assert response.json()['first_name'] == "test"
    assert response.json()['last_name'] == "test"
    assert response.json()['role'] == "admin"
    assert response.json()['phone_number'] == "123123123"


# test expected status code for successful password change
def test_change_password_success(test_user):
    response = client.put("/user/password", json={'password': "test", "new_password": "newpassword"})
    assert response.status_code == status.HTTP_204_NO_CONTENT

# test expected status code when invalid current password is returned
def test_change_password_invalid_current_password(test_user):
    response = client.put("/user/password", json={'password': "blahblahblah", "new_password": "newpassword"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Current password is invalid'}

# test successful phone number change
def test_change_phone_number_success(test_user):
    response = client.put("/user/phonenumber/22222")
    assert response.status_code == status.HTTP_204_NO_CONTENT

