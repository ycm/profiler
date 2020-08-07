#!/usr/bin/env python3
# constituency_retrieval_util.py

import pandas as pd

def get_full_indices_includings_pauses(indices):
    # [2,3,4] -> [1,2,3,4]
    return list(range(indices[0] - 1 + indices[-1] + 1))

def get_partial_column(df, indices, column_name):
    col = list(df[column_name])
    return [col[i] for i in indices]

if __name__ == "__main__":
    df_child = pd.read_csv('output/performance_matrix/330_child_updated_20200729/47041.tsv', sep='\t')
    print(get_partial_column(df_child, [1,2], 'pitch_slope'))