from ..utils import api_call

transactions = {
    "create": api_call({
        "method": 'POST',
        "path": '/rest/v1.0/transactions/create',
    }),
    "retrieve": api_call({
        "method": 'GET',
        "path": '/rest/v1.0/transactions/retrieve/{transaction_pid}'
    }),
    "list": api_call({
        "method": 'GET',
        "path": '/rest/v1.0/transactions/list'
    })
}
