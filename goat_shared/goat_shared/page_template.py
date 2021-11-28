import json
from string import Template
import time

def create_template(template):
    return Template(template).safe_substitute if type(template) == str and '$' in template else lambda _: template

class PageTemplate:
    def __init__(self, data_or_file):
        if not type(data_or_file) == dict:
            with open(data_or_file, 'r') as f:
                data_or_file = json.load(f)

        self.raw = data_or_file
        self.templateName = data_or_file['templateName']
        self.compiled = {key: create_template(
            value) for key, value in self.raw.items()}
        self.time = int(time.time())
