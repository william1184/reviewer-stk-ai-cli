def check_mock_is_running():
    import requests

    try:

        url = "http://localhost:3001/zup/oidc/oauth/token"

        payload = "client_id=TESTE&grant_type=client_credentials&client_secret=TESTE"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        response = requests.request("POST", url, data=payload, headers=headers)

        return response.ok
    except requests.exceptions.ConnectionError:
        return False


if __name__ == "__main__":
    print(check_mock_is_running())
