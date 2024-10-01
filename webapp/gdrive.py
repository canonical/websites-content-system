import base64
import os
import tempfile

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GoogleDriveClient:
    # If modifying these scopes, delete the file token.json.
    SCOPES = [
        "https://www.googleapis.com/auth/drive.metadata.readonly",
        "https://www.googleapis.com/auth/drive.file",
    ]

    def __init__(self):
        self.credentials = self._get_credentials()
        self.service = self._build_service()
        self.GOOGLE_DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
        self.COPYD0C_TEMPLATE_ID = os.getenv("COPYD0C_TEMPLATE_ID")

    def _get_credentials(self):
        """
        Load credentials from a base64 encoded environment variable.
        """
        credentials_text = os.getenv("GOOGLE_SERVICE_ACCOUNT")
        with tempfile.NamedTemporaryFile(delete_on_close=False) as f:
            f.write(base64.decode(credentials_text))
            f.close()

            return service_account.Credentials.from_service_account_file(
                f.name,
                scopes=self.SCOPES,
            )

    def _build_service(self):
        return build("drive", "v3", credentials=self.credentials)

    def create_copydoc_from_template(self, webpage):
        """
        Create a copydoc from a template. The document is created in the folder
        for the webpage project.
        """
        parents = [self.GOOGLE_DRIVE_FOLDER_ID]
        # Create a folder if it does not exist
        if not self.find_folder(webpage.project.name):
            parents = [self.create_folder(webpage.project.name)]
        try:
            copy_metadata = {
                "name": webpage.url,
                "parents": parents,
            }
            copy = (
                self.service.files()
                .copy(
                    fileId=self.COPYD0C_TEMPLATE_ID,
                    body=copy_metadata,
                )
                .execute()
            )
            return copy
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

    def create_folder(self, name):
        """
        Create a folder in the Google Drive.
        """
        try:
            folder_metadata = {
                "name": name,
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [self.GOOGLE_DRIVE_FOLDER_ID],
            }
            folder = (
                self.service.files()
                .create(body=folder_metadata, fields="id")
                .execute()
            )
            return folder
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

    def find_folder(service, folder_name):
        """
        Check if a folder with the given name exists in Google Drive, to
        prevent creating duplicate folders.
        """
        query = (
            f"name = '{folder_name}' and mimeType = "
            "'application/vnd.google-apps.folder' and trashed = false"
        )
        results = (
            service.files()
            .list(
                q=query, spaces="drive", fields="files(id, name)", pageSize=10
            )
            .execute()
        )

        items = results.get("files", [])
        return items

    def list_files(self, page_size=10):
        try:
            results = (
                self.service.files()
                .list(
                    pageSize=page_size,
                    fields="nextPageToken, files(id, name)",
                )
                .execute()
            )
            items = results.get("files", [])
            return items
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None
