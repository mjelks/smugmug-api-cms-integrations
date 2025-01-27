# Go through all Blog Galleries in SmugMug and upsert Ghost Posts accordingly
import requests as req;

# PIPEDREAM SETUP :
# https://pipedream.com/docs/code/python/#using-environment-variables
import os;
# SMUGMUG_API_ENDPOINT = os.environ['SMUGMUG_API_URI'];
# SMUGMUG_API_KEY = os.environ['SMUGMUG_API_KEY'];


from dotenv import load_dotenv
load_dotenv()
SMUGMUG_API_ENDPOINT = os.getenv("SMUGMUG_API_URL")
SMUGMUG_API_KEY = os.getenv("SMUGMUG_API_KEY")

# API Endpoints array (used for the upsert-age)
# To get all folders: 
# https://api.smugmug.com/api/v2/folder/user/michaeljelks/Public/Blog-Galleries!folders?APIKey=<APIKey>
# '62NhRR' # that's the top level of '/Public/Blog-Galleries'
# 2020, 2021, 2022, 2023, 2024, 2025 
#top_level_gallery_nodes = ["bsSZNc", "WVvsqb", "4xf5Zv", "2V4zJm", "DtBdtj"];
top_level_gallery_nodes = ["DtBdtj"]; # let's use 2025 now
all_gallery_contents = [];

# let's make this more efficient by only grabbing the last 10 galleries that have been recently modified:
# https://api.smugmug.com/api/v2/node/<NODE_ID>!children?SortDirection=Descending&SortMethod=DateModified&Type=All
def smugmug_gallery_endpoint(node_id, get_children, count=1):
  children = '!children' if get_children else ''
#   print(f'{SMUGMUG_API_ENDPOINT}/api/v2/node/{node_id}{children}?APIKey={SMUGMUG_API_KEY}&SortDirection=Descending&SortMethod=DateModified&count={count}')
  return f'{SMUGMUG_API_ENDPOINT}/api/v2/node/{node_id}{children}?APIKey={SMUGMUG_API_KEY}&SortDirection=Descending&SortMethod=DateModified&count={count}';

def fetch_smugmug_gallery_info(node_id, get_children=True):
  headers = {'Accept': 'application/json'};

  json_response = req.get(
      smugmug_gallery_endpoint(node_id, get_children), headers=headers
    ).json();
  contents = json_response['Response']['Node'];

  return contents;

def fetch_feture_image(node_id, size="M"):
    json_response = req.get(smugmug_image_endpoint(node_id), headers=headers).json();
    contents = json_response['Response']['ImageSizeDetails']

def parse_gallery_contents(contents, parent_gallery=''):
  # gallery_contents = []; # array of hashes

  # unless contents are nil ...
  for gallery_item in contents:
    name = gallery_item['Name'];
    uris = gallery_item['Uris'];
    all_gallery_contents.append(
      {
        'NodeID': gallery_item['NodeID'],
        'DateAdded': gallery_item['DateAdded'],
        'DateModified': gallery_item['DateModified'],
        'ParentGallery': parent_gallery,
        'Description': gallery_item['Description'],
        'Name': name,
        'HighlightImageURI': uris['HighlightImage']['Uri'],
        'AlbumImagesURI': uris['Album']['Uri'] + "!images"
      }
    );

  # return gallery_contents;

# top level perform the action
for node_id in top_level_gallery_nodes:
  # need this just to get the top Level gallery Name
  # unfortunately not included with !children call :(
  top_level_gallery_contents = fetch_smugmug_gallery_info(node_id, False);

  # get the gallery contents for the current child node
  current_gallery_contents = fetch_smugmug_gallery_info(node_id);
 
  parse_gallery_contents(current_gallery_contents, top_level_gallery_contents['Name']);

# print(len(all_gallery_contents));
print(all_gallery_contents);

# now that we have the galleries: all_gallery_contents, we need to upsert on ghost.org
# (this was the second part of script on pipedream)

######### PART TWO !!!!! ##################
#########                ##################
###########################################


import jwt	# pip install pyjwt
from datetime import datetime as date
from dateutil import parser as date_parse
from datetime import datetime, timedelta
GHOST_ADMIN_POSTS_ENDPOINT = os.getenv("GHOST_ADMIN_POSTS_ENDPOINT");
GHOST_ADMIN_API_KEY = os.getenv("GHOST_ADMIN_API_KEY");
JSON_HEADERS = {'Accept': 'application/json'};

def smugmug_dynamic_endpoint(endpoint_fragment):
  return f'{SMUGMUG_API_ENDPOINT}{endpoint_fragment}?APIKey={SMUGMUG_API_KEY}';

# https://api.smugmug.com/api/v2/image/NwkFnBn-1!sizedetails
def smugmug_image_endpoint(node_id):
  return f'{SMUGMUG_API_ENDPOINT}/api/v2/image/{node_id}!sizedetails?APIKey={SMUGMUG_API_KEY}';

