from flask import Flask, request, jsonify, render_template
import requests
import json
import sys
import logging
from urllib.parse import urlparse

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

def filter_japanese(json_data):
    filtered_data = []
    for item in json_data['data']:
        voice_actors = item['voice_actors']
        japanese_actors = [actor for actor in voice_actors if actor['language'] == 'Japanese']
        if japanese_actors:
            item['voice_actors'] = japanese_actors
            filtered_data.append(item)
    return {'data': filtered_data}

def filter_japanese_names(json_data):
    data = json_data
    japanese_names = []
    
    for item in data["data"]:
        voice_actors = item["voice_actors"]
        for actor in voice_actors:
#            print("Actor: " + json.dumps(actor))
            if actor["language"] == "Japanese":
                print("Entro")
                inner_array = []
                inner_array.append(actor["person"]["name"])
                inner_array.append(actor["person"]["url"])
                inner_array.append(actor["person"]["images"]["jpg"]["image_url"])
                japanese_names.append(inner_array)
    filtered_data = {"japanese_names": japanese_names}
    
    return {'data': japanese_names}

def extractMalId(url):
    parsed_url = urlparse(url)
    path_segments = parsed_url.path.split("/")
    second_segment = path_segments[2]
    return second_segment

def extractMalTitle(url):
    parsed_url = urlparse(url)
    path_segments = parsed_url.path.split('/')
    if len(path_segments) >= 4:
        fourth_segment = path_segments[3]
        print(f"Fourth Segment: {fourth_segment}")
    else:
        fourth_segment = "Anime"
        print("URL doesn't have a fourth segment.")  
    return fourth_segment

@app.route("/")
def index():
    return render_template("index.html")
#    return app.send_static_file("index.html")

@app.route("/search")
def search():
    term = request.args.get("term")

    # Perform search logic here and get the search results
    results = perform_search(term)

    return jsonify(results)


@app.route('/result', methods=['POST'])
def concatenate():
    text1 = request.form['text1']
    text2 = request.form['text2']
    malid1 = extractMalId(text1)
    malid2 = extractMalId(text2)
    title1 = extractMalTitle(text1)
    title2 = extractMalTitle(text2)
    result = searchCommonSeiyuus(malid1,malid2)
    trimmed_arrays = [[s.strip() for s in inner_array] for inner_array in result]
    trimmed_data = [json.loads(string.strip()) for string in result]
    app.logger.info('Processing default request')
    app.logger.info(result)
    app.logger.info(trimmed_data)
    print(result)
    print("Hola", file=sys.stdout)
    return render_template('result.html', result=trimmed_data, anime1=title1, anime2=title2)


def perform_search(term):
    # Perform actual search logic here
    # Return a list of search results
    # For demonstration, let's return a dummy list
    return ["Result 1", "Result 2", "Result 3"]

def searchCommonSeiyuus(malid1,malid2):
    array = []
# URL of the website that returns JSON
    url1 = "https://api.jikan.moe/v4/anime/" + malid1 + "/characters"
    url2 = "https://api.jikan.moe/v4/anime/" + malid2 + "/characters"
    try:
    # Send a GET request to the URL
       response1 = requests.get(url1)
       response2 = requests.get(url2)

    # Check if the request was successful (status code 200)
       if response1.status_code == 200:
        # Extract JSON data from the response
           json_data1 = response1.json()
#           print(json.dumps(json_data1))
           json_data1 = filter_japanese_names(json_data1)
#           print("Filtrado: " + json.dumps(json_data1))
    # Check if the request was successful (status code 200)
       if response2.status_code == 200:
        # Extract JSON data from the response
           json_data2 = response2.json()
           json_data2 = filter_japanese_names(json_data2)
#           print(json.dumps(json_data2))


# Extract the 'data' array from each JSON
       json1_array = json_data1['data']
       json2_array = json_data2['data']

# Convert the 'data' arrays to sets for easy comparison
       json1_set = set(json.dumps(obj, sort_keys=True) for obj in json1_array)
       json2_set = set(json.dumps(obj, sort_keys=True) for obj in json2_array)

# Find the common objects between the sets
       common_objects = json1_set.intersection(json2_set)

# Convert the common objects back to JSON objects
       common_objects = [json.loads(obj) for obj in common_objects]
       result = ""
# Print the common objects
       for obj in common_objects:
          result += json.dumps(obj, indent=2)
          array.append(json.dumps(obj, indent=2).strip())
       print(array[0])   


    except requests.exceptions.RequestException as e:
       print("An error occurred:", e)
    return  array
