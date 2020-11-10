#!/usr/bin/env python

import sys, os, json, string, difflib
import pandas as pd
from collections import defaultdict

from better_align_util import get_before_util, get_after_util, better_align

# data

# PASSAGE_WITH_LINE_BREAK_AND_RECSTRING = 'data/moby-passages-36/passages-with-line-break-and-recstring.tsv'
# PASSAGES_WITH_LINE_BREAKS = 'data/moby-passages-36/passages-with-line-breaks.tsv'

####
# ITEM_NUMBER = 2201
ITEM_NUMBER = int(sys.argv[1]) 
# ALIGNMENT = 'data/moby-passages-36/data-2202/child/alignment_2202_184.csv'
# F0 = 'data/moby-passages-36/data-2202/child/F0_2202_184.csv'

# ALIGNMENT = 'data/moby/session-info/2202/alignment_2202_182.csv'
ALIGNMENT = sys.argv[2]
F0 = sys.argv[3]
# F0 =        'data/moby/session-info/2202/f0_2202_182.csv'
####

# Output

# OUTPUT_DIR = 'output/performance-matrix/test/'
OUTPUT_DIR = sys.argv[4]
FILENAME_PREFIX = OUTPUT_DIR + ''

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# print(sys.argv)    
    
# df_full_texts_and_recstrings = pd.read_csv(PASSAGE_WITH_LINE_BREAK_AND_RECSTRING, sep='\t')
# item_number_to_recstring = dict(zip(df_full_texts_and_recstrings.Item, df_full_texts_and_recstrings['Rec String']))
# df_text_with_line_breaks = pd.read_csv(PASSAGES_WITH_LINE_BREAKS, sep='\t', names=['Item', 'Passage'])
# item_number_to_text_with_line_breaks = dict(zip(df_text_with_line_breaks.Item, df_text_with_line_breaks.Passage))
# item_number_to_text_with_line_breaks = {
#     k: v[:v.index('#')].replace('$$', ' PARBREAK ').replace('$', ' LINEBREAK ').replace(' 45 ', ' forty five ')
#     for k, v in item_number_to_text_with_line_breaks.items()
# }

with open('data/moby/jsons/item_to_passage.json') as f:
    item_number_to_text_with_line_breaks = json.load(f)
with open('data/moby/jsons/item_to_recstring.json') as f:
    item_number_to_recstring = json.load(f)

def get_processed_token(token):
    rv = token
    while rv[0] in string.punctuation:
        rv = rv[1:]
    while rv[-1] in string.punctuation:
        rv = rv[:-1]
    return rv.lower()

for item, text_with_breaks in item_number_to_text_with_line_breaks.items():
    recstring = item_number_to_recstring[item]
    text_with_breaks_processed = [
        get_processed_token(token)
        for token in text_with_breaks.split()
        if token != 'LINEBREAK' and token != 'PARBREAK'
    ]
    assert recstring.split() == text_with_breaks_processed, (text_with_breaks_processed, recstring.split())
gen = lambda lst: (x for x in lst)
df_alignment_child = pd.read_csv(ALIGNMENT, sep=',')
session, sframe, nframes, word = df_alignment_child.session, df_alignment_child.sframe, df_alignment_child.nframes, df_alignment_child.word
session, sframe, nframes, word = gen(session), gen(sframe), gen(nframes), gen(word)

print(ALIGNMENT)

session_to_alignment = defaultdict(list)
for session_id in session:
    sframe_val, nframes_val, word_val = next(sframe), next(nframes), next(word)
    if word_val[0] == '<':
        word_val = '<pause>'
    session_to_alignment[session_id].append([word_val, sframe_val, nframes_val])
df_f0_child = pd.read_csv(F0, sep=',')
df_f0_child.value = [[float(y.split(':')[0]) for y in x.split()] for x in df_f0_child.value]
session, value = df_f0_child.session, df_f0_child.value
session, value = gen(session), gen(value)
session_to_f0 = {}
for session_id in session:
    session_to_f0[session_id] = next(value)

