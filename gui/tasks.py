import logging
from magine.enrichment.enrichr import Enrichr, db_types, standard_dbs
import os
import pandas as pd
from gui.models import EnrichmentOutput
from magine.logging import get_logger

logger = get_logger(__name__, log_level=logging.INFO)
# from magine_gui_app.celery import app
# from celery.utils.log import get_task_logger

# logger = get_task_logger(__name__)


def run(samples, sample_ids, label, p_name, already_there):
    standard_dbs = []
    dbs = ['drug', 'disease', 'ontologies', 'pathways', 'transcription',
           'kinases', 'histone', 'cell_type']
    dbs = ['drug']
    for i in dbs:
        standard_dbs += db_types[i]

    for genes, sample_id in zip(samples, sample_ids):
        print("Starting {}".format(sample_id))

        current = "{}_{}_{}".format(label, sample_id, p_name)
        print(standard_dbs)
        if current not in already_there:
            # run_set_of_dbs.apply_async(
            #     args=(list(genes), sample_id, standard_dbs, label, p_name),
            #     countdown=30
            # )
            run_set_of_dbs(
               list(genes), sample_id, standard_dbs, label, p_name
            )

        print("Finished {}".format(sample_id))


# @app.task(name='gui.enrichment_functions.tasks.run_set_of_dbs')
def run_set_of_dbs(sample, sample_id, dbs, label, p_name):
    # logger.info("Running enrichment")
    e = Enrichr()
    df = e.run(sample, dbs)
    if df.shape[0] == 0:
        print("No results found")
        return
    df['significant'] = False
    crit = (df['adj_p_value'] <= 0.05) & (df['combined_score'] > 0)
    df.loc[crit, 'significant'] = True

    df['sample_id'] = sample_id
    df['category'] = label
    df['project_name'] = p_name

    EnrichmentOutput.objects.bulk_create(
        [EnrichmentOutput(**r) for r in df.to_dict(orient='records')]
    )
    # logger.info("Done with enrichment for {} : {}".format(sample_id, dbs))


def run_enrichment_for_project(exp_data, project_name, output_path=None):
    """

    Parameters
    ----------
    exp_data : magine.data.experimental_data.ExprerimentalData
    project_name : str
    output_path : str
        Location to save all individual enrichment output files created.

    """
    already_there = set()
    for i in EnrichmentOutput.objects.filter(project_name=project_name):
        already_there.add("{}_{}_{}".format(str(i.category), str(i.sample_id),
                                            project_name))
    databases = standard_dbs

    logger.info("Running enrichment on project")
    logger.info("Running {} databases".format(len(databases)))

    e = Enrichr(verbose=True)
    all_df = []
    if output_path is None:
        _dir = os.path.join(os.getcwd(), 'enrichment_output')
    else:
        _dir = output_path

    if not os.path.exists(_dir):
        logger.info("Creating output directory: {}".format(_dir))
        os.mkdir(_dir)

    def _run_new(samples, timepoints, category):
        logger.info("Running {}".format(category))
        for genes, sample_id in zip(samples, timepoints):
            if not len(genes):
                continue
            logger.info('\t time point = {}'.format(sample_id))
            current = "{}_{}_{}".format(category, sample_id, project_name)
            # if current in already_there:
            #     continue
            name = os.path.join(_dir, current + '.csv.gz')
            try:
                df = pd.read_csv(name, index_col=None, encoding='utf-8')
            except:
                df = e.run(genes, databases)
                df['sample_id'] = sample_id
                df['category'] = category
                df.to_csv(name, index=False, encoding='utf-8',
                          compression='gzip')
            df['sample_id'] = sample_id
            df['category'] = category
            all_df.append(df)

    #  run all protein labeled species grouped by time point
    #  ( label-free, ph-silac, etc are all combined)
    if len(exp_data.proteins.sample_ids) != 0:
        sample = exp_data.proteins.sig
        _run_new(sample.by_sample, sample.sample_ids, 'proteomics_both')
        _run_new(sample.up_by_sample, sample.sample_ids, 'proteomics_up')
        _run_new(sample.down_by_sample, sample.sample_ids, 'proteomics_down')

    # #  run all RNA labeled species grouped by time point
    # if len(exp_data.rna.sample_ids) != 0:
    #     sample = exp_data.rna.sig
    #     _run_new(sample.by_sample, sample.sample_ids, 'rna_both')
    #     _run_new(sample.down_by_sample, sample.sample_ids, 'rna_down')
    #     _run_new(sample.up_by_sample, sample.sample_ids, 'rna_up')
    #
    # #  run each experimental 'source' by time point
    # #  ( label-free, ph-silac, etc are all separate)
    # for source in exp_data.exp_methods:
    #     df = exp_data[source].sig
    #     col_options = df['species_type'].unique()
    #     # make sure there is only a single species type and it is protein
    #     # this makes sure that the RNA seq doesnt get ran twice
    #     if len(col_options) != 1:
    #         continue
    #     if col_options[0] == 'protein':
    #         _run_new(df.by_sample, df.sample_ids, '{}_both'.format(source))
    #         _run_new(df.up_by_sample, df.sample_ids, '{}_up'.format(source))
    #         _run_new(df.down_by_sample, df.sample_ids,
    #                  '{}_down'.format(source))

    # merge all outputs
    final_df = pd.concat(all_df, ignore_index=True)
    print(final_df.columns)
    final_df = final_df[
        ['term_name', 'rank', 'combined_score', 'adj_p_value', 'p_value',
         'genes', 'z_score', 'n_genes', 'sample_id', 'category', 'db']
    ]

    # remove rows without a term name
    final_df = final_df[~final_df['term_name'].isnull()].copy()
    final_df = final_df[~final_df['adj_p_value'].isnull()].copy()
    final_df = final_df[~final_df['combined_score'].isnull()].copy()
    print(final_df.shape)
    print(final_df[~final_df.isnull()].shape)
    final_df = final_df[~final_df.isnull()].copy()
    print(final_df['adj_p_value'].dtype)
    print(final_df['combined_score'].dtype)
    final_df['significant'] = False
    # Adds significant column
    final_df.loc[(final_df['adj_p_value'] <= 0.05) &
                 (final_df['combined_score'] > 0.0), 'significant'] = True
    final_df['project_name'] = project_name
    final_df = final_df[final_df['adj_p_value'] < 0.2]
    EnrichmentOutput.objects.bulk_create(
        [EnrichmentOutput(**r) for r in final_df.to_dict(orient='records')]
    )
    logger.info("Saving output: {}_enrichment.csv.gz".format(project_name))
    final_df.to_csv('{}_enrichment.csv.gz'.format(project_name),
                    encoding='utf-8', compression='gzip', index=False)
