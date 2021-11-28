from goat_shared.version_manager import VERSION_TemplateDataManager
from goat_shared.page_template import PageTemplate
from frontend.settings import GOAT_TMP_DIR
import os
import weakref
from random import randint

BUCKET_TEMPLATES_DIR_PREFIX =os.environ['BUCKET_TEMPLATES_DIR_PREFIX']
_save_dir = os.path.join(GOAT_TMP_DIR, BUCKET_TEMPLATES_DIR_PREFIX)
_cache = dict()
_available_templates = []

def get_template(templateName):
    global _cache
    global _available_templates
    
    if VERSION_TemplateDataManager.is_updated():
        _cache = dict()
        _available_templates = [x[0:len(x) - 5] for x in os.listdir(_save_dir) if x.endswith('.json')]
    
    if not templateName:
        templateName = _available_templates[randint(0, len(_available_templates) - 1)]
        
    template = None
    if templateName in _cache:
        template = _cache[templateName]()
    if template:
        return template
    
    filepath = os.path.join(_save_dir, templateName + '.json')
    if not os.path.exists(filepath):
        return None
    
    template = PageTemplate(filepath)
    _cache[templateName] = weakref.ref(template)

    return template

    
