# NgramFetcher.py
# fetches ngram frequencies from Google Books.

# Google Ngram parser from https://github.com/Prooffreader/google_ngrams_py
# slightly modified to work with Python 3

# coding: utf-8

import pandas as pd
import urllib.request
import json
import google_ngram

class Gngram(object):
    """Searches Google Ngram Viewer for search terms and creates pandas dataframes of results
    
    Arguments: ngrams must be list
               years is list of length 2, endpoints (inclusive)\
               corpus: 15 is English
               If case_insensitive = True, will return df_parents and df_expansion;
                   otherwise just df_parents
    
    Dataframe objects:
             df_parents: a dataframe with years as Index and search terms as columns and
                         words per million words as value
             df_expansion: similar, but with df_parent columns expanded in different cases
                           where applicable (e.g. the, The, THE)
                           
    Dict objects (not necessarily useful, but included for the sake of thoroughness):
             ngram_type: dict of column name : Goolge ngram defined type, 
                         e.g. {"the (All): NGRAM", "the": "expansion" ... }
             parent_expansion: dict of parent column name : list of expansion column names
                               e.g. {"the (All)": ["The", "the", "THE"]}
             expansion_parent: dict of expansion column name: parent column name
                               e.g. {'the': 'the (All)', 'The', 'the (All)', ...}
                               
    Other:
             html: the raw html returned from Google Ngrams Viewer
             json: the json object of results extracted from the raw html (it's inline in the html)
             url: the Google Ngrams Viewer url that returned the results."""
             
    def __init__(self, ngrams = ['example', 'list'], years=[1800, 2008], corpus=15, smoothing=0, case_insensitive=False):
        self.url = "https://books.google.com/ngrams/graph?content="
        for i in range(len(ngrams)):
            ngrams[i] = ngrams[i].replace("'", "%27")
            ngrams[i] = ngrams[i].replace(" ", "+")
            if i > 0:
                self.url += '%2C+'
            self.url += ngrams[i] 
        if case_insensitive == True:
            self.url += "&case_insensitive=on"
        self.url += '&year_start='
        self.url += str(years[0])
        self.url += '&year_end='
        self.url += str(years[1])
        self.url += '&corpus='
        self.url += str(corpus)
        self.url += '&smoothing=0'
        self.html = urllib.request.urlopen(self.url)
        self.json = ""
        for line in self.html:
            ln = str(line)
            if "var data" in ln:
                self.json = ln
                break
        self.json = self.json.replace("b'", '')
        self.json = self.json.replace('var data =', '')
        self.json = self.json.strip()[:-4]
        self.json = eval(self.json)
        
        self.df_parents = pd.DataFrame()
        self.df_expansions = pd.DataFrame()
        self.parent_expansion = {} # dict of lists
        self.expansion_parent = {} # reverse of above, just dict
        self.ngram_type = {} # pairs column names and types
        for i in range(len(self.json)):
            ngram = self.json[i]['ngram']
            parent = self.json[i]['parent']
            timeseries = self.json[i]['timeseries']
            for pos in range(len(timeseries)):
                timeseries[pos] *= 1000000 # change from proportion to words per million words
            self.ngram_type[ngram] = self.json[i]['type']
            df_temp = pd.DataFrame({ngram: timeseries}, index=range(years[0], years[1]+1))
            if parent == '':
                if len(self.df_parents) == 0:
                    self.df_parents = df_temp.copy()
                else:
                    self.df_parents = pd.concat([self.df_parents, df_temp], axis=1)
            else:
                if len(self.df_expansions) == 0:
                    self.df_expansions = df_temp.copy()
                else:
                    self.df_expansions = pd.concat([self.df_expansions, df_temp], axis=1)
                if parent not in self.parent_expansion.keys():
                    self.parent_expansion[parent] = [ngram]
                else:
                    self.parent_expansion[parent].append(ngram)
                self.expansion_parent[ngram] = parent

class NgramFetcher:
    def __init__(self, jsonpath, years=[1940, 2000], case_insensitive=True):
        self.path = jsonpath
        try:
            with open(self.path) as f:
                self.store = json.load(f)
                self.years = self.store['__years']
                self.case_insensitive = self.store['__case_insensitive']
            print('Finished loading', jsonpath)
        except:
            print('Failed to open path', jsonpath)
            print('Creating new json instead.')
            self.years = years
            self.case_insensitive = case_insensitive
            self.store = {
                '__years': years,
                '__case_insensitive': case_insensitive}
    def fetch(self, words): # words <- str (e.g. 'children played with')
        # returns mean and whether or not the result had to be scraped
        words_key = '*'.join([w.strip() for w in words.split()]) # _START_ the children jumped -> _START_*the*children
        
        if words_key in self.store and self.store[words_key] != 0:
            return self.store[words_key], False
        if words == '_START_' or words == '.':
            return 0, False
        try:
            print('trying:', words)
            g = google_ngram.Gngram([words], years=self.years, case_insensitive=self.case_insensitive)
            mean = float(g.df_parents.mean())
        except urllib.request.HTTPError:
            print('Ngram not found for:', words)
            mean = 0
        self.store[words_key] = mean
        return mean, True
    
    def save(self, fp=None):
        path = fp if fp else self.path
        with open(path, 'w') as f:
            json.dump(self.store, f)
            print('File saved to', path)