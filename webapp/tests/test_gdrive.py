from typing import Callable, Literal, Optional

import pytest

from webapp import create_app
from webapp.gdrive import GoogleDriveClient
from webapp.tests.fixtures import db_session, project, webpage


class MockService(GoogleDriveClient):
    """
    Mock Google sdk service calls:
        service.files().list().execute().
        service.files().create().execute().
    """

    def __init__(self):
        self._files = self._get_files()
        self.files = lambda: self

    def _get_files(self) -> list[dict]:
        return [
            {"id": "1", "name": "ubuntu.com"},
            {"id": "123", "name": "ubuntu.com/landscape"},
            {"id": "456", "name": "canonical.com/data/spark"},
        ]

    def list(self, **kwargs):
        self.execute = self.__execute__("list")
        return self

    def create(self, **kwargs):
        # Check that these values are passed in the create call
        kwargs["body"]["mimeType"]
        kwargs["body"]["parents"][0]
        self.execute = self.__execute__("create", kwargs["body"]["name"])
        return self

    def copy(self, **kwargs):
        # Check that these values are passed in the copy call
        kwargs["fileId"]
        kwargs["body"]["mimeType"]
        kwargs["body"]["parents"][0]
        self.execute = self.__execute__("copy", kwargs["body"]["name"])
        return self

    def __execute__(
        self,
        name: Literal["create", "list", "copy"],
        value: Optional[str] = None,
    ) -> Callable:
        if name == "list":
            return lambda: {"files": self._files}
        elif name == "create" or name == "copy":
            # URLS have leading and trailing slashes, so remove them
            if value:
                value = value.strip("\\/")
            new_file = {"id": f"id-{value}", "name": value}
            self._files.append(new_file)
            # Return a predictable, unique id
            return lambda: {"id": f"id-{value}", "name": value}


@pytest.fixture
def mock_gdrive(monkeypatch):
    monkeypatch.setattr(
        "webapp.gdrive.GoogleDriveClient._build_service",
        lambda _, x: MockService(),
    )


def test_app_starts_without_gdrive():
    app = create_app()
    assert "gdrive" not in app.config


def test_initialize_client(mock_gdrive):
    app = create_app()
    assert "gdrive" in app.config


def test_item_exists(mock_gdrive):
    app = create_app()
    gdrive = app.config["gdrive"]
    assert gdrive._item_exists("ubuntu.com/landscape/features") == "123"


def test_create_folder(mock_gdrive):
    app = create_app()
    gdrive = app.config["gdrive"]
    assert gdrive.create_folder("folder1", "folderparent") == "id-folder1"


def test_build_webpage_folder(mock_gdrive, webpage):
    app = create_app()
    gdrive = app.config["gdrive"]
    assert gdrive.build_webpage_folder(webpage) == "id-data"

def test_copy_file(mock_gdrive):
    app = create_app()
    gdrive = app.config["gdrive"]
    assert gdrive.copy_file("1", "file1", ["parent1"]).get("name") == "file1"


def test_create_copydoc_from_template(mock_gdrive, webpage):
    app = create_app()
    gdrive = app.config["gdrive"]
    assert (
        gdrive.create_copydoc_from_template(webpage).get("name")
        == "data/opensearch"
    )