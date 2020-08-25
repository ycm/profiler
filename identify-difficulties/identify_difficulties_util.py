#!/usr/bin/env python3

# identify_difficulties_util.py

import pandas as pd

def find_problem_words_given_df_naive(perf_df, pause_threshold, expected_pauses):
    token_list            = perf_df.token
    matches_expected_list = perf_df.matches_expected
    nframes_list          = perf_df.nframes
    rv                    = []
    for idx, (token, matches_expected) in \
        enumerate(zip(token_list, matches_expected_list)):
        if idx % 2 == 0: # <pause>
            continue
        if not matches_expected:
            rv.append(idx)
            continue
        prev_pause_length = nframes_list[idx - 1]
        if prev_pause_length >= pause_threshold:
            if idx - 1 not in expected_pauses:
                rv.append(idx)
    return rv

def helper_find_overlap_proportion(D, Q):
    return len(set(D) & set(Q)) / len(Q)


def compute_difficult_words_overlap_proportion(
    difficult_words_indices,
    text_analysis_column_1,
    text_analysis_column_2=None,
    text_analysis_column_3=None,
    mode='binary',
    n_bins_if_continuous=5):
    assert mode in {'binary', 'discrete', 'continuous'}, 'Invalid mode.'

    # difficult_words_indices are indices of a PERF MATRIX.
    # perf matrices have twice as many rows as a TEXT ANALYSIS MATRIX.
    difficult_indices = [(i - 1) // 2 for i in difficult_words_indices]
    # print('debug: difficult indices from', difficult_words_indices)
    # print('to:', difficult_indices)
    if mode == 'binary':
        # True
        text_analysis_true_indices =\
            [idx for idx, value in enumerate(text_analysis_column_1) if value]
        
        true_overlap_proportion = helper_find_overlap_proportion(
            difficult_indices, text_analysis_true_indices
        )

        # False
        text_analysis_false_indices =\
            [idx for idx, val in enumerate(text_analysis_column_1) if not val]

        false_overlap_proportion = helper_find_overlap_proportion(
            difficult_indices, text_analysis_false_indices
        )

        return {
            'true_overlap_proportion': true_overlap_proportion,
            'false_overlap_proportion': false_overlap_proportion
        }

    assert text_analysis_column_2 and text_analysis_column_3,\
        'Need text analysis columns for two more readings.'
        
    if mode == 'discrete':
        possible_separating_values = sorted(list(set(text_analysis_column_1) |\
            set(text_analysis_column_2) | set(text_analysis_column_3)))

        rv = {}
        for separating_value in possible_separating_values:
            less_than_value_indices = [
                idx for idx, value in enumerate(text_analysis_column_1)
                if value < separating_value
            ]

            less_than_value_overlap_proportion = helper_find_overlap_proportion(
                difficult_indices, less_than_value_indices
            )

            more_than_value_indices = [
                idx for idx, value in enumerate(text_analysis_column_1)
                if value >= separating_value
            ]

            more_than_value_overlap_proportion = helper_find_overlap_proportion(
                difficult_indices, more_than_value_indices
            )

            rv['less_than_' + str(separating_value) + '_proportion'] =\
                less_than_value_overlap_proportion
            rv['more_than_' + str(separating_value) + '_proportion'] =\
                more_than_value_overlap_proportion

        return rv

    if mode == 'continuous':
        pass




# PERFORMANCE_MATRIX_1 = '../output/performance_matrix/330_child_updated_20200809/30908.tsv'
# df = pd.read_csv(PERFORMANCE_MATRIX_1, sep='\t')

# rv = find_problem_words_given_df_naive(df, None, None)

# print(rv)