import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'magine_gui_app.settings')
import sys
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(path)
from django.core.wsgi import get_wsgi_application
get_wsgi_application()
from magine_gui_app.settings import BASE_DIR
_dir = BASE_DIR
# Create your tests here.
from gui.models import GeneList, Gene, Project, EnrichmentOutput
from gui.enrichr_helper import run_enrichment



def delete_all():
    GeneList.objects.all().delete()
    Gene.objects.all().delete()
    Project.objects.all().delete()
# delete_all()
# quit()


def add_gene_list():
    x = [
        ('BAX', 1),
        ('BCL2', 1),
        ('TP53', 1),
        ('CASP3', -1),
        ('CASP8', -1),
         ]

    GeneList.objects.all().delete()
    new_gene_list = GeneList.objects.create(sample_id='test_1')
    Gene.objects.all().delete()
    for i in x:
        new_gene_list.gene_list.create(name=i[0], fold_change=i[1])
        new_gene_list.save()

    print(new_gene_list.up_genes())
    print(new_gene_list.down_genes())


def test_project():
    sample_1 = [
        ('BAX', 1),
        ('BCL2', 1),
        ('TP53', 1),
        ('CASP3', -1),
        ('CASP8', -1),
    ]

    sample_2 = [
        ('PARP1', 1),
        ('AKT1', 1),
        ('ASCL1', 1),
        ('SMARCAL1', -1),
        ('CYCS', -1),
    ]

    new_project = Project.objects.create(project_name='main_project')

    for name, sample in zip(['sample_1', 'sample_2'], [sample_1, sample_2]):

        new_gene_list = GeneList.objects.create(sample_id=name)
        for i in sample:
            new_gene_list.gene_list.create(name=i[0], fold_change=i[1])
        new_gene_list.save()
        new_project.samples.add(new_gene_list)
    new_project.save()
    print(new_project.samples.all().values_list())


def run_enrichment_for_project():
    project = Project.objects.all()
    for p in project:
        project_name = p.project_name
        list_samples = []
        list_sample_ids = []
        for i in p.samples.all():
            list_samples.append(i.up_genes())
            list_samples.append(i.down_genes())
            list_sample_ids.append(i.sample_id+'_up')
            list_sample_ids.append(i.sample_id+'_down')
        print(list_samples, list_sample_ids, project_name)
        data = run_enrichment(list_samples, list_sample_ids, project_name)
        EnrichmentOutput.objects.bulk_create(data)


if __name__ == '__main__':
    test_project()
    run_enrichment_for_project()
