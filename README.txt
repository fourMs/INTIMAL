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

=== spaCy ===

Required components:

 * spaCy (the package itself)
 * es (Spanish data model)

Installing the software and data:

{{{
python -m pip install -U --user spacy
python -m spacy download es --user
}}}
