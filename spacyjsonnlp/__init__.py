#!/usr/bin/env python3

"""
(C) 2019 Damir Cavar, Oren Baldinger, Maanvitha Gongalla, Anurag Kumar, Murali Kammili, Boli Fang

Wrappers for spaCy to JSON-NLP output format.

Licensed under the Apache License 2.0, see the file LICENSE for more details.

Brought to you by the NLP-Lab.org (https://nlp-lab.org/)!
"""
import functools
import re
from typing import Callable, Dict, Tuple

import spacy
from collections import OrderedDict, defaultdict, Counter

from benepar.spacy_plugin import BeneparComponent
from pyjsonnlp import get_base, get_base_document, remove_empty_fields, build_constituents, find_head, build_coreference
from pyjsonnlp.pipeline import Pipeline

name = "spacypyjsonnlp"

__version__ = "0.0.2"

# allowed model names
MODEL_NAMES = ('en', 'en_core_web_md', 'xx_ent_wiki_sm', 'de_core_news_sm', 'es_core_news_sm',
               'pt_core_news_sm', 'fr_core_news_sm', 'it_core_news_sm', 'nl_core_news_sm')
CONSTITUENTS = {'en': 'benepar_en2', 'en_core_web_md': 'benepar_en2', 'de_core_news_sm': 'benepar_de'}
COREF = {'en': 'en_coref_md', 'en_core_web_md': 'en_coref_md'}
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
def get_model(spacy_model: str, coref: bool, constituents: bool) -> Callable:
    if spacy_model not in MODEL_NAMES:
        raise ModuleNotFoundError(f'No such spaCy model "{spacy_model}"')
    if coref and spacy_model in COREF:
        nlp = spacy.load(COREF[spacy_model])
    else:
        nlp = spacy.load(spacy_model)
    if constituents and spacy_model in CONSTITUENTS:
        nlp.add_pipe(BeneparComponent(CONSTITUENTS[spacy_model]))
    return nlp


class SpacyPipeline(Pipeline):
    @staticmethod
    def process(text: str = '', spacy_model='en', coreferences=False, constituents=False, dependencies=True, expressions=True) -> OrderedDict:
        """Process provided text"""
        doc = get_model(spacy_model, coreferences, constituents)(text)
        j: OrderedDict = get_base()
        d: OrderedDict = get_base_document('1')
        j['documents'][d['id']] = d

        d['meta']['DC.source'] = 'SpaCy {}'.format(spacy.__version__)
        d['text'] = text

        model_lang = spacy_model[0:2]
        lang = Counter()  # track the frequency of each language
        sent_lookup: Dict[int, int] = {}  # map sentence end_char to our index
        token_lookup: Dict[Tuple[int, int], int] = {}  # map (sent_id, spacy token index) to our token index

        # tokens and sentences
        token_id = 1
        for sent_num, sent in enumerate(doc.sents):
            current_sent = {
                'id': str(sent_num),
                'tokenFrom': token_id,
                'tokenTo': token_id + len(sent),  # begin inclusive, end exclusive
                'tokens': []
            }
            if constituents:
                # noinspection PyProtectedMember
                d['constituents'].append(build_constituents(sent_num, sent._.parse_string))

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
                        'Overt': 'Yes',
                        'Stop': 'Yes' if token.is_stop else 'No',
                        'Alpha': 'Yes' if token.is_alpha else 'No',
                    },
                    'misc': {
                        'SpaceAfter': 'No'
                    }
                }

                # shape
                if WORD_REGEX.findall(token.text):
                    t['shape'] = token.shape_

                # space after?
                if token.idx != 0 and token.idx != last_char_index:
                    # we don't know there was a space after the previous token until we see where this one
                    # starts in relation to where the last one finished
                    d['tokenList'][token_id-1]['misc']['SpaceAfter'] = 'Yes'
                last_char_index = t['characterOffsetEnd']

                # morphology
                try:
                    # noinspection PyUnresolvedReferences
                    for i, kv in enumerate(nlp.vocab.morphology.tag_map.get(token.tag_, {}).items()):
                        if i > 0:  # numeric k/v pair at the beginning
                            t['features'][kv[0]] = kv[1].title()
                except:
                    pass

                # entities
                if token.ent_type_:
                    t['entity'] = token.ent_type_

                # maybe check if a non-model language
                if model_lang != 'xx':
                    t['features']['Foreign'] = 'No' if model_lang == token.lang_ else 'Yes'

                # bookkeeping
                lang[token.lang_] += 1
                token_lookup[(sent_num, token.i)] = token_id
                current_sent['tokens'].append(token_id)
                d['tokenList'][token_id] = t
                token_id += 1

            d['tokenList'][token_id-1]['misc']['SpaceAfter'] = 'Yes'  # EOS tokens have spaces after them
        d['tokenList'][token_id-1]['misc']['SpaceAfter'] = 'No'  # EOD tokens do not

        # noun phrases
        if expressions:
            for chunk in doc.noun_chunks:
                # note that this includes NPs containing a single noun
                sent_id = sent_lookup[chunk.sent.sent.end_char]
                e = {
                    'type': 'NP',
                    'head': token_lookup[(sent_id, chunk.root.i)],
                    'dependency': chunk.root.dep_,
                    'tokens': [token_lookup[(sent_id, token.i)] for token in chunk]
                }
                for token in chunk.rights:
                    e['tokens'].append(token_lookup[(sent_id, token.i)])
                # ignore noun phrases consisting of one token
                if len(e['tokens']) == 1:
                    continue
                d['expressions'].append(e)

        # dependencies
        if dependencies:
            deps = {
                'style': 'universal',
                'arcs': {}
            }
            d['dependencies'].append(deps)
            for sent_num, sent in enumerate(doc.sents):
                for token in sent:
                    dependent = token_lookup[(sent_num, token.i)]
                    deps['arcs'][dependent] = [{
                        'sentenceId': str(sent_num),
                        'label': token.dep_ if token.dep_ != 'ROOT' else 'root',
                        'governor': token_lookup[(sent_num, token.head.i)] if token.dep_ != 'ROOT' else 0,
                        'dependent': dependent
                    }]

        # coref
        # noinspection PyProtectedMember
        if coreferences and doc._.coref_clusters is not None:
            # noinspection PyProtectedMember
            for cluster in doc._.coref_clusters:
                r = build_coreference(cluster.i)
                r['representative']['tokens'] = [t.i+1 for t in cluster.main]
                r['representative']['head'] = find_head(d, r['representative']['tokens'], 'universal')
                for m in cluster.mentions:
                    if m[0].i in r['representative']['tokens']:
                        continue  # don't include the representative in the mention list
                    ref = {'tokens': [t.i+1 for t in m]}
                    ref['head'] = find_head(d, ref['tokens'], 'universal')
                    r['referents'].append(ref)
                d['coreferences'].append(r)

        d['meta']['DC.language'] = max(lang)

        return remove_empty_fields(j)
