import base64
import hashlib
import requests
import canonicaljson
import urllib.parse

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization

from narvi.resources.accounts import accounts
from narvi.resources.transactions import transactions


class RequestClient(object):
    def __init__(self, api_key_id, private_key_file_path, host):
        self.api_key_id = api_key_id
        self.host = host
        self.private_key = self._load_api_key(private_key_file_path)

    @staticmethod
    def _load_api_key(private_key_file_path):
        with open(private_key_file_path, 'rb') as private_key_file:
            return serialization.load_pem_private_key(private_key_file.read(), password=None)

    def sign_request(self, url, method, nonce, query_params=None, payload=None):
        """Generate a signature for the request."""

        hash_elems = [url, method, nonce]

        if query_params:
            hash_elems.append(canonicaljson.encode_canonical_json(query_params).decode())

        if payload:
            hash_elems.append(canonicaljson.encode_canonical_json(payload).decode())

        descriptor = hashlib.sha256(("".join([elem for elem in hash_elems])).encode()).digest()
        signature = self.private_key.sign(descriptor, ec.ECDSA(hashes.SHA256()))
        return base64.b64encode(signature).decode('utf-8')

    def send_request(self, url, method, nonce, query_params=None, payload=None):
        """Send an API request and return the response."""

        full_url = urllib.parse.urljoin(self.host, url)

        headers = {
            'API-KEY-ID': self.api_key_id,
            'API-REQUEST-TIMESTAMP': nonce,
            'API-REQUEST-SIGNATURE': self.sign_request(full_url, method, nonce, query_params, payload),
            'Content-Type': 'application/json',
        }

        response = requests.request(method, full_url, headers=headers, json=payload, params=query_params)

        if response.status_code not in [200, 201]:
            raise Exception(f"Request failed with status code {response.status_code}. Response: {response.text}")

        return response.json()


class NarviAccountClient(object):
    def __init__(self, api_key_id, private_key_file_path, host=None):
        if host is None:
            host = "https://api.narvi.com"
        self.request_client = RequestClient(api_key_id, private_key_file_path, host)

    @classmethod
    def url2params(cls, url):
        if not url:
            return {}

        query = urllib.parse.urlsplit(url).query
        if not query:
            return {}

        return dict(urllib.parse.parse_qsl(query))

    def accounts_list(self, cursor=None):
        query_params = {}
        if cursor is not None:
            query_params["cursor"] = cursor

        return accounts["list"](client=self.request_client, query_params=query_params)

    def accounts_retrieve(self, account_pid):
        return accounts["retrieve"](client=self.request_client, account_pid=account_pid)

    def transaction_create(self, account_pid, amount, currency, title, recipient_account_number,
                           recipient_name, recipient_address=None, recipient_zip_code=None,
                           recipient_city=None, recipient_country=None):

        recipient = {"number": recipient_account_number, "name": recipient_name}
        if recipient_address:
            recipient["address"] = recipient_address
        if recipient_zip_code:
            recipient["zip_code"] = recipient_zip_code
        if recipient_city:
            recipient["city"] = recipient_city
        if recipient_country:
            recipient["country"] = recipient_country

        payload = {
            "account_pid": account_pid,
            "amount": amount,
            "currency": currency,
            "remittance_information": {"ustrd": title},
            "recipient": recipient
        }

        return transactions["create"](client=self.request_client, payload=payload)

    def transactions_list(self, account_pid, kind=None, added__lte=None, added__gte=None, cursor=None):
        query_params = {"account_pid": account_pid}
        if kind is not None:
            query_params["kind"] = kind
        if added__lte is not None:
            query_params["added__lte"] = str(added__lte)
        if added__gte is not None:
            query_params["added__gte"] = str(added__gte)
        if cursor is not None:
            query_params["cursor"] = cursor
        return transactions["list"](client=self.request_client, query_params=query_params)

    def transactions_retrieve(self, transaction_pid):
        return transactions["retrieve"](client=self.request_client, transaction_pid=transaction_pid)