print('len:', len(session_to_alignment))

def CREATE_FEATURE_VECTOR(
    token='',
    matches_expected=0,
    sframe=0,
    nframes=0,
    pitch_mean=0,
    pitch_start=0,
    pitch_end=0,
    pitch_high=0,
    pitch_low=0,
    pitch_slope=0):
    rv = {
        'token': token,
        'matches_expected': matches_expected,
        'sframe': sframe,
        'nframes': nframes,
        'pitch_mean': pitch_mean,
        'pitch_start': pitch_start,
        'pitch_end': pitch_end,
        'pitch_high': pitch_high,
        'pitch_low': pitch_low,
        'pitch_slope': pitch_slope
    }
    return rv

session_to_features = {}
new_feature_names = [
    'token',
    'matches_expected'
    'sframe',
    'nframes',
    'pitch_mean',
    'pitch_start',
    'pitch_end',
    'pitch_high',
    'pitch_low',
    'pitch_slope'
]

print('len:', len(session_to_alignment))
for session, alignment in session_to_alignment.items():
    recording_mean = sum(session_to_f0[session]) / len(session_to_f0[session])
    session_to_features[session] = []
    for token, sframe, nframes in alignment:
        f0s = session_to_f0[session][sframe:sframe + nframes]
        f0s = [x for x in f0s if x]
        pitch_mean = sum(f0s) / len(f0s) if f0s else 0
        pitch_start = f0s[0]
        pitch_end = f0s[-1]
        pitch_high = max(f0s)
        pitch_low = min(f0s)
        pitch_slope = (pitch_end - pitch_start) / len(f0s)        
        new_features = CREATE_FEATURE_VECTOR(
            token=token,
            sframe=sframe,
            nframes=nframes,
            pitch_mean=pitch_mean,
            pitch_start=pitch_start,
            pitch_end=pitch_end,
            pitch_high=pitch_high,
            pitch_low=pitch_low,
            pitch_slope=pitch_slope
        )
        session_to_features[session].append(new_features)
recstring_330_with_pauses = ('<pause> ' + ' <pause> '.join(item_number_to_recstring[str(ITEM_NUMBER)].split()) + ' <pause>').split()
recstring_330_with_pauses[:5]

differ = difflib.Differ()

session_to_naive_alignment = {}
for session, features in session_to_features.items():
    transcribed_tokens = [x['token'] for x in features]
    diff = differ.compare(transcribed_tokens, recstring_330_with_pauses)
    
    # remove '?' lines
    diff = (x for x in list(diff) if x[0] != '?')
    
    # +: in full recstring but not in transcribed tokens (often, dummy <pause>s)
    # -: in transcribed tokens but not in full recstring (child added words)
    
    naive_alignment = [[] for x in recstring_330_with_pauses]
    for idx in range(len(naive_alignment)):
        while True:
            diff_next = next(diff)
            if diff_next[0] == ' ':
                naive_alignment[idx].append(diff_next[2:])
                break
            if diff_next[0] == '+':
                break
            
            # diff_next[0] == '-'
            naive_alignment[idx].append(diff_next[2:])
    session_to_naive_alignment[session] = naive_alignment
session_to_features_added_pause = {}
for session, features in session_to_features.items():
    tokens = [x['token'] for x in features]
    if tokens[-1] != '<pause>':
        features.append(CREATE_FEATURE_VECTOR(token='<pause>'))
    if token[0] != '<pause>':
        features.insert(0, CREATE_FEATURE_VECTOR(token='<pause>'))
    session_to_features_added_pause[session] = features
session_to_features = session_to_features_added_pause

print('len:', len(session_to_features))
session_to_naive_alignment = {}
for session, features in session_to_features.items():
    transcribed_tokens = [x['token'] for x in features]
    try:
        session_to_naive_alignment[session] = better_align(transcribed_tokens, recstring_330_with_pauses)
    except:
        print('Failed at session', session)
