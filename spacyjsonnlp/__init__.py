#!/usr/bin/env python3

"""
(C) 2019 Damir Cavar, Oren Baldinger, Maanvitha Gongalla, Anurag Kumar, Murali Kammili, Boli Fang

Wrappers for spaCy to JSON-NLP output format.

Licensed under the Apache License 2.0, see the file LICENSE for more details.

Brought to you by the NLP-Lab.org (https://nlp-lab.org/)!
"""
import functools
import re
from collections import OrderedDict, defaultdict, Counter
from typing import Dict, Tuple

import neuralcoref
import spacy
from benepar.spacy_plugin import BeneparComponent
from pyjsonnlp import get_base, get_base_document, remove_empty_fields, build_constituents, find_head, build_coreference
from pyjsonnlp.pipeline import Pipeline
from pyjsonnlp.tokenization import segment
from spacy.language import Language
from spacy.tokens import Doc

from dependencies import DependencyAnnotator

name = "spacypyjsonnlp"
__version__ = '0.0.10'

# allowed model names
MODEL_NAMES = ('en_core_web_sm', 'en_core_web_md', 'en_core_web_lg' 'xx_ent_wiki_sm', 'de_core_news_sm', 'es_core_news_sm',
               'pt_core_news_sm', 'fr_core_news_sm', 'it_core_news_sm', 'nl_core_news_sm')
CONSTITUENTS = {'en': 'benepar_en2', 'de': 'benepar_de'}
COREF = {'en_core_web_sm', 'en_core_web_md', 'en_core_web_lg', 'xx_ent_wiki_sm'}
WORD_REGEX = re.compile(r'^[A-Za-z]+$')

__cache = defaultdict(dict)


def cache_it(func):
    """A decorator to cache function response based on params. Add it to top of function as @cache_it."""

    global __cache

    @functools.wraps(func)
    def cached(*args):
        f_name = func.__name__
        s = ''.join(map(str, args))
        if s not in __cache[f_name]:
            __cache[f_name][s] = func(*args)
        return __cache[f_name][s]
    return cached


@cache_it
def get_model(spacy_model: str, coref: bool, constituents: bool) -> Language:
    if spacy_model == 'en':
        spacy_model = 'en_core_web_sm'
    if spacy_model not in MODEL_NAMES:
        raise ModuleNotFoundError(f'No such spaCy model "{spacy_model}"')
    nlp = spacy.load(spacy_model)
    if coref and spacy_model in COREF:
        neuralcoref.add_to_pipe(nlp)
    if constituents:
        model = CONSTITUENTS.get(spacy_model[:2], "")
        if model:
            nlp.add_pipe(BeneparComponent(model))
    return nlp


class SyntokTokenizer(object):
    def __init__(self, vocab):
        self.vocab = vocab

    def __call__(self, text):
        words = []
        spaces = []
        for sent in segment(text):
            for token in sent:
                words.append(token.value)
                spaces.append(token.space_after)
        return Doc(self.vocab, words=words, spaces=spaces)


