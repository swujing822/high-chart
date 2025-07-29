from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
import os

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def main():
    creds = None
    if os.path.exists('drive/token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # if not creds or not creds.valid:
    #     if creds and creds.expired and creds.refresh_token:
    #         creds.refresh(Request())
    #     else:
    #         flow = InstalledAppFlow.from_client_secrets_file('desk.json', SCOPES)
    #         creds = flow.run_local_server(port=0)
    #     with open('token.json', 'w') as token:
    #         token.write(creds.to_json())

    service = build('drive', 'v3', credentials=creds)

    # ✅ 上传 drive.zip
    file_metadata = {'name': 'drive.zip'}
    media = MediaFileUpload('drive.zip', mimetype='application/zip')
    uploaded = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print("✅ 上传成功，文件 ID:", uploaded.get("id"))

if __name__ == '__main__':
    main()
