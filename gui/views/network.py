from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import get_template
from django.views import View
from django.http import JsonResponse
from magine.networks.exporters import nx_to_json
import gui.forms.network as forms
from .common import check_species_list
from gui.network_functions import path_between, create_subgraph, neighbors,\
    expand_neighbors
import json
import networkx as nx

class SubgraphView(View):
    def get(self, request):
        form = forms.ListOfSpeciesFrom(request.GET)
        if form.is_valid():
            list_of_species = form.cleaned_data['list_of_species'].split(',')
            names = check_species_list(list_of_species)
            graph = create_subgraph(names)
            return _return_subgraph(graph)
        else:
            form = forms.ListOfSpeciesFrom()
            return render(request, 'form_species_list.html', {'form': form})


class ShortestPathView(View):
    def get(self, request):
        form = forms.PathBetweenForm(request.GET)
        if form.is_valid():
            start = form.cleaned_data['start']
            end = form.cleaned_data['end']
            start = start.upper()
            end = end.upper()
            bi_dir = form.cleaned_data['bi_dir']
            graph = path_between(start, end, bi_dir)
            return _return_subgraph(graph)

        else:
            form = forms.PathBetweenForm()
            content = {'form': form}
            return render(request, 'form_species_to_species.html', content)


class NeighborsView(View):
    def get(self, request):
        form = forms.NodeNeighborsForm(request.GET)
        if form.is_valid():
            node = form.cleaned_data['node']
            start = node.upper()

            up_stream = form.cleaned_data['up_stream']
            down_stream = form.cleaned_data['down_stream']
            max_dist = int(form.cleaned_data['max_dist'])
            graph = neighbors(start, up_stream, down_stream, max_dist)
            return _return_subgraph(graph)

        else:
            form = forms.NodeNeighborsForm(initial={'max_dist': '1'})
            return render(request, 'form_graph_neighbors.html', {'form': form})


def neighbor_expand(request):
    list_of_species = request.GET['list_of_species'].split(',')
    names = check_species_list(list_of_species)
    net = expand_neighbors(names, up=True, down=True, max_dist=1)
    return JsonResponse(net)


def network_stats(request):
    return HttpResponse(
        get_template('network_stats.html', using='jinja2').render()
    )


def _return_subgraph(graph):
    return HttpResponse(
        get_template('subgraph_view.html', using='jinja2').render(graph))
