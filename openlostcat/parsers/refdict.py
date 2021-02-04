from openlostcat.operators.bool_operators import BoolREF
from openlostcat.operators.filter_operators import FilterREF
from openlostcat.utils import error
from openlostcat.operators.abstract_bool_operator import AbstractBoolOperator
from openlostcat.operators.abstract_filter_operator import AbstractFilterOperator


class RefDict:
    """

    """

    def __init__(self, filter_ref_dict = {}, bool_ref_dict = {}):
        """

        :param filter_ref_dict:
        :param bool_ref_dict:
        """
        self.bool_ref_dict = bool_ref_dict
        self.filter_ref_dict = filter_ref_dict

    @staticmethod
    def is_ref(ref_name):
        """

        :param ref_name:
        :return:
        """
        return ref_name.startswith("#")

    @staticmethod
    def is_bool_ref(ref_name):
        """

        :param ref_name:
        :return:
        """
        return ref_name.startswith("##")

    def get_ref(self, ref_name):
        """

        :param ref_name:
        :return:
        """
        try:
            if self.is_bool_ref(ref_name):
                return self.bool_ref_dict[ref_name]
            elif self.is_ref(ref_name):
                return self.filter_ref_dict[ref_name]
            else:
                error("Syntax error: invalid reference name. A reference name must start with '#': ", ref_name)
        except KeyError:
            error("The given reference can not be found: ", ref_name)

    def set_ref(self, ref_name, ref_operator):
        """

        :param ref_name:
        :param ref_operator:
        :return:
        """
        if not self.is_ref(ref_name):
            error("Syntax error: invalid reference name. A reference name must start with '#': ", ref_name)
        if self.is_bool_ref(ref_name):
            # self.bool_ref_dict[ref_name] = BoolREF(ref_name, get_as_bool_op(ref_operator))
            self.bool_ref_dict[ref_name] = BoolREF(ref_name, AbstractFilterOperator.get_as_bool_op(ref_operator))
        else:
            if AbstractBoolOperator.is_bool_op(ref_operator):
                error("Invalid reference definition. A bool expression is given but a filter expression is expected: ", ref_operator)
            self.filter_ref_dict[ref_name] = FilterREF(ref_name, ref_operator)

