from goat_shared.version_manager import VERSION_VariablesDataManager
from frontend.settings import GOAT_TMP_DIR
import os
import json

_TMP_META_PATH = os.path.join(GOAT_TMP_DIR, 'VariablesDataManager.csv__meta.json') 

class _VariablesDataManager:
    def __init__(self):
        self.load_info = None
        self.load_error = None
    
    def init(self):
        if not VERSION_VariablesDataManager.is_updated(): return
        self.load_error = None
        self.title = 'Variables Data'

        with open(_TMP_META_PATH, 'r') as f:
            data = json.load(f)

            self.table_structure = data['table_structure']
            self.header_groups = data['header_groups']
            self.headers = data['headers']
            self.row_count = data['row_count']
            self.load_info = data['load_info']
            self.load_error = None
    
variables_data_manager = _VariablesDataManager()
