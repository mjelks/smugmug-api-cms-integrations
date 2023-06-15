#!/usr/local/bin/python3

from dotenv import dotenv_values;
import requests as req;
import os;

class SmugmugApi:

  def __init__(self, env_vars=None):
    config = dotenv_values() if not env_vars else env_vars
    self.SMUGMUG_API_ENDPOINT = config['SMUGMUG_API_ENDPOINT'];
    self.SMUGMUG_API_KEY = config['SMUGMUG_API_KEY'];
    self.JSON_HEADERS = {'Accept': 'application/json'};

  def smugmug_get_request(self, endpoint, params=''):
    # return req.get(endpoint, headers=JSON_HEADERS, params=).json()['Response'];
    # /api/v2/album/SJT3DX!images
    # url = self.smugmug_dynamic_endpoint('/api/v2/album/SJT3DX!images');
    response_payload = { "status": '', "response": '' };
    url = self.smugmug_dynamic_endpoint(endpoint);
    all_params = { 'APIKey': self.SMUGMUG_API_KEY };
    try:
        all_params.update(params); # merge in _filters & _expand options
        response = req.get(url, headers=self.JSON_HEADERS, params=all_params);
        response_payload['status'] = response.status_code
        if response.status_code == 200:
            response_payload['response'] = response.json()['Response']
        response.raise_for_status()
    except req.exceptions.HTTPError as errh:
        print("HTTP Error");
        # leave this uncommented for debugging on local dev only
        # as there is sensitive API_KEY in the GET call as part of error msg
        # print(errh.args[0])

    return response_payload

  def smugmug_dynamic_endpoint(self, endpoint_fragment):
    return f'{self.SMUGMUG_API_ENDPOINT}{endpoint_fragment}';

  def smugmug_get_album_images(self, album_node_id):
    # /api/v2/album/<album_node_id>
    gallery_album_endpoint = '/api/v2/album/' + album_node_id;
    expansion_params = {'_expand': 'AlbumImages'};
    response = self.smugmug_get_request(gallery_album_endpoint, expansion_params);
