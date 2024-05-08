from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def get_video_id_from_query(youtube_api_key: str, query: str) -> str:
    """
    Retrieves the video ID from a YouTube query.
    """
    youtube = build('youtube', 'v3', developerKey=youtube_api_key)

    try:
        search_response = youtube.search().list(
            q=query,
            part='id',
            maxResults=1
        ).execute()

        video_id = search_response['items'][0]['id']['videoId']
        return video_id

    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred: {e.content}")

def get_song_audio_url(client, song_name: str, youtube_api_key: str) -> str:
    """
    Prints out the first audio stream URL for a video found by song name.
    """
    video_id = get_video_id_from_query(youtube_api_key, song_name)
    if not video_id:
        print(f"No video found for '{song_name}'.")
        return

    video = client.get_video(video_id)
    audio_streams = video.get_streams('audio')

    if not audio_streams:
        print(f"No audio streams found for '{song_name}'.")
        return

    audio_stream = audio_streams[0]
    print(f"Audio stream URL: {audio_stream.url} ({audio_stream.mime_type})")
    return audio_stream.url




