from functools import wraps
from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import List, Optional


def validate_input(model):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create a pydantic basemodel instance with provided kwargs
            # Throws a ValidationError if the input data is invalid
            model(**kwargs)
            # Call the original function with validated inputs
            return func(*args, **kwargs)

        return wrapper

    return decorator


class ChangesRequestModel(BaseModel):
    due_date: str
    reporter_id: int
    webpage_id: int
    type: int
    description: str
    summary: str = ""


class RemoveWebpageModel(BaseModel):
    webpage_id: int
    due_date: str = ""
    reporter_id: int = None
    description: str = ""

    @field_validator("due_date")
    @classmethod
    def date_validation(cls, value: str) -> str:
        assert datetime.strptime(value, "%Y-%m-%d") >= datetime.now()
        return value


class UserModel(BaseModel):
    id: int
    name: str
    email: str
    team: Optional[str]
    department: Optional[str]
    jobTitle: Optional[str]


class CreatePageModel(BaseModel):
    project: str
    name: str
    copy_doc: Optional[str] = None
    owner: UserModel
    reviewers: Optional[List[UserModel]]
    parent: str
