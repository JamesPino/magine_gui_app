import zipfile

import pandas as pd

from .metabolites import process_metabolites
from .proteomics import process_label_free, process_subcell_label_free
from .rna import process_rna_seq
from .silac import process_silac, process_phsilac
from .standard_cols import *
from .utils import convert_to_rankable_time

valid_cols = [identifier, label, fold_change, flag, p_val, species_type,
              sample_id, exp_method]


def process_raptr_zip(filename):
    all_data = []

    with zipfile.ZipFile(filename) as zip_file:
        # get the list of files
        for i in zip_file.namelist():
            print('on {}'.format(i))
            if 'progenesis' in i:
                all_data.append(
                    process_metabolites(zip_file.open(i))[valid_cols])
            elif 'subcell' in i:
                all_data.append(
                    process_subcell_label_free(zip_file.open(i))[valid_cols])
            elif '_silac' in i:
                all_data.append(process_silac(zip_file.open(i))[valid_cols])
            elif 'ph-silac' in i:
                all_data.append(process_phsilac(zip_file.open(i))[valid_cols])
            elif 'protalizer_protein' in i:
                all_data.append(
                    process_label_free(zip_file.open(i))[valid_cols])
            elif 'cuffdiff' in i:
                all_data.append(process_rna_seq(zip_file.open(i))[valid_cols])
            else:
                print("Dont know {}".format(i))
    data = pd.concat(all_data, ignore_index=True)
    data = convert_to_rankable_time(data)
    return data[valid_cols]