class SpacyPipeline(Pipeline):
    @staticmethod
    def process(text: str = '', spacy_model='en_core_web_sm', coreferences=False, constituents=False, dependencies=True, expressions=True) -> OrderedDict:
        """Process provided text"""
        nlp = get_model(spacy_model, coreferences, constituents)
        nlp.tokenizer = SyntokTokenizer(nlp.vocab)
        doc = nlp(text)
        j: OrderedDict = get_base()
        d: OrderedDict = get_base_document(1)
        j['documents'][d['id']] = d

        d['meta']['DC.source'] = 'SpaCy {}'.format(spacy.__version__)
        d['text'] = text

        model_lang = spacy_model[0:2]
        lang = Counter()  # track the frequency of each language
        sent_lookup: Dict[int, int] = {}  # map sentence end_char to our index
        token_lookup: Dict[Tuple[int, int], int] = {}  # map (sent_id, spacy token index) to our token index

        # tokens and sentences
        token_id = 1
        sent_num = 1
        for sent in doc.sents:
            current_sent = {
                'id': sent_num,
                'tokenFrom': token_id,
                'tokenTo': token_id + len(sent),  # begin inclusive, end exclusive
                'tokens': []
            }
            if constituents:
                try:
                    d['constituents'].append(build_constituents(sent_num, sent._.parse_string))
                except Exception:
                    pass

            sent_lookup[sent.end_char] = sent_num
            d['sentences'][current_sent['id']] = current_sent
            last_char_index = 0
            for token in sent:
                t = {
                    'id': token_id,
                    'text': token.text,
                    'lemma': token.lemma_,
                    'xpos': token.tag_,
                    'upos': token.pos_,
                    'entity_iob': token.ent_iob_,
                    'characterOffsetBegin': token.idx,
                    'characterOffsetEnd': token.idx + len(token),
                    'lang': token.lang_,
                    'features': {
                        'Overt': True,
                        'Stop': True if token.is_stop else False,
                        'Alpha': True if token.is_alpha else False,
                    },
                    'misc': {
                        'SpaceAfter': False
                    }
                }

                # shape
                if WORD_REGEX.findall(token.text):
                    t['shape'] = token.shape_

                # space after?
                if token.idx != 0 and token.idx != last_char_index:
                    # we don't know there was a space after the previous token until we see where this one
                    # starts in relation to where the last one finished
                    d['tokenList'][token_id-1]['misc']['SpaceAfter'] = True
                last_char_index = t['characterOffsetEnd']

                # morphology
                for i, kv in enumerate(nlp.vocab.morphology.tag_map.get(token.tag_, {}).items()):
                    if i > 0:  # numeric k/v pair at the beginning
                        t['features'][kv[0]] = str(kv[1]).title()

                # entities
                if token.ent_type_:
                    t['entity'] = token.ent_type_

                # maybe check if a non-model language
                if model_lang != 'xx':
                    t['features']['Foreign'] = False if model_lang == token.lang_ else True

                # bookkeeping
                lang[token.lang_] += 1
                token_lookup[(sent_num, token.i)] = token_id
                current_sent['tokens'].append(token_id)
                d['tokenList'][token_id] = t
                token_id += 1

            d['tokenList'][token_id-1]['misc']['SpaceAfter'] = True  # EOS tokens have spaces after them
            sent_num += 1

        d['tokenList'][token_id-1]['misc']['SpaceAfter'] = False  # EOD tokens do not

        # noun phrases
        if expressions:
            chunk_id = 1
            for chunk in doc.noun_chunks:
                if len(chunk) > 1:
                    sent_id = sent_lookup[chunk.sent.sent.end_char]
                    d['expressions'].append({
                        'id': chunk_id,
                        'type': 'NP',
                        'head': token_lookup[(sent_id, chunk.root.i)],
                        'dependency': chunk.root.dep_.lower(),
                        'tokens': [token_lookup[(sent_id, token.i)] for token in chunk]
                    })
                    chunk_id += 1

        # dependencies
        if dependencies:
            deps = {
                'style': 'universal',
                'arcs': {}
            }
            d['dependencies'].append(deps)
            for sent_num, sent in enumerate(doc.sents):
                for token in sent:
                    dependent = token_lookup[(sent_num+1, token.i)]
                    deps['arcs'][dependent] = [{
                        'sentenceId': sent_num+1,
                        'label': token.dep_ if token.dep_ != 'ROOT' else 'root',
                        'governor': token_lookup[(sent_num+1, token.head.i)] if token.dep_ != 'ROOT' else 0,
                        'dependent': dependent
                    }]

            # clause, grammar extractions
            clause_annotator = DependencyAnnotator()
            clause_annotator.annotate(j)

        # coref
        # noinspection PyProtectedMember
        if coreferences and doc._.coref_clusters is not None:
            # noinspection PyProtectedMember
            for cluster in doc._.coref_clusters:
                r = build_coreference(cluster.i)
                r['representative']['tokens'] = [t.i+1 for t in cluster.main]
                r['representative']['head'] = find_head(d, r['representative']['tokens'], 'universal')
                for m in cluster.mentions:
                    if m[0].i+1 in r['representative']['tokens']:
                        continue  # don't include the representative in the mention list
                    ref = {'tokens': [t.i+1 for t in m]}
                    ref['head'] = find_head(d, ref['tokens'], 'universal')
                    r['referents'].append(ref)
                d['coreferences'].append(r)

        d['meta']['DC.language'] = max(lang)

        return remove_empty_fields(j)


if __name__ == "__main__":
    test_text = "The Mueller Report is a very long report. We spent a long time analyzing it. Trump wishes we didn't, but that didn't stop the intrepid NlpLab."
    print(SpacyPipeline.process(test_text, spacy_model='en_core_web_sm', coreferences=True, constituents=False))
