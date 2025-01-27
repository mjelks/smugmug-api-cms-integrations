#!/usr/local/bin/python3

from dotenv import load_dotenv
import requests as req;
import os;
import json;

class SmugmugApi:

  def __init__(self, env_vars=None):
    config = dotenv_values() if not env_vars else env_vars
    self.SMUGMUG_API_URL = config['SMUGMUG_API_URL'];
    self.SMUGMUG_API_KEY = config['SMUGMUG_API_KEY'];
    self.SMUGMUG_USERNAME = config['SMUGMUG_USERNAME'];
    self.JSON_HEADERS = {'Accept': 'application/json'};
    self.api_prefix = '/api/v2'

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
            # response_payload['expansion'] = response.json()['Expansions']
            response_payload['Response'] = response.json()['Response']
        response.raise_for_status()
    except req.exceptions.HTTPError as errh:
        print("HTTP Error");
        # leave this uncommented for debugging on local dev only
        # as there is sensitive API_KEY in the GET call as part of error msg
        # print(errh.args[0])

    return response_payload

  def smugmug_dynamic_endpoint(self, endpoint_fragment):
    return f'{self.SMUGMUG_API_URL}{endpoint_fragment}';

  # def smugmug_gallery_endpoint(node_id, get_children, count=50):
  #     children = '!children' if get_children else ''
  #     return f'/api/v2/node/{node_id}{children}&count={count}';


  def gallery_config(self, count=50):
      config = {
            "expand_method": "inline",
            "shorturis": True,
            "filteruri": {
                "ChildNodes": "ChildNodes"
            },
            "expand": {
                "ChildNodes": {
                    "expand_method": "inline",
                    "filter": ["NodeID", "DateAdded", "DateModified", "Name"],
                    "filteruri": ["Album", "HighlightImage"],
                    "shorturis": True,
                    "optional": False,
                    "args": {
                        "count": count
                    },
                    "expand": {
                        "Album": {
                            "expand_method": "inline"
                        },
                        "HightlightImage": {
                            "expand_method": "inline",
                            "filter": ["Uri"],
                            "filteruri": ["ImageSizeDetails"]
                        }
                    }
                }
            }
        }

      return config;

  def gallery_config_deux(self, count=50):
    config = {
        # "expand_method": "inline",
        "filter": ["Date", "ImagesLastUpdated", "HighlightAlbumImageUri"],
        "shorturis": True,
        # "filteruri": {
        #     "ChildNodes": "ChildNodes"
        # },
        "expand": {
            "AlbumImages": {
                "expand_method": "inline",
                "filter": ["Uri", "Date"],
                "filteruri": ["ImageSizeDetails", "HighlightImage"],
                "shorturis": True,
                "optional": False,
                "args": {
                    "count": count
                },
                "expand": {
                    # "Album": {
                    #     "expand_method": "inline"
                    # },
                    "HightlightImage": {
                        "expand_method": "inline",
                        "filter": ["Uri"],
                        "filteruri": ["ImageSizeDetails"]
                    }
                }
            }
        }
    }

    return config;

  # https://api.smugmug.com/api/v2/folder/user/<SMUGMUG_USERNAME/Public/Blog-Galleries?_filter=NodeID&_filteruri=AlbumList
  def smugmug_get_node_id_from_folder_path(self, folder_path):
    albumlist_endpoint = f'{self.api_prefix}/folder/user/{self.SMUGMUG_USERNAME}/{folder_path}';
    config_params = {
        "filter": "NodeID",
        "filteruri": { "AlbumList": "AlbumList" }
    }

    response = self.smugmug_get_request(albumlist_endpoint, config_params);

    return response['Response']['Folder']['NodeID'];

  # bsSZNc
  # https://api.smugmug.com/api/v2/node/bsSZNc?_expand=ChildNodes.Album.AlbumImages.ImageSizeDetails
  def fetch_smugmug_gallery_info(self, node_id, count=50):
      gallery_info_endpoint = f'{self.api_prefix}/node/{node_id}';

      config_params = {'_config': json.dumps(self.gallery_config(count))}

      return self.smugmug_get_request(gallery_info_endpoint, config_params);
      #smugmug_gallery_endpoint(node_id, get_children), headers=headers
      #contents = json_response['Response']['Node'];
      # breakpoint();


      #response_payload['Response']['Node']['Uris']['ChildNodes']['Node'][0]['Uris']['HighlightImage']['Uri']

      # return response_payload;

  def parse_smugmug_gallery_info(self, payload):
    all_gallery_contents = [];
    album_contents = payload['Response']['Node']['Uris']['ChildNodes']['Node'];
    breakpoint();

    # unless contents are nil ...
    for gallery_item in album_contents:
       name = gallery_item['Name'];
       uris = gallery_item['Uris'];
       all_gallery_contents.append(
       {
        'NodeID': gallery_item['NodeID'],
        'DateAdded': gallery_item['DateAdded'],
        'DateModified': gallery_item['DateModified'],
        'ParentGallery': parent_gallery,
        'Name': name,
        'HighlightImageURI': uris['HighlightImage']['Uri'],
        'AlbumImagesURI': uris['Album']['Uri'] + "!images"
        }
    );

    return all_gallery_contents;

  def smugmug_get_album_images(self, album_node_id):
    # /api/v2/album/<album_node_id>
    gallery_album_endpoint = f'/{self.api_prefix}/album/{album_node_id}';
    expansion_params = {'_expand': 'AlbumImages'};
    response = self.smugmug_get_request(gallery_album_endpoint, expansion_params);
