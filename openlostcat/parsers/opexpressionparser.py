from openlostcat.utils import error
from openlostcat.operators.filter_operators import FilterAND, FilterOR, FilterNOT, AtomicFilter, FilterIMPL, FilterConst
from openlostcat.operators.bool_operators import BoolAND, BoolOR, BoolNOT, BoolConst, BoolIMPL
from openlostcat.operators.quantifier_operators import ANY, ALL
from openlostcat.parsers.refdict import RefDict
from openlostcat.operators.abstract_bool_operator import AbstractBoolOperator
from openlostcat.operators.abstract_filter_operator import AbstractFilterOperator
import re


class OpExpressionParser:
    """Parser for operator subexpressions from JSON

    """

    def __init__(self, ref_dict=None):
        """ Initializer

        :param ref_dict: A reference dictionary object containing any named subexpressions
        being referred in the rules to be parsed
        """
        if ref_dict is None:
            ref_dict = RefDict()
        self.ref_dict = ref_dict

    def get_ref_dict(self):
        return self.ref_dict

    def set_ref_dict(self, ref_dict):
        self.ref_dict = ref_dict

    @staticmethod
    def __create_multiary_operator(op_list, filter_op_class, bool_op_class):
        """Creates an operator with multiple arity, its level depending on the operands

        :param op_list:         list of operands (subexpressions as operator objects)
        :param filter_op_class: a set/filter-level operator class to be used if the operands are of set/filter-level
        :param bool_op_class:   a category/bool-level operator class to be used if the operands are of that level
        :return:                an operator object of either the given filter_op_class or bool_op_class type
        """
        return bool_op_class(
            AbstractFilterOperator.get_as_bool_op_list(op_list)) if AbstractBoolOperator.is_bool_op_list(
            op_list) else filter_op_class(op_list)

    @staticmethod
    def __op_list_len_check(op_list):
        return len(op_list) == 1

    def __create_or(self, source_list):
        return self.__parse_standalone_operator(source_list[0]) \
            if OpExpressionParser.__op_list_len_check(source_list) \
            else self.__create_multiary_operator(
            [self.__parse_standalone_operator(e) for e in source_list], FilterOR, BoolOR)

    def __create_and(self, source_dict):
        return self.__parse_keyvalue_operator(*next(iter(source_dict.items()))) \
            if OpExpressionParser.__op_list_len_check(source_dict) \
            else self.__create_multiary_operator(
            [self.__parse_keyvalue_operator(*t) for t in source_dict.items()], FilterAND, BoolAND)

    def __create_impl(self, source_list):
        return self.__create_multiary_operator(
            [self.__parse_standalone_operator(e) for e in source_list],
            FilterIMPL, BoolIMPL)

    def __create_not(self, source):
        def create_unary_operator(op, filter_op_class, bool_op_class):
            return bool_op_class(op) if AbstractBoolOperator.is_bool_op(op) else filter_op_class(op)
        return create_unary_operator(self.__parse_standalone_operator(source),
                                     FilterNOT, BoolNOT)

    @staticmethod
    def __get_operator_prefix(key_str):
        """Determines whether the key string is an operator name and gets its operator type prefix

        :param key_str: input string (JSON key)
        :return: the operator type prefix if the input is an operator name, empty string otherwise
        """
        try:
            return re.findall("^__([^_]*)_", key_str)[0]
        except IndexError:
            return ""

    @staticmethod
    def __check_json_type(source, type_list):
        """Determines whether a json element is any of the given types

        :param source: data item to be determined
        :param type_list: types to be checked and accepted
        :return: bool as the result of the type check
        """
        return any(isinstance(source, type_candidate) for type_candidate in type_list)

    def __parse_keyvalue_operator(self, k, v):
        """Creates an operator (subexpression) by parsing a JSON key-value pair

        :param k: key
        :param v: value
        :return: operator object (used as a subexpression)
        """
        def create_and_check(x, create_fv, type_list, error_message):
            return create_fv(x) if self.__check_json_type(x, type_list) else error(error_message, x)
        switcher = {
            "OR": lambda x: create_and_check(x, self.__create_or, [list],
                                             "__OR_ key must contain a list element"),
            "AND": lambda x: create_and_check(x, self.__create_and, [dict],
                                              "__AND_ key must contain a dict element"),
            "NOT": lambda x: create_and_check(x, self.__create_not, [list, dict],
                                              "__NOT_ must contain a list or dict elements"),
            "REF": lambda x: create_and_check(x, self.ref_dict.get_ref, [str],
                                              "__REF_ must contain a string elements"),
            "IMPL": lambda x: create_and_check(x, self.__create_impl, [list],
                                               "__IMPL_ key must contain a list element"),
            "BOOLCONST": BoolConst,
            "FILTERCONST": FilterConst,
            "ANY": lambda x: ANY(k, self.__parse_standalone_operator(x)),
            "ALL": lambda x: ALL(k, self.__parse_standalone_operator(x))
        }
        return switcher.get(self.__get_operator_prefix(k), lambda x: AtomicFilter(k, x))(v)

    def __parse_standalone_operator(self, source):
        """Creates an operator by parsing a standalone JSON value (without an attribute name (key))
        (used mostly for parsing nested operands such as at quantifiers, or for parsing json list(array) items)

        :param source: value
        :return: operator object (used as a subexpression)
        """
        switcher = {
            list: self.__create_or,
            dict: self.__create_and,
            str: self.ref_dict.get_ref,
            bool: BoolConst
        }
        return switcher.get(type(source),
                            lambda x: error("Atomic value is not allowed here: ", x))(source)

    def parse(self, source):
        """The main parser method to be called from outside

        :param source: a json object to be parsed
        :return: operator object (used as a subexpression)
        """
        return self.__parse_standalone_operator(source)
