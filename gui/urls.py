from django.conf.urls import url, include
import gui.views as views
import gui.views.network as net_views
import gui.views.enrichment as enri_views

network_urls = [
    url(r'^expand$', net_views.neighbor_expand, name='expand'),
    url(r'^subgraph$', net_views.SubgraphView.as_view(), name='subgraph'),
    url(r'^path$', net_views.ShortestPathView.as_view(), name='path'),
    url(r'^neighbors$', net_views.NeighborsView.as_view(), name='neighbors'),
    url(r'^network_stats$', net_views.network_stats, name='network_stats'),
]

enrichment_urls = [
    url(r'^filter$', enri_views.ProjectEnrichmentView.as_view(), name='filter'),
    url(r'^enrichment$', enri_views.EnrichmentResultsView.as_view(),
        name='enrichment'),
]

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^new/$', views.NewProjectView.as_view(), name='add'),

    url(r'^projects/(?P<project_name>[\w|\W]+)/',
        include([
            url(r'^details$', views.project_details, name='details'),
            url(r'^results$', enri_views.project_enrichment, name='results'),
        ])
        ),

]
urlpatterns += network_urls + enrichment_urls
