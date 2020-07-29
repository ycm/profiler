#!/usr/bin/env python3

import difflib

child_tokens = ['room', '<pause>', '<pause>', 'room', 'six', '<pause>', 'is', 'learning', 'to', 'grow', 'plants', '<pause>', 'each', 'student', '<pause>', 'has', 'a', 'plant', '<pause>', 'and', 'a', 'pot', '<pause>', 'the', 'kids', '<pause>', 'will', 'learn', 'to', 'take', 'care', 'of', 'the', 'houseplants', 'as', 'they', 'grow', '<pause>', 'everyday', '<pause>', 'they', 'will', 'write', 'in', 'their', 'journals', '<pause>', 'as', 'they', 'learn', 'about', 'the', 'needs', 'of', 'their', 'plants', '<pause>', 'at', 'the', 'end', 'of', 'the', 'school', 'year', '<pause>', 'they', 'will', 'take', 'their', 'plants', 'home', '<pause>', 'but', 'for', 'now', '<pause>', 'the', 'classroom', 'is', 'much', 'greener', '<pause>', 'with', '<pause>', 'so', 'many', 'different', 'plants', 'around', 'the', 'room', '<pause>']
gold = ['<pause>', 'room', '<pause>', 'six', '<pause>', 'is', '<pause>', 'learning', '<pause>', 'to', '<pause>', 'grow', '<pause>', 'plants', '<pause>', 'each', '<pause>', 'student', '<pause>', 'has', '<pause>', 'a', '<pause>', 'plant', '<pause>', 'and', '<pause>', 'a', '<pause>', 'pot', '<pause>', 'the', '<pause>', 'kids', '<pause>', 'will', '<pause>', 'learn', '<pause>', 'to', '<pause>', 'take', '<pause>', 'care', '<pause>', 'of', '<pause>', 'the', '<pause>', 'houseplants', '<pause>', 'as', '<pause>', 'they', '<pause>', 'grow', '<pause>', 'everyday', '<pause>', 'they', '<pause>', 'will', '<pause>', 'write', '<pause>', 'in', '<pause>', 'their', '<pause>', 'journals', '<pause>', 'as', '<pause>', 'they', '<pause>', 'learn', '<pause>', 'about', '<pause>', 'the', '<pause>', 'needs', '<pause>', 'of', '<pause>', 'their', '<pause>', 'plants', '<pause>', 'at', '<pause>', 'the', '<pause>', 'end', '<pause>', 'of', '<pause>', 'the', '<pause>', 'school', '<pause>', 'year', '<pause>', 'they', '<pause>', 'will', '<pause>', 'take', '<pause>', 'their', '<pause>', 'plants', '<pause>', 'home', '<pause>', 'but', '<pause>', 'for', '<pause>', 'now', '<pause>', 'the', '<pause>', 'classroom', '<pause>', 'is', '<pause>', 'much', '<pause>', 'greener', '<pause>', 'with', '<pause>', 'so', '<pause>', 'many', '<pause>', 'different', '<pause>', 'plants', '<pause>', 'around', '<pause>', 'the', '<pause>', 'room', '<pause>']

def get_before_util(i, lst):
    while i > 0:
        i -= 1
        if lst[i] is not None:
            return lst[i]
    return -1

def get_after_util(i, lst):
    after = -1
    for j in range(i, len(lst)):
        if lst[j] is not None:
            return lst[j]
    return after

