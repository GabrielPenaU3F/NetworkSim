from abc import ABC

from src.physical_layer.physical_layer import PhysicalLayer


class Config(ABC):

    def build(self):
        pass


class PhysicalConfig(Config):

    def __init__(self, channel_cls, channel_params,
                 code_cls, code_params):
        self.channel_cls = channel_cls
        self.channel_params = channel_params
        self.code_cls = code_cls
        self.code_params = code_params

    def build(self):
        channel = self.channel_cls(**self.channel_params)
        code = self.code_cls(**self.code_params)
        return PhysicalLayer(channel, code)
