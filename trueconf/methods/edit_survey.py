from __future__ import annotations
from dataclasses import dataclass
from trueconf.methods.base import TrueConfMethod
from trueconf.types.responses.edit_survey_response import EditSurveyResponse


@dataclass
class EditSurvey(TrueConfMethod[EditSurveyResponse]):
    __api_method__ = "editSurvey"
    __returning__ = EditSurveyResponse

    message_id: str
    server: str
    path: str
    title: str
    description: str
    button_text: str = "{{Go to survey}}"

    def __post_init__(self):
        super().__init__()

    def payload(self):
        return {
            "messageId": self.message_id,
                "content": {
                    "path": self.path,
                    "title": self.title,
                    "description": self.description,
                    "buttonText": self.button_text,
                    "alt": f"📊 <a href='https://{self.server}/webtools/survey?id={self.path}&error=autologin_not_supported'>{self.title}</a>"
                }
        }
