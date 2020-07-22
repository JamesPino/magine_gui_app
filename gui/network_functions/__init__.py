import os

import networkx as nx

from gui.network_functions.networkx_tools import from_networkx
from magine.networks.visualization.notebooks.cyjs_options import styles
from magine.networks.exporters import nx_to_json
from magine.networks.subgraphs import Subgraph

_g_path = os.path.join(os.path.dirname(__file__),
                       'networks',
                       'background_network.p.gz')


g = nx.read_gpickle(_g_path)
subgraph_gen = Subgraph(g)


def create_subgraph(list_of_species):
    sg = subgraph_gen.paths_between_list(list_of_species)
    return prep_g(sg)


def neighbors_including_cross_interactions(node, up, down):

    species = [node]
    if up:
        species += g.predecessors(node)
    if down:
        species += g.successors(node)

    sg = g.subgraph(species)

    return prep_g(sg)


def neighbors(node, up, down, max_dist=1):

    sg = subgraph_gen.neighbors(node, up, down, max_dist)

    return prep_g(sg)


def expand_neighbors(node, up, down, max_dist=1):

    sg = subgraph_gen.expand_neighbors(
        network=None,
        nodes=node,
        upstream=up,
        downstream=down,
        max_dist=max_dist
    )
    for i in sg.nodes:
        sg.node[i]['color'] = 'white'
    return nx_to_json(sg)


def path_between(source, end, bi_dir):
    sg = subgraph_gen.paths_between_pair(source, end,
                                         single_path=False,
                                         bidirectional=bi_dir)
    return prep_g(sg)


def _filter_edges(graph, edge_type):
    to_remove = set()
    for i, j, d in graph.edges(data=True):
        # print(d.keys())
        if edge_type in d['interactionType']:
            to_remove.add((i, j))

    graph.remove_edges_from(to_remove)
    nodes = set(graph.nodes())
    for i in nodes:
        if graph.degree(i) == 0:
            graph.remove_node(i)
    return graph


def _get_edge_types(graph):
    edge_types = set()
    for i, j, d in graph.edges(data=True):
        if 'interactionType' in d:
            for e in d['interactionType'].split('|'):
                edge_types.add(e)
    return edge_types


def prep_g(sg):
    for i in sg.nodes:
        sg.node[i]['color'] = 'white'
    data = nx_to_json(sg)
    data['edge_list'] = _get_edge_types(sg)
    data['style_json'] = styles['default']
    return data


if __name__ == '__main__':
    # neighbors('BAX', True, False)
    # neighbors('BAX', False, True)
    neighbors('CEPBP', True, True)
    # create_subgraph('H2AFX,ATM,MRE11,RAD50,TP53BP1'.split(','))