def smugmug_dynamic_endpoint_json(endpoint):
  return req.get(endpoint, headers=JSON_HEADERS).json()['Response'];

def fetch_smugmug_image_info(node_id):
  json_response = req.get(
      smugmug_image_endpoint(node_id),
      headers=JSON_HEADERS
    ).json();
  contents = json_response['Response']['Node'];

  return contents;

def generate_token():
    # Split the key into ID and SECRET
    id, secret = GHOST_ADMIN_API_KEY.split(':')

    # Prepare header and payload
    iat = int(date.now().timestamp())

    header = {'alg': 'HS256', 'typ': 'JWT', 'kid': id}
    payload = {
        'iat': iat,
        'exp': iat + 5 * 60,
        'aud': '/admin/'
    }

    # Create the token (including decoding secret)
    token = jwt.encode(payload, bytes.fromhex(secret), algorithm='HS256', headers=header);

    return token;

def find_existing_posts(headers, filters):
    existing_posts = False;
    endpoint = f'{GHOST_ADMIN_POSTS_ENDPOINT}?filter={filters}';

    r = req.get(endpoint, headers=headers).json();
    if "posts" in r:
        existing_posts = r['posts']

    return existing_posts;

def update_existing_post(headers, post_id, post_body):
    endpoint = f'{GHOST_ADMIN_POSTS_ENDPOINT}{post_id}'
    response = req.put(endpoint, params={'source': 'html'}, json=body, headers=headers)

    if response.status_code != 200:
        print("Conflict error:")
        print(response.text)  # Print the raw response text
        try:
            # Attempt to parse JSON error message
            error_message = response.json()
            print("Error details:", error_message)
        except ValueError:
            print("No JSON error message in response.")

def smugmug_get_image_data(image_uri, preferred_size="ImageSizeSmall"):
    r = smugmug_dynamic_endpoint_json(smugmug_dynamic_endpoint(image_uri));

    # next we need to get the image size details and then return the medium one for now
    # https://api.smugmug.com/api/v2/image/FsBJhJm-0!sizedetails
    image_size_endpoint = r['Image']['Uris']['ImageSizeDetails']['Uri'];
    r = smugmug_dynamic_endpoint_json(smugmug_dynamic_endpoint(image_size_endpoint));

    return {
        "uri": r['ImageSizeDetails'][preferred_size]['Url'],
        "alt": '',
        "caption": '',
        "width": r['ImageSizeDetails'][preferred_size]['Width'],
        "height": r['ImageSizeDetails'][preferred_size]['Height']
    };

def smugmug_get_image_data_deux(image_object, preferred_size="ImageSizeSmall"):
    image_size_endpoint = image_object['Uris']['ImageSizeDetails']['Uri'];
    # print(image_size_endpoint);
    r = smugmug_dynamic_endpoint_json(smugmug_dynamic_endpoint(image_size_endpoint));

    return {
        "uri": r['ImageSizeDetails'][preferred_size]['Url'],
        "alt": '',
        "caption": '',
        "width": r['ImageSizeDetails'][preferred_size]['Width'],
        "height": r['ImageSizeDetails'][preferred_size]['Height']
    };

def smugmug_get_gallery_images(gallery_uri, preferred_size="ImageSizeSmall"):
    final_image_items = [];

    r = smugmug_dynamic_endpoint_json(smugmug_dynamic_endpoint(gallery_uri));

    for image_object in r['AlbumImage']:
        image_hash = smugmug_get_image_data_deux(image_object, preferred_size);
        final_image_items.append(image_hash);

    return final_image_items;

# https://ghost.org/docs/admin-api/#creating-a-post
def generate_post_json(smugmug_data, feature_image_data={}, html=''):
    
    post_body = {
        "posts": [
            {
                "title": smugmug_data['Name'],
                "feature_image": feature_image_data['uri'],
                "feature_image_alt": feature_image_data['alt'],
                "feature_image_caption": feature_image_data['caption'],
                "authors": ["info@bicyclelad.com"],
                # "html": "<!--kg-card-begin: html-->" + html + "<!--kg-card-end: html-->",
                "html": html,
                "tags": [smugmug_data['ParentGallery']],
                "published_at": smugmug_data['DateAdded'],
                "updated_at": smugmug_data['DateModified'],
                "codeinjection_foot": smugmug_data['NodeID'],
                # "featured": True,
                "status": "published"
            }
        ]
    }

    return post_body;

