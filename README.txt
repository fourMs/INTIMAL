== Required Packages ==

=== NLTK ===

Required components:

 * nltk (the package itself)
 * omw (Open Multilingual WordNet)
 * stopwords

Installing the software and data:

{{{
git clone https://github.com/nltk/nltk.git
cd nltk
python setup.py build
python setup.py install --user
cd ..
python -c 'import nltk; nltk.download("wordnet")'
python -c 'import nltk; nltk.download("omw")'
python -c 'import nltk; nltk.download("stopwords")'
}}}
