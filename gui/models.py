import json
import pandas as pd
from django.db import models
from django.utils import timezone
from picklefield.fields import PickledObjectField

from gui.data_functions import get_all_tables
from magine.data.experimental_data import ExperimentalData, load_data


class Data(models.Model):
    project_name = models.CharField(max_length=200)
    upload_date = models.DateField(blank=True, null=True)
    data = PickledObjectField(compress=True, blank=True, null=True)
    time_points = models.CharField(max_length=2000, blank=True)
    modality = models.CharField(max_length=2000, blank=True)
    time = models.CharField(max_length=2000, blank=True)
    all_measured = models.CharField(max_length=20000, blank=True)
    uni_measured = models.CharField(max_length=20000, blank=True)
    sig_measured = models.CharField(max_length=20000, blank=True)
    sig_uni = models.CharField(max_length=20000, blank=True)

    def publish(self):
        self.upload_date = timezone.now()

    def set_exp_data(self, file, set_time_point=False):
        if isinstance(file, pd.DataFrame):
            exp_data = ExperimentalData(file)
            data = ExperimentalData(file).data
        else:
            data = load_data(file, low_memory=False)

        if set_time_point:
            data['time'] = data['sample_id']
        self.time_points = json.dumps(sorted((data['sample_id'].unique())))
        time, all_m, uni_m, sig_m, sig_uni = get_all_tables(exp_data)
        self.time = json.dumps(time)
        self.all_measured = json.dumps(all_m)
        self.uni_measured = json.dumps(uni_m)
        self.sig_measured = json.dumps(sig_m)
        self.sig_uni = json.dumps(sig_uni)
        self.data = data
        self.save()

    def get_time_points(self):
        return json.loads(self.time_points)

    def get_all_measured(self):
        return json.loads(self.all_measured)

    def return_magine_data(self, project_name):
        data = self.objects.filter(project_name=project_name)[0]
        return ExperimentalData(data.data)

    def _str__(self):
        return self.project_name


class EnrichmentOutput(models.Model):
    project_name = models.CharField(max_length=200, blank=True)
    category = models.CharField(max_length=200, blank=True)
    db = models.CharField(max_length=200, blank=True)

    term_name = models.CharField(max_length=20000, blank=True)
    term_id = models.CharField(max_length=20000, blank=True)
    sample_id = models.CharField(max_length=20000, blank=True)
    genes = models.CharField(max_length=20000, blank=True)

    n_genes = models.IntegerField(blank=True, default=0)
    rank = models.IntegerField(blank=True, default=0)

    z_score = models.FloatField(blank=True, default=0)
    p_value = models.FloatField(blank=True, default=0)
    adj_p_value = models.FloatField(blank=True, default=0)
    combined_score = models.FloatField(blank=True, default=0)
    significant = models.BooleanField(blank=True)




