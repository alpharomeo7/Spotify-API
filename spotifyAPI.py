import requests, json
import time
class SpotifyAPI:
  def __init__(self):
    self._encoded_client_credentials = '<Your Encoded CRedideitnals>' # base64 encoded "client_id:client_secret"
    self._create_headers()
    self._base_url = 'https://api.spotify.com/v1/'


  def _create_headers(self):
    ## Obtaining bearer token
  
    headers = {
        'Authorization': 'Basic ' + self._encoded_client_credentials,
    }

    data = {
      'grant_type': 'client_credentials'
    }

    response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)
    bearer_token = 'Bearer ' + json.loads(response.text)['access_token']

    headers = {
        'Authorization': bearer_token,
    }
    self._headers = headers
    print("New Headers Created")
 
  def _request_api(self, endpoint):
    """
    Requests API and Returns JSON Response
    """
    response = requests.get(self._base_url + endpoint, headers = self._headers)

    if response.status_code == 200:
      return json.loads(response.text)

    if response.status_code == 401: 
      print("Headers Expired")
      self._create_headers()
      self._request_api(endpoint)

    if response.status_code == 429:
      print("Max Request Limit reached")
      time.sleep(3)
      self._request_api(endpoint)
   
  def album(self, album_id): 
    return self._request_api('albums/{}'.format(album_id))
    
  def artist(self, artist_id): 
    return self._request_api('artists/{}'.format(artist_id))
    
  def albums_of(self, artist_id): 
    return self._request_api('artists/{}/albums?limit=50'.format(artist_id))['items']

  def tracks_of_(self, album_id): 
    return self._request_api('albums/{}/tracks?limit=50'.format(album_id))['items']

  def audio_analysis_of(self, track_ids):
    results = []
    query = ','.join(track_ids)
    response = self._request_api('audio-features/?ids='+query)
    if(response is None): 
      return[]
    results +=  response["audio_features"]
    return results
  
  def top_tracks_of(self, artist_id,country): 
    print(self._base_url + 'artists/{}/top-tracks'.format(artist_id))
    return self._request_api('artists/{}/top-tracks'.format(artist_id))

  def search_artist(self, name): 
    try: 
      return self._request_api('search?q=' + name+ '&type=artist')['artists']['items'][0]
    except: 
      return None
      
s = SpotifyAPI()


class Album:
  def __init__(self, album_id): 
    self._album_id = album_id
    self.info = s.album(self._album_id)
    self._tracks = self.info['tracks']['items']



  def analyze(self): 
    track_ids = [track['id'] for track in self._tracks] 
    self._analyzed_tracks = [track for track in s.audio_analysis_of(track_ids) if track]
    for a_track in self._analyzed_tracks: 
        track = self._get_track(a_track['id'])
        a_track['name'] = track['name']
        a_track['album'] = self.info['name']
        a_track['release_date'] = self.info['release_date']
        a_track['release_year'] = int(self.info['release_date'][:4])
        a_track['genres'] = self.info['genres']
    return self._analyzed_tracks
  
  def _get_track(self,track_id): 
    for track in self._tracks: 
      if track['id'] == track_id: 
        return track

  def __repr__(self): 
    return self.info['name']
 
    

class Artist: 
  def __init__(self,artist_id): 
    self.info = s.artist(artist_id) 
    self._album_ids = [ a['id'] for a in s.albums_of(artist_id)]
    self.albums = [Album(album_id) for album_id in self._album_ids]
    self.info['albums'] = len(self.albums)
    self.info['first_release_date'] = min([a.info['release_date'] for a in self.albums])
    self.info['last_release_date'] = max([a.info['release_date'] for a in self.albums])
    #self.top_tracks = s.top_tracks_of(artist_id)
    self.analyzed_tracks = []
  
  def analyze(self):
    for album in self.albums: 
      self.analyzed_tracks += album.analyze()
    return self

  def save(self):
    with open(self.info['id']+'.json','w') as outputfile: 
      json.dump({'info':self.info, 'analyzed_tracks': self.analyzed_tracks},outputfile, indent = "\t")
