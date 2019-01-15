import os
import sys

import pandas as pd
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'magine_gui_app.settings')
sys.path.append(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
)
get_wsgi_application()

from gui.data_functions.add_raptr_project import add_project_from_zip
from gui.models import Data, EnrichmentOutput
from magine_gui_app.settings import BASE_DIR
_dir = BASE_DIR


def add_project(proj_name):
    print('Adding project data\n\t{}'.format(proj_name))
    Data.objects.filter(project_name=proj_name).delete()
    new = Data.objects.create(project_name=proj_name)
    new.set_exp_data(
        os.path.join(os.path.dirname(__file__), '{}.csv.gz'.format(proj_name)),
        set_time_point=True,
    )
    new.save()
    print('Done adding project data')


def dump_project(proj_name):
    data = EnrichmentOutput.objects.filter(project_name=proj_name)
    df = pd.DataFrame(list(data.values()))
    df.to_csv('{}_enrichment_dump.csv.gz'.format(proj_name),
              compression='gzip')


def load_project(proj_name):

    df = pd.read_csv('{}_enrichment_dump.csv.gz'.format(proj_name),
                     index_col=0)

    already_there = set()
    for i in EnrichmentOutput.objects.filter(project_name=proj_name):
        already_there.add("_".join(
            [i.db, i.category, i.sample_id, proj_name])
        )
    dict_list = df.to_dict(orient='records')

    to_add = [EnrichmentOutput(**row) for row in dict_list if
              "_".join([row['db'], row['category'], row['sample_id'],
                        row['project_name']]) not in already_there]
    if len(to_add) != 0:
        EnrichmentOutput.objects.bulk_create(to_add)


def do_all(project_name, raptr_file):
    add_project_from_zip(project_name, raptr_file)
    # add_enrichment(project_name)


if __name__ == '__main__':
    do_all('cisplatin',
           'export_Cisplatin_magine_20171024-122628586.zip')


