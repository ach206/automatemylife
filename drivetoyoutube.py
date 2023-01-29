import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
import json

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
CREDS = None
def auth():
    # Use the application default credentials
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
    creds = None
    if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
    return creds

youtube = build('youtube', 'v3', credentials=auth())


def uploadVideos(videos):
    # Iterate through the files and upload the mp4 file to YouTube
    if not videos:
        print('No files found.')
    for key, value in videos.items():
        file = key
        file_path = value
        # Create a MediaFileUpload object for the mp4 file
        media = MediaFileUpload(
            file_path, chunksize=-1, resumable=True)
        # Create a request to upload the mp4 file to YouTube
        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": file,
                    "description": "Uploaded from Google Drive"
                },
                "status": {
                    "privacyStatus": "private"
                }
            },
            media_body=media
        )
        request.execute()


def find_mp4_files(directory):
    mp4_files = []
    mp4_filenames = {}
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".mp4"):
                mp4_files.append(os.path.join(root, file))
    for video in mp4_files:
        mp4_filenames[os.path.basename(video)] = video
    uploadVideos(mp4_filenames)


mp4_files = find_mp4_files("/Users/camillionaire/Downloads")