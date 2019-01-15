import json

from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import get_template
from django.views import View

from gui.forms.project import ProjectForm
from gui.data_functions.add_raptr_project import add_project_from_zip
from gui.enrichr_helper import add_enrichment
from gui.models import Data


def index(request):
    try:
        projects = Data.objects.all()
    except:
        projects = {}

    _data = {'projects': projects}
    return HttpResponse(
        get_template('welcome.html', using='jinja2').render(_data)
    )


def project_details(request, project_name):
    ex = Data.objects.get(project_name=project_name)
    meas = json.loads(ex.all_measured)
    uni = json.loads(ex.uni_measured)
    time = json.loads(ex.time)
    uni_sig = json.loads(ex.sig_uni)
    sig = json.loads(ex.sig_measured)
    t = get_template('table_stats.html', using='jinja2')
    content = {
        'data': ex,
        'all_measured': t.render({"all_measured": meas, 'time': time}),
        'uni_measured': t.render({"all_measured": uni, 'time': time}),
        'sig_measured': t.render({"all_measured": sig, 'time': time}),
        'sig_uni': t.render({"all_measured": uni_sig, 'time': time}),
    }
    return render(request, 'project_details.html', content)


class NewProjectView(View):
    def post(self, request):
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            proj_name = form.cleaned_data['project_name']
            add_project_from_zip(proj_name=proj_name,
                                 filename=form.cleaned_data['file'])
            add_enrichment(proj_name)
            return project_details(request, proj_name)
        form = ProjectForm()
        return render(request, 'add_data.html', {'form': form})

    def get(self, request):
        form = ProjectForm()
        return render(request, 'add_data.html', {'form': form})



