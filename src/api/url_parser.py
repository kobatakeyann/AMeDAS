from urllib.parse import parse_qs, urlparse


def get_query_params(url: str) -> dict:
    parsed_url = urlparse(url).query
    query_params = parse_qs(parsed_url)
    return query_params
