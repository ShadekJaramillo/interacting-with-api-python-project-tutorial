import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from dotenv import load_dotenv

def set_API_client(spotify_client: spotipy.Spotify):
    global spotify
    spotify = spotify_client

def album_ids(artist_id, album_type, *args, **kwargs):
    response = spotify.artist_albums(artist_id, album_type = album_type, *args, **kwargs)
    albums = response['items']
    is_album_type = lambda album: album['album_type'] == album_type and album['album_group'] == album_type
    album_id_list = [album['id'] for album in albums if is_album_type(album)]

    return album_id_list

def track_ids_from_album(album_id):
    tracks = spotify.album_tracks(album_id)['items']
    ids = [track['id'] for track in tracks]
    return ids

def create_packs(id_list):
    num_packs = len(id_list) // 50

    packs = [id_list[n:n+50] for n in range(num_packs)]
    packs.append(id_list[num_packs*50:])

    return packs

def tracks_from_ids(track_id_list):
    track_id_packs = create_packs(track_id_list)

    tracks = []
    for track_id_pack in track_id_packs:
        tracks.extend(spotify.tracks(track_id_pack)['tracks'])

    return tracks

def artist_tracks(artist_id, album_type, *args, **kwargs):
    "same arguments as the spotify.artist_albums function"
    album_id_list = album_ids(artist_id, album_type, *args, **kwargs)
    track_ids = []
    for album_id in album_id_list:
        track_ids.extend(track_ids_from_album(album_id))

    tracks = tracks_from_ids(track_ids)
    return tracks

def create_df_from_tracks(track_list):
    songs = []
    for track in track_list:
        songs.append({'name':track['name'],
                    'popularity':track['popularity'],
                    'duration_min':track['duration_ms']/60000,
                    'album': track['album']['name']})
        
    df = pd.DataFrame(songs)
    return df


if __name__ == "__main__":
    # load the .env file variables
    load_dotenv()

    # Spotify API credentials
    client_id = os.environ.get("CLIENT_ID")
    client_secret = os.environ.get("CLIENT_SECRET")

    auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    artist_id = '0yLwGBQiBqhXOvmTfH2A7n'
    results = spotify.artist_top_tracks(artist_id)


    songs = []
    for track in results['tracks']:
        songs.append({'name':track['name'],
                    'popularity':track['popularity'],
                    'duration_min':track['duration_ms']/60000})
        
    df = pd.DataFrame(songs)
    print('Important Note:\nThe rest of the activity including plots and analysis are in the explore.ipynb notebook')
    print(df)
