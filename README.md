# spaCy to JSON-NLP

(C) 2019 by [Damir Cavar], [Oren Baldinger], Maanvitha Gongalla, Anurag Kumar, Murali Kammili

Brought to you by the [NLP-Lab.org]!


This only works with spaCy 2.1.0!

I had the same issue. I downgraded Spacy from 2.1.4 to 2.1.0 and numpy to 1.14.5 to resolve.


## Introduction

Currently this module requires Python 3.6+.

This module provides a [spaCy] v2.1 wrapper for [JSON-NLP]. It takes the [spaCy] output and generates a [JSON-NLP] output. It also provides a Microservice wrapper that allows you to launch the [spaCy] module as a persistent RESTful service using [Flask] or other WSGI-based server.

Since this microservice is built on [spaCy], you will need to have its models download, for example:

    python -m spacy download en
    python -m spacy download en_core_web_md

## Additional Pipeline Modules

[spaCy] allows for the addition of additional models as pipeline modules. We provide such integrations for coreference and phrase structure trees.

### Anaphora and Coreference Resolution

We provide [HuggingFace] coreference resolution, a fast system tightly integrated into [spaCy]. Note that the first time the parser is run, it will download the coreference models if they are not already present. These models only work for English.

### Phrase Structure Trees (Constituency Parse)

We provide the CPU version of the [benepar] parser, a highly accurate phrase structure parser. Bear in mind it is a Tensorflow module, as such it has a notable start-up time, and relatively high memory requirements (4GB+).

If you have a GPU available, you can install the GPU version of the module with:

    pip install --upgrade benepar[gpu] 

## Microservice

The [JSON-NLP] repository provides a Microservice class, with a pre-built implementation of [Flask]. To run it, execute:
    
    python spacyjsonnlp/server.py
 
Since `server.py` extends the [Flask] app, a WSGI file would contain:

    from spacyjsonnlp.server import app as application
    
To disable a pipeline component (such as phrase structure parsing), add

    application.constituents = False
    
The full list of properties that can be disabled or enabled are
- constituents
- dependencies
- coreference
- expressions

The microservice exposes the following URIs:
- /constituents
- /dependencies
- /coreference
- /expressions
- /token_list

These URIs are shortcuts to disable the other components of the parse. In all cases, `tokenList` will be included in the `JSON-NLP` output. An example url is:

    http://localhost:5000/dependencies?text=I am a sentence

Text is provided to the microservice with the `text` parameter, via either `GET` or `POST`. If you pass `url` as a parameter, the microservice will scrape that url and process the text of the website.

The [spaCy] language model to use for parsing can be selected with the `spacy_model` parameter.

Here is an example `GET` call:

    http://localhost:5000?spacy_model=en&constituents=0&text=I am a sentence.

[Damir Cavar]: http://damir.cavar.me/ "Damir Cavar"
[Oren Baldinger]: https://oren.baldinger.me/ "Oren Baldinger"
[NLP-Lab.org]: http://nlp-lab.org/ "NLP-Lab.org"
[JSON-NLP]: https://github.com/dcavar/JSON-NLP "JSON-NLP"
[Flair]: https://github.com/zalandoresearch/flair "Flair"
[spaCy]: https://spacy.io/ "spaCy"
[NLTK]: http://nltk.org/ "Natural Language Processing Toolkit"
[Polyglot]: https://github.com/aboSamoor/polyglot "Polyglot"
[Xrenner]: https://github.com/amir-zeldes/xrenner "Xrenner"
[CONLL-U]: https://universaldependencies.org/format.html "CONLL-U"
[Flask]: http://flask.pocoo.org/ "Flask"
[HuggingFace]: https://github.com/huggingface/neuralcoref/ "Hugging Face"
[benepar]: https://github.com/nikitakit/self-attentive-parser "Berkeley Neural Parser"
