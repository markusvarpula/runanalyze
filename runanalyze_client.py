import os
import requests
from dotenv import load_dotenv
import json
from pathlib import Path

# Ladda API-nyckeln från .env
load_dotenv()
API_TOKEN = os.getenv("RUNALYZE_API_TOKEN")
print("API_TOKEN:", API_TOKEN)  # Debugging line to check if the token is loaded
BASE_URL = "https://runalyze.com/api/v1"

HEADERS = {
    "token": API_TOKEN,
    "Accept": "application/json"
}
print("HEADERS:", HEADERS)  # Debugging line to check headers

def get_activities(limit=20):
    #url = f"{BASE_URL}/activity?limit={limit}"
    url = f"{BASE_URL}/activity?order[id]=desc&limit={limit}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        return response.json()  # Direkt returnera listan
    else:
        print("Fel vid hämtning:", response.status_code, response.text)
        return []

# Ny funktion för att hämta aktiviteter efter given timestamp
def get_activities_since(timestamp, limit=100):
    url = f"{BASE_URL}/activity?timestamp_start={timestamp}&order[id]=desc&limit={limit}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        return response.json()
    else:
        print("Fel vid hämtning:", response.status_code, response.text)
        return []
    
def load_or_fetch_activities(limit=100, cache_file="activities_cache.json", refresh=True):
    cache_path = Path(cache_file)
    cached_activities = []

    if cache_path.exists():
        print("Laddar aktiviteter från cache...")
        with open(cache_path, "r", encoding="utf-8") as f:
            cached_activities = json.load(f)

    if not refresh:
        return cached_activities

    latest_ts = max((a.get("timestamp", 0) for a in cached_activities), default=0)
    print(f"Hämtar nya aktiviteter från Runalyze efter timestamp {latest_ts}...")
    new_activities = get_activities_since(latest_ts, limit=limit)

    if new_activities:
        all_activities = cached_activities + new_activities
        # Ta bort dubbletter baserat på ID
        unique_activities = {a["id"]: a for a in all_activities}.values()
        sorted_activities = sorted(unique_activities, key=lambda x: x.get("timestamp", 0), reverse=True)
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(sorted_activities, f, ensure_ascii=False, indent=2)
        return list(sorted_activities)
    else:
        return cached_activities

if __name__ == "__main__":
    activities = load_or_fetch_activities(limit=100)
    for act in activities:
        date_time = act.get('date_time', 'okänt datum')
        sport = act.get('sport', {}).get('name', 'okänd sport')
        distance = act.get('distance', 0)
        duration = act.get('duration', 0)
        print(f"{date_time} - {sport}: {distance} km på {duration} sekunder")