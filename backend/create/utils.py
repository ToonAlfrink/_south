import csv
from datetime import datetime
import time
from os import path
from backend.settings import BUCKET_VARIABLES_DIR_PREFIX
from common.templates_data_manager import templates_data_manager
from common.variables_data_manager import variables_data_manager
from goat_shared.utils import decode, run_task_in_new_thread, str_error
from common.data_bucket_manger import boto_bucket
from common.data_bucket_manger import get_cache
from goat_shared.utils import str_error,  get_logger

logging = get_logger('CreateViewUtils')

class _UploadCsvStatusData:
    def __init__(self):
        self.data = None
        self.error = None
        self.active = False
        self.parse_status = None
        self.uploaded_all = None
        self.variables_init_state = None
    
    def discard(self):
        self.data = None
        self.error = None
        self.active = False
        self.uploaded_all = None
        self.variables_init_state = None

upload_csv_status_data = _UploadCsvStatusData()

def file_upload_cache_key(file): return 'file-upload-' + BUCKET_VARIABLES_DIR_PREFIX + path.basename(file.name)

def upload_csv_files(upload_dict):
    global upload_csv_status_data

    upload_csv_status_data.parse_status['allow_upload'] = False
    uploadable = []

    for item in upload_csv_status_data.data.values():
        if not item.get('file'):
            item['upload_status'] = 'N/A'
        elif not upload_dict.get(item['file'].name) == 'on':
            item['upload_status'] = 'skipped'
        else:
            uploadable.append(item)
    
    if len(uploadable) == 0: 
        upload_csv_status_data.active = False
        return

    def upload(uploadable):
        for item in uploadable:
          item['upload_status'] = 'waiting'

        for item in uploadable:
          try:
            key = BUCKET_VARIABLES_DIR_PREFIX + path.basename(item['file'].name)
            cache = get_cache(file_upload_cache_key(item['file']), False)
            item['upload_status']= 'uploading'
            boto_bucket.put_object(Body=cache.data, Key=key)
            
            item['upload_status']= 'uploaded'
          except BaseException as err:
              logging.info
              item['upload_status']= 'failed'
              item['error']= str(err)
              item['error_stack']= str_error(err)

        def progress_listener(data):
            upload_csv_status_data.variables_init_state = data

        variables_data_manager.fresh_init(templates_data_manager.templates(), progress_listener)
        upload_csv_status_data.uploaded_all = True
    
    run_task_in_new_thread(lambda : upload(uploadable))
    

def check_csv_files(files, progress_listener):
    for file in files:
        try:
            start = time.time()
            cache = get_cache(file_upload_cache_key(file), False)
            file_size = file.size

            progress_listener(file, {
                'status': 'parsing',
                'size': file_size
            })

            reader = csv.reader(cache.data.splitlines())
            next(reader)
            progress_listener(file, {
                'status': 'parsed',
                'allow_upload': True,
                'time': datetime.fromtimestamp(start),
                'time_taken': int(time.time() - start),
                'size': file_size,
                'row_count': len(list(reader)),
                'file': file
            })
        except BaseException as err:
            logging.error('Upload Error', exc_info=True)
            progress_listener(file, {
                'status': 'failed',
                'error': str(err),
                'error_stack': str_error(err)
            })

def parse_csv_files(request):
    global upload_csv_status_data

    upload_csv_status_data.active = True
    upload_csv_status_data.parse_status = {}
    files = request.FILES.getlist('csv_file')
    files = files if isinstance(files, list) else [files]
    upload_csv_status_data.data = {f.name: {'status': 'waiting'} for f in files}
    upload_csv_status_data.error = None
    files_valid = []

    for file in files:
        try:
          if not file.name.endswith('.csv'):
                file_size = file.size
                upload_csv_status_data.data[file.name] = {'status': 'failed', 'size': file_size, 'error': 'Only csv files are allowed'}
                continue

          key = file_upload_cache_key(file)
          cache = get_cache(key)
          cache.data = decode(file.read())
          cache.key = key
          cache.e_tag = '0'
          cache.save()
          files_valid.append(file)
        except BaseException as err:
          logging.error('Csv Parsing Error', exc_info=True)
          upload_csv_status_data.data[file.name] = {'status': 'failed','error': str(err),'error_stack': str_error(err)}
          upload_csv_status_data.error = str_error(err)
    
    if len(files_valid) == 0: 
        upload_csv_status_data.active = False
        return

    def update():
        global upload_csv_status_data
        try:
            def progress_listener(file, content):
                upload_csv_status_data.data[file.name] = content
                if 'error_stack' in content:
                    upload_csv_status_data.error = content['error_stack']

            check_csv_files(files_valid, progress_listener)
            upload_csv_status_data.parse_status = {'allow_upload': any(item['status'] == 'parsed' for item in upload_csv_status_data.data.values())}
        except BaseException as e:
            logging.error('Check Csv Error', exc_info=True)
            upload_csv_status_data.error = str_error(e)
            for item in upload_csv_status_data.data:
                if upload_csv_status_data.data[item].get('status') == 'waiting':
                    upload_csv_status_data.data[item]['status'] = 'skipped'
        finally:
            upload_csv_status_data.active = None
    
    run_task_in_new_thread(update)

