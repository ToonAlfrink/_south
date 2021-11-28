import csv
import functools
import json
import time
from datetime import datetime
from os import environ, path
from typing import List

from backend.settings import (BUCKET_CONFIGS_DIR_PREFIX, GOAT_TMP_DIR,
                              BUCKET_VARIABLES_DIR_PREFIX, MONGO_BATCH_SIZE)
from pymongo.errors import BulkWriteError

from common.data_bucket_manger import (boto_key_list, boto_read_file,
                                       boto_write_json_file)
from common.sitemap_builder import (SiteMapBuilder, create_robots_txt, remove_site_maps)
from common.status_manager import status_manager
from goat_shared.page_template import PageTemplate
from goat_shared.utils import (create_progress_bar, get_logger, sanitize_slug,
                          str_error)

from goat_shared.mongo_db_manager import mongodb_db
from goat_shared.version_manager import VERSION_VariablesDataManager

logging = get_logger('VariablesDataManager')

_TMP_PATH = path.join(GOAT_TMP_DIR, 'VariablesDataManager.csv')
_TMP_META_PATH = _TMP_PATH+ '__meta.json'
_encoding_sorter = ['utf-8', 'ISO-8859-1', 'utf-16']

class _VariablesDataManager:
    def __init__(self):
        self.load_info = None
        self.load_error = None
    
    def init(self, templates):
        status_manager.set_state(_VariablesDataManager, False)
        self.load_error = None
        self.title = 'Variables Data'

        data = mongodb_db.rows.find_one({'_id': 0})
        force_refresh = environ.get('GOAT_FORCE_REFRESH', 'false').lower() == 'true'

        if not data or not path.exists(_TMP_PATH) or force_refresh:
            logging.debug(f'variables not setup, initializing database. db data found: {bool(data)}, local data found: {path.exists(_TMP_PATH)}, force refresh: {force_refresh}')
            self.fresh_init(templates)
            VERSION_VariablesDataManager.update()
            return

        self.table_structure = data['table_structure']
        self.header_groups = data['header_groups']
        self.headers = data['headers']
        self.row_count = data['row_count']
        self.load_info = data['load_info']
        self.load_error = None
        status_manager.set_state(_VariablesDataManager, True)
        
    def fresh_init(self, templates, progress_listener = lambda _: None, handleError=False):
        status_manager.set_state(_VariablesDataManager, False)
        self.load_error = None
        all_start = time.time()
        headers_list = None
        rows_structure = None
        files_lines = []
        load_info = {'started_on': time.time(), 'started_on_datetime': datetime.now().isoformat(), 'ended_on': None, 'files': dict(), 'total': 0, 'progress': 0, 'progress_status': 'Reading Files', 'completed': False, 'load_error': None, 'urls_counts': dict()}
        final_encoding = 'utf-8'
        
        try:
            files_keys = boto_key_list(BUCKET_VARIABLES_DIR_PREFIX)
            load_info['total'] = len(files_keys)

            def reset_progress(total, status):
                load_info['total'] = total
                load_info['progress'] = 0
                load_info['progress_status'] = status
                progress_listener(load_info)

            def next_progress(status, increment = 1):
                load_info['progress'] += increment
                load_info['progress_status'] = status
                progress_listener(load_info)

            def set_progress(progress, status, total = -1):
                load_info['total'] = load_info['total'] if total < 0 else load_info['total']
                load_info['progress'] = progress
                load_info['progress_status'] = status
                progress_listener(load_info)

            for key in files_keys:
                next_progress('Reading: ' + key)
                if not key.lower().endswith('.csv'):
                    continue

                start = int(time.time())
                (lines_data, encoding) = boto_read_file(key, True)
                lines = lines_data.splitlines()
                final_encoding = final_encoding if _encoding_sorter.index(final_encoding) >= _encoding_sorter.index(encoding) else encoding
                load_info['files'][key] = {"file_key": key, 'file_encoding': encoding, 'row_count': len(lines) - 1, 'empty': len(lines) < 2, 'time': start, 'file_load_time_taken': int(time.time()) - start}

                if(len(lines) < 2): continue
                files_lines.append((key, lines))

                next_progress(None, 0)

            if len(files_lines) == 0:
                load_info['no_files_found'] = True
                next_progress(None, 0)
                return

            reset_progress(len(files_lines), 'Parsing files')
            logging.debug('Csv Files found: ' + str(len(files_lines)))
            progress_bar = create_progress_bar('Parsing files', max=len(files_lines))

            for key, lines in files_lines:
                next_progress('Parsing CSV: ' + key)
                progress_bar.next()

                reader = csv.reader(lines)
                headers = next(reader)
                data = list(reader)

                rows = (key, data)

                if not headers_list:
                    headers_list = [headers]
                    rows_structure = [[rows]]
                    continue
                
                if headers in headers_list:
                    index = headers_list.index(headers)
                    row = next((x for x in rows_structure if x[index] == None), None)
                    if not row:
                        row = [None] * len(rows_structure[-1])
                        rows_structure.append(row)
                    row[index] = rows
                else:
                    rows_structure = [x + [None] for x in rows_structure]
                    rows_structure[0][len(headers_list)] = rows
                    headers_list += [headers]
            
            progress_bar.finish()
            boto_write_json_file(load_info, BUCKET_CONFIGS_DIR_PREFIX+'_VariablesDataManager.json')

            rows_list = []
            empty_list = [[None]*len(h) for h in headers_list]

            for rows in rows_structure:
                rows = [x[1] if x else None for x in rows]
                max_count = max(len(x) if x else 0 for x in rows)
                rows = [iter(r) if r else iter([]) for r in rows]

                for _ in range(0, max_count):
                    row = []
                    for n in range(0, len(headers_list)):
                        row += next(rows[n], empty_list[n])
                    rows_list.append(row)

            headers = functools.reduce(lambda a,b: a + b, headers_list)

            collection = mongodb_db.get_collection('rows-temp')
            collection.drop()
            row_count = len(rows_list)
            reset_progress(row_count, 'Saving to MongoDB')
            progress_bar = create_progress_bar('Saving to MongoDB', row_count)

            for n in range(0 , row_count, MONGO_BATCH_SIZE):
                upper_bound = min(n + MONGO_BATCH_SIZE, row_count)
                if n == upper_bound: continue
                collection.insert_many([{'_id': n + 1, 'row': rows_list[n]} for n in range(n, upper_bound)])
                progress_bar.next(MONGO_BATCH_SIZE)
                set_progress(min(row_count, n + MONGO_BATCH_SIZE), 'Saving to MongoDB')
            
            progress_bar.finish()
            set_progress(row_count, 'Saved to MongoDB')
            self._update_urls_data(headers, rows_list, templates, lambda progress, total: set_progress(progress, 'Creating Urls', total))

            set_progress(row_count, 'DONE Preparing Variables DB')

            load_info['final_encoding'] = final_encoding
            self.table_structure = [[f'{y[0]} ({len(y[1])})' if y else None for y in x] for x in rows_structure]
            self.header_groups = headers_list
            self.headers = headers
            self.row_count = row_count
            self.load_info = load_info
            self.load_error = None

            metadata = {
                "_id": 0,
                "headers": headers,
                "created_on": datetime.now().isoformat(),
                "row_count": row_count,
                'load_info': load_info,
                'table_structure' : self.table_structure,
                'header_groups': self.header_groups
            }

            collection.insert_one(metadata)
            collection.rename('rows', dropTarget=True)

            with open(_TMP_PATH, 'w', encoding=final_encoding, newline='') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(rows_list)
            
            load_info['total_time_taken'] = int(time.time() - all_start)
            load_info['ended_on'] = time.time()
            load_info['ended_on_datetime'] = datetime.now().isoformat()
            load_info['completed'] = True

            with open(_TMP_META_PATH, 'w') as f:
                json.dump(metadata, f)

            progress_listener(load_info)
        except BaseException as err:
            logging.error('VariablesDataManager error', exc_info=True)
            load_info['load_error'] = str_error(err)
            self.load_error = err
            if not handleError:
                raise err
        finally:
            status_manager.set_state(_VariablesDataManager, True)
    
    def update_urls_data(self, templates, progress_listener):
        status_manager.set_state(_VariablesDataManager, False)

        try:
            urls_counts_data = self.load_info['urls_counts'].copy()
            self._update_urls_data('LOAD', 'LOAD', templates, progress_listener)
            self.load_info['urls_counts'] = urls_counts_data
        finally:
            status_manager.set_state(_VariablesDataManager, True)

    def _update_urls_data(self, headers: List[str], rows_list: List[List[str]], templates: List[PageTemplate], progress_listener = lambda a,b : None):
        if not templates or len(templates) == 0:
            logging.info('no templates specified')
            return

        if not rows_list or len(rows_list) == 0:
            logging.info('no rows specified')
            return

        # regex = re.compile(r'(topic\d+|product)(Slug|BlockTitle|BlockDescription)')
        # document_defs = [key for key in FIRST_TEMPLATE if regex.match(key)]
        # section_urls = {key: {regex.search(x).group(2).lower().replace('block', ''): x for x in value} for key, value in groupby(section_variables, key=lambda k: regex.search(k).group(1))}

        fields_groups = ['topic01', 'topic02', 'topic03', 'topic04', 'topic05', 'product']
        document_defs = {x: {'_id': x + 'Slug',
                             'description': x + 'Description',
                             'title': x + 'Title',
                             'breadcrumb': x + 'Breadcrumb'} for x in fields_groups}
        section_variables = functools.reduce(
            lambda a, b: a + b, (list(x.values()) for x in document_defs.values()))
        

        progress_bar = None
        if not headers == 'LOAD':
            total = len(rows_list) * len(document_defs) * len(templates)
            progress_bar = create_progress_bar('Creating Urls', total)
            progress_listener(0, total)

        for template in templates:
            if type(template) != PageTemplate:
                template = PageTemplate(template)

            saved_urls = set()
            meta_db = mongodb_db.urls_meta.find_one({"_id": template.templateName})
            remove_site_maps(template.templateName)
            sitemap = SiteMapBuilder()

            if meta_db and not any(meta_db['template'].get(key) != template.raw[key] for key in section_variables):
                logging.info('skip update of urls for: ' + template.templateName)
                continue

            if headers == 'LOAD':
                with open(_TMP_PATH, 'r', encoding=self.load_info['final_encoding']) as f:
                    reader = csv.reader(f)
                    headers = next(reader)
                    rows_list = list(reader)
                    
                total = len(rows_list) * len(document_defs) * len(templates)
                progress_bar = create_progress_bar('Creating Urls', total)
                progress_listener(0, total)

            mongodb_db.urls.delete_many(filter={'templateName': template.templateName})
            start_count = mongodb_db.urls.estimated_document_count()

            to_be_saved = []
            progress = 0
            progress_bar_count = 0

            for n in range(0, len(rows_list)):
                variables = dict(zip(headers, rows_list[n]))
                breadcrumb = []

                for group, section in document_defs.items():
                    progress_bar_count += 1
                    item = {key: template.compiled[template_var](variables) for key, template_var in section.items()}
                    item['group'] = group
                    item['_id'] = sanitize_slug(item['_id'])
                    if not item['_id']: continue
                    breadcrumb = breadcrumb + [item['_id']]
                    if item['_id'] in saved_urls: continue
                    item['breadcrumbs'] = breadcrumb
                    item['row_id'] = n + 1
                    item['templateName'] = template.templateName
                    saved_urls.add(item['_id'])
                    to_be_saved.append(item)
                    sitemap.add(item['_id'])

                if len(to_be_saved) >= MONGO_BATCH_SIZE:
                    progress_bar.next(progress_bar_count)
                    progress_bar_count = 0
                    try:
                      mongodb_db.urls.insert_many(to_be_saved, ordered=False)
                    except BulkWriteError:
                      pass
                    progress += len(to_be_saved)
                    progress_listener(progress, total)
                    to_be_saved = []
            
            if len(to_be_saved) != 0:
                progress_bar.next(progress_bar_count)
                try:
                    mongodb_db.urls.insert_many(to_be_saved, ordered=False)
                except BulkWriteError:
                    pass
            
            total_count = mongodb_db.urls.estimated_document_count() - start_count
            products_count = mongodb_db.urls.count_documents({'templateName': template.templateName, 'group': 'product'})
            mongodb_db.urls_meta.update_one({"_id": template.templateName},
                                                     {"$set": {'template': {x: template.raw[x] for x in section_variables},
                                                               "_id": template.templateName,
                                                               "count" : total_count,
                                                               'products_count': products_count,
                                                               'topics_count': total_count - products_count,
                                                               "created_on": datetime.now().isoformat()}}, upsert=True)
            sitemap.finish(template.templateName)
            VERSION_VariablesDataManager.update_child(template.templateName)
            progress_listener(progress + len(to_be_saved), total)
        
        progress_bar.finish()
        create_robots_txt()

    def getdata(self):
        return self.load_info

    def ready(self):
        return status_manager.get_state(_VariablesDataManager)

status_manager.set_state(_VariablesDataManager, False)
variables_data_manager = _VariablesDataManager()
