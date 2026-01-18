from flask import Flask, request, jsonify, render_template
import requests
import os

# Note the 'template_folder' argument tells Flask where to look for HTML
app = Flask(__name__, template_folder='templates')

# --- CONFIGURATION ---
GOOGLE_API_KEY = os.environ.get('AIzaSyBdSHG0NPDssnxk4JGmwcvTLQKSFWaMmpw')
SEARCH_ENGINE_ID = os.environ.get('03c0188218abb4c62')

# --- ROUTE FOR HOMEPAGE (Fixes the 404) ---
@app.route('/')
def home():
    return render_template('index.html')

# --- EXISTING BACKEND LOGIC ---
def get_google_specs(query):
    if not GOOGLE_API_KEY or not SEARCH_ENGINE_ID:
        return ["API Keys not configured"]
    url = "https://www.googleapis.com/customsearch/v1"
    params = {'key': GOOGLE_API_KEY, 'cx': SEARCH_ENGINE_ID, 'q': f"{query} full specifications features", 'num': 2}
    try:
        resp = requests.get(url, params=params)
        data = resp.json()
        specs = []
        if 'items' in data:
            for item in data['items']:
                specs.append(item.get('snippet', 'No details found.'))
        return specs
    except Exception as e:
        return [f"Error fetching specs: {str(e)}"]

def get_youtube_reviews(query):
    if not GOOGLE_API_KEY:
        return []
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {'part': 'snippet', 'q': f"{query} review", 'key': GOOGLE_API_KEY, 'type': 'video', 'maxResults': 1}
    try:
        resp = requests.get(url, params=params)
        data = resp.json()
        videos = []
        if 'items' in data:
            for item in data['items']:
                videos.append({'id': item['id']['videoId'], 'title': item['snippet']['title']})
        return videos
    except:
        return []

@app.route('/api/compare', methods=['POST'])
def compare():
    data = request.json
    devices = data.get('devices', [])
    if len(devices) < 2:
        return jsonify({'error': 'Please provide two devices'}), 400

    results = []
    for device in devices:
        specs_snippets = get_google_specs(device)
        reviews = get_youtube_reviews(device)
        results.append({'name': device, 'specs': specs_snippets, 'videos': reviews})

    recommendation = (f"Compare the specs above. generally look for higher numbers in RAM, Battery, "
                      f"and Storage. Watch the reviews to see if {devices[0]} or {devices[1]} fits your needs.")

    return jsonify({'results': results, 'recommendation': recommendation})

# For local testing
if __name__ == '__main__':
    app.run(debug=True)