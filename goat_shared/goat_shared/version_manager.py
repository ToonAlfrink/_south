from pymemcache.client import base
import time
import os
from .utils import get_logger

client = base.Client(
    (os.environ['MEMCACHED_HOST'], int(os.environ['MEMCACHED_PORT'])))
logging = get_logger('VersionControl')


class _Version:
    def __init__(self, key):
        self.key = key
        self.last_version = -1

    def update(self):
        client.set(self.key, int(time.time()))

    def update_child(self, child_key):
        client.set(f'{self.key}.{child_key}', int(time.time()))

    def is_updated(self):
        v = client.get(self.key)
        if v == self.last_version:
            return False
        logging.debug(f'version change, {self.key} {self.last_version} -> {v}')
        self.last_version = v
        return True
    
    def get_child_version_string(self, child_key):
        return client.get(f'{self.key}.{child_key}', b'-1').decode()

    def get_version_string(self):
        return client.get(self.key, b'-1').decode()


VERSION_ImgDataManager = _Version('VersionImgData')
VERSION_TemplateDataManager = _Version('TemplateDataManager')
VERSION_VariablesDataManager = _Version('VariablesDataManager')
