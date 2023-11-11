import dataclasses
from typing import Dict, Any, List, Tuple, Union

from kenar_sample_addon.kenar.models.encoder import CustomEncoderModel
from kenar_sample_addon.kenar.models.widgets import Widget


class Addon(CustomEncoderModel):

    def __init__(self, widgets: List[Widget], link_in_spec: str = None, semantic: Dict[str, Any] = None):
        self.widgets = widgets
        self.link_in_spec = link_in_spec
        self.semantic = semantic

    def get_encoder_value(self):
        return {
            'widgets': {
                'widget_list': self.widgets,
            },
            'link_in_spec': self.link_in_spec,
            'semantic': self.semantic,
        }


class StickyAddon(Addon, CustomEncoderModel):
    def __init__(self, widgets: List[Widget], categories: Union[List[str], Tuple[str]],  semantic: Dict[str, Any] = None):
        super().__init__(widgets, semantic=semantic)
        self.categories = categories

    def get_encoder_value(self):
        return {
            'widgets': {
                'widget_list': self.widgets,
            },
            'semantic': self.semantic,
            'categories': self.categories,
        }
