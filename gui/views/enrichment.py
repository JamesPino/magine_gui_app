from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import get_template
from django.views import View

import gui.forms.enrichment as forms
import gui.enrichr_helper as enrichr_help

from gui.views.common import check_species_list
from gui.models import EnrichmentOutput


class EnrichmentResultsView(View):
    def get(self, request):
        form = forms.ListOfSpeciesOntology(request.GET)
        if form.is_valid():
            genes = form.cleaned_data['list_of_species'].split(',')
            list_of_species = check_species_list(genes)
            ont = form.cleaned_data['ontology']
            data = enrichr_help.return_table(list_of_species, ont)

            template = get_template('simple_table_view.html', using='jinja2')
            return HttpResponse(template.render(data))
        else:
            form = forms.ListOfSpeciesOntology()
            content = {'form': form}
            return render(request, 'form_ontology_from_list.html', content)


class ProjectEnrichmentView(View):
    def get(self, request):
        form = forms.EnrichmentDatasetForm(request.GET)
        if form.is_valid():
            project_name = form.cleaned_data['project_name']
            category = form.cleaned_data['category']
            dbs = form.cleaned_data['db']
            data = enrichr_help.return_table_from_model(project_name, category,
                                                        dbs)
            template = get_template('simple_table_view.html', using='jinja2')
            return HttpResponse(template.render(data))
        else:
            form = forms.EnrichmentDatasetForm()
            content = {'form': form}
            return render(request, 'form_enrichment_from_project.html',
                          content)


def project_enrichment(request, project_name):
    ex = EnrichmentOutput.objects.filter(project_name=project_name).values()
    data = enrichr_help.model_to_json(ex)
    return render(request, 'simple_table_view.html', data)