import time
from os import makedirs, path
from typing import List
from common.sitemap_builder import create_robots_txt, remove_site_maps
from goat_shared.page_template import PageTemplate
from backend.settings import BUCKET_CONFIGS_DIR_PREFIX, GOAT_TMP_DIR
from common.data_bucket_manger import boto_copy_file, boto_key_list, boto_delete_file
from common.data_bucket_manger import boto_bucket, boto_write_json_file
from common.status_manager import status_manager
from goat_shared.utils import sanitize_template_name
import json 
import weakref
from goat_shared.version_manager import VERSION_TemplateDataManager
from goat_shared.utils import get_logger
import os
from goat_shared.mongo_db_manager import mongodb_db

logging = get_logger('TemplateDataManager')

BUCKET_TEMPLATES_DIR_PREFIX = os.environ['BUCKET_TEMPLATES_DIR_PREFIX']
BUCKET_DELETED_TEMPLATES_DIR_PREFIX = os.environ['BUCKET_DELETED_TEMPLATES_DIR_PREFIX']
makedirs(path.join(GOAT_TMP_DIR, BUCKET_TEMPLATES_DIR_PREFIX), exist_ok=True)

def template_path(templateName):
     return path.join(GOAT_TMP_DIR, BUCKET_TEMPLATES_DIR_PREFIX + templateName + '.json')

class _ListWrap:
     def __init__(self, data):
         self.data = data

class _TemplateDataManager:
   def __init__(self):
        self.load_info = None
        self.load_error = None
    
   def getdata(self):
        return self.load_info

   def init(self, handleError = False):
        status_manager.set_state(_TemplateDataManager, False)
        
        self.load_error = None
        self.title = 'Template Data'
        templates = []

        try:
            load_info = []
            for key in boto_key_list(BUCKET_TEMPLATES_DIR_PREFIX):
                 if not key.endswith('.json'): continue
                 target = path.join(GOAT_TMP_DIR, key)
                 makedirs(path.dirname(target), exist_ok=True)
                 boto_bucket.download_file(key, target)

                 templates.append(PageTemplate(target))
                 load_info.append({'file_key': key, 'templateName': templates[-1].templateName, 'save_path': target, 'time': int(time.time())})
             
            self.load_info = load_info
            self.load_error = None
            self.templates_ref = weakref.ref(_ListWrap(templates))
            VERSION_TemplateDataManager.update()
            status_manager.set_state(_TemplateDataManager, True)
        except BaseException as err:
            logging.error('Failed to init TemplateDataManager', exc_info=True)
            status_manager.set_state(_TemplateDataManager, True)
            if not handleError: raise err
            self.load_error = err
     
   def templates(self) -> List[PageTemplate]: 
        data = self.templates_ref() if self.templates_ref else None
        data = data.data if data else None
        if data: return data

        data = [PageTemplate(info['save_path']) for info in self.load_info]
        self.templates_ref = weakref.ref(_ListWrap(data))

        return data

   def template_names(self):
        return [x['templateName'] for x in self.load_info]

   def set_template(self, data: dict):
        try:
          status_manager.set_state(_TemplateDataManager, False)
          data_template_name = sanitize_template_name(data.get('templateName', 'default'))
          data['templateName'] = data_template_name
          file_key = BUCKET_TEMPLATES_DIR_PREFIX + data_template_name + '.json'

          try:
            boto_copy_file(file_key, BUCKET_DELETED_TEMPLATES_DIR_PREFIX + data_template_name + f'-{int(time.time())}.json')
          except:
            pass

          boto_write_json_file(data, file_key)
          boto_write_json_file({'file_key': file_key, 'created_date': int(time.time())}, BUCKET_CONFIGS_DIR_PREFIX + '_TemplateDataManager.json')
          logging.debug('write:' + file_key)

          with open(path.join(GOAT_TMP_DIR, file_key), 'w') as f:
               json.dump(data, f)

          for n in range(0, len(self.load_info)):
               if self.load_info[n]['templateName'] == data_template_name:
                    self.load_info[n] = {'templateName': data_template_name, 'file_key': file_key, 'time': time.time()}
                    return data

          self.load_info.append({'templateName': data_template_name, 'file_key': file_key, 'time': time.time()})
          VERSION_TemplateDataManager.update()
          return data
        finally:
          status_manager.set_state(_TemplateDataManager, True)

   def ready(self):
        return status_manager.get_state(_TemplateDataManager)
   
   def get_counts(self, templateName):
     counts = mongodb_db.urls_meta.find_one({'_id': templateName}, projection={'_id': False, 'topics_count': True, 'products_count': True})
     return counts if counts else {'products_count': 0, 'topics_count': 0}

   def template_exists(self, templateName):
        return path.exists(template_path(templateName))
     
   def delete_template(self, templateName):
        try:
          status_manager.set_state(_TemplateDataManager, False)
          file_key = BUCKET_TEMPLATES_DIR_PREFIX + templateName + '.json'
          boto_copy_file(file_key, BUCKET_DELETED_TEMPLATES_DIR_PREFIX + 'deleted-' + templateName + f'-{int(time.time())}.json')
          boto_delete_file(file_key)

          logging.debug('delete:' + file_key)
          try:
            os.remove(template_path(templateName))
          except: 
               pass

          self.load_info = [x for x in self.load_info if x['templateName'] != templateName]
          remove_site_maps(templateName)
          create_robots_txt()
          mongodb_db.urls_meta.delete_one({'_id': templateName})
          mongodb_db.urls.delete_many({'templateName': templateName})
          
          VERSION_TemplateDataManager.update()
        finally:
          status_manager.set_state(_TemplateDataManager, True)


   def read_template(self, templateName):
        file_path = template_path(templateName)
        if path.exists(file_path):
             with open(file_path, 'r') as f:
               return json.load(f)

status_manager.set_state(_TemplateDataManager, False)
templates_data_manager = _TemplateDataManager()

