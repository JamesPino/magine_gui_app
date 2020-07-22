import numpy as np
from magine.data.experimental_data import ExperimentalData


def convert_to_dict(table):
    t = table.replace('-', np.nan)
    t_dict = t.to_dict()
    new_dict = dict()
    for time, i in sorted(t_dict.items()):
        for key, value in i.items():
            if value not in (np.nan, 'Total Unique Across'):
                if np.isfinite(value):
                    value = int(value)
            if key in new_dict:

                new_dict[key][time] = value
            else:
                new_dict[key] = dict()
                new_dict[key][time] = value

    return new_dict


def get_all_tables(data):
    """

    Parameters
    ----------
    data: ExperimentalData

    Returns
    -------

    """

    sample_ids = data.sample_ids
    sample_ids.append('Total Unique Across')
    all_measured = convert_to_dict(
        data.create_summary_table(False, index='identifier')
    )
    uni_measured = convert_to_dict(
        data.create_summary_table(False, index='label')
    )
    sig_measured = convert_to_dict(
        data.create_summary_table(True, index='identifier')
    )
    sig_uni = convert_to_dict(
        data.create_summary_table(True, index='label')
    )
    return sample_ids, all_measured, uni_measured, sig_measured, sig_uni

