import youtube_dl
import media
import variables as var
from googleapiclient.discovery import build


def get_youtube_recommendation(url):
    video_id = url.split('=')[-1]
    google_api_key = var.config.get('secrets', 'google_api_key')
    if not google_api_key:
        raise Exception('Google API credentials are not provided')

    youtube = build('youtube', 'v3', developerKey=google_api_key)
    response = youtube.search().list(relatedToVideoId=video_id, part='snippet', type='video').execute()
    if len(response['items']) > 0:
        video_id = response['items'][0]['id']['videoId']
        return 'https://www.youtube.com/watch?v=' + video_id


def search_youtube_url(query):
    google_api_key = var.config.get('secrets', 'google_api_key')
    if not google_api_key:
        raise Exception('Google API credentials are not provided')

    youtube = build('youtube', 'v3', developerKey=google_api_key)

    search_response = youtube.search().list(
        q=query,
        part='id,snippet',
        type='video',
        maxResults=1
    ).execute()

    if len(search_response['items']) > 0:
        video_id = search_response['items'][0]['id']['videoId']
        return 'https://www.youtube.com/watch?v=' + video_id


def get_url_info(index=-1):
    ydl_opts = {
        'noplaylist': True
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        for i in range(2):
            try:
                print(var.playlist)
                info = ydl.extract_info(var.playlist[index]['url'], download=False)
                var.playlist[index]['duration'] = info['duration'] / 60
                var.playlist[index]['title'] = info['title']
            except youtube_dl.utils.DownloadError:
                pass
            except KeyError:
                return True
            else:
                return True
    return False
