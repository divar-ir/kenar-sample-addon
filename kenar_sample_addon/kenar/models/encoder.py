import abc
import json
from enum import Enum


class CustomEncoderModel(abc.ABC):

    @abc.abstractmethod
    def get_encoder_value(self):
        pass


class KenarCustomEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, CustomEncoderModel):
            return obj.get_encoder_value()
        elif isinstance(obj, Enum):
            return obj.name

        return obj
