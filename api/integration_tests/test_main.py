import os

import requests


# get LAMBDA_URL from environment variable
LAMBDA_URL = os.environ.get("LAMBDA_URL")


def test_main():
    visits = get_response()
    assert int(visits) > 0

    # make sure the counter is incrementing
    visits2 = get_response()
    assert int(visits2) == int(visits) + 1


def get_response():
    req = requests.get(LAMBDA_URL)
    assert req.status_code == 200
    data = req.json()
    assert "visits" in data
    visit_data = data["visits"]
    assert "visits" in visit_data
    assert "timestamp" in data
    visits = visit_data["visits"]
    return visits
