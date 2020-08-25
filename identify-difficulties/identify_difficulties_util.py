#!/usr/bin/env python3

# identify_difficulties_util.py

import math
import pandas as pd

# def truncate(number, digits):
#     stepper = 10.0 ** digits
#     return math.trunc(stepper * number) / stepper

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
    if not Q:
        return -1
    return len(set(D) & set(Q)) / len(Q)


def compute_difficult_words_overlap_proportion(
    difficult_words_indices,
    column_name,
    text_analysis_column_1,
    text_analysis_column_2=None,
    text_analysis_column_3=None,
    mode='binary',
    n_splits_if_continuous=5):
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
            column_name + '_true_overlap_proportion': true_overlap_proportion,
            column_name + '_false_overlap_proportion': false_overlap_proportion
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

            if less_than_value_overlap_proportion >= 0 and\
                more_than_value_overlap_proportion >= 0:
                rv[column_name + '_less_than_' + str(separating_value) +\
                    '_proportion'] = less_than_value_overlap_proportion
                rv[column_name + '_more_than_' + str(separating_value) +\
                    '_proportion'] = more_than_value_overlap_proportion

        return rv

    if mode == 'continuous':
        all_values = text_analysis_column_1 + text_analysis_column_2 +\
            text_analysis_column_3
        min_value, max_value = min(all_values), max(all_values)

        bin_size = (max_value - min_value) / (n_splits_if_continuous + 1)

        rv = {}
        for i in range(n_splits_if_continuous):
            separating_value = min_value + (i + 1) * bin_size
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

            if less_than_value_overlap_proportion >= 0 and\
                more_than_value_overlap_proportion >= 0:
                rv[column_name + '_less_than_' + str(separating_value) +\
                    '_proportion'] = less_than_value_overlap_proportion
                rv[column_name + '_more_than_' + str(separating_value) +\
                    '_proportion'] = more_than_value_overlap_proportion

        return rv

        




# PERFORMANCE_MATRIX_1 = '../output/performance_matrix/330_child_updated_20200809/30908.tsv'
# df = pd.read_csv(PERFORMANCE_MATRIX_1, sep='\t')

# rv = find_problem_words_given_df_naive(df, None, None)

# print(rv)