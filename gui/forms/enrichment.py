import django.forms.widgets as widg
from django import forms
import gui.models as models
from magine.enrichment.enrichr import db_types


class ListOfSpeciesOntology(forms.Form):
    list_of_species = forms.CharField(widget=widg.Textarea(), empty_value='')
    CHOICES = ((i, i) for i in db_types)
    ontology = forms.ChoiceField(choices=CHOICES)

    class Meta:
        fields = ('species_list', 'ontology')


class EnrichmentDatasetForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(EnrichmentDatasetForm, self).__init__(*args, **kwargs)

        # select which projects to show
        c = models.EnrichmentOutput.objects.values_list(
            'project_name', 'project_name').distinct()

        self.fields['project_name'] = forms.MultipleChoiceField(
            c, widget=widg.CheckboxSelectMultiple)
        self.fields['project_name'].initial = c

        # select which dbs to show
        c = models.EnrichmentOutput.objects.values_list('db', 'db').distinct()

        self.fields['db'] = forms.MultipleChoiceField(
            c, widget=widg.CheckboxSelectMultiple
        )
        self.fields['db'].initial = c

        # select which categories
        c = models.EnrichmentOutput.objects.values_list(
            'category', 'category').distinct()

        self.fields['category'] = forms.MultipleChoiceField(
            c, widget=widg.CheckboxSelectMultiple
        )
        self.fields['category'].initial = c
        # self.fields['category'].widget = widg.CheckboxSelectMultiple

    class Meta:
        model = models.EnrichmentOutput
        fields = ['project_name', 'category', 'db', ]


