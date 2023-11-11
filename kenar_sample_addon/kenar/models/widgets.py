from enum import Enum
from typing import Optional

from kenar_sample_addon.kenar.models.encoder import CustomEncoderModel
from kenar_sample_addon.kenar.models.actions import Action, ActionType
from kenar_sample_addon.kenar.models.icons import Icon


class WidgetType(Enum):
    LEGEND_TITLE_ROW = 0
    DESCRIPTION_ROW = 1
    SUBTITLE_ROW = 2
    SELECTOR_ROW = 3
    EVENT_ROW = 4


class Widget(CustomEncoderModel):
    def __init__(self, widget_type: WidgetType):
        super().__init__()
        self.widget_type: WidgetType = widget_type

    def get_encoder_value(self):
        widget = {
            "widget_type": self.widget_type,
            "data": {
                '@type': self.any_pb_signature(),
            }
        }
        for slot in self.__slots__:
            if slot not in ('widget_type',):
                widget['data'][slot] = getattr(self, slot)
        return widget

    def any_pb_signature(self):
        return f'type.googleapis.com/widgets.' \
               f'{"".join(f"{s[0].upper()}{s[1:].lower()}" for s in self.widget_type.name.split(sep="_"))}Data'


class LegendTitleRow(Widget):
    __slots__ = ('widget_type', 'title', 'subtitle', 'has_divider', 'image_url')

    def __init__(self,
                 title: Optional[str] = None,
                 subtitle: Optional[str] = None,
                 has_divider: Optional[bool] = None):
        self.title = title
        self.subtitle = subtitle
        self.has_divider = has_divider
        self.image_url = 'logo'

        super().__init__(WidgetType.LEGEND_TITLE_ROW)


class DescriptionRow(Widget):
    __slots__ = ('widget_type', 'text', 'has_divider', 'is_primary', 'expandable', 'small', 'padded')

    def __init__(self, text: Optional[str] = None,
                 is_primary: Optional[bool] = None,
                 has_divider: Optional[bool] = None,
                 expandable: Optional[bool] = None,
                 small: Optional[bool] = None,
                 padded: Optional[bool] = None):
        self.text = text
        self.is_primary = is_primary
        self.has_divider = has_divider
        self.expandable = expandable
        self.small = small
        self.padded = padded

        super().__init__(WidgetType.DESCRIPTION_ROW)


class SubtitleRow(Widget):
    __slots__ = ('widget_type', 'text', 'has_divider')

    def __init__(self, text: Optional[str],
                 has_divider: Optional[bool], ):
        self.text = text
        self.has_divider = has_divider

        super().__init__(WidgetType.SUBTITLE_ROW)


class SelectorRow(Widget):
    __slots__ = ('widget_type', 'title', 'has_divider', 'has_notification', 'icon',
                 'notification_text', 'description', 'has_arrow', 'small', 'action')

    def __init__(self, title: Optional[str] = None,
                 description: Optional[str] = None,
                 notification_text: Optional[str] = None,
                 icon: Optional[Icon] = None,
                 is_primary: Optional[bool] = None,
                 has_divider: Optional[bool] = None,
                 has_notification: Optional[bool] = None,
                 small: Optional[bool] = None,
                 has_arrow: Optional[bool] = None,
                 action: Optional[Action] = None):
        self.title = title
        self.is_primary = is_primary
        self.has_divider = has_divider
        self.has_notification = has_notification
        self.small = small
        self.has_arrow = has_arrow
        self.description = description
        self.notification_text = notification_text
        self.icon = icon

        self.action = action

        super().__init__(WidgetType.SELECTOR_ROW)


class EventRow(Widget):
    __slots__ = ('widget_type', 'title', 'subtitle', 'has_indicator', 'label', 'has_divider', 'image_url', 'padded',
                 'icon')

    def __init__(self, title: Optional[str] = None,
                 subtitle: Optional[str] = None,
                 label: Optional[str] = None,
                 image_url: Optional[str] = None,
                 icon: Optional[Icon] = None,
                 is_primary: Optional[bool] = None,
                 has_divider: Optional[bool] = None,
                 has_indicator: Optional[bool] = None,
                 padded: Optional[bool] = None):
        super().__init__(WidgetType.EVENT_ROW)
        self.title = title
        self.is_primary = is_primary
        self.has_divider = has_divider
        self.has_indicator = has_indicator
        self.padded = padded
        self.subtitle = subtitle
        self.label = label
        self.icon = icon
        self.image_url = image_url

