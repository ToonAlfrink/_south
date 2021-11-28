import os
from goat_shared.version_manager import VERSION_TemplateDataManager, VERSION_VariablesDataManager
from frontend.settings import GOAT_MAIN_MAX_CARD_COUNT, GOAT_TMP_DIR
import json
from goat_shared.utils import get_logger

logging = get_logger('RenderCacheManager')

class _RenderCacheManager:
    def __init__(self) -> None:
        self.template_version = None
        self.variable_version = None
        self.variable_version = dict()

    def enabled(): return True

    def init(self):
        variable_version = VERSION_VariablesDataManager.get_version_string()
        template_version = VERSION_TemplateDataManager.get_version_string() + '-' + variable_version

        if self.template_version != template_version:
            self.cache_html_dir = os.path.join(GOAT_TMP_DIR, 'main_cache', template_version, 'renders')
            logging.debug('template version change: %s -> %s, new template cache dir: %s'%(self.template_version, template_version, self.cache_html_dir))
            self.template_version = template_version
            os.makedirs(self.cache_html_dir, exist_ok=True)

        if self.variable_version != variable_version:
            logging.debug('variables version change: %s -> %s'%(self.variable_version, variable_version))
            self.cache_json_dir = os.path.join(GOAT_TMP_DIR, 'main_cache_json', variable_version, 'variables')
            self.variable_version = variable_version
            logging.debug('variable version change: %s -> %s, new variable cache dir: %s'%(self.variable_version, variable_version, self.cache_json_dir))
            self.variable_version = dict()
            os.makedirs(self.cache_json_dir, exist_ok=True)

    def open_html(self, content_id): 
        filepath = os.path.join(self.cache_html_dir, content_id+'.html')
        if not os.path.exists(filepath): return None
        return open(filepath, 'r', encoding='utf-8')

    def read_variables(self, content_id, templateName):
        v = VERSION_VariablesDataManager.get_child_version_string(templateName)
        if self.variable_version.get('templateName') != v:
            return None

        filepath = os.path.join(self.cache_json_dir, content_id+'.json')
        if not os.path.exists(filepath): return filepath

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if data.get('VariablesDataManager.'+templateName) == v:
                return data

    def write_variables(self, content_id, templateName, data):
        data['VariablesDataManager.'+templateName] = VERSION_VariablesDataManager.get_child_version_string(templateName)

        with open(os.path.join(self.cache_json_dir, content_id+'.json'), 'w', encoding='utf-8') as f:
            data = json.dump(data, f)
    
    def write_html(self, content_id, content):
        with open(os.path.join(self.cache_html_dir, content_id+'.html'), 'w', encoding='utf-8') as f:
            f.write(content)

class _RenderCacheDisabledManager(_RenderCacheManager):
    def enabled(self): return False
    def init(self): pass
    def open_html(self, content_id): pass
    def read_variables(self, content_id, templateName): pass
    def write_variables(self, content_id, templateName, data): pass
    def write_html(self, content_id, content): pass

render_cache_manager = _RenderCacheDisabledManager() # _RenderCacheManager()

