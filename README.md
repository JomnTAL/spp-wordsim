Software accompanying this paper from the RepEval 2017 EMNLP Workshop 

# Requirements #

Every python script requires python 3 with the following packages (that can be installed using pip):
* Numpy
* Scipy
* PrettyTable

You may need to make some small changes to the bash scripts if they don't use the correct python version by changing the python command used in the scripts.

# Downloading the SPP datasets #

The SPP datasets need to be fetched from the <http://spp.montana.edu/> website.
The 8 datasets are under the menus:
* Search... -> Lexical Decision Data... -> By item
* Search... -> Naming Data... -> By item

In both of these menus, download the datasets by going to the tabs "Assoc Related (1661)", "Assoc Unrel (1661)", "Other Assoc Related (1661)" and "Other Assoc Unrel (1661)".

Place these files into the 'data/raw/ldt' folder for the 4 lexical decision datasets and 'data/raw/nt' for the 4 naming datasets.

Full description of the datasets can be found in [this paper](http://www.montana.edu/khutchison/documents/spp.pdf).

# Building the dataset #

Once the raw datasets have been downloaded, you can use the 'build_dataset.sh' script.
It will automatically extract all the needed information from the raw datasets and it will also build the two splits.
The first one is a dev-test split. The second one is a train-dev-test split.
You can find the folds used to make these splits in 'data/folds'.

# Scripts #

Here are the different scripts that are used in the paper:
* wordsim.py (spearman's correlations shown in the first experiment)
* corrmatrix.py (needed to do the steiger test)
* corrstats.py (does the steiger test)
* datasets_correlations.py (spearman's correlations shown in second experiment)

You can use the --help flag to get the usage of these commands.

Additional useful scripts available in data/tools/:
* extract\_embedding\_wordset.py (returns only the words that appear in all the given word embedding models)

# Word embeddings #

Here are the links to the off-the-shelf word embeddings used in the paper:
* [GloVe](http://nlp.stanford.edu/data/glove.twitter.27B.zip)
  + Dimension: 200
  + Window: 10
  + Corpus: Twitter
* [SkipGram](https://drive.google.com/file/d/0B7XkCwpI5KDYNlNUTTlSS21pQmM/edit?usp=sharing)
  + Dimension: 300
  + Window: 5
  + Corpus: Google News
* [Multilingual](http://www.wordvectors.org/web-eacl14-vectors/de-projected-en-512.txt.gz)
  + Dimension: 512
  + Window: ?
  + Corpus: WMT-2011 (English, Spanish, German, French), WMT-2012 (French)
* [Dependency-based](http://u.cs.biu.ac.il/~yogo/data/syntemb/deps.words.bz2)
  + Dimension: 300
  + Window: Dynamic
  + Corpus: Wikipedia
* [FastText](https://s3-us-west-1.amazonaws.com/fasttext-vectors/wiki.en.vec)
  + Dimension: 300
  + Window: 5
  + Corpus Wikipedia
