from collections import OrderedDict
from unittest import TestCase

from spacyjsonnlp.dependencies import DependencyAnnotator

j = OrderedDict({
  "meta": {
    "DC.conformsTo": "0.2.9",
    "DC.created": "2019-04-25T20:31:28",
    "DC.date": "2019-04-25T20:31:28"
  },
  "documents": {
    1: {
      "meta": {
        "DC.conformsTo": "0.2.9",
        "DC.source": "SpaCy 2.1.3",
        "DC.created": "2019-04-25T20:31:28",
        "DC.date": "2019-04-25T20:31:28",
        "DC.language": "en"
      },
      "id": 1,
      "text": "I want to buy a big red car.",
      "tokenList": OrderedDict({
        1: {
          "id": 1,
          "text": "I",
          "lemma": "-PRON-",
          "xpos": "PRP",
          "upos": "PRON",
          "entity_iob": "O",
          "characterOffsetBegin": 0,
          "characterOffsetEnd": 1,
          "lang": "en",
          "features": {
            "Overt": "Yes",
            "Stop": "Yes",
            "Alpha": "Yes",
            "PronType": "Prs",
            "Foreign": "No"
          },
          "misc": {
            "SpaceAfter": "Yes"
          },
          "shape": "X"
        },
        2: {
          "id": 2,
          "text": "want",
          "lemma": "want",
          "xpos": "VBP",
          "upos": "VERB",
          "entity_iob": "O",
          "characterOffsetBegin": 2,
          "characterOffsetEnd": 6,
          "lang": "en",
          "features": {
            "Overt": "Yes",
            "Stop": "No",
            "Alpha": "Yes",
            "VerbForm": "Fin",
            "Tense": "Pres",
            "Foreign": "No"
          },
          "misc": {
            "SpaceAfter": "Yes"
          },
          "shape": "xxxx"
        },
        3: {
          "id": 3,
          "text": "to",
          "lemma": "to",
          "xpos": "TO",
          "upos": "PART",
          "entity_iob": "O",
          "characterOffsetBegin": 7,
          "characterOffsetEnd": 9,
          "lang": "en",
          "features": {
            "Overt": "Yes",
            "Stop": "Yes",
            "Alpha": "Yes",
            "PartType": "Inf",
            "VerbForm": "Inf",
            "Foreign": "No"
          },
          "misc": {
            "SpaceAfter": "Yes"
          },
          "shape": "xx"
        },
        4: {
          "id": 4,
          "text": "buy",
          "lemma": "buy",
          "xpos": "VB",
          "upos": "VERB",
          "entity_iob": "O",
          "characterOffsetBegin": 10,
          "characterOffsetEnd": 13,
          "lang": "en",
          "features": {
            "Overt": "Yes",
            "Stop": "No",
            "Alpha": "Yes",
            "VerbForm": "Inf",
            "Foreign": "No"
          },
          "misc": {
            "SpaceAfter": "Yes"
          },
          "shape": "xxx"
        },
        5: {
          "id": 5,
          "text": "a",
          "lemma": "a",
          "xpos": "DT",
          "upos": "DET",
          "entity_iob": "O",
          "characterOffsetBegin": 14,
          "characterOffsetEnd": 15,
          "lang": "en",
          "features": {
            "Overt": "Yes",
            "Stop": "Yes",
            "Alpha": "Yes",
            "Foreign": "No"
          },
          "misc": {
            "SpaceAfter": "Yes"
          },
          "shape": "x"
        },
        6: {
          "id": 6,
          "text": "big",
          "lemma": "big",
          "xpos": "JJ",
          "upos": "ADJ",
          "entity_iob": "O",
          "characterOffsetBegin": 16,
          "characterOffsetEnd": 19,
          "lang": "en",
          "features": {
            "Overt": "Yes",
            "Stop": "No",
            "Alpha": "Yes",
            "Degree": "Pos",
            "Foreign": "No"
          },
          "misc": {
            "SpaceAfter": "Yes"
          },
          "shape": "xxx"
        },
        7: {
          "id": 7,
          "text": "red",
          "lemma": "red",
          "xpos": "JJ",
          "upos": "ADJ",
          "entity_iob": "O",
          "characterOffsetBegin": 20,
          "characterOffsetEnd": 23,
          "lang": "en",
          "features": {
            "Overt": "Yes",
            "Stop": "No",
            "Alpha": "Yes",
            "Degree": "Pos",
            "Foreign": "No"
          },
          "misc": {
            "SpaceAfter": "Yes"
          },
          "shape": "xxx"
        },
        8: {
          "id": 8,
          "text": "car",
          "lemma": "car",
          "xpos": "NN",
          "upos": "NOUN",
          "entity_iob": "O",
          "characterOffsetBegin": 24,
          "characterOffsetEnd": 27,
          "lang": "en",
          "features": {
            "Overt": "Yes",
            "Stop": "No",
            "Alpha": "Yes",
            "Number": "Sing",
            "Foreign": "No"
          },
          "misc": {
            "SpaceAfter": "No"
          },
          "shape": "xxx"
        },
        9: {
          "id": 9,
          "text": ".",
          "lemma": ".",
          "xpos": ".",
          "upos": "PUNCT",
          "entity_iob": "O",
          "characterOffsetBegin": 27,
          "characterOffsetEnd": 28,
          "lang": "en",
          "features": {
            "Overt": "Yes",
            "Stop": "No",
            "Alpha": "No",
            "PunctType": "Peri",
            "Foreign": "No"
          },
          "misc": {
            "SpaceAfter": "No"
          }
        }
      }),
      "sentences": {
        1: {
          "id": 1,
          "tokenFrom": 1,
          "tokenTo": 10,
          "tokens": [
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9
          ]
        }
      },
      "dependencies": [
        {
          "style": "universal",
          "arcs": {
            1: [
              {
                "sentenceId": 1,
                "label": "nsubj",
                "governor": 2,
                "dependent": 1
              }
            ],
            2: [
              {
                "sentenceId": 1,
                "label": "root",
                "governor": 0,
                "dependent": 2
              }
            ],
            3: [
              {
                "sentenceId": 1,
                "label": "aux",
                "governor": 4,
                "dependent": 3
              }
            ],
            4: [
              {
                "sentenceId": 1,
                "label": "xcomp",
                "governor": 2,
                "dependent": 4
              }
            ],
            5: [
              {
                "sentenceId": 1,
                "label": "det",
                "governor": 8,
                "dependent": 5
              }
            ],
            6: [
              {
                "sentenceId": 1,
                "label": "amod",
                "governor": 8,
                "dependent": 6
              }
            ],
            7: [
              {
                "sentenceId": 1,
                "label": "amod",
                "governor": 8,
                "dependent": 7
              }
            ],
            8: [
              {
                "sentenceId": 1,
                "label": "dobj",
                "governor": 4,
                "dependent": 8
              }
            ],
            9: [
              {
                "sentenceId": 1,
                "label": "punct",
                "governor": 2,
                "dependent": 9
              }
            ]
          }
        }
      ],
      "constituents": [
        {
          "sentenceId": 1,
          "labeledBracketing": "(ROOT (S (NP (PRP I)) (VP (VBP want) (S (VP (TO to) (VP (VB buy) (NP (DT a) (JJ big) (JJ red) (NN car)))))) (. .)))"
        }
      ],
      "expressions": [
        {
          "id": 1,
          "type": "NP",
          "head": 8,
          "dependency": "dobj",
          "tokens": [
            5,
            6,
            7,
            8
          ]
        }
      ]
    }
  }
})


