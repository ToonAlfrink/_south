import json
from os import path
from goat_shared.version_manager import VERSION_ImgDataManager
from frontend.settings import GOAT_TMP_DIR

_save_path = path.join(GOAT_TMP_DIR, 'ImgDataManager.json')

class _ImgDataManager:
    def init(self):
        if not VERSION_ImgDataManager.is_updated(): return

        with open(_save_path, 'r') as f:
            self.data = json.load(f)
            self.counter = {x: 0 for x in self.data}

    def next_file(self, name):
        index = (self.counter[name] + 1) % len(self.data[name])
        self.counter[name] = index
        return self.data[name][index]


img_data_manager = _ImgDataManager()
