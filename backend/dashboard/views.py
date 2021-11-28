from datetime import datetime
import os
from django.http.response import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseNotFound, JsonResponse
from django.shortcuts import redirect, render
from backend.settings import LOGIN_URL
from goat_shared.utils import run_task_in_new_thread, str_error
from common.variables_data_manager import variables_data_manager
from common.templates_data_manager import templates_data_manager
from common.img_manager import img_data_manager
import psutil
from goat_shared.utils import HttpResponseNotAuthenticated
from common.status_manager import status_manager
import json
from goat_shared.mongo_db_manager import mongodb_db
from goat_shared.utils import str_error, get_logger

logging = get_logger('DashboardView')

START_TIME = datetime.now().isoformat()

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect(f'{LOGIN_URL}?next={request.path}')

    model = {
        'variable_details': variables_data_manager.load_info,
        'statuses': status_manager.states,
        'status_ready': status_manager.ready(),
        'variable_header_groups': variables_data_manager.header_groups,
        'variable_table_structure': variables_data_manager.table_structure,
        'variable_details_err': variables_data_manager.load_error,
        'templates_details': [{**x, **templates_data_manager.get_counts(x['templateName'])} for x in templates_data_manager.load_info],
        'templates_details_err': templates_data_manager.load_error,
        'img_details': img_data_manager.getdata(),
        'img_details_err': img_data_manager.load_error,
        'START_TIME': START_TIME,
        'urls_details': list(mongodb_db.urls_meta.find(projection={'_id': False, 'id': '$_id', 'count': True, 'created_on': True}))
    }
    try:
        python_process = psutil.Process(os.getpid())

        return render(request, 'dashboard.html', {
            **model,
            'cpu_times': python_process.cpu_times()._asdict(),
            'virtual_memory':  python_process.memory_info()._asdict(),
        })
    except BaseException:
        logging.error('Failed to get CPU details', exc_info=True)
    
    return render(request, 'dashboard.html', model)


def _common_handler(request, url, target, init_callback=None, data_getter=None):
    if not request.user.is_authenticated:
        return HttpResponseNotAuthenticated()

    if request.method == 'POST' and status_manager.ready():
        if not init_callback:
            def init_callback(): return target.init(handleError=True)
        run_task_in_new_thread(init_callback)
        return redirect('/dashboard/' + url)

    if target.load_error:
        return HttpResponse(str_error(target.load_error), content_type='text/plain')

    return JsonResponse(data_getter() if data_getter else target.getdata(), safe=False) if target.ready() else render(request, 'dashboard_status.html', {
        'title': target.title,
        'data': json.dumps(data_getter(), indent=2) if data_getter else None,
        'updated_on': datetime.now().isoformat()
    })

def urls_list(request, lang = None):
    if not request.user.is_authenticated:
        return HttpResponseNotAuthenticated()

    if request.method != 'GET':
        return HttpResponseNotAllowed([request.method])

    if not status_manager.ready():
        return render(request, 'maintenance.html')

    templateName = request.GET.get('templateName')
    templateName = templateName if templateName and templateName.upper() != 'ALL' else None
    filter = {'templateName': templateName} if templateName else None

    pagination = {
        'limit': int(request.GET.get('limit', '30')),
        'skip': int(request.GET.get('skip', '0')),
        'total': mongodb_db.urls.estimated_document_count() if not filter else mongodb_db.urls_meta.find_one(projection={'_id': False, 'count': True})['count']
    }

    data = list(mongodb_db.urls.find(filter=filter).skip(pagination['skip']).limit(pagination['limit']))
    rows = {x['_id']: x for x in mongodb_db.rows.find({'_id': {'$in': [x['row'].id for x in data]}})}

    for n in range(0, len(data)):
        data[n]['id'] = data[n]['_id']
        data[n]['row'] = rows.get(data[n]['row'].id)
    
    return render(request, 'urls-list.html', {
        'urls': data,
        'pagination': pagination,
        'lang': 'en-us' if not lang else lang,
        'templateName': templateName if templateName else 'ALL',
        'template_names': templates_data_manager.template_names(),
    })

def reload_img(request):
    return _common_handler(request, 'reload-imgs/', img_data_manager)


_reload_variables_progress = {'data': None}

def reload_variables(request):
    def init_callback():
        _reload_variables_progress['data'] = {'status': 'LOADING...'}
        def progress_listener(data):
            _reload_variables_progress['data'] = data
        variables_data_manager.fresh_init(
            templates_data_manager.templates(), progress_listener)
    return _common_handler(request, 'reload-variables/', variables_data_manager, init_callback, lambda: _reload_variables_progress['data'] if _reload_variables_progress['data'] else variables_data_manager.getdata())


def reload_templates(request):
    return _common_handler(request, 'reload-templates/', templates_data_manager)

def raw_template(request, templateName):
    if not request.user.is_authenticated:
        return HttpResponseNotAuthenticated()

    if request.method != 'GET':
        return HttpResponseNotAllowed([request.method])

    template = templates_data_manager.read_template(templateName)
    return JsonResponse(template) if template else HttpResponseNotFound('template not found with templateName:' + templateName)


def delete_template(request, templateName):
    if not request.user.is_authenticated:
        return HttpResponseNotAuthenticated()

    if request.method != 'POST':
        return HttpResponseNotAllowed([request.method])
    
    if templateName == 'default':
        return HttpResponseBadRequest('deleting default template is not allowed')
    
    if not templates_data_manager.template_exists(templateName):
        return HttpResponseNotFound(f'template with name: "{templateName}" not found')
    
    templates_data_manager.delete_template(templateName)

    return redirect('/dashboard/')


