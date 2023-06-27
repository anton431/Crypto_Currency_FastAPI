from conftest import client
from utils import authentication_token_from_username


def test_create_user():
    response = client.post("/users/", json={
        "username": "Gogo",
        "password": "Golang"
    })

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "username": "Gogo",
        "budget": 0
    }


def test_read_users_me():
    headers = authentication_token_from_username(client=client,
                                                 username="Gogo2")
    response = client.get("/users/me/", headers=headers)
    assert response.status_code == 200
    assert response.json() == {'id': 2, 'username': 'Gogo2',
                               'budget': 0}


def test_get_current_tickers():
    headers = authentication_token_from_username(client=client,
                                                 username="Gogo2")
    response = client.post("/currency/", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_all_tickers():
    respose = client.get("/currencies/")
    assert respose.status_code == 200
    assert len(respose.json()) == 0


def test_users_me_update():
    headers = authentication_token_from_username(client=client,
                                                 username="Gogo2")
    json = {
        "username": "Gogo3",
        "password": "Golang"
    }
    response = client.put("/users/me/update", json=json,
                          headers=headers)
    assert response.status_code == 200
    assert response.json()["username"] == "Gogo3"
