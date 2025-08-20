from pymemcache.client import Client
from pymemcache.serde import pickle_serde

memcache_client = Client(('localhost', 11211), serde=pickle_serde)
