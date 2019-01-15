from django.db import models


class Measurement(models.Model):
    DATA_TYPE = (
        'metabolite',
        'protein',
        'rna'
    )

    gene = models.CharField(max_length=200, blank=True)
    protein = models.CharField(max_length=200, blank=True)
    compound = models.CharField(max_length=200, blank=True)
    compound_id = models.CharField(max_length=200, blank=True)
    name = models.CharField(max_length=200, blank=True)
    p_value_group_1_and_group_2 = models.FloatField()
    treated_control_fold_change = models.FloatField()
    significant_flag = models.BooleanField()
    exp_method = models.CharField(max_length=200)
    species_type = models.CharField(max_length=200)
    sample_id = models.CharField(max_length=200)
    data_type = models.CharField(max_length=100)
    project_name = models.CharField(max_length=200, blank=True)


class Dataset(models.Model):
    project_name = models.CharField(max_length=200)
    measurements = models.ManyToManyField(Measurement)


class Gene(models.Model):
    name = models.CharField(max_length=200, blank=True)
    fold_change = models.IntegerField(blank=True, default=0)


class GeneList(models.Model):
    gene_list = models.ManyToManyField(Gene)
    sample_id = models.CharField(max_length=200, blank=True)

    def up_genes(self):
        return [i[0] for i in
                self.gene_list.filter(fold_change__gt=0).values_list('name')]

    def down_genes(self):
        return [i[0] for i in
                self.gene_list.filter(fold_change__lt=0).values_list('name')]

    class Meta:
        ordering = ('sample_id',)


class Project(models.Model):
    project_name = models.CharField(max_length=200, blank=True, unique=True,
                                    primary_key=True)

    samples = models.ManyToManyField(GeneList)
