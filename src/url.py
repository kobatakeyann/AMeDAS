import urllib.request

def acquire_query(url):
   query = urllib.parse.urlparse(url).query
   query_dictionary = urllib.parse.parse_qs(query)
   return query_dictionary

