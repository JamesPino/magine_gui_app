import re
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


def convert_to_rankable_time(data):
    def h_to_hr(row):
        if row[sample_id].endswith('h') or row[sample_id].endswith('hr'):
            number = re.findall('\d+', row[sample_id])
            if len(set(number)) == 1:
                return number[0] + 'hr'
            else:
                return row[sample_id].replace('h', 'hr')
            # return number.replace('h', 'hr')
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
    data[sample_id] = data.apply(pad_string, axis=1)

    return data


# function to correct genes converting to months (if touched by excel)
_names = {}
for i in range(16):
    _names['{0}-Sep'.format(i)] = 'SEPT{0}'.format(i)
    _names['{0}-Mar'.format(i)] = 'MARCH{0}'.format(i)
    _names['{0}-Dec'.format(i)] = 'DEC{0}'.format(i)
