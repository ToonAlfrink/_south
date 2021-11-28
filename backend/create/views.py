import time
import os

from backend.settings import BUCKET_CONFIGS_DIR_PREFIX, LOGIN_URL
from common.status_manager import status_manager
from common.variables_data_manager import variables_data_manager
from common.templates_data_manager import templates_data_manager
from common.data_bucket_manger import boto_read_json_file
from django.core.exceptions import BadRequest
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseNotAllowed, HttpResponseNotFound, HttpResponseServerError
from django.shortcuts import redirect, render
from datetime import datetime
from goat_shared.utils import HttpResponseNotAuthenticated, run_task_in_new_thread, str_error
from goat_shared.mongo_db_manager import mongodb_db

from create.utils import parse_csv_files, upload_csv_files, upload_csv_status_data
import json
from goat_shared.utils import str_error, sanitize_template_name, get_logger

logging = get_logger('CreateView')

fields_groups = ['topic01', 'topic02', 'topic03', 'topic04', 'topic05', 'product']
subfields = ['Slug', 'Breadcrumb', 'Chip']

def maintenance(request: HttpRequest): return render(request, 'maintenance.html')

def home(request: HttpRequest):
    if not request.user.is_authenticated:
        return redirect(f'{LOGIN_URL}?next={request.path}')
    if upload_csv_status_data.active:
        return redirect('/create/upload-csv-status/')
    if not status_manager.ready(): return redirect(f'create/maintenance/?from={request.path}')

    try:
        create_model = boto_read_json_file(BUCKET_CONFIGS_DIR_PREFIX + 'create_page_model.json')
    except BaseException as e:
       return HttpResponseServerError("""
        <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta http-equiv="X-UA-Compatible" content="IE=edge">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Error With Create Model</title>
            </head>
            <body>
                <code><pre>%s</pre></code>
            </body>
            </html>
        """%str_error(e))
    
    basedOn = request.GET.get('basedOn')
    basedOnTemplate = templates_data_manager.read_template(basedOn) if basedOn else None

    if basedOn and not basedOnTemplate:
        return HttpResponseNotFound(f'base template with name "{basedOn}" not found')

    templateName = sanitize_template_name(request.GET.get('templateName'))

    if templateName != request.GET.get('templateName', 'default'):
        return redirect('/create?='+"&".join(f'{k}={v if k != "templateName" else templateName}' for k, v in request.GET.items()))

    template = templates_data_manager.read_template(templateName)
    template_data_new = not template

    if not template: 
        template = basedOnTemplate if basedOnTemplate else templates_data_manager.read_template('default')
        template['templateName'] = templateName
    
    model = {
        'template_data': template,
        'template_data_new': template_data_new,
        'success_saved': int(time.time()) - request.session.get('success_saved') < 1000 if request.session.get('success_saved') else False,
        'show_dialog': bool(request.session.get('show_dialog')),
        'updated_on': datetime.now().isoformat(),
        'lang': request.GET.get('lang'),
        'headers_values': list(set(variables_data_manager.headers)),
        'template_names': templates_data_manager.template_names(),
        'goat_step_counter': 0,
        **templates_data_manager.get_counts(templateName),
        **create_model
    }

    if('show_dialog' in request.session):
        request.session['show_dialog'] = False

    request.session['success_saved'] = None
    request.session['templateName'] = templateName

    return render(request, 'create.html', model)

save_status_data = {'saving': False}

def save_status(request: HttpRequest):
    if not request.user.is_authenticated:
        return HttpResponseNotAuthenticated()
    if request.method != 'GET':
        return HttpResponseNotAllowed([request.method])

    if not save_status_data.get('saving'): return redirect('/create/')
    return render(request, 'save-status.html', save_status_data)
    

def save(request: HttpRequest):
    if not request.user.is_authenticated:
        return HttpResponseNotAuthenticated()

    if request.method != 'POST':
        return HttpResponseNotAllowed([request.method])
    
    if save_status_data['saving']: 
        return redirect('/create/save-status/?templateName=' + request.session['templateName']) if 'templateName' in request.session else redirect('/create/save-status/')
    if not status_manager.ready(): return redirect(f'/maintenance/?from={request.path}')

    data = request.POST.dict()
    del data['csrfmiddlewaretoken']

    data['p_updatedOn'] = int(time.time())

    save_status_data['saving'] = True
    request.session['templateName'] = data['templateName']
    updated = templates_data_manager.set_template(data)

    def update():
        try:
          save_status_data['file'] = updated['templateName']

          def progress_listener(progress, total):
            save_status_data['progress'] = progress
            save_status_data['total'] = total
            
          variables_data_manager.update_urls_data([updated], progress_listener)
        except BaseException as e:
          logging.error('Update Urls Error', exc_info=True)
          save_status_data['error'] = str_error(e)
        finally:
            save_status_data['saving'] = False

    run_task_in_new_thread(update)

    request.session['show_dialog'] = True

    if(data.get('language')): return redirect('/create/?'+data['language'])
    return redirect('/create/save-status/')

def upload_csv_status(request):
    if not request.user.is_authenticated:
            return HttpResponseNotAuthenticated()

    if upload_csv_status_data.uploaded_all: 
        upload_csv_status_data.uploaded_all = False
        return redirect('/dashboard/reload-variables/')

    return render(request, 'upload-csv-status.html', {
        'data': upload_csv_status_data.data,
        'error': upload_csv_status_data.error,
        'active': upload_csv_status_data.active,
        'parse_status': upload_csv_status_data.parse_status,
        'variables_init_state': json.dumps(upload_csv_status_data.variables_init_state, indent=2),
        'updated_on': datetime.now().isoformat()
    })

def upload_csv(request: HttpRequest):
    if not request.user.is_authenticated:
        return HttpResponseNotAuthenticated()

    if request.method != 'POST':
        return HttpResponseNotAllowed([request.method])

    if not upload_csv_status_data.parse_status or not upload_csv_status_data.parse_status.get('allow_upload'):
        return HttpResponse('No Upload Queue Found', status_code=409)
    
    if not status_manager.ready(): return redirect('/create/upload-csv-status/')
    
    if not 'upload' in request.POST:
        upload_csv_status_data.discard()
        return redirect('/create/')

    upload_csv_files(request.POST.dict())
    return redirect('/create/upload-csv-status/')

def process_csv(request: HttpRequest):
    if not request.user.is_authenticated:
        return HttpResponseNotAuthenticated()
    if request.method != 'POST':
        return HttpResponseNotAllowed([request.method])

    if upload_csv_status_data.active:
        return HttpResponse('Old upload in progress', status_code=409)

    if not status_manager.ready(): return redirect(f'/maintenance/?from={request.path}')

    if not request.FILES or not request.FILES.get('csv_file'):
        raise BadRequest('No Files Specified')

    parse_csv_files(request)

    return redirect('/create/upload-csv-status/')

def edit(request):
    if request.GET.get('raw', 'false').lower() == 'true':
        with open(os.path.join(__file__, '../templates/create.html'), 'r') as f:
            return HttpResponse(f.read().replace('create.min.js', ''))
