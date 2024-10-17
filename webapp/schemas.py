from functools import wraps

from typing import List, Optional
from pydantic import BaseModel


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
