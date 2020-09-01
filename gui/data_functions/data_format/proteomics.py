import re
import numpy as np
import pandas as pd

from .utils import load_from_zip
from .standard_cols import *


def process_label_free(filename):
    label_free = load_from_zip(filename)

    label_free[identifier] = label_free['primary_genes']
    label_free.dropna(subset=[identifier], inplace=True)
    label_free[species_type] = protein

    label_free[label] = label_free.apply(find_mod, axis=1)

    label_free[exp_method] = 'label_free'
    label_free[p_val] = label_free['p_value_group_1_and_group_2']
    label_free[fold_change] = label_free['treated_control_fold_change']
    label_free[flag] = label_free['significant_flag']
    label_free.loc[:, sample_id] = label_free['time_points']
    return label_free


def process_subcell_label_free(filename):
    label_free = load_from_zip(filename)

    label_free = label_free.loc[~label_free['translocation'].isnull()]

    label_free[exp_method] = 'label_free_translocation'

    label_free[identifier] = label_free['primary_genes']
    label_free.dropna(subset=[identifier], inplace=True)

    label_free[label] = label_free.apply(find_mod, axis=1)
    label_free[label] = label_free[label] + '_' + \
                        label_free['from_components'] + '_to_' + \
                        label_free['to_components']

    label_free[species_type] = protein
    label_free[flag] = True
    label_free[p_val] = 0.0001
    label_free[fold_change] = 2.
    label_free.loc[:, sample_id] = label_free['time_points']
    return label_free


def find_mod(row):
    s = str(row['protein'])
    if s.startswith('Acetylation'):
        change = 'ace'
        residue = s[s.find("(") + 1:s.find(")")]
        loc = re.findall('@\d+', s)[0].strip('@')
        name = "{0}_{1}({2}){3}_lf".format(row['gene'], residue, change,
                                           loc)

    elif s.startswith('Phosphorylation'):
        change = 'ph'
        residue = s[s.find("(") + 1:s.find(")")]
        loc = re.findall('@\d+', s)[0].strip('@')
        name = "{0}_{1}({2}){3}_lf".format(row['gene'], residue, change,
                                           loc, )
    else:
        name = row['gene'] + '_lf'
    return name
