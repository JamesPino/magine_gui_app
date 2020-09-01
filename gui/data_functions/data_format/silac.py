import re

from .utils import load_from_zip
from .standard_cols import *


def process_silac(filename):
    data = load_from_zip(filename)


    # data = data[data['n_significant'] == 2]

    data.loc[:, fold_change] = data['mean_treated_untreated_fold_change']
    data.loc[:, flag] = False
    data.loc[:, p_val] = 1.0

    criteria = (data['tier_level'] == 1) & (data['fold_change_magnitude'] == 2)
    data.loc[criteria, p_val] = 0.049
    data.loc[criteria, flag] = True

    data.loc[:, exp_method] = 'silac'
    data.loc[:, identifier] = data['primary_genes']
    data.loc[:, label] = data['primary_genes'] + '_silac'

    data.loc[:, species_type] = 'protein'
    data.loc[:, sample_id] = data['time_points']

    return data


def process_phsilac(filename):
    data = load_from_zip(filename)

    data.loc[:, 'phosphorylated_amino_acid'] = \
        data['phosphorylated_amino_acid'].astype(str)

    mod_sites = data[['modified_sequence', 'modified_seq_location',
                      'phosphorylated_amino_acid']]
    protein_names = []
    for i, row in mod_sites.iterrows():
        seq = row['modified_sequence'].strip('_')
        aa = row['phosphorylated_amino_acid']
        loc = row['modified_seq_location']

        if aa == 'nan':
            reg = '_'.join(loc.split(','))
            reg = reg.replace(' ', '')

            out_string = ''
            for word in ['(ca)', '(ox)']:
                if word in seq:
                    out_string += '_' + word
            protein_names.append("{}_{}_phsilac".format(out_string, reg))
            continue
        aa = aa.split(',')

        if loc == 'NA, NA':
            protein_names.append("_{}_phsilac".format(seq))
            continue
        start_loc = int(loc.split(',')[0])
        s = '_'
        for word in ['(ca)', '(ox)']:
            seq = seq.replace(word, '')
        mod = -2
        for n, m in enumerate(re.finditer('(ph)', seq)):
            s += '{0}(ph){1}_'.format(aa[n], m.start() + start_loc + mod)
            mod -= 4
        s += 'phsilac'
        protein_names.append(s)

    data.loc[:, label] = data['primary_genes'] + protein_names
    data.loc[:, identifier] = data['primary_genes']
    data.loc[:, fold_change] = data['both_fold_change_mean']
    data.loc[:, p_val] = 1.0
    data.loc[:, flag] = False

    criteria = (data['overall_significance'].isin(['SIGNIFICANT',
                                                   'significant']))

    data.loc[criteria, p_val] = 0.049
    data.loc[criteria, flag] = True

    data.loc[:, exp_method] = 'ph_silac'
    data.loc[:, species_type] = 'protein'
    data.loc[:, sample_id] = data['time_points']

    return data

