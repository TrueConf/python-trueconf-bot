from enum import Enum


class SurveyType(str, Enum):
    NON_ANONYMOUS = "{{Survey}}"
    ANONYMOUS = "{{Anonymous survey}}"
