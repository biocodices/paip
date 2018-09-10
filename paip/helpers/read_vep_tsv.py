import pandas as pd


def read_vep_tsv(vep_tsv_filepath):
    """
    Read the Variant Effect Predictor annotations TSV file as a DataFrame.
    The generated dataframe will have 'vep_' prefixed in every column.
    """
    # The headers are in the first line that starts with a single "#"
    with open(vep_tsv_filepath) as f:
        for line in f:
            if line.startswith('#') and not line.startswith('##'):
                fields = [field.strip().strip('#').lower()
                          for field in line.split('\t')]
                break

    df = pd.read_table(vep_tsv_filepath,
                       comment='#', names=fields, na_values='-')
    df = df.applymap(lambda value: None if pd.isnull(value) else value)

    return df

