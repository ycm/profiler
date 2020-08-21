#!/usr/bin/env python3

# text_analysis_util.py
# Utility functions for compiling text analysis matrix

import string

def given_word_test_if_word_is_end_of_sentence(word):
    if word in {'Ms.', 'Mrs.', 'Mr.', 'Dr.'}:
        return False
    while word[-1] in {'"', "'"}:
        word = word[:-1]
    return word[-1] in {'.', '!', '?'}

def given_word_remove_punctuation(word):
    if word in {'$', '*'}:
        return ''

    while word[0] == '"' or word[0] == "'":
        word = word[1:]
    while word[-1] == '"' or word[-1] == "'":
        word = word[:-1]

    if word not in {'Ms.', 'Mrs.', 'Mr.', 'Dr.'}:
        if word[-1] in {'.', '!', ',', '?'}:
            word = word[:-1]
            while word[0] == '"' or word[0] == "'":
                word = word[1:]
            while word[-1] == '"' or word[-1] == "'":
                word = word[:-1]
    return word

def text_analysis_tokenize(full_text):
    text_cleaned = full_text[:full_text.index('#')] \
        .replace('$$', ' * ') \
        .replace('$', ' $ ') 

    text_split_on_space = text_cleaned.split()

    return text_split_on_space

def turn_token_to_recstring_format(token):
    rv = token
    while rv and rv[0] in string.punctuation:
        rv = rv[1:]
    while rv and rv[-1] in string.punctuation:
        rv = rv[:-1]
    return rv.lower()

def turn_tokens_to_recstring(passage):
    rv = []
    for word in passage:
        if word == '*' or word == '$':
            continue
        while word[0] in string.punctuation:
            word = word[1:]
        while word[-1] in string.punctuation:
            word = word[:-1]
        rv.append(word.lower())
    return rv

if __name__ == "__main__":
    # rv = text_analysis_tokenize("Meg wanted to bake a pie. She asked her mother for help.$$They measured the flour, sugar, and butter for the crust. $Her mother showed her how to roll out the crust. Meg sliced $the apples and put them in the pie pan. They put the pie $in the hot oven and waited forty five minutes.$$As the pie baked, a delicious smell filled the kitchen. When $the timer rang, they took the pie out of the oven and $set it on the window sill to cool.#1#1.35#1#0.535")
    # print(rv)

    pass