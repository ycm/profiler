# Text matrix methodology

*Andrew Yang for AMI*

*Created June 23, 2020*

## Misc

Punctuation: `[',', '.', '"', '-', '?', !', "'",]`

## Featurization

### Tokenize passage

- Using `spacy` package in Python to divide a passage into sentences and sentences into words.

- After tokenizing the sentences, we convert them to basic strings and add a `_START_` token to the beginning of each sentence. Commas, exclamation points, and question marks are replaced with `_._`. This is done to work with the Google ngram viewer

### FEATURE: Google ngram frequency

- Using Google Books Ngram Viewer to retrieve ngram frequencies.
- A feature titled `ngram_x_y` means a `x+y+1`-gram with no more than `x` tokens before and `y` after. 
- Ex. `_START_ Sam and Jo went for a hike.`
  - `ngram_1_1` of `and` is `Sam and Jo`
  - `ngram_2_0` of `Sam` is `_START_ Sam`.
  - `ngram_0_2` of `.` is `.`.

- Using corpus 15 (English) with books from 1940 to 2000. Results are averaged across these years.
- A frequency of 0 is reported for ngrams that do not appear in search results.
- Frequencies are reported in [number per million].
- Currently implemented: `ngram_1_1`, `ngram_1_0`, `ngram_2_0`.

### FEATURE: Word length

- Number of letters in a word.
- For the time being, numerals are treated like words, so `42` has length 2.
- `_START_` token and punctuation have length 0.

### FEATURE: CMU pronunciation length

- Using `cmudict-0.7b`.
- For words with multiple pronunciations, take the first that appears.
- Count number of segments in the CMU pronunciation:
  - `PRONOUNCE  P R AH0 N AW1 N S` has length 7.

- `_START_` token and punctuation have length 0.

```python
from CMUSounds import CMUSounds
cmu = CMUSounds()
cmu_lengths = [] 
for token in tokens:
	pron = cmu.get(token) 
	if not pron: 
		cmu_lengths.append(0) 
	else: 
		cmu_lengths.append(pron.count(' ') + 1)
# df['cmu_len'] = cmu_lengths
```

### FEATURE: Dolch sight words

- Using standard Dolch pre-primer to third grade sight words and standard Dolch nouns.
- Words are separated into grade level (pre-primer through third grade)
- For the time being, standard Dolch nouns are all pre-primer.
  - The nouns `Santa Claus` and `good-bye` are rendered as `Santa`, `Claus`, `goodbye`, and `bye`. We exclusive `good` because it is already a primer-level sight word.
- `_START_` token and punctuation count are considered pre-primer sight words.
- Features are **cumulative**: a feature titled `dolch_first_grade` covers everything from pre-primer to first grade. 
- A token is `1` if it is a Dolch sight word at or below the appropriate level and `0` otherwise.

```python
import json
with open('data/general-resources/dolch-sight-words.json') as f:
	dolch = json.load(f)
  
def is_sight_word(tokens, levels): 
	sight_words = set(word for level in levels for word in dolch[level]) 
	return [1 if token in {'.', '!', '?', ':', ',', '_START_'} or token in sight_words else 0 for token in tokens] 

f_pre_primer = is_sight_word(tokens, ['pre-primer'])
f_primer = is_sight_word(tokens, ['pre-primer', 'primer'])
f_first_grade = is_sight_word(tokens, ['pre-primer', 'primer', 'first-grade'])
f_second_grade = is_sight_word(tokens, ['pre-primer', 'primer', 'first-grade', 'second-grade'])
f_third_grade = is_sight_word(tokens, ['pre-primer', 'primer', 'first-grade', 'second-grade', 'third-grade'])

df['dolch_0a'] = f_pre_primer
df['dolch_0b'] = f_primer
df['dolch_1'] = f_first_grade
df['dolch_2'] = f_second_grade
df['dolch_3'] = f_third_grade
```

### FEATURE: $k$-th occurrence

- A Moby.Read item consists of title, introduction, and passage.
- Every token in the passage is assigned an integer corresponding to if it is the first, second, third, etc. time that it is appearing **in the entire item**.
  - Ex. If the word `introduction` appears in the title or introduction, we expect the child to have an easier time with this word, considering they have just heard a model prononciation.
- Some words may be underlined in the introduction. For the time being the underlining is ignored.

Dictionaries: (type, item) $\to$ title/intro strings

```
data/moby-passages-36/passage-title-dict.pkl
data/moby-passages-36/passage-intro-dict.pkl
```

Complete JSON: `data/moby-passages-36/processed_items.json`

- A feature named `occ_7` is 1 if the token **has occurred at least 7 times before**.
- Case insensitive
- Features go from `occ_0` to `occ_9`.
- `_START_` token and punctuation are assigned the value 0 everywhere.

