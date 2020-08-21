#!/usr/bin/env python3

# LTS_util

import json

class LTS_util:
    def __init__(self,
        path='../data/moby-passages-36/from-susan/lts-20200703.json'):

        with open(path) as f:
            self.store = json.load(f)
        
        self.default_return = {'sight_word': [],
            'is_compound': 0,
            'lts': [],
            'decodable': 0,
            'grade_level_if_decodable': 0,
            'n_morphs': 0}
    
    def get(self, word):
        if word in self.store:
            return self.store[word]
        return self.default_return