from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def get_video_ids_from_query(youtube_api_key: str, query: str, max_results: int = 5) -> list:
    """
    Retrieves a list of video IDs from a YouTube query.
    """
    youtube = build('youtube', 'v3', developerKey=youtube_api_key)

    try:
        search_response = youtube.search().list(
            q=query,
            part='id',
            maxResults=max_results
        ).execute()

        video_ids = [item['id']['videoId'] for item in search_response['items']]
        return video_ids

    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred: {e.content}")
        return []

def get_song_audio_url(client, song_name: str, youtube_api_key: str) -> str:
    """
    Prints out the first audio stream URL for a video found by song name.
    """
    video_ids = get_video_ids_from_query(youtube_api_key, song_name)
    if not video_ids:
        print(f"No videos found for '{song_name}'.")
        return

    for video_id in video_ids:
        try:
            print(f'Trying Video ID: {video_id}')
            video = client.get_video(video_id)
            print(f"Video requested: {video}")
            audio_streams = video.get_streams('audio')
            print(f"Audio from video requested: {audio_streams}")

            if audio_streams:
                audio_stream = audio_streams[0]
                print(f"Audio stream URL: {audio_stream.url} ({audio_stream.mime_type})")
                return audio_stream.url
            else:
                print(f"No audio streams found for video ID {video_id}.")

        except Exception as e:
            print(f"Error with video ID {video_id}: {e}")

    print(f"Unable to find a working audio stream for '{song_name}'.")
    return