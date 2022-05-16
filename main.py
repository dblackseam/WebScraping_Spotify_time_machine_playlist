from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pprint import pprint
import os

CID_SPOTIFY = os.environ["CLIENT_ID_SPOTIFY"]
CLIENT_SECRET_SPOTIFY = os.environ["CLIENT_SECRET_SPOTIFY"]
URI = "http://example.com"
SCOPE = "playlist-modify-private playlist-read-private user-read-recently-played"

# OAuth's authentication below ⬇
token = SpotifyOAuth(client_id=CID_SPOTIFY,
                     client_secret=CLIENT_SECRET_SPOTIFY,
                     redirect_uri=URI,
                     scope=SCOPE)

spotipy_api = spotipy.Spotify(oauth_manager=token)
user_id = spotipy_api.current_user()["id"]

user_year = input("Which year do you want to travel to? First things first you'll have to enter a year: ")
user_month = input("Which month of the year? (format = 03,12,etc.): ")
user_day = input("Which date of the month? (01,02,03...31): ")
formatted_date = f"{user_year}-{user_month}-{user_day}"

response = requests.get(f"https://www.billboard.com/charts/hot-100/{formatted_date}/")
soup = BeautifulSoup(response.text, "html.parser")

song_titles = soup.select(".o-chart-results-list__item h3")
formatted_song_titles = [title.getText().strip().replace("'", "") for title in song_titles]

artists_names = soup.select(".o-chart-results-list__item .a-font-primary-s")
formatted_artist_names = [artist.getText().strip().split("Featuring")[0] for artist in artists_names]

artist_song_tuples = tuple(zip(formatted_artist_names, formatted_song_titles))

songs_uri_list = []
for artist0_song1 in artist_song_tuples:
    song_in_spotify = spotipy_api.search(q=f"artist:{artist0_song1[0]} track:{artist0_song1[1]}", limit=2)
    if not song_in_spotify["tracks"]["items"]:
        pass
    else:
        songs_uri_list.append(song_in_spotify["tracks"]["items"][0]["uri"])

create_playlist = spotipy_api.user_playlist_create(user=user_id,
                                                   name=f"{formatted_date} Billboard 100",
                                                   public="False")

spotipy_api.playlist_add_items(playlist_id=create_playlist["id"], items=songs_uri_list)

