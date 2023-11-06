from ..utils import api_call

accounts = {
    "list": api_call({
        "method": 'GET',
        "path": '/rest/v1.0/account/list',
    }),
    "retrieve": api_call({
        "method": 'GET',
        "path": '/rest/v1.0/account/retrieve/{account_pid}'
    })
}
