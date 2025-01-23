from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def fetch_data(url: str):
    try:
        response = Request(url)
        with urlopen(response) as res:
            res_data = res.read()
            return res_data
    except HTTPError as http_err:
        raise HTTPError(
            http_err.url,
            http_err.code,
            http_err.reason,
            http_err.headers,
            http_err.fp,
        )
    except URLError as url_err:
        raise URLError(url_err)
