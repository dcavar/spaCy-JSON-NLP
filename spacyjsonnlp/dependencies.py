from collections import OrderedDict
from typing import List

from pyjsonnlp.annotation import Annotator
from pyjsonnlp.dependencies import UniversalDependencyParse
from pyjsonnlp.tokenization import subtract_tokens


class DependencyAnnotator(Annotator):
    clause_arcs = ('csubj', 'ccomp', 'xcomp', 'advcl', 'acl')
    clause_types = (('csubj', 'subject'), ('xcomp', 'relative'), ('ccomp', 'complement'), ('advcl', 'adverbial'), ('acl', 'adjectival'))
    compound_arcs = ('conj', 'cc')
    sov = (('subject', 'nsubj', ()),
           ('object', 'obj', ()),
           ('object', 'dobj', ()),
           ('indirectObject', 'iobj', ()),
           ('indirectObject', 'dative', ()))

    def annotate(self, nlp_json: OrderedDict) -> None:
        for doc in nlp_json['documents'].values():
            c_id = 1
            d = UniversalDependencyParse(doc['dependencies'][0], doc['tokenList'])
            for s_id, sent in doc['sentences'].items():
                s_head = d.sentence_heads[s_id]

                # subject/object/verb
                self.annotate_item(d, s_head, sent)

                # clauses
                depth = 0
                item = sent
                item_head = s_head
                parent_clause_id = 0
                item_tokens = [d.tokens[t_id] for t_id in range(sent['tokenFrom'], sent['tokenTo'])]
                while item['complex']:
                    if 'clauses' not in doc:
                        doc['clauses'] = {}
                    for arc, clause_type in self.clause_types:
                        if d.is_arc_present_below(item_head, arc):
                            # clause
                            c_head, clause_tokens = d.get_leaves_by_arc(arc, head=item_head, sentence_id=s_id)
                            clause = self.build_clause(c_id, s_id, parent_clause_id, clause_type, clause_tokens)
                            doc['clauses'][c_id] = clause
                            self.annotate_item(d, c_head, clause)
                            parent_clause_id = c_id
                            c_id += 1

                            # matrix clause at the sentence level
                            if depth == 0:
                                matrix_tokens = subtract_tokens(item_tokens, clause_tokens)
                                matrix = self.build_clause(c_id, s_id, 0, 'matrix', matrix_tokens)
                                doc['clauses'][c_id] = matrix
                                clause['parentClauseId'] = c_id
                                self.annotate_item(d, s_head, matrix)
                                c_id += 1

                            depth += 1
                            item = clause
                            item_head = c_head
                            # don't need item tokens
                            break

    @staticmethod
    def build_clause(clause_id: int, sent_id: int, parent_clause_id: int, clause_type: str, tokens: List[dict]) -> dict:
        clause = {
            'id': clause_id,
            'sentenceId': sent_id,
            'clauseType': clause_type,
            'tokens': [t['id'] for t in tokens]
        }
        if parent_clause_id:
            clause['parentClauseId'] = parent_clause_id
        return clause

    @staticmethod
    def build_grammar(d: UniversalDependencyParse, head: int) -> dict:
        return {
            'head': head,
            'semantic': [t['id'] for t in d.collect_compounds(head)],
            'phrase': [t['id'] for t in d.get_leaves(head)]
        }

    def annotate_item(self, d: UniversalDependencyParse, head: int, item: dict) -> None:
        # root
        item['root'] = head

        # subject/object/verb
        if d.tokens[head]['upos'][0] == 'V' or d.tokens[head]['xpos'][0] == 'V':
            item['mainVerb'] = self.build_grammar(d, head)
        for k, arc, follow in self.sov:
            grammar_head = d.get_child_with_arc(head, arc, follow)
            if grammar_head:
                item[k] = self.build_grammar(d, grammar_head['id'])

        # compound/complex/fragment
        item['compound'] = any(map(lambda a: d.is_arc_present_below(head, a), self.compound_arcs))
        item['complex'] = any(map(lambda a: d.is_arc_present_below(head, a), self.clause_arcs))
        # todo fragment (the syntax parser will tell this)

        # transitivity
        if 'mainVerb' in item:
            if 'indirectObject' in item:
                item['transitivity'] = 'ditransitive'
            elif 'object' in item:
                item['transitivity'] = 'transitive'
            elif not item['complex'] and d.is_arc_present_below(head, 'nsubj'):
                item['transitivity'] = 'intransitive'

        # negation
        item['negated'] = bool(d.get_child_with_arc(head, 'neg'))

        # todo sentence types
        # todo tense
        # todo modality
