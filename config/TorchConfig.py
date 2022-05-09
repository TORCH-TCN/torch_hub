import json


class TorchConfig:

    def __init__(self, dict) -> None:
        vars(self).update(dict)

    @staticmethod
    def from_json(json_file) -> "TorchConfig":
        f = open(json_file)
        config = json.load(f, object_hook=TorchConfig)
        f.close()
        return config
