from fastapi.testclient import TestClient


def user_authentication_headers(client: TestClient, data) -> dict[str, str]:
    response_token = client.post("/token/", data=data, headers={
        'Content-Type': 'application/x-www-form-urlencoded',
        'accept': 'application/json'})

    auth_token = response_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}

    return headers


def authentication_token_from_username(client: TestClient,
                                       username: str) -> dict[str, str]:
    """
    Register user and return a valid token for the user with given username.
    """
    password = "password"
    data = {
        "username": username,
        "password": password
    }
    client.post("/users/", json=data)

    return user_authentication_headers(client=client, data=data)
