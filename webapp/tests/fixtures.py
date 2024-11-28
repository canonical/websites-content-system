import pytest

from webapp import create_app
from webapp.models import Project, Webpage, db


@pytest.fixture(scope="session")
def db_session():
    app = create_app()
    with app.app_context():
        db.create_all()
        yield db.session
        db.session.close()
        db.drop_all()


@pytest.fixture(scope="session")
def project(db_session):
    project = Project(name="ubuntu.com")
    db_session.add(project)
    db_session.commit()
    return project


@pytest.fixture(scope="session")
def webpage(db_session, project):
    webpage = Webpage(
        name="/data/opensearch",
        url="/data/opensearch",
        project_id=project.id,
    )
    db_session.add(webpage)
    db_session.commit()
    return webpage
