#!/usr/local/bin/python3
import pytest;
import os;
from src.smugmug_api import SmugmugApi;


SCOPE="function"
#SCOPE="session"

@pytest.fixture(scope=SCOPE)
def newSmugmugApi():
    instance = SmugmugApi();
    yield instance;

class TestSmugmugApi():
    def test_init(env_vars):
        actual = SmugmugApi();
        # assert newSmugmugApi.SMUGMUG_API_ENDPOINT == os.environ['SMUGMUG_API_ENDPOINT'];
        assert actual.SMUGMUG_API_ENDPOINT == os.environ['SMUGMUG_API_ENDPOINT'];
        assert actual.SMUGMUG_API_KEY == os.environ['SMUGMUG_API_KEY'];
        assert actual.JSON_HEADERS == {'Accept': 'application/json' };

    # @pytest.mark.parametrize('endpoint_fragment', '/foo/biz')
    def test_smugmug_dynamic_endpoint(endpoint_fragment):
        endpoint_suffix = '/foo/biz';
        expected = os.environ['SMUGMUG_API_ENDPOINT'] + endpoint_suffix;
        actual = SmugmugApi();
        assert actual.smugmug_dynamic_endpoint('/foo/biz') == expected;

    def test_smugmug_get_request_good(valid_endpoint):
        sample_endpoint = '/api/v2/album/RdQFjC!images'
        actual = SmugmugApi();
        assert actual.smugmug_get_request(sample_endpoint)['status'] == 200;

    def test_smugmug_get_request_bad(invalid_endpoint):
        sample_endpoint = '/foo/biz'
        actual = SmugmugApi();
        assert actual.smugmug_get_request(sample_endpoint)['status'] == 404;
