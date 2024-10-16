from enum import Enum

class JiraStatusTransitionCodes(Enum):
    TRIAGED = 11
    PROGRESS = 21
    IN_REVIEW = 31
    BLOCKED = 41
    TO_BE_DEPLOYED = 51
    DONE = 61
    REJECTED = 71
    UNTRIAGED = 81

