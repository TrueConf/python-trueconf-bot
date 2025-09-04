from __future__ import annotations
from __future__ import annotations
from dataclasses import dataclass
from trueconf.methods.base import TrueConfMethod
from trueconf.types.responses.send_survey_response import SendSurveyResponse


@dataclass
class SendSurvey(TrueConfMethod[SendSurveyResponse]):
    __api_method__ = "sendSurvey"
    __returning__ = SendSurveyResponse

    chat_id: str
    server: str
    path: str
    title: str
    secret: str
    description: str
    button_text: str = "{{Go to survey}}"
    reply_message_id: str | None = None
    app_version: int = 1

    def __post_init__(self):
        super().__init__()

    def payload(self):
        return {
            "chatId": self.chat_id,
            "replyMessageId": self.reply_message_id,
            "content": {
                "url": f"https://{self.server}/webtools/survey",
                "appVersion": self.app_version,
                "path": self.path,
                "title": self.title,
                "description": self.description,
                "buttonText": self.button_text,
                "secret": self.secret,
                "alt": f"📊 <a href='https://{self.server}/webtools/survey?id={self.path}&error=autologin_not_supported'>{self.title}</a>"
            }
        }
