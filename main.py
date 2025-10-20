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
        character = item["character"]
        voice_actors = item["voice_actors"]
        for actor in voice_actors:
            if actor["language"] == "Japanese":
                # Create a more detailed object with character and actor info
                actor_data = {
                    "actor_name": actor["person"]["name"],
                    "actor_url": actor["person"]["url"],
                    "actor_image": actor["person"]["images"]["jpg"]["image_url"],
                    "character_name": character["name"],
                    "character_url": character["url"],
                    "character_image": character["images"]["jpg"]["image_url"] if character["images"] and character["images"]["jpg"] else None
                }
                japanese_names.append(actor_data)
    
    return {'data': japanese_names}

def extractMalId(url):
    parsed_url = urlparse(url)
    path_segments = parsed_url.path.split("/")
    second_segment = path_segments[2]
    return second_segment

def getAnimeTitle(mal_id):
    """Fetch the actual anime title from Jikan API"""
    try:
        url = f"https://api.jikan.moe/v4/anime/{mal_id}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            # Try to get the English title first, then Japanese, then default title
            anime_data = data.get('data', {})
            title = (anime_data.get('title_english') or 
                    anime_data.get('title_japanese') or 
                    anime_data.get('title') or 
                    "Unknown Anime")
            return title
        else:
            return "Unknown Anime"
    except requests.exceptions.RequestException as e:
        print(f"Error fetching anime title: {e}")
        return "Unknown Anime"

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
    
    # Get proper anime titles from API
    title1 = getAnimeTitle(malid1)
    title2 = getAnimeTitle(malid2)
    
    result = searchCommonSeiyuus(malid1, malid2)
    
    app.logger.info('Processing default request')
    app.logger.info(f'Found {len(result)} common voice actors')
    app.logger.info(f'Anime 1: {title1}, Anime 2: {title2}')
    
    return render_template('result.html', result=result, anime1=title1, anime2=title2)


#def perform_search(term):
    # Perform actual search logic here
    # Return a list of search results
    # For demonstration, let's return a dummy list
    #return ["Result 1", "Result 2", "Result 3"]

def perform_search(term):
    # Jikan API base URL for anime search
    base_url = "https://api.jikan.moe/v4/anime"
    # Query parameters
    params = {
        "q": term,      # Search term provided by the user
        "limit": 7,     # Limit to top 7 results
        "sfw": "true"   # Filter out NSFW content
    }
    
    try:
        # Send GET request to Jikan API
        response = requests.get(base_url, params=params)
        
        # Check if request was successful
        if response.status_code == 200:
            json_data = response.json()
            results = []
            # Extract relevant fields from each anime
            for item in json_data.get("data", []):
                result = {
                    "mal_id": item.get("mal_id"),
                    "title": item.get("title"),
                    "url": item.get("url"),
                    "image_url": item.get("images", {}).get("jpg", {}).get("image_url"),
                    "synopsis": item.get("synopsis"),
                    "score": item.get("score"),
                    "type": item.get("type")
                }
                results.append(result)
            return results
        else:
            app.logger.error(f"API request failed with status code {response.status_code}")
            return []
            
    except requests.exceptions.RequestException as e:
        app.logger.error(f"An error occurred during the API request: {e}")
        return []



def searchCommonSeiyuus(malid1, malid2):
    # URL of the website that returns JSON
    url1 = "https://api.jikan.moe/v4/anime/" + malid1 + "/characters"
    url2 = "https://api.jikan.moe/v4/anime/" + malid2 + "/characters"
    
    try:
        # Send a GET request to the URL
        response1 = requests.get(url1)
        response2 = requests.get(url2)

        # Check if the request was successful (status code 200)
        if response1.status_code == 200 and response2.status_code == 200:
            # Extract JSON data from the response
            json_data1 = response1.json()
            json_data2 = response2.json()
            
            # Filter to get Japanese voice actors with character info
            filtered_data1 = filter_japanese_names(json_data1)
            filtered_data2 = filter_japanese_names(json_data2)
            
            # Group characters by voice actor for each anime
            actors_anime1 = {}
            actors_anime2 = {}
            
            for actor_data in filtered_data1['data']:
                actor_name = actor_data['actor_name']
                if actor_name not in actors_anime1:
                    actors_anime1[actor_name] = {
                        'actor_info': {
                            'name': actor_data['actor_name'],
                            'url': actor_data['actor_url'],
                            'image': actor_data['actor_image']
                        },
                        'characters': []
                    }
                actors_anime1[actor_name]['characters'].append({
                    'name': actor_data['character_name'],
                    'url': actor_data['character_url'],
                    'image': actor_data['character_image']
                })
            
            for actor_data in filtered_data2['data']:
                actor_name = actor_data['actor_name']
                if actor_name not in actors_anime2:
                    actors_anime2[actor_name] = {
                        'actor_info': {
                            'name': actor_data['actor_name'],
                            'url': actor_data['actor_url'],
                            'image': actor_data['actor_image']
                        },
                        'characters': []
                    }
                actors_anime2[actor_name]['characters'].append({
                    'name': actor_data['character_name'],
                    'url': actor_data['character_url'],
                    'image': actor_data['character_image']
                })
            
            # Find common voice actors
            common_actors = []
            for actor_name in actors_anime1:
                if actor_name in actors_anime2:
                    common_actor = {
                        'actor_info': actors_anime1[actor_name]['actor_info'],
                        'characters_anime1': actors_anime1[actor_name]['characters'],
                        'characters_anime2': actors_anime2[actor_name]['characters']
                    }
                    common_actors.append(common_actor)
            
            return common_actors

    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)
        return []

if __name__ == "__main__":
    app.run(debug=True)