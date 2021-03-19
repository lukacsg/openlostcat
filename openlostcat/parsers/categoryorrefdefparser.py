from openlostcat.utils import error
from openlostcat.category import Category
from .opexpressionparser import OpExpressionParser
from openlostcat.parsers.refdict import RefDict
from openlostcat.operators.bool_operators import BoolOR
from openlostcat.operators.abstract_filter_operator import AbstractFilterOperator


class CategoryOrRefDefParser:
    """Parser for location categories or references (named subexpressions) from JSON,
    described by logical rules on osm tag bundle sets

    """

    def __init__(self, op_exp_parser=None, ref_dict=None):
        """Initializer

        :param op_exp_parser: Nested parser for operator (sub)expressions (optional)
        :param ref_dict: A reference dictionary object containing any named subexpressions
        being referred in the rules to be parsed - passed further to op_exp_parser
        """
        if ref_dict is None:
            ref_dict = RefDict()
        self.op_exp_parser.set_ref_dict(ref_dict)
        if op_exp_parser is None:
            op_exp_parser = OpExpressionParser()
        self.op_exp_parser = op_exp_parser

    def get_ref_dict(self):
        return self.op_exp_parser.get_ref_dict()

    def set_ref_dict(self, ref_dict):
        self.op_exp_parser.set_ref_dict(ref_dict)

    def parse(self, source):
        """The main parser method to be called from outside

        :param source: a json object to be parsed, either as a category or
            reference definition (the latter starting with #)
        :return: category or reference definition object
        """
        if not isinstance(source, dict):
            error("A category or reference definition must contain a JSON object: ", source)
        if len(source) > 1:
            error("A category or reference definition must have exactly one key-value pair: ", source)
        kv = next(iter(source.items()))
        if RefDict.is_ref(kv[0]):
            ref_operator = self.op_exp_parser.parse(kv[1])
            return RefDict.create_ref(kv[0], ref_operator)
        else:
            return Category(kv[0], self.parse_category_rules(kv[1]))

    def parse_category_rules(self, rules):
        """Creates a category/bool-level operator (expression) object by parsing

        :param rules: a standalone json value with rule descriptions
        :return: category/bool-level operator (expression) object
          Rermark: If multiple rules are given as json list, it will be parsed as an OR of category/bool-level operands
          (if no quantifiers are explicitly used, the list elements are wrapped by separate quantifiers
           instead of a single top-level quantifier, so they appear as separate rules joined by a top-level OR operator)
        """
        if isinstance(rules, list):
            # A category-level list is interpreted as a list of bool level rules
            # (each item forced as a bool op instead of a filter-or)
            return BoolOR(AbstractFilterOperator.get_as_bool_op_list([self.op_exp_parser.parse(r) for r in rules]))
        else:
            # Any other json element as category is interpreted as a single bool-level operator
            # (any filter-level ops forced as bool ops by wrapping them into an ANY quantifier)
            return AbstractFilterOperator.get_as_bool_op(self.op_exp_parser.parse(rules))
