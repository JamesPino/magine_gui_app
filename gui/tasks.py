from magine.enrichment.enrichr import Enrichr, db_types
from gui.models import EnrichmentOutput
# from magine_gui_app.celery import app
# from celery.utils.log import get_task_logger

# logger = get_task_logger(__name__)


def run(samples, sample_ids, label, p_name, already_there):
    standard_dbs = []
    dbs = ['drug', 'disease', 'ontologies', 'pathways', 'transcription',
           'kinases', 'histone', 'cell_type']
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
