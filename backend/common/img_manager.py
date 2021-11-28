
import json
import os

from backend.settings import GOAT_TMP_DIR

from common.data_bucket_manger import boto_bucket
from common.status_manager import status_manager

from goat_shared.utils import get_logger
from goat_shared.version_manager import VERSION_ImgDataManager

logging = get_logger('ImgDataManager')

GOAT_VALID_IMG_EXTS = [x.strip() for x in os.environ['GOAT_VALID_IMG_EXTS'].split(',') if x.strip()]
BUCKET_MEDIA_PREFIX = os.environ['BUCKET_MEDIA_PREFIX']

_save_path = os.path.join(GOAT_TMP_DIR, 'ImgDataManager.json')

class _ImgDataManager:
    def __init__(self):
        self.load_error = None

    def getdata(self):
        with open(_save_path, 'r') as f:
            return json.load(f)

    def init(self, handleError=False):
        status_manager.set_state(_ImgDataManager, False)
        data = dict()
        self.load_error = None
        self.title = 'Image Data'

        try:
            for entry in boto_bucket.objects.filter(Prefix=BUCKET_MEDIA_PREFIX):
                if not any(entry.key.lower().endswith(ext) for ext in GOAT_VALID_IMG_EXTS):
                    continue
                filename = entry.key.replace(BUCKET_MEDIA_PREFIX, '')
                key = filename[0:filename.index('/')]
                if not key in data:
                    data[key] = []
                data[key].append(filename[filename.index('/') + 1:])

            self.load_error = None
            with open(_save_path, 'w') as f:
                json.dump(data, f)
            
            VERSION_ImgDataManager.update()
            status_manager.set_state(_ImgDataManager, True)
        except BaseException as err:
            logging.error('Failed to init ImgDataManager: ', exc_info=True)
            status_manager.set_state(_ImgDataManager, True)
            if not handleError:
                raise err
            self.load_error = err

    def ready(self):
        return status_manager.get_state(_ImgDataManager)


status_manager.set_state(_ImgDataManager, False)
img_data_manager = _ImgDataManager()
