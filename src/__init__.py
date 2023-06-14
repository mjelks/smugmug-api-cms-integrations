#!/usr/local/bin/python3

import src.smugmug_api;

# x = smugmug_api.SmugmugApi({'SMUGMUG_API_ENDPOINT': 'foo', 'SMUGMUG_API_KEY': 'askdfjaks'});
x = smugmug_api.SmugmugApi();

print(x.smugmug_dynamic_endpoint("/foozle"));
