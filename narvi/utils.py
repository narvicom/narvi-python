import datetime


def api_call(spec):
    def wrapper(client, **kwargs):
        method = spec["method"]
        nonce = str(int(datetime.datetime.now().timestamp() * 1000))
        url = spec["path"].format(**kwargs)
        query_params = kwargs.get('query_params', None)
        payload = kwargs.get('payload', None)

        return client.send_request(url, method, nonce, query_params=query_params, payload=payload)

    return wrapper
