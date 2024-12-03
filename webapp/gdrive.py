import difflib
from typing import Any, Optional

from flask import Flask
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from webapp.models import Webpage


class GoogleDriveClient:
    # If modifying these scopes, delete the file token.json.
    SCOPES = ["https://www.googleapis.com/auth/drive"]

    def __init__(
        self, credentials: dict, drive_folder_id: str, copydoc_template_id: str
    ):
        self.service = self._build_service(credentials)
        self.GOOGLE_DRIVE_FOLDER_ID = drive_folder_id
        self.COPYD0C_TEMPLATE_ID = copydoc_template_id

    def _build_service(self, credentials: dict) -> Any:
        """
        Build a google drive service object.

        Args:
            credentials (dict): A dict containing google authentication keys.

        Returns:
            googleapiclient.discovery.Resource: A google drive service object.
        """
        credentials = service_account.Credentials.from_service_account_info(
            credentials,
            scopes=self.SCOPES,
        )
        return build("drive", "v3", credentials=credentials)

    def _item_exists(
        self,
        folder_name: str,
        parent=None,
        mime_type="'application/vnd.google-apps.folder'",
    ) -> Optional[str]:
        """
        Check whether an item exists in Google Drive. Optionally, check if the
        item exists in a specific parent folder. If there are several matches,
        we take the result closest to the site (project) name.

        Args:
            folder_name (str): The name of the folder to check.
            parent (str): The parent folder to check in.
            mime_type (str): The mime type of the item to check.

        Returns:
            str: The id of the item if it exists, otherwise None.

        Raises:
            ValueError: If an error occurs while querying the Google Drive API
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
            item_names = [item["name"] for item in data]
            # Get the closest match to the folder name, or return None.
            try:
                result = difflib.get_close_matches(folder_name, item_names)[0]
            except IndexError:
                return None

            # Return the file id
            result_id = next(
                item["id"] for item in data if item["name"] == result
            )
            return result_id
        return None

    def create_folder(self, name: str, parent: str) -> str:
        """
        Create a folder in the Google Drive.

        Args:
            name (str): The name of the folder to create.
            parent (str): The parent folder to create the folder in.

        Returns:
            str: The id of the created folder.

        Raises:
            ValueError: If an error occurs while creating the folder.
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

    def build_webpage_folder(self, webpage) -> str:
        """
        Create a folder hierarchy in Google Drive for a webpage. The path is
        derived from the webpage's URL, with each part of the path representing
        a folder. The topmost folder will be the project name.

        Args:
            webpage (Webpage): The webpage object to create a folder hierarchy.

        Returns:
            str: The id of the folder, which is a leaf node in the hierarchy.
        """
        folders = [f"/{f}" for f in webpage.url.split("/")[:-1] if f != ""]
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
            if not (folder_id := self._item_exists(folder, parent)):
                folder_id = self.create_folder(folder, parent)
            parent = folder_id

        # Return the last parent folder
        return parent

    def copy_file(self, fileID: str, name: str, parents: list[str]) -> dict:
        """
        Copy a file in Google Drive.

        Args:
            fileID (str): The id of the file to copy.
            name (str): The name to give the copied file.
            parents (list[str]): Ids of folders to copy the file to.

        Returns:
            dict: The metadata of the copied file.

        Raises:
            ValueError: If an error occurs while copying the file.
        """
        try:
            copy_metadata = {
                "name": name,
                "parents": parents,
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
        except Exception as error:
            raise ValueError(
                f"An error occurred when copying copydoc template: {error}"
            )

    def create_copydoc_from_template(self, webpage: Webpage) -> dict:
        """
        Create a copydoc from a template. The document is created in the folder
        for the webpage project.

        Args:
            webpage (Webpage): The webpage object to create a copydoc for.

        Returns:
            dict: The metadata of the copied file.
        """
        # Create the folder hierarchy for the webpage
        webpage_folder = self.build_webpage_folder(webpage)

        # Clone the template document to the new folder
        return self.copy_file(
            fileID=self.COPYD0C_TEMPLATE_ID,
            name=webpage.url,
            parents=[webpage_folder],
        )


def init_gdrive(app: Flask) -> None:
    try:
        app.config["gdrive"] = GoogleDriveClient(
            credentials=app.config["GOOGLE_CREDENTIALS"],
            drive_folder_id=app.config["GOOGLE_DRIVE_FOLDER_ID"],
            copydoc_template_id=app.config["COPYDOC_TEMPLATE_ID"],
        )
    except Exception as error:
        app.logger.info(f"Unable to initialize gdrive: {error}")
