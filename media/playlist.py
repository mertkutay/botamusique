import re
import base64
import requests
import youtube_dl
import variables as var
import media.url


def refresh_spotify_token():
    url = 'https://accounts.spotify.com/api/token'

    client_id = var.config.get('secrets', 'spotify_client_id')
    client_secret = var.config.get('secrets', 'spotify_client_secret')
    refresh_token = var.config.get('secrets', 'spotify_refresh_token')

    if not(client_id and client_secret and refresh_token):
        raise Exception('Spotify API credentials are not provided')

    auth = base64.b64encode(':'.join([client_id, client_secret]).encode()).decode('utf-8')

    res = requests.post(url,
                        headers={
                            'Authorization': 'Basic ' + auth
                        },
                        data={
                            'grant_type': 'refresh_token',
                            'refresh_token': refresh_token
                        }).json()
    access_token = res['access_token']

    var.config.set('secrets', 'spotify_access_token', access_token)


def get_spotify_playlist(url, start_index=1, user=""):
    playlist_id = re.search(r'playlist/(\w+)\??', url).group(1)

    access_token = var.config.get('secrets', 'spotify_access_token')

    res = requests.get('https://api.spotify.com/v1/playlists/{}'.format(playlist_id),
                       headers={'Authorization': 'Bearer {}'.format(access_token)}).json()
    # TODO: differentiate auth error from id error
    if 'error' in res:
        refresh_spotify_token()
        return get_spotify_playlist(url, start_index=1, user="")

    for item in res['tracks']['items']:
        title = '{} - {} ft. {}'.format(item['track']['artists'][0]['name'],
                                        item['track']['name'],
                                        ', '.join([artist['name'] for artist in item['track']['artists'][1:]]))

        for j in range(start_index, start_index + var.config.getint('bot', 'max_track_playlist')):
            music = {'type': 'url',
                     'title': title,
                     'url': media.url.search_youtube_url(title),
                     'user': user,
                     'from_playlist': True,
                     'playlist_title': res['name'],
                     'playlist_url': url,
                     'ready': 'validation'}
            var.playlist.append(music)
    return True


def get_playlist_info(url, start_index=1, user=""):
    if url.startwith('https://open.spotify.com'):
        return get_spotify_playlist(url, start_index=1, user="")

    ydl_opts = {
        'extract_flat': 'in_playlist'
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        for i in range(2):
            try:
                info = ydl.extract_info(url, download=False)
                playlist_title = info['title']
                for j in range(start_index, start_index + var.config.getint('bot', 'max_track_playlist')):
                    music = {'type': 'url',
                             'title': info['entries'][j]['title'],
                             'url': "https://www.youtube.com/watch?v=" + info['entries'][j]['url'],
                             'user': user,
                             'from_playlist': True,
                             'playlist_title': playlist_title,
                             'playlist_url': url,
                             'ready': 'validation'}
                    var.playlist.append(music)
            except youtube_dl.utils.DownloadError:
                pass
            else:
                return True
    return False


def get_music_info(index=0):
    ydl_opts = {
        'playlist_items': str(index)
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        for i in range(2):
            try:
                info = ydl.extract_info(var.playlist[0]['url'], download=False)
                if var.playlist[0]['current_index'] == index:
                    var.playlist[0]['current_duration'] = info['entries'][0]['duration'] / 60
                    var.playlist[0]['current_title'] = info['entries'][0]['title']
                elif var.playlist[0]['current_index'] == index - 1:
                    var.playlist[0]['next_duration'] = info['entries'][0]['duration'] / 60
                    var.playlist[0]['next_title'] = info['entries'][0]['title']
            except youtube_dl.utils.DownloadError:
                pass
            else:
                return True
    return False
