import requests
import json
import os
from dotenv import load_dotenv
from datetime import date
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")
CHANNEL_HANDLE ="MrBeast"
maxResults = 50

def get_playlist_id():
    try:
        url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={API_KEY}"
        response = requests.get(url)
        # Raise an exception if the request failed
        response.raise_for_status() 
        data = response.json()
        channel_item = data['items'][0]
        channel_playlist_id = channel_item["contentDetails"]["relatedPlaylists"]["uploads"]
        #print(channel_playlist_id)
        return channel_playlist_id
    
            # Handles request-related errors
    except requests.exceptions.RequestException as e:
      raise e
    
def get_video_ids(playlistId):
    video_ids = []
    pageTokens = None
    
    base_url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={maxResults}&playlistId={playlistId}&key={API_KEY}"
    try:
       while True:
          url = base_url
          if pageTokens:
             url+= f"&pageToken={pageTokens}"
          
          response = requests.get(url)
        # Raise an exception if the request failed
          response.raise_for_status()
          data = response.json()


          for items in data.get("items", []):
             video_id = items['contentDetails']['videoId']
             video_ids.append(video_id)
        
          pageTokens = data.get("nextPageToken")

          if not pageTokens:
             break
          
       return video_ids
    except requests.exceptions.RequestException as e:
      raise e

def extract_video_data(video_ids):
    extracted_data = []

    def batch_list(video_id_lst, batch_size):
        for index in range(0, len(video_id_lst), batch_size):
            yield video_id_lst[index:index + batch_size]

    try:
        for batch in batch_list(video_ids, maxResults):
            video_ids_str = ",".join(batch)

            url = f"https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails,snippet,statistics&id={video_ids_str}&key={API_KEY}"

            response = requests.get(url)
            response.raise_for_status()

            data = response.json()

            for item in data.get("items", []):
                snippet = item["snippet"]
                contentDetails = item["contentDetails"]
                statistics = item["statistics"]

                video_data = {
                    "video_id": item["id"],
                    "title": snippet["title"],
                    "publishedAt": snippet["publishedAt"],
                    "duration": contentDetails["duration"],
                    "viewCount": statistics.get("viewCount"),
                    "likeCount": statistics.get("likeCount"),
                    "commentCount": statistics.get("commentCount"),
                }

                extracted_data.append(video_data)

        return extracted_data

    except requests.exceptions.RequestException as e:
        raise e
    

def save_to_json(extracted_data):
    os.makedirs("data", exist_ok=True)
    file_path = f"./data/YT_data.json_{date.today()}"
    
    with open(file_path, "w", encoding="utf-8") as json_outfile:
        json.dump(extracted_data, json_outfile, indent=4, ensure_ascii= False)



if __name__ == "__main__":
    playlistID = get_playlist_id()
    video_ids = get_video_ids( playlistID)
    video_data =extract_video_data(video_ids)
    save_to_json(video_data)





