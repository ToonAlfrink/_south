from sitemap42 import Sitemap, Sitemapindex
from datetime import datetime

from backend.settings import BASE_DIR, BUCKET_CONFIGS_DIR_PREFIX
import os
import re
from common.data_bucket_manger import boto_bucket, boto_read_file, boto_write_file
from goat_shared.utils import get_logger

logging = get_logger('SiteMapBuilder')


SITEMAP_DIR = BASE_DIR.parent / os.environ['SITEMAP_DIR']
SITEMAP_INDEX_DIR = BASE_DIR.parent / os.environ['SITEMAP_INDEX_DIR']
ROBOTS_PATH = BASE_DIR.parent / os.environ['ROBOTS_PATH']
SITEMAP_INDEX_LIMIT = int(os.environ['SITEMAP_INDEX_LIMIT'])
SITEMAP_LIMIT = int(os.environ['SITEMAP_LIMIT'])
DOMAIN_URL_WITH_LANG = os.environ['DOMAIN_URL_WITH_LANG']
DOMAIN_URL=os.environ['DOMAIN_URL']
SITE_MAP_DIR_PREFIX=os.environ['SITE_MAP_DIR_PREFIX']

os.makedirs(SITEMAP_DIR, exist_ok=True)
os.makedirs(SITEMAP_INDEX_DIR, exist_ok=True)

def counter_start(dir):
    regex = re.compile(r'^.+?-+(\d+)\.xml$')
    files = [int(m.group(1)) for m in (regex.match(f) for f in os.listdir(dir)) if m]
    if len(files) == 0: return 1
    return max(max(files), 0) + 1

class SiteMapBuilder:
    def __init__(self):
        self.maps = dict()
        self.modtime = datetime.now()
        self.sitemap = Sitemap()
        self.counter = counter_start(SITEMAP_DIR)
        self.sitemap_files = list()

    def add(self, url):
        self.sitemap.append(DOMAIN_URL_WITH_LANG + url, changefreq='daily', priority=0.5, lastmod=self.modtime)
        if len(self.sitemap.items) >= SITEMAP_LIMIT:
            self.flush()
    
    def flush(self):
        if len(self.sitemap.items) == 0: return
        sitemap_file_name = 'sitemap-%03.0f.xml'%self.counter if self.counter < 1001 else str(self.counter)
        self.sitemap.write(SITEMAP_DIR / sitemap_file_name)
        self.sitemap_files.append(sitemap_file_name)
        self.counter += 1
        self.sitemap = Sitemap()

    def finish(self, templateName):
        self.flush()
        if not self.sitemap_files: return

        counter2 = counter_start(SITEMAP_INDEX_DIR)
        sitemap_url = DOMAIN_URL + os.path.basename(SITEMAP_DIR) + '/'
        sitemapindex = Sitemapindex()
        file_name = 'sitemapindex-%03.0f.xml'%counter2 if counter2 < 1001 else str(counter2)
        siteindex_txt = [file_name]

        for item in self.sitemap_files:
            sitemapindex.append(sitemap_url + item, lastmod=self.modtime)
            siteindex_txt.append('\t' + item)

            if len(sitemapindex.items) >= SITEMAP_INDEX_LIMIT:
                sitemapindex.write(SITEMAP_INDEX_DIR / file_name)

                counter2 += 1
                sitemapindex = Sitemapindex()
                file_name = 'sitemapindex-%03.0f.xml'%counter2 if counter2 < 1001 else str(counter2)
                siteindex_txt.append(file_name)
        
        if len(sitemapindex.items) != 0:
            sitemapindex.write(SITEMAP_INDEX_DIR / file_name)
        
        boto_write_file(SITE_MAP_DIR_PREFIX + templateName + ".txt", '\n'.join(siteindex_txt))

def create_robots_txt():
    if os.path.exists(ROBOTS_PATH):
        os.remove(ROBOTS_PATH)
    boto_bucket.download_file(BUCKET_CONFIGS_DIR_PREFIX + 'robots-init.txt', str(ROBOTS_PATH))
    sitemapindex_url = DOMAIN_URL + os.path.basename(SITEMAP_INDEX_DIR) + '/'

    with open(ROBOTS_PATH, 'a', encoding='utf-8') as f:
        f.write("\n".join(f'Sitemap: {sitemapindex_url}{x}' for x in os.listdir(SITEMAP_INDEX_DIR)))


def remove_site_maps(templateName):
    data = boto_read_file(SITE_MAP_DIR_PREFIX + templateName + ".txt")
    if not data: return

    delete_count = 0
    failed_delete_count = 0

    for line in data.splitlines():
        if not line: continue
        try:
            os.remove(os.path.join(SITEMAP_DIR if line[0] == '\t' else SITEMAP_INDEX_DIR, line.strip()))
            delete_count += 1
        except:
            failed_delete_count += 1
