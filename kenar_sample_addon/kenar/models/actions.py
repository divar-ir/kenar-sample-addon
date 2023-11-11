from enum import Enum
from typing import Optional

from kenar_sample_addon.kenar.models.encoder import CustomEncoderModel


class ActionType(Enum):
    def get_encoder_value(self):
        return self.value

    LOAD_WEB_VIEW_PAGE = 0
    OPEN_WEB_PAGE = 1


class Action(CustomEncoderModel):

    def __init__(self, action_type: ActionType, fallback_link: Optional[str] = None):
        self.action_type: ActionType = action_type
        self.fallback_link = fallback_link

    def get_encoder_value(self):
        action = {
            "type": self.action_type,
            "fallback_link": self.fallback_link,
            "payload": {
                '@type': self._any_pb_signature(),
            }
        }
        for slot in self.__slots__:
            if slot not in ('fallback_link', 'type'):
                action['payload'][slot] = getattr(self, slot)
        return action

    def _any_pb_signature(self):
        return f'type.googleapis.com/widgets.' \
               f'{"".join(f"{s[0].upper()}{s[1:].lower()}" for s in self.action_type.name.split(sep="_"))}Payload'


class LoadWebViewPage(Action):
    __slots__ = ('action_type', 'fallback_link', 'url')

    def __init__(self, url):
        self.url = url

        super().__init__(ActionType.LOAD_WEB_VIEW_PAGE, url)


class OpenWebPage(Action):
    __slots__ = ('action_type', 'fallback_link', 'link')

    def __init__(self, link):
        self.link = link

        super().__init__(ActionType.OPEN_WEB_PAGE, link)