# COPIED FROM ABOVE:
# features = {
#     'token': token,
#     'matches_expected': matches_expected,
#     'sframe': sframe,
#     'nframes': nframes,
#     'pitch_mean': pitch_mean,
#     'pitch_end': pitch_end,
#     'pitch_high': pitch_high,
#     'pitch_low': pitch_low,
#     'pitch_slope': pitch_slope
# }

N_FEATURES = len(new_feature_names)

print('len:', len(session_to_naive_alignment))
new_compiled_features = {}
for session, naive_alignment in session_to_naive_alignment.items():
    features = session_to_features[session]
    recompiled_features = []
    previous_features_matrix_row_idx = 0
    
    for expected_token, aligned_token_group in zip(recstring_330_with_pauses, naive_alignment):
        if aligned_token_group == []:
            recompiled_features.append(CREATE_FEATURE_VECTOR(matches_expected=0))
            continue
        if len(aligned_token_group) == 1:
            is_correct_token = 1 if aligned_token_group[0] == expected_token else 0
            old_features = features[previous_features_matrix_row_idx]
            old_features['matches_expected'] = is_correct_token
            
            if aligned_token_group[0] == '<pause>':
                old_features['pitch_mean'] = 0
                old_features['pitch_start'] = 0
                old_features['pitch_end'] = 0
                old_features['pitch_high'] = 0
                old_features['pitch_low'] = 0
                old_features['pitch_slope'] = 0
            
            recompiled_features.append(old_features)
            previous_features_matrix_row_idx += 1
        
        else:
            # multiple tokens
            num_tokens = len(aligned_token_group)
            features_for_token_group = [features[i] for i in range(previous_features_matrix_row_idx, previous_features_matrix_row_idx + num_tokens)]
            
            '''
            Now compile new features
            '''
            last_token_in_token_group = aligned_token_group[-1]
            features_for_last_token = features_for_token_group[-1]
            # if last_token_in_token_group == expected_token:
            #     token = expected_token
            # else:
            #     token = ' '.join(aligned_token_group)
            token = ' '.join(aligned_token_group)
            sframe = features_for_token_group[0]['sframe'] # sframe for updated feature is the sframe for the first token in the aligned token group
            nframes = sum(f['nframes'] for f in features_for_token_group)
            
            # pitch-related features can match that of the last token, even if it is not the expected token
            pitch_mean = features_for_last_token['pitch_mean']
            pitch_start = features_for_last_token['pitch_start']
            pitch_end = features_for_last_token['pitch_end']
            pitch_high = features_for_last_token['pitch_high']
            pitch_low = features_for_last_token['pitch_low']
            pitch_slope = features_for_last_token['pitch_slope']
            
            if token == '<pause>':
                pitch_mean = 0
                pitch_start = 0
                pitch_end = 0
                pitch_high = 0
                pitch_low = 0
                pitch_slope = 0
            
            new_feature_to_add = CREATE_FEATURE_VECTOR(
                token=token,
                matches_expected=0,
                sframe=sframe,
                nframes=nframes,
                pitch_mean=pitch_mean,
                pitch_start=pitch_start,
                pitch_end=pitch_end,
                pitch_high=pitch_high,
                pitch_low=pitch_low,
                pitch_slope=pitch_slope
            )
            recompiled_features.append(new_feature_to_add)
            previous_features_matrix_row_idx += num_tokens
    new_compiled_features[session] = recompiled_features
    
for sess, align in new_compiled_features.items():
    for feature in align:
        if feature['token'] == '<pause>':
            assert feature['pitch_slope'] == 0

print('dumping to:', FILENAME_PREFIX)
            
print('len:', len(new_compiled_features))
for session, features in new_compiled_features.items():
    matrix = pd.DataFrame(features)
    matrix.index = recstring_330_with_pauses
    matrix.to_csv(FILENAME_PREFIX + str(session) + '.tsv', sep='\t')