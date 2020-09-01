import pandas as pd

from .utils import load_from_zip
from .standard_cols import *


def process_rna_seq(filename):
    data = load_from_zip(filename)
    data = data[data['status'] == 'OK']
    s = data['gene'].str.split(',').apply(pd.Series, 1).stack()
    s.index = s.index.droplevel(-1)
    s.name = 'gene'
    del data['gene']
    data = data.join(s)

    data[flag] = data['significant_flag']

    data.loc[:, p_val] = data['q_value']
    crit = (data[fold_change] > 0) & (data[fold_change] < 1.5) & data[flag]

    data.loc[crit, flag] = False

    crit = (data[fold_change] < 0) & (data[fold_change] > -1.5) & data[flag]
    data.loc[crit, flag] = False

    data.loc[:, identifier] = data['gene']
    data.loc[:, label] = data[identifier] + '_rnaseq'
    data.loc[:, exp_method] = 'rna_seq'
    data.loc[:, species_type] = rna
    data.loc[:, sample_id] = data['time_points']

    return data
