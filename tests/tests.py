from conftest import client


def test_create_user():
    response = client.post("/users/", json={
        "username": "Gogo12",
        "password": "Gogo12"
    })

    assert response.status_code == 200
