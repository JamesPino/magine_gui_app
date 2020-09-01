import re

import numpy as np
import pandas as pd
from .standard_cols import *


def load_from_zip(filename):
    """ Creates a pandas.Dataframe from omics data files

    Parameters
    ----------

    filename : zipfile.ZipFile
        name of file

    Returns
    -------
    pd.Dataframe

    """

    data = pd.read_csv(filename, parse_dates=False, low_memory=False,
                       encoding='utf8')
    if 'compound' in data.columns.values:
        return data

    if 'gene' in data.dtypes:
        data['primary_genes'] = data['gene']
        data = check_data(data, 'primary_genes')
        return data

    if 'primary_genes' in data.dtypes:
        data['gene'] = data['primary_genes']
        data = check_data(data, 'primary_genes')
        return data

    else:
        return data


def check_data(data, keyword):
    genes = list(data[keyword])
    for n in _names:
        if n in genes:
            data.loc[data[keyword] == n, keyword] = _names[n]
    return data


def convert_time_to_hours(d):
    """ replaces string of time point with float

    Parameters
    ----------
    d: pandas.Dataframe
        pandas.Dataframe

    Returns
    -------

    """
    t = d['time_points']
    if isinstance(t, float):
        return t
    if 's' in t:
        time = float(t.replace('s', '')) / 3600.
    elif 'min' in t:
        time = float(t.replace('min', '')) / 60.
    elif 'hr' in t:
        t = t.replace('hr', '')
        if 'h' in t:
            t = t.replace('h', '')
        time = float(t)
    elif 'h' in t:
        time = float(t.replace('h', ''))
    else:
        print('no time')
        return None
    return time


def convert_to_rankable_time(data):
    def h_to_hr(row):
        if row[sample_id].endswith('h'):
            return row[sample_id].replace('h', 'hr')
        else:
            return row[sample_id]

    def m_to_min(row):
        if row[sample_id].endswith('m'):
            return row[sample_id].replace('m', 'min')
        else:
            return row[sample_id]

    def pad_string(row):
        t = row[sample_id]
        t = t.replace(' ', '')
        number = re.findall('\d+', t)[0]

        nondigits = t.replace(number, '')
        if 'min' in nondigits:
            out = '{0:05d}_{1}'
        elif 'hr' in nondigits:
            out = '{0:03d}_{1}'
        elif 's' in nondigits:
            out = '{0:06d}_{1}'

        out = out.format(int(number), nondigits)
        return out
    data[sample_id] = data.apply(h_to_hr, axis=1)
    data[sample_id] = data.apply(m_to_min, axis=1)
    data[sample_id] = data.apply(pad_string, axis=1)

    return data


_names = {}
for i in range(16):
    _names['{0}-Sep'.format(i)] = 'SEPT{0}'.format(i)
    _names['{0}-Mar'.format(i)] = 'MARCH{0}'.format(i)
    _names['{0}-Dec'.format(i)] = 'DEC{0}'.format(i)
