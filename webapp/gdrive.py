import difflib

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GoogleDriveClient:
    # If modifying these scopes, delete the file token.json.
    SCOPES = ["https://www.googleapis.com/auth/drive"]

    def __init__(
        self, credentials, drive_folder_id=None, copydoc_template_id=None
    ):
        self.credentials = self._get_credentials(credentials)
        self.service = self._build_service()
        self.GOOGLE_DRIVE_FOLDER_ID = drive_folder_id
        self.COPYD0C_TEMPLATE_ID = copydoc_template_id

    def _get_credentials(self, credentials):
        """Load credentials from an object."""

        return service_account.Credentials.from_service_account_info(
            credentials,
            scopes=self.SCOPES,
        )

    def _build_service(self):
        return build("drive", "v3", credentials=self.credentials)

    def _item_exists(
        self,
        folder_name,
        parent=None,
        mime_type="'application/vnd.google-apps.folder'",
    ):
        """
        Check whether an item exists in Google Drive.
        """
        query = (
            f"name = '{folder_name}' and "
            f"mimeType = {mime_type} and "
            "trashed = false"
        )
        if parent:
            query += f" and '{parent}' in parents"
        try:
            results = (
                self.service.files()
                .list(
                    q=query,
                    spaces="drive",
                    fields="files(id, name)",
                    pageSize=10,
                )
                .execute()
            )
        except HttpError as error:
            raise ValueError(f"An error occurred: Query:{query} Error:{error}")

        if data := results.get("files"):
            # Get the closest match to the folder name, if there are several
            item_names = [item["name"] for item in data]
            result = difflib.get_close_matches(folder_name, item_names)[0]
            # Return the file id
            result_id = next(
                item["id"] for item in data if item["name"] == result
            )
            return result_id

    def create_folder(self, name, parent):
        """
        Create a folder in the Google Drive.
        """
        try:
            folder_metadata = {
                "name": name,
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [parent],
            }
            folder = (
                self.service.files()
                .create(body=folder_metadata, fields="id")
                .execute()
            )
            return folder.get("id")
        except HttpError as error:
            raise ValueError(
                f"An error occurred when creating a new folder: {error}"
            )

    def build_webpage_folder(self, webpage):
        """
        Create a folder hierarchy in Google Drive for a webpage.
        """
        folders = webpage.url.split("/")[:-1]
        # Check if the project folder exists, or create one
        if not (
            parent := self._item_exists(
                webpage.project.name, parent=self.GOOGLE_DRIVE_FOLDER_ID
            )
        ):
            parent = self.create_folder(
                webpage.project.name, self.GOOGLE_DRIVE_FOLDER_ID
            )

        # Create subfolders
        for folder in folders:
            if folder != "":
                folder_id = self.create_folder(folder, parent)
                parent = folder_id

        # Return the last parent folder
        return parent

    def copy_file(self, fileID, name, parents):
        """
        Create a copydoc from a template. The document is created in the folder
        for the webpage project.
        """
        try:
            copy_metadata = {
                "name": name,
                "parents": [parents],
                "mimeType": "application/vnd.google-apps.file",
            }
            copy = (
                self.service.files()
                .copy(
                    fileId=fileID,
                    body=copy_metadata,
                )
                .execute()
            )
            return copy
        except HttpError as error:
            raise ValueError(
                f"An error occurred when copying copydoc template: {error}"
            )

    def create_copydoc_from_template(self, webpage):
        """
        Create a copydoc from a template. The document is created in the folder
        for the webpage project.
        """
        # Create the folder hierarchy for the webpage
        webpage_folder = self.build_webpage_folder(webpage)

        # Clone the template document to the new folder
        doc_name = f'{webpage.url} - "{webpage.title}"'
        self.copy_file(
            fileID=self.COPYD0C_TEMPLATE_ID,
            name=doc_name,
            parents=webpage_folder,
        )


def init_gdrive(app):
    app.config["gdrive"] = GoogleDriveClient(
        credentials=app.config["GOOGLE_CREDENTIALS"],
        drive_folder_id=app.config["GOOGLE_DRIVE_FOLDER_ID"],
        copydoc_template_id=app.config["COPYD0C_TEMPLATE_ID"],
    )
