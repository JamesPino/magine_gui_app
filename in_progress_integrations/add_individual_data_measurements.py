import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'magine_gui_app.settings')
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(path)

from django.core.wsgi import get_wsgi_application
get_wsgi_application()
from gui.models import Measurement, Dataset
import pandas as pd


def add_data():
    df = pd.read_csv(os.path.join(os.path.dirname(__file__),
                                  'example_apoptosis.csv'))
    Dataset.objects.all().delete()
    dataset = Dataset.objects.create(project_name='apoptosis')
    for i, row in df.iterrows():
        print(row)
        if 'time' in row:
            sample_id = row['time']
        else:
            sample_id = row['sample_id']
        data_type = row['data_type']
        gene = row['gene']
        protein = row['protein']
        compound = row['compound']
        treated_control_fold_change = row['treated_control_fold_change']
        species_type = row['species_type']
        significant_flag = row['significant_flag']
        p_value_group_1_and_group_2 = row['p_value_group_1_and_group_2']
        m = Measurement.objects.create(
            data_type=data_type,
            sample_id=sample_id,
            gene=gene,
            protein=protein,
            compound=compound,
            treated_control_fold_change=treated_control_fold_change,
            species_type=species_type,
            p_value_group_1_and_group_2=p_value_group_1_and_group_2,
            significant_flag=significant_flag,
        )
        m.save()
        dataset.measurements.add(m)
    dataset.save()
    print(dataset.measurements.all())

if __name__ == '__main__':
    add_data()