class TestDependencyAnnotator(TestCase):
    def setUp(self) -> None:
        self.d = DependencyAnnotator()

    def test_annotate(self):
        nlp_json = OrderedDict(j)
        self.d.annotate(nlp_json)
        sent = nlp_json['documents'][1]['sentences'][1]
        assert [2] == sent['root'], sent['root']
        expected = {'head': 2, 'semantic': [2], 'phrase': [1, 2, 3, 4, 5, 6, 7, 8, 9]}
        assert expected == sent['mainVerb'], sent['mainVerb']
        expected = {'head': 1, 'semantic': [1], 'phrase': [1]}
        assert expected == sent['subject'], sent['subject']
        assert not sent['compound']
        assert sent['complex']
        assert not sent['negated']

        expected = {1: {'id': 1, 'sentenceId': 1, 'clauseType': 'relative', 'tokens': [3, 4, 5, 6, 7, 8], 'root': [4], 'mainVerb': {'head': 4, 'semantic': [4], 'phrase': [3, 4, 5, 6, 7, 8]}, 'object': {'head': 8, 'semantic': [8], 'phrase': [5, 6, 7, 8]}, 'compound': False, 'complex': False, 'transitivity': 'transitive', 'negated': False, 'parentClauseId': 2}, 2: {'id': 2, 'sentenceId': 1, 'clauseType': 'matrix', 'tokens': [1, 2, 9], 'root': [2], 'mainVerb': {'head': 2, 'semantic': [2], 'phrase': [1, 2, 3, 4, 5, 6, 7, 8, 9]}, 'subject': {'head': 1, 'semantic': [1], 'phrase': [1]}, 'compound': False, 'complex': True, 'negated': False}}
        actual = nlp_json['documents'][1]['clauses']
        assert expected == actual, actual