def better_align(rec_tokens, gold_tokens):
    assert rec_tokens[0] == '<pause>'
    rec_no_pause = [x for x in rec_tokens if x != '<pause>']
    gold_no_pause = [x for x in gold_tokens if x != '<pause>']
    
    diff_alignment = list(difflib.Differ().compare(rec_no_pause, gold_no_pause))
    diff_alignment = [x for x in diff_alignment if x[0] != '?']

    # Collapse all '-' lines (insertion) into next token
    if diff_alignment[0][0] == '+':
        collapsed_alignment = [['OMISSION']]
    else:
        collapsed_alignment = [[diff_alignment[0]]]
    for line in diff_alignment[1:]:
        x = 'OMISSION' if line[0] == '+' else line
        if collapsed_alignment[-1][-1][0] == '-':
            collapsed_alignment[-1].append(x)
        else:
            collapsed_alignment.append([x])

    # for x in diff_alignment:
    #     print(x)
    # for x in collapsed_alignment:
    #     print(x)

    # Insert spaces where pauses *could* go
    generator = (x for x in collapsed_alignment)
    collapsed_alignment_full_length = []
    for x in generator:
        if any(y[0] != '-' for y in x):
            collapsed_alignment_full_length.append([])
        collapsed_alignment_full_length.append(x)

    if len(collapsed_alignment_full_length) < len(gold_tokens):
        assert len(collapsed_alignment_full_length) + 1 == len(gold_tokens)
        collapsed_alignment_full_length.append([])

    # for x in collapsed_alignment:
    #     print(x)
    
    # for d in diff_alignment:
    #     print(d)

    # for i in range(len(collapsed_alignment_full_length)):
    #     print(collapsed_alignment_full_length[i], gold_tokens[i])

    # The alignment should be the correct length (height) now
    # for i in range(len(gold_tokens)):
    #     print(gold_tokens[i], collapsed_alignment_full_length[i])
    # print(collapsed_alignment_full_length[-1])

    assert len(collapsed_alignment_full_length) == len(gold_tokens), str(len(collapsed_alignment_full_length)) + ' ' + str(len(gold_tokens))
    
    # Insert pauses in correct positions
    collapsed_alignment_positions = []
    for x in range(len(collapsed_alignment_full_length)):
        for y in range(len(collapsed_alignment_full_length[x])):
            if collapsed_alignment_full_length[x][y] != 'OMISSION':
                collapsed_alignment_positions.append((x, collapsed_alignment_full_length[x][y]))
    
    generator = (x for x in collapsed_alignment_positions)
    # for i in range(len(rec_no_pause)):
    #     print(rec_no_pause[i], collapsed_alignment_positions[i])
    # print(collapsed_alignment_positions[-1])

    assert len(collapsed_alignment_positions) == len(rec_no_pause), str(len(collapsed_alignment_positions)) + ' ' + str(len(rec_no_pause))

    collapsed_alignment_positions = [x[0] for x in collapsed_alignment_positions]

    rec_tokens_numbered = []
    for token in rec_tokens:
        if token == '<pause>':
            rec_tokens_numbered.append(None)
        else:
            rec_tokens_numbered.append(next(generator)[0])

    rec_tokens_numbered_complete = []
    for i in range(len(rec_tokens_numbered)):
        if rec_tokens_numbered[i] is None:
            # print(rec_tokens_numbered)
            before = get_before_util(i, rec_tokens_numbered)
            after = get_after_util(i, rec_tokens_numbered)
            # print(before, rec_tokens_numbered[i], after)
            if before == -1:
                rec_tokens_numbered_complete.append(0)
                
            elif after == -1:
                rec_tokens_numbered_complete.append(len(gold_tokens) - 1)
                # print(i)
            elif before == after:
                rec_tokens_numbered_complete.append(before)
            elif (after - before) % 2 == 0:
                # assert before != -1 and after != -1
                rec_tokens_numbered_complete.append((after + before) // 2)
                
            else:
                rec_tokens_numbered_complete.append(after)
                
            
        else:
            rec_tokens_numbered_complete.append(rec_tokens_numbered[i])

    # print(len(rec_tokens_numbered_complete))
    # print(len(gold_tokens), rec_tokens[-5:], gold_tokens[-5:])

    assert sorted(rec_tokens_numbered_complete) == rec_tokens_numbered_complete
    assert len(rec_tokens_numbered_complete) == len(rec_tokens)

    final_alignment = [[] for _ in gold_tokens]
    for position, token in zip(rec_tokens_numbered_complete, rec_tokens):
        final_alignment[position].append(token)
    
    assert len(gold_tokens) == len(final_alignment)

    # Sanity check that the processed tokens match the original, after the steps above
    assert len([y for x in final_alignment for y in x if y != '<pause>']) == len(rec_no_pause)

    # for x, y in zip(gold_tokens, final_alignment):
    #     print(x, y)

    return final_alignment
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

if __name__ == "__main__":
    final = better_align(child_tokens, gold)
    for x, y in zip(gold, final):
        print(x, y )