import enum
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from webapp.database import db


class DateTimeMixin(object):
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )


class WebpageStatus(enum.Enum):
    NEW = 1
    TO_DELETE = 2
    DONE = 3


class Project(db.Model, DateTimeMixin):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    name = Column(String)


class Webpage(db.Model, DateTimeMixin):
    __tablename__ = "webpages"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    name = Column(String)
    url = Column(String)
    title = Column(String)
    description = Column(String)
    copy_doc_link = Column(String)
    parent_id = Column(Integer, ForeignKey("webpages.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))
    status = Column(Enum(WebpageStatus))

    project = relationship("Project", back_populates="webpages")
    owner = relationship("User", back_populates="webpages")


class User(db.Model, DateTimeMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    jira_account_id = Column(String)


class Stakeholder(db.Model, DateTimeMixin):
    __tablename__ = "stakeholders"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    webpage_id = Column(Integer, ForeignKey("webpages.id"))

    user = relationship("User", back_populates="stakeholders")
    webpage = relationship("Webpage", back_populates="stakeholders")


class JiraTask(db.Model, DateTimeMixin):
    __tablename__ = "jira_tasks"

    id = Column(Integer, primary_key=True)
    jira_id = Column(Integer)
    webpage_id = Column(Integer, ForeignKey("webpages.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String)
    created_at = Column(String)

    webpage = relationship("Webpage", back_populates="jira_tasks")
    user = relationship("User", back_populates="jira_tasks")
