import datetime
from django.http.response import FileResponse, HttpResponse, HttpResponseNotAllowed, HttpResponseNotFound, JsonResponse
from django.shortcuts import render
from django.http.request import HttpRequest
from frontend.settings import GOAT_MAIN_MAX_CARD_COUNT, GOAT_TMP_DIR
from frontend.view_utils import build_interlinks, build_rows, find_by_url, get_breadcrumbs
from django.template import loader
from frontend.cache_manager import render_cache_manager

from frontend.templates_data_manager import get_template
import re
import htmlmin

def home(request: HttpRequest, lang_iso_code: str = None, content_id: str = None):
    if request.method != 'GET':
        return HttpResponseNotAllowed([request.method])

    render_cache_manager.init()
    cached = render_cache_manager.open_html(content_id) if content_id else None
    if cached: 
        with cached as f:
            return HttpResponse(f.read())

    first = find_by_url(content_id)
    if not first and content_id: 
        return HttpResponseNotFound(f'No Data found for: "{content_id}" for lang: {lang_iso_code}')

    template = get_template(first['templateName'] if first else None)

    if not template:
        return JsonResponse({'content': first['templateName'], 'message': 'Template File Not Found'}, status_code=404)

    model = render_cache_manager.read_variables(content_id, template.templateName)
    model = model['model'] if model else None

    if not model:
        compiled_rows = build_rows(first, template, GOAT_MAIN_MAX_CARD_COUNT + 30 + 1)
        model_first = compiled_rows.pop(0)

        regex = re.compile(r"^value\d\dTitle$")

        if first:
            nth = re.findall('topic(\d+)', first['group'])
            nth = int(nth[0]) -1 if nth else 5
        
        values_block_items = [value for key, value in model_first.items() if value and regex.match(key)]

        model = {**model_first,
                'data_list': compiled_rows[0:GOAT_MAIN_MAX_CARD_COUNT],
                'values_block_items': values_block_items,
                'values_titles': values_block_items * 4,
                'chip_data': compiled_rows[GOAT_MAIN_MAX_CARD_COUNT:],
                'interlink_values': build_interlinks(first, template, 60),
                'lang_iso_code': lang_iso_code,
                'content_id': content_id,
                'skip_lang_check': 'skip_lang_check' in request.GET,
                'keywords': first['row'] if first else [],
                'revised_date': datetime.datetime.now().isoformat(),
                'footer_breadcrumbs': get_breadcrumbs(first['breadcrumbs']) if first and first['breadcrumbs'] else []
                }
        
        if first:
            model['heroBlockTitle'] = first['title']
            model['heroBlockDescription'] = first['description']
        
        if not render_cache_manager.enabled():
            return render(request, 'main.html', model)

        if content_id:
            render_cache_manager.write_variables(content_id, template.templateName, {'content_id': content_id, 'first': first, 'model':model})
            content = htmlmin.minify(loader.render_to_string('main.html', model, request))
            render_cache_manager.write_html(content_id, content)
            return HttpResponse(content)

    return render(request, 'main.html', model)
