# class for retrieving cmu sounds

class CMUSounds:
    def __init__(self, path='data/general-resources/cmudict-0.7b.txt'):
        self.store = {}
        with open(path, encoding='latin-1') as f:
            for line in f:
                if line[0] == ';' or ('(' in line and ')' in line): # skip words with multiple pronounciations
                    continue
                word, sounds = line.split('  ')
                self.store[word] = sounds.strip()
    def get(self, word):
        w = word.upper()
        return self.store[w] if w in self.store else ''
