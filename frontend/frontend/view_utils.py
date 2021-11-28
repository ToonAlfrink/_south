from random import randint

from goat_shared.mongo_db_manager import mongodb_db
from goat_shared.page_template import PageTemplate
from frontend.variables_data_manager import variables_data_manager

def find_by_url(url):
    data = mongodb_db.urls.find_one({'_id': url.lower().strip()}) if url else None
    if not data: return None

    data['row'] = mongodb_db.rows.find_one({'_id': data['row_id']}, projection={"_id": False, 'row': True})['row']
    return data

def build_rows(first, template: PageTemplate, size):
    rows = [x['row'] for x in mongodb_db.rows.aggregate([{'$sample': {'size': size}}, {'$project': {'_id': False, 'row': True}}])]
    if first:
        rows[0] = first['row']

    template = template.compiled.items()
    compiled_rows = []

    for row in rows:
        variables = dict(zip(variables_data_manager.headers, row))
        item = {key: builder(variables) for key, builder in template}
        item['__row'] = row
        compiled_rows.append(item)
    
    return compiled_rows

def build_interlinks(first, template: PageTemplate, size):
    filter = {'templateName': template.templateName, 'group': 'topic02'} if first else {'group': 'topic02'}
    return list({x['row'][1]: x for x in mongodb_db.urls.aggregate([
        {'$match': filter},
        {'$sample': {'size': size}},
        {'$lookup': {
            'from': 'rows',
            'localField': 'row_id',
            'foreignField': '_id',
            'as': 'row',
        }},
        {'$project': {'_id': False, 'id': '$_id', 'row': {'$slice': [{'$first': '$row.row'}, 2]}}},
    ])}.values())

def get_breadcrumbs(breadcrumbs):
    return sorted(mongodb_db.urls.find({'_id': {'$in': breadcrumbs}}, projection={'url': '$_id', 'breadcrumb': True}), key=lambda u: breadcrumbs.index(u['url']))
