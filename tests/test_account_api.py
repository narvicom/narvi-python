from unittest.mock import patch, mock_open

import pytest

from narvi.main import NarviAccountClient

PRIVATE_KEY = """-----BEGIN EC PRIVATE KEY-----
MHcCAQEEIKE0CvV8msB6nqufE4rwOLAHKISAxKEvVnSUHGf0rYkVoAoGCCqGSM49
AwEHoUQDQgAEY4bb/T0oOCX/E7EdwZYFzXdNu2J/VQpPFNTAyhX6suMINcnepXMf
J+2o4N7O00tNUOCUfPclxdqqqgwcx/H5mA==
-----END EC PRIVATE KEY-----"""


class TestAccountAPi(object):
    @pytest.fixture
    def http_client(self):
        with patch("builtins.open", mock_open(read_data=PRIVATE_KEY.encode())):
            return NarviAccountClient(
                api_key_id="NYZRLPY8PS02GWEB",
                private_key_file_path='/tmp/narvi_priv.pem'
            )

    @pytest.fixture
    def transaction_item(self):
        return {
            'pid': '7FMQ149XK2XDIK3K',
            'account_pid': 'KFGKJ5L27ASGTZAO',
            'amount': 100,
            'fee': 2,
            'currency': 'EUR',
            'added': '1699203119.059233',
            'recipient': {
                'number': 'FI8379600186405354',
                'name': 'John Doe',
                'address': None,
                'city': None,
                'zip_code': None,
                'country': None
            },
            'remittance_information': {
                'ustrd': 'Test transfer'
            },
            'source': 'ACCOUNT_API',
            'kind': 'DEBIT',
            'status': 'PENDING'
        }

    def test_list_account(self, requests_mock, http_client):
        mocker = requests_mock.register_uri(
            "GET",
            "/rest/v1.0/account/list",
            status_code=200,
            json={'next': None, 'previous': None, 'results': [
                {'pid': 'KFGKJ5L27ASGTZAO', 'number': 'FI2279600000000000', 'role': 'ADMIN', 'balance': 2546,
                 'currency': 'EUR', 'name': 'aloha', 'kind': 'PRIVATE'},
                {'pid': 'ODZ5SP5YO9NZCDGU', 'number': 'FI4279634267890562', 'role': 'ADMIN', 'balance': 9900790,
                 'currency': 'EUR', 'name': 'Name 2', 'kind': 'PRIVATE'},
                {'pid': 'DIRPN6V8EHO46EPR', 'number': 'FI2112345600000785', 'role': 'ADMIN', 'balance': 13959,
                 'currency': 'EUR', 'name': 'Name 1', 'kind': 'PRIVATE'},
                {'pid': '7WP6GEDZ5ER618AD', 'number': 'FI1410093000123458', 'role': 'ADMIN', 'balance': 297,
                 'currency': 'EUR', 'name': 'Name 0', 'kind': 'PRIVATE'}]}
        )
        response = http_client.accounts_list()
        assert len(response['results']) == 4
        assert mocker.called_once

        request = mocker.request_history[0]
        request_headers = request._request.headers

        assert "API-REQUEST-SIGNATURE" in request_headers
        assert "API-REQUEST-TIMESTAMP" in request_headers
        assert "API-KEY-ID" in request_headers

        assert request_headers["API-KEY-ID"] == "NYZRLPY8PS02GWEB"

    def test_retrieve_account(self, requests_mock, http_client):
        account_id = "KFGKJ5L27ASGTZAO"

        mocker = requests_mock.register_uri(
            "GET",
            f"/rest/v1.0/account/retrieve/{account_id}",
            status_code=200,
            json={
                'pid': 'KFGKJ5L27ASGTZAO',
                'number': 'FI2279600000000000',
                'role': 'ADMIN',
                'balance': 2546,
                'currency': 'EUR',
                'name': 'aloha',
                'kind': 'PRIVATE'
            },
        )
        response = http_client.accounts_retrieve(account_id)
        assert response['pid'] == account_id
        assert response['number'] == 'FI2279600000000000'
        assert mocker.called_once

        request = mocker.request_history[0]
        request_headers = request._request.headers

        assert "API-REQUEST-SIGNATURE" in request_headers
        assert "API-REQUEST-TIMESTAMP" in request_headers
        assert "API-KEY-ID" in request_headers

        assert request_headers["API-KEY-ID"] == "NYZRLPY8PS02GWEB"

    def test_list_transaction(self, requests_mock, http_client, transaction_item):
        mocker = requests_mock.register_uri(
            "GET",
            "/rest/v1.0/transactions/list",
            status_code=200,
            json={'next': None, 'previous': None, 'results': [transaction_item, transaction_item, transaction_item]}
        )
        response = http_client.transactions_list(None)
        assert len(response['results']) == 3
        assert mocker.called_once

        request = mocker.request_history[0]
        request_headers = request._request.headers

        assert "API-REQUEST-SIGNATURE" in request_headers
        assert "API-REQUEST-TIMESTAMP" in request_headers
        assert "API-KEY-ID" in request_headers

        assert request_headers["API-KEY-ID"] == "NYZRLPY8PS02GWEB"

    def test_retrieve_transaction(self, requests_mock, http_client, transaction_item):
        mocker = requests_mock.register_uri(
            "GET",
            f"/rest/v1.0/transactions/retrieve/{transaction_item['pid']}",
            status_code=200,
            json=transaction_item,
        )
        response = http_client.transactions_retrieve(transaction_item['pid'])
        assert response['pid'] == transaction_item['pid']
        assert response['kind'] == 'DEBIT'
        assert mocker.called_once

        request = mocker.request_history[0]
        request_headers = request._request.headers

        assert "API-REQUEST-SIGNATURE" in request_headers
        assert "API-REQUEST-TIMESTAMP" in request_headers
        assert "API-KEY-ID" in request_headers

        assert request_headers["API-KEY-ID"] == "NYZRLPY8PS02GWEB"

    def test_create_transaction(self, requests_mock, http_client):
        mocker = requests_mock.register_uri(
            "POST",
            "/rest/v1.0/transactions/create",
            status_code=201,
            json={'status': 'success'}
        )

        response = http_client.transaction_create(
            account_pid="U66CQW7T7M2HUMK2",
            currency="EUR",
            amount=10,  # 1 EUR
            title="Christmas gift",
            recipient_name="Uncle Bunny",
            recipient_account_number="PL61109010140000071219812874",
            recipient_country="PL"
        )

        assert response['status'] == 'success'
        assert mocker.called_once

        request = mocker.request_history[0]
        request_headers = request._request.headers
        request_json = request.json()

        assert "API-REQUEST-SIGNATURE" in request_headers
        assert "API-REQUEST-TIMESTAMP" in request_headers
        assert "API-KEY-ID" in request_headers
        assert request_headers["API-KEY-ID"] == "NYZRLPY8PS02GWEB"
        assert request_json == {
            "account_pid": "U66CQW7T7M2HUMK2",
            "currency": "EUR",
            "amount": 10,
            "recipient": {
                "name": "Uncle Bunny",
                "number": "PL61109010140000071219812874",
                "country": "PL",
            },
            "remittance_information": {
                "ustrd": "Christmas gift",
            },
        }
