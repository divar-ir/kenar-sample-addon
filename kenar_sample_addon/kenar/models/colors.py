from enum import Enum
from typing import Dict, Any

from kenar_sample_addon.kenar.models.encoder import CustomEncoderModel


class Color(Enum):

    SUCCESS_PRIMARY = 0
    SUCCESS_SECONDARY = 1
    WARNING_PRIMARY = 2
    WARNING_SECONDARY = 3
    ERROR_PRIMARY = 4
    TEXT_PRIMARY = 5
    TEXT_SECONDARY = 6
    TEXT_HINT = 7
    TEXT_DIVIDER = 8
    ICON_PRIMARY = 9
    ICON_SECONDARY = 10
    ICON_HINT = 11
    ICON_DIVIDER = 12
    WHITE_PRIMARY = 13
