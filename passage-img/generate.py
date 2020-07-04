#!/usr/bin/env python

'''
$: line break
*: paragraph break
'''

import os, sys, string, re, json

grade_1 = [1401, 1603, 1903, 1505, 1804, 1807, 1502, 1703, 2001]
grade_2 = [350, 2203, 2401, 330, 2201, 2202, 310, 2102, 2302]
grade_3 = [420, 2403, 2701, 320, 450, 2503, 410, 2101, 2504]
grade_4 = [520, 2402, 2904, 2601, 2801, 3105, 2803, 2902, 3106]
item_to_grade = {}
for idx, grade in enumerate([grade_1, grade_2, grade_3, grade_4]):
    for item in grade:
        item_to_grade[str(item)] = idx + 1

with open('../data/moby-passages-36/passages-with-line-breaks.tsv') as f:
    item_to_passage = {}
    for line in f:
        item_number, passage = line.strip().split('\t')
        passage = passage[:passage.index('#')].replace('$$', ' * ').replace('$', ' $ ')
        item_to_passage[item_number] = passage

with open('../data/moby-passages-36/from-susan/lts-20200703.json') as f:
    LTS = json.load(f)

with open('../data/moby-passages-36/item_to_complete_passage.json') as f:
    item_to_complete_passage = json.load(f)

for item_number, passage in item_to_passage.items():
    words = [x for x in passage.split(' ') if x]
    
    folder = 'passage_' + item_number
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    f = open(os.path.join(folder, 'passage_' + item_number + '.tex'), 'w')
    
    passage_title = item_to_complete_passage[item_number][0]

    print('''\\documentclass{article}[12pt]
\\usepackage{geometry}
\\usepackage{xcolor}
\\usepackage{times}
\\usepackage{ulem}
\\definecolor{darkgreen}{rgb}{.1,.6,.1}
\\usepackage{helvet}
\\setlength\\parindent{0pt}
\\renewcommand{\\familydefault}{\\sfdefault}
\\renewcommand{\\baselinestretch}{1.7}
\\renewcommand{\\ULthickness}{1pt}
\\def\colorul#1#2{\\color{#1}\\uline{{\\color{black}#2}}\\color{black}}
\\begin{document}
''', file=f)
    
    # print(item_to_grade)
    
    print('\\textbf{' + passage_title +'. Grade ' + str(item_to_grade[item_number])+ '.}\n\n{\\colorul{darkgreen}{Not sight word}, \\colorul{red}{Not decodable}, \\colorul{blue}{Not decodable at grade level}\\\\\n\n', file=f)
        
    for word in words:
        # print(word)
        
        if word == '$':
            print('\\\\', file=f)
            continue
        
        if word == '*':
            # print('', file=f)
            print('\\\\', file=f)
            # print('', file=f)
            continue
        
        w = word.lower().replace(',', '').replace('.', '').replace('"', '').replace('!', '').replace('?', '')
        
        if w[0] == w[-1] == '\'':
            w = w[1:-1]
        
        if w.isdigit() or LTS[w]['sight_word'] == [-1]:
            NotSightWord = NotDecodable = NotDecodableAtGradeLevel = False
        else:
            NotSightWord = not LTS[w]['sight_word']
            NotDecodable = not LTS[w]['decodable']
            NotDecodableAtGradeLevel = False
            if not NotDecodable and LTS[w]['grade_level_if_decodable'] > item_to_grade[item_number]:
                NotDecodableAtGradeLevel = True
       
        output_word = word
        if NotSightWord:
            output_word = '\colorul{darkgreen}{' + output_word + '}' 
        if NotDecodable:
            output_word = '\colorul{red}{' + output_word + '}'
        if NotDecodableAtGradeLevel:
            output_word = '\colorul{blue}{' + output_word + '}'
        print(output_word, end='\,\,\,', file=f)
        
    print('\n\\end{document}', file=f)
    
    f.close()
    # break
