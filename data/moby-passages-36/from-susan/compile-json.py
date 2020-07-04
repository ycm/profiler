#!/usr/bin/env python

import sys, json

def compile_json(input_tsv_name, output_json_name):
    out = {}
    with open(input_tsv_name) as f:
        next(f)
        for line in f:
            #print(line.strip())
            word, sight_word, compound, lts, morphs, svocab_lts, d_nd = line.strip().split('\t')
            word = word[1:-1] if word[0] == word[-1] == '"' else word
            sight_word = sight_word[1:-1] if sight_word and sight_word[0] == sight_word[-1] == '"' else sight_word
            #compound = compound[1:-1] if compound[0] == compound[-1] == '"' else compound
            lts = lts[1:-1] if lts and lts[0] == lts[-1] == '"' else lts
            morphs = int(morphs[1:-1]) if morphs[0] == morphs[-1] == '"' else int(morphs)
            svocab_lts = svocab_lts[1:-1] if svocab_lts and svocab_lts[0] == svocab_lts[-1] == '"' else svocab_lts
            d_nd = d_nd[1:-1] if d_nd[0] == d_nd[-1] == '"' else d_nd
            
            if ',' in sight_word:
                sight_word = ''
            sight_word = set(x.strip() for x in sight_word.split(',') if x.strip()) & {'-1', '0', '1'}
            sight_word = sorted(list(set(int(x) for x in sight_word)))
            
            compound = 1 if compound.strip() else 0
            
            lts = set(int(x.strip()) for x in lts.replace('ND', '').replace('D', '').replace('S', '').split(',') if x.strip())
            svocab_lts = set(int(x.strip()) for x in svocab_lts.replace('?', '').replace('ND', '').replace('D', '').split(',') if x.strip())
            all_lts = lts | svocab_lts
            
            decodable = 1 if d_nd == 'D' else 0

            grade_level_if_decodable = -1
            if decodable:
                # print(word, all_lts)
                if all_lts & {1, 2}:
                    grade_level_if_decodable = 1
                if all_lts & {3, 4, 8, 9}:
                    grade_level_if_decodable = 2
                if all_lts & {5, 6, 7, 11}:
                    grade_level_if_decodable = 3
                if all_lts & {10, 12}:
                    grade_level_if_decodable = 4
            all_lts = sorted(list(all_lts))
            
            d = {
                'sight_word': sight_word,
                'is_compound': compound,
                'lts': all_lts,
                'decodable': decodable,
                'grade_level_if_decodable': grade_level_if_decodable,
                'n_morphs': morphs
            }
            out[word] = d
    
    with open(output_json_name, 'w') as f:
        json.dump(out, f)

def main():
    if len(sys.argv) < 3:
        print('usage: {} <input tsv> <output json filename>')
    else:
        compile_json(sys.argv[1], sys.argv[2])

if __name__ == '__main__':
    main()
