import enum
from datetime import datetime, timezone

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship
from sqlalchemy.orm.session import Session


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base, engine_options={"poolclass": None})


def get_or_create(session: Session, model: Base, commit=True, **kwargs):
    """
    Return an instance of the specified model if it exists, otherwise create a
    new instance.

    :param session: The database session to use for querying and committing
        changes.
    :param model: The model class to query and create instances of.
    :param kwargs: The filter criteria used to query the database for an
        existing instance.
    :return: An instance of the specified model.
    """
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        instance = model(**kwargs)
        session.add(instance)
        # Allow adding multiple instances before committing
        if commit:
            session.commit()
        return instance, True


class DateTimeMixin(object):
    created_at: Mapped[datetime] = Column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
        nullable=False,
    )


class WebpageStatus(enum.Enum):
    NEW = "NEW"
    TO_DELETE = "TO_DELETE"
    AVAILABLE = "AVAILABLE"


class Project(db.Model, DateTimeMixin):
    __tablename__ = "projects"

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String, nullable=False)
    webpages = relationship("Webpage", back_populates="project")


class Webpage(db.Model, DateTimeMixin):
    __tablename__ = "webpages"

    id: int = Column(Integer, primary_key=True)
    project_id: int = Column(Integer, ForeignKey("projects.id"))
    name: str = Column(String, nullable=False)
    url: str = Column(String, nullable=False)
    title: str = Column(String)
    description: str = Column(String)
    copy_doc_link: str = Column(String)
    parent_id: int = Column(Integer, ForeignKey("webpages.id"))
    owner_id: int = Column(Integer, ForeignKey("users.id"))
    status: str = Column(Enum(WebpageStatus), default=WebpageStatus.NEW)

    project = relationship("Project", back_populates="webpages")
    owner = relationship("User", back_populates="webpages")
    reviewers = relationship("Reviewer", back_populates="webpages")
    jira_tasks = relationship("JiraTask", back_populates="webpages")


class User(db.Model, DateTimeMixin):
    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String, nullable=False)
    email: str = Column(String)
    jira_account_id: str = Column(String)
    team: str = Column(String)
    department: str = Column(String)
    hrc_id: int = Column(Integer)
    job_title: str = Column(String)

    webpages = relationship("Webpage", back_populates="owner")
    reviewers = relationship("Reviewer", back_populates="user")
    jira_tasks = relationship("JiraTask", back_populates="user")


class Reviewer(db.Model, DateTimeMixin):
    __tablename__ = "reviewers"

    id: int = Column(Integer, primary_key=True)
    user_id: int = Column(Integer, ForeignKey("users.id"))
    webpage_id: int = Column(Integer, ForeignKey("webpages.id"))

    user = relationship("User", back_populates="reviewers")
    webpages = relationship("Webpage", back_populates="reviewers")


class JiraTask(db.Model, DateTimeMixin):
    __tablename__ = "jira_tasks"

    id: int = Column(Integer, primary_key=True)
    jira_id: int = Column(Integer)
    webpage_id: int = Column(Integer, ForeignKey("webpages.id"))
    user_id: int = Column(Integer, ForeignKey("users.id"))
    status: str = Column(String)  # Will be filled from Jira API
    created_at: str = Column(String)

    webpages = relationship("Webpage", back_populates="jira_tasks")
    user = relationship("User", back_populates="jira_tasks")


def init_db(app: Flask):
    Migrate(app, db)
    db.init_app(app)

    # Create default project and user
    @app.before_request
    def create_default_project():
        app.before_request_funcs[None].remove(create_default_project)
        get_or_create(db.session, Project, name="Default")
        get_or_create(db.session, User, name="Default")
