import json
import os

import boto3
from botocore.errorfactory import ClientError

from common.models import BotoCache
from goat_shared.utils import decode, get_logger

logging = get_logger('BotoManager')
BUCKET_NAME = os.environ['BUCKET_NAME']

boto_resource = boto3.resource('s3', region_name='sfo3', endpoint_url=os.environ['AWS_ENDPOINT_URL'])
boto_bucket = boto_resource.Bucket(BUCKET_NAME)

def boto_key_list(prefix): return [e.key for e in boto_bucket.objects.filter(Prefix=prefix)]

def boto_download_dir(prefix, target_dir, ext=None):
    downloaded = []
    for entry in boto_bucket.objects.filter(Prefix=prefix):
        if ext and not entry.key.lower().endswith(ext):
            continue
        target = os.path.join(target_dir, entry.key.replace(prefix, ''))
        os.makedirs(target, exist_ok=True)
        boto_bucket.download_file(entry.key, target)
        downloaded.append(entry.key.replace(prefix, ''))

    return downloaded

def boto_file_exists(file_key):
    try:
        return bool(boto_bucket.Object(file_key).last_modified)
    except ClientError:
        return False

def boto_read_file(file_key, return_encoding = False) -> str:
    try:
        return decode(boto_bucket.Object(file_key).get()['Body'].read(), return_encoding)
    except ClientError:
        logging.debug('40: Failed to read file: ' + file_key, exc_info=True)
        return None

def boto_write_file(file_key, body):
    boto_bucket.put_object(Body=body, Key=file_key)

def get_cache(file_key, create_instance_on_fail = True):
    try:
        return BotoCache.objects.get(pk=file_key)
    except BotoCache.DoesNotExist:
        return BotoCache() if create_instance_on_fail else None

def boto_write_json_file(data, file_key, allow_cache = True):
    data_str = json.dumps(data, indent=2)
    boto_bucket.put_object(Body=data_str, Key=file_key)

    if not allow_cache: return

    cache = get_cache(file_key)
    cache.key = file_key
    cache.e_tag = boto_bucket.Object(file_key).e_tag
    cache.data = data_str
    cache.save()

def boto_read_json_file(file_key, allow_cache = True):
    if allow_cache:
        key = boto_bucket.Object(file_key)
        cache = get_cache(file_key)
        if cache.data and cache.e_tag == key.e_tag: 
            logging.debug('Cache loaded: ' + file_key)
            return json.loads(cache.data)

    data_str = decode(key.get()['Body'].read())
    data = json.loads(data_str)
    cache.key = file_key
    cache.e_tag = key.e_tag
    cache.data = data_str
    cache.save()

    logging.debug('Live loaded: ' + file_key)
    return data

def boto_copy_file(src, target):
    boto_bucket.copy({'Bucket': BUCKET_NAME, 'Key': src}, target)

def boto_delete_file(file_key):
    boto_bucket.Object(file_key).delete()
