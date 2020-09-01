import logging
from magine.enrichment.enrichr import Enrichr, db_types, standard_dbs
import os
import pandas as pd
from gui.models import EnrichmentOutput
from magine.logging import get_logger

logger = get_logger(__name__, log_level=logging.INFO)
logger.setLevel(logging.INFO)
USE_CELERY = False
TESTING = True

if USE_CELERY:
    from magine_gui_app.celery import app

    @app.task(name='gui.tasks.run_set_of_dbs')
    def run_set_of_dbs(sample, sample_id, dbs, label, p_name):
        logger.info("Running enrichment")
        e = Enrichr()
        df = e.run(sample, dbs)
        if df.shape[0] == 0:
            print("No results found")
            return
        df = _check_nan_add_sig(df)
        df['sample_id'] = sample_id
        df['category'] = label
        df['project_name'] = p_name

        EnrichmentOutput.objects.bulk_create(
            [EnrichmentOutput(**r) for r in df.to_dict(orient='records')]
        )
        logger.info("Done with enrichment for {} : {}".format(sample_id, dbs))


def run(samples, sample_ids, label, p_name, already_there):
    standard_dbs = []
    if TESTING:
        dbs = ['drug']
    else:
        dbs = ['drug', 'disease', 'ontologies', 'pathways', 'transcription',
               'kinases', 'histone', 'cell_type']

    for i in dbs:
        standard_dbs += db_types[i]

    for genes, sample_id in zip(samples, sample_ids):
        print("Starting {}".format(sample_id))

        current = "{}_{}_{}".format(label, sample_id, p_name)
        print(standard_dbs)
        if current not in already_there:
            run_set_of_dbs.apply_async(
                args=(list(genes), sample_id, standard_dbs, label, p_name),
                countdown=30
            )
        print("Finished {}".format(sample_id))


def run_enrichment_for_project(exp_data, project_name, output_path=None):
    """

    Parameters
    ----------
    exp_data : magine.data.ExperimentalData
    project_name : str
    output_path : str
        Location to save all individual enrichment output files created.

    """
    logger.info("Running enrichment for project".format(project_name))

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

    if USE_CELERY:
        _run = run
    else:
        _run = _run_new
    #  run all protein labeled species grouped by time point
    #  ( label-free, ph-silac, etc are all combined)
    if len(exp_data.proteins.sample_ids) != 0:
        sample = exp_data.proteins.sig
        if TESTING:
            _run(sample.by_sample, sample.sample_ids, 'proteomics_both')
        else:
            _run(sample.by_sample, sample.sample_ids, 'proteomics_both')
            _run(sample.up_by_sample, sample.sample_ids, 'proteomics_up')
            _run(sample.down_by_sample, sample.sample_ids, 'proteomics_down')
    if not TESTING:
        #  run all RNA labeled species grouped by time point
        if len(exp_data.rna.sample_ids) != 0:
            sample = exp_data.rna.sig
            _run(sample.by_sample, sample.sample_ids, 'rna_both')
            _run(sample.down_by_sample, sample.sample_ids, 'rna_down')
            _run(sample.up_by_sample, sample.sample_ids, 'rna_up')

        #  run each experimental 'source' by time point
        #  ( label-free, ph-silac, etc are all separate)
        for source in exp_data.exp_methods:
            df = exp_data[source].sig
            col_options = df['species_type'].unique()
            # make sure there is only a single species type and it is protein
            # this makes sure that the RNA seq doesnt get ran twice
            if len(col_options) != 1:
                continue
            ids = df.sample_ids
            if col_options[0] == 'protein':
                _run(df.by_sample, ids, '{}_both'.format(source))
                _run(df.up_by_sample, ids, '{}_up'.format(source))
                _run(df.down_by_sample, ids, '{}_down'.format(source))

    if not USE_CELERY:
        # merge all outputs
        final_df = pd.concat(all_df, ignore_index=True)
        final_df = final_df[
            ['term_name', 'rank', 'combined_score', 'adj_p_value', 'p_value',
             'genes', 'z_score', 'n_genes', 'sample_id', 'category', 'db']
        ]

        final_df = _check_nan_add_sig(final_df)
        final_df['project_name'] = project_name
        EnrichmentOutput.objects.bulk_create(
            [EnrichmentOutput(**r) for r in final_df.to_dict(orient='records')]
        )
        logger.info("Saving output: {}_enrichment.csv.gz".format(project_name))
        final_df.to_csv('{}_enrichment.csv.gz'.format(project_name),
                        encoding='utf-8', compression='gzip', index=False)


def _check_nan_add_sig(df):
    # remove rows without a term name
    df = df[~df['term_name'].isnull()].copy()
    df = df[~df['term_name'] == ''].copy()
    df = df[~df['adj_p_value'].isnull()].copy()
    df = df[~df['combined_score'].isnull()].copy()
    df = df[~df.isnull()].copy()
    df['combined_score'] = df['combined_score'].astype(float)
    df['significant'] = False
    # Adds significant column
    df.loc[(df['adj_p_value'] <= 0.05) &
           (df['combined_score'] > 0.0), 'significant'] = True
    df = df[df['adj_p_value'] < 0.2]
    return df
