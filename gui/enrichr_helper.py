import json
import pandas as pd

from magine.enrichment.enrichr import Enrichr, db_types
from magine.html_templates.html_tools import create_yadf_filters, \
    _format_simple_table


cols = ['term_name', 'combined_score', 'adj_p_value', 'rank',  'genes',
        'n_genes', 'sample_id', 'db']


def _add_check(row):
    """
    Add checkmark column to table

    Parameters
    ----------
    row

    Returns
    -------

    """
    i = row.name
    out = '<input type="checkbox" id="checkbox{0}" name="{1}"> ' \
          '<label for="checkbox{0}"></label>'.format(i, row.genes)
    return out


def model_to_json(model):
    df = pd.DataFrame(list(model))
    if 'id' in df.columns:
        del df['id']
    if 'project_name' in df.columns:
        del df['project_name']
    print(df.shape)
    df.remove_duplicates(inplace=True)
    print(df.shape)
    tmp_table = _format_simple_table(df)

    tmp_table['checkbox'] = tmp_table.apply(_add_check, axis=1)
    cols.append('checkbox')
    tmp_table = tmp_table[cols]
    d = create_yadf_filters(tmp_table)
    data = tmp_table.to_dict('split')
    data['filters'] = d
    template_vars = {"data": data}
    return template_vars


def return_table(list_of_genes, ont='pathways'):
    cols = ['term_name', 'combined_score', 'adj_p_value', 'rank',
            'genes', 'n_genes', 'db']
    e = Enrichr()
    df = e.run(list_of_genes, gene_set_lib=db_types[ont])[cols]
    tmp_table = _format_simple_table(df)
    tmp_table['genes'] = tmp_table['genes'].str.split(',').str.join(', ')
    d = create_yadf_filters(tmp_table)
    data = tmp_table.to_dict('split')

    data['filters'] = d
    template_vars = {"data": data}
    return template_vars


def return_table_from_model(project_name, category, dbs):
    from gui.models import EnrichmentOutput
    cols = ['term_name', 'combined_score', 'adj_p_value', 'rank', 'genes',
            'n_genes', 'sample_id', 'db', 'category']
    if len(project_name) > 1:
        cols.insert(0, 'project_name')

    df = EnrichmentOutput.objects.all().filter(project_name__in=project_name)
    df = df.filter(category__in=category)
    df = df.filter(db__in=dbs)

    df = pd.DataFrame(list(df.values()))[cols]
    df.drop_duplicates(inplace=True)
    df = df[df['adj_p_value'] < 0.2]

    tmp_table = _format_simple_table(df)

    tmp_table['genes'] = tmp_table['genes'].str.split(',').str.join(', ')

    tmp_table['checkbox'] = tmp_table.apply(_add_check, axis=1)
    cols.insert(0, 'checkbox')
    tmp_table = tmp_table[cols]
    data = tmp_table.to_dict('split')
    data['filters'] = json.dumps(create_yadf_filters(tmp_table))
    template_vars = {"data": data}
    return template_vars


def add_enrichment(project_name, reset_data=False):
    from gui.models import Data, EnrichmentOutput
    from gui.tasks import run_enrichment_for_project
    if reset_data:
        EnrichmentOutput.objects.filter(project_name=project_name).delete()
    exp_data = Data.return_magine_data(Data, project_name=project_name)
    run_enrichment_for_project(exp_data, project_name)


if __name__ == '__main__':
    return_table(['BAX', 'BCL2', 'MCL1', 'CASP3', 'CASP8'])

