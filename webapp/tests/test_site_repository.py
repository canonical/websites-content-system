from webapp import create_app
from webapp.site_repository import SiteRepository


def test_initialize_site_repository():
    app = create_app()
    site_repository = SiteRepository(
        "ubuntu.com",
        app,
    )
    assert site_repository.repository_uri == "ubuntu.com"