def gallery_image_format(image_data):
    html = """
    <figure class="kg-card kg-gallery-card kg-width-wide">
        <div class="kg-gallery-container">
            <div class="kg-gallery-row">
    """

    # for idx, x in enumerate(xs):
    for idx, image_object in enumerate(image_data):
        if (idx % 3 == 0):
            html += '</div><div class="kg-gallery-row">';
        image_uri = image_object['uri'];
        image_width = image_object['width'];
        image_height = image_object['height'];
        image_uri_html = f'<img src="{image_uri}" sizes="(min-width: 720px) 720px" loading="lazy" width="{image_width}" height="{image_height}" />';
        html += f'<div class="kg-gallery-image">{image_uri_html}</div>';

    html += """
            </div>
        </div>
    </figure>
    """

    return html;

def parse_publish_date_from_post_title(smugmug_data):
    publish_date = datetime.now()

    # Check if 'Name' starts with a date pattern (i typically use 2024/12/01: here is the title of my post)
    if smugmug_data['Name']:
        parts = smugmug_data['Name'].split(": ", 1)  # Split into date and title parts
        # print(parts)
        if len(parts) > 1:
            date_str, title = parts
            # print(date_str)
            try:
                # utc_datetime_str = "2024-12-01T00:00:00.000Z"
                utc_publish_date = date.strptime(date_str.strip(), "%Y/%m/%d")

                los_angeles_datetime = utc_publish_date + timedelta(hours=8)
                formatted_los_angeles_datetime = los_angeles_datetime.strftime("%Y-%m-%dT%H:%M:%S.000Z")

                return formatted_los_angeles_datetime
            except ValueError:
                print("Invalid date format. Using current date as publish date.")
        else:
            print("No valid title found. Using current date as publish date.")
    else:
        print("No 'Name' field found in smugmug_data.")

token = generate_token();
headers = {'Authorization': 'Ghost {}'.format(token)};

# Make an authenticated request to create a post
# url = 'http://localhost:8080/ghost/api/admin/posts/'
#url = 'http://phpa.jelksmedical.com:8080/ghost/api/admin/posts/'
# body = {'posts': [{'title': 'Hello World'}]}
# print(headers);
for smugmug_data in all_gallery_contents:
    # feature_image_data = smugmug_feature_image_data(smugmug_data['HighlightImageURI']);
    # print(feature_image_data);

    # body_image_data = smugmug_get_gallery_images(smugmug_data['AlbumImagesURI']);
    # print(body_image_data);

    # check if we already have a post :
    existing_posts = find_existing_posts(headers, "codeinjection_foot:"+smugmug_data['NodeID']);

    # create the ghost post body contents:
    feature_image_data = smugmug_get_image_data(smugmug_data['HighlightImageURI'], 'ImageSizeX2Large');
    body_image_data = smugmug_get_gallery_images(smugmug_data['AlbumImagesURI'], 'ImageSizeX2Large');
    body_image_html = gallery_image_format(body_image_data);
    if (bool(smugmug_data['Description'].strip())):
        description = smugmug_data['Description'].replace('\n', '<br />');
        body_image_html = f'<p>{description}</p>{body_image_html}';
    body = generate_post_json(smugmug_data, feature_image_data, body_image_html);
    # use the date from title if possible as the 'Publish Date'
    parsed_publish_date = parse_publish_date_from_post_title(smugmug_data)
    if (parsed_publish_date):
        body['posts'][0]['published_at'] = parsed_publish_date #parsed_publish_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    if (len(existing_posts) < 1):
        print("Going to Insert Post for Gallery Item: " + smugmug_data['Name']);
        r = req.post(GHOST_ADMIN_POSTS_ENDPOINT, params={'source': 'html'}, json=body, headers=headers);
    else:
        print("going to update post!")
        # print(existing_posts[0]);
        # print(smugmug_data)
        existing_date_published = date_parse.parse(existing_posts[0]['published_at']);
        existing_date_updated = date_parse.parse(existing_posts[0]['updated_at']);
        smugmug_date_modified = date_parse.parse(smugmug_data['DateModified']);
        print("existing date published vs vs updated vs smugmug date modified")
        print(existing_date_published)
        print(existing_date_updated)
        print(smugmug_date_modified)
        modified_at_smugmug = (smugmug_date_modified - existing_date_updated).total_seconds()
        print("timedelta 1:")
        if (modified_at_smugmug > 0):
            print("do it!")
            post_id = existing_posts[0]['id']
            date_published = date_parse.parse(existing_posts[0]['published_at']);
            date_modified = date_parse.parse(smugmug_data['DateModified']);
            if (post_id):
                # print(body['posts'][0]['updated_at'])
                # the updated_at needs to match the existing updated_at from Ghost to avoid 409 error (somebody is currently editing error)
                body['posts'][0]['updated_at'] = existing_posts[0]['updated_at']
                # body['posts'][0]['updated_at'] = smugmug_date_modified.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                # print(body['posts'][0])    
                update_existing_post(headers, post_id, body)
            else:
                print("No post id found")