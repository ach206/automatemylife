import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
import json

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/youtube.upload']

# Use the application default credentials
creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
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

initialize_drive = build('drive', 'v2', credentials=creds)
selected_folder_id = '13NzfUDyseTmw6Nj7XDeYTdkuEx73XUE3'
youtube = build('youtube', 'v3', credentials=creds)

def get_files_in_folder(service, folder_id):
  """Print files belonging to a folder.

  Args:
    service: Drive API service instance.
    folder_id: ID of the folder to print files from.
  """
  file_ids = []
  try:
    param = {}
    children = service.children().list(folderId=folder_id, **param).execute()
    # get the ID's of the files and append them to list
    for child in children.get('items', []):
      file_ids.append(child['id'])
    # do something with ID's
    doSomething(file_ids)

  except HttpError as error:
      print(F'An error occurred: {error}')


def doSomething(ids):
    # Iterate through the files and upload the mp4 file to YouTube
    if not ids:
        print('No files found.')
    for item in ids:
        file = initialize_drive.files().get(fileId=item).execute()
        print(json.dumps(file, sort_keys=True, indent=4))
        file_id = file['id']
        file_name = file['title']
        # Create a MediaFileUpload object for the mp4 file
        media = MediaFileUpload(
            '../../../Downloads/2023-01-13-215700325.mp4', mimetype=file['mimeType'], chunksize=-1, resumable=True)
        # Create a request to upload the mp4 file to YouTube
        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": file_name,
                    "description": "Uploaded from Google Drive"
                },
                "status": {
                    "privacyStatus": "private"
                }
            },
            media_body=media
        )
        response = request.execute()
        print(response)
        # print(F'File ID: {file_id} has been upload to YouTube with video ID: {response["id"]}')


get_files_in_folder(service=initialize_drive, folder_id=selected_folder_id)
