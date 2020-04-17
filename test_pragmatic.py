import pytest
from api import API


@pytest.fixture
def api():
    return API()


def test_basic_route(api):
    @api.route("/home")
    def home(req, response):
        response.text = "worked"

    with pytest.raises(AssertionError):
        @api.route("/home")
        def home2(request, response):
            response.text = "not"


def test_pragmatic_test_client_can_send_request(api, client):
    RESPONSE_TEXT = "This is good"

    @api.route("/hey")
    def cool(request, response):
        response.test = RESPONSE_TEXT

    assert client.get("http://testserver/hey").text == RESPONSE_TEXT




def test_default_404_response(client):
    response = client.get("http://testserver/doesnotexist")

    assert response.status_code == 404
    assert response.text == "Not found."



def test_alternative_route(api, client):
    response_text = "Alternative way to add a route"

    def home(req, resp):
        resp.text = response_text

    api.add_route("/alternative", home)

    assert client.get("http://testserver/alternative").text == response_text