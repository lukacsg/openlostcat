from .abstract_bool_operator import AbstractBoolOperator
from openlostcat.utils import error, indent, base_indent_num


class BoolAND(AbstractBoolOperator):
    """Category (bool)-level AND operator (subexpression with boolean operands)

    """

    str_template = "AND(\n{operators}\n)"

    def __init__(self, bool_operators):
        self.bool_operators = bool_operators

    def apply(self, tag_bundle_set):
        result_meta_info = []
        for op in self.bool_operators:
            (op_result, op_result_meta_info) = op.apply(tag_bundle_set)
            result_meta_info += self.prefix_meta_info_paths("FilterAND", op_result_meta_info)
            if not op_result:
                return False, result_meta_info
        return True, result_meta_info

    def __str__(self):
        return self.str_template.format(operators=indent(
            '\n'.join([str(operator) for operator in self.bool_operators]),
            base_indent_num))


class BoolOR(AbstractBoolOperator):
    """Category (bool)-level OR operator (subexpression with boolean operands)

    """

    str_template = "OR[\n{operators}\n]"

    def __init__(self, bool_operators):
        self.bool_operators = bool_operators

    def apply(self, tag_bundle_set):
        result_meta_info = []
        for op in self.bool_operators:
            (op_result, op_result_meta_info) = op.apply(tag_bundle_set)
            result_meta_info += self.prefix_meta_info_paths("FilterOR", op_result_meta_info)
            if op_result:
                return True, result_meta_info
        return False, result_meta_info

    def __str__(self):
        return self.str_template.format(operators=indent(
            '\n'.join([str(operator) for operator in self.bool_operators]),
            base_indent_num))


class BoolNOT(AbstractBoolOperator):
    """Category (bool)-level NOT operator (subexpression with a boolean operand)

    """

    str_template = "NOT(\n{operator}\n)"

    def __init__(self, bool_operator):
        self.bool_operator = bool_operator

    def apply(self, tag_bundle_set):
        (op_result, op_result_meta_info) = self.bool_operator.apply(tag_bundle_set)
        return not op_result, self.prefix_meta_info_paths("FilterNOT", op_result_meta_info)

    def __str__(self):
        return self.str_template.format(operator=indent(str(self.bool_operator), base_indent_num))


class BoolREF(AbstractBoolOperator):
    """Category (bool)-level reference subexpression (boolean type)

    """

    str_template = "REF {name}(\n{operator}\n)"

    def __init__(self, name, bool_operator, with_cache=True):
        """

        :param name:
        :param bool_operator:
        :param with_cache:
        """
        self.name = name
        self.bool_operator = bool_operator
        # cache for an ongoing evaluation where key is the object reference of the tag bundle being categorized
        # (we assume the tag_bundle_set is not changed, if it is mutable, disable the cache by with_cache = False)
        self.with_cache = with_cache
        self.cached_key = None
        self.cached_value = None

    def apply(self, tag_bundle_set):
        if not self.with_cache or self.cached_key is not tag_bundle_set:
            self.cached_key = tag_bundle_set
            self.cached_value = self.bool_operator.apply(tag_bundle_set)
        return self.cached_value

    def __str__(self):
        return self.str_template.format(name=self.name, operator=indent(str(self.bool_operator), base_indent_num))


class BoolConst(AbstractBoolOperator):
    """Category (bool)-level constant subexpression (boolean type)

    """

    str_template = "CONST({const})"

    def __init__(self, const_val):
        """

        :param const_val:
        """
        if not isinstance(const_val, bool):
            error("Const must be initialized with a bool value.", const_val)
        self.const_val = const_val

    def apply(self, tag_bundle_set):
        return self.const_val, [(str(self), tag_bundle_set)]

    def __str__(self):
        return self.str_template.format(const=self.const_val)


class BoolIMPL(AbstractBoolOperator):
    """Category (bool)-level implication operator (subexpression with boolean operands)

    """

    str_template = "IMPL(\n{operators}\n)"

    def __init__(self, bool_operators):
        if len(bool_operators) < 2:
            error("Implication must contain at lest 2 elements :", bool_operators)
        self.bool_operators = bool_operators
        self.impl_op = BoolOR([BoolNOT(op) for op in bool_operators[:-1]] + [bool_operators[-1]])

    def apply(self, tag_bundle_set):
        return self.impl_op.apply(tag_bundle_set)

    def __str__(self):
        return self.str_template.format(operators=indent(
            '\n => \n'.join([str(operator) for operator in self.bool_operators]),
            base_indent_num))
