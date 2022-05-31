import json


class TorchConfig:

    def __init__(self, dict) -> None:
        vars(self).update(dict)

    @staticmethod
    def from_json(json_file) -> object:
        f = open(json_file)
        config = json.load(f)
        f.close()
        return config
