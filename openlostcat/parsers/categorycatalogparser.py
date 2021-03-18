from openlostcat.utils import error
from openlostcat.category import Category
from openlostcat.categorycatalog import CategoryCatalog
from openlostcat.parsers.refdict import RefDict
from .categoryorrefdefparser import CategoryOrRefDefParser
import json


class CategoryCatalogParser:
    """Parser for catalog of location categories with properties from JSON
    described by logical rules on osm tag bundle sets

    """

    category_rule_collection_type = "CategoryRuleCollection"
    """Top-level fixed string value for determining whether the JSON input is intended to be a category catalog
    """

    category_rules_key = "categoryRules"
    """Top-level JSON key of the categories with their rules
    """

    properties_key = "properties"
    """Top-level JSON key for the catalog properties
    """

    def __init__(self, category_or_refdef_parser=CategoryOrRefDefParser(), ref_dict=None):
        """Initializer

        :param category_or_refdef_parser: Nested parser for single categories and reference definitions (optional)
        :param ref_dict: A reference dictionary object containing any named subexpressions
        being referred in the rules to be parsed (optional, usually created here as an empty dict)
        """
        if ref_dict is None:
            ref_dict = RefDict()
        self.ref_dict = ref_dict
        self.category_or_refdef_parser = category_or_refdef_parser
        self.category_or_refdef_parser.set_ref_dict(self.ref_dict)

    def validate(self, category_rule_collection):
        """Validates the JSON input whether it has its correct required top-level fields

        :param category_rule_collection: JSON input
        :return: True if it is a valid input for parsing (top-level check)
        """
        if not isinstance(category_rule_collection, dict) or "type" not in category_rule_collection or \
                category_rule_collection["type"] != self.category_rule_collection_type or \
                self.category_rules_key not in category_rule_collection:
            return False
        return True

    def get_properties(self, category_rule_collection):
        """Gets properties from the JSON input

        :param category_rule_collection: JSON input
        :return: Property dictionary
        """
        if self.properties_key not in category_rule_collection or not isinstance(
                category_rule_collection[self.properties_key], dict):
            return {}
        return category_rule_collection[self.properties_key]

    def __get_category_rules(self, category_catalog):
        """Gets the categories with their rules to be parsed

        :param category_catalog: full JSON input with top-level keys and properties
        :return: JSON with the categories and their rules to be parsed on its top-level
        (a single category wrapped in an array)
        """
        category_rule_collection = category_catalog[self.category_rules_key]
        rule_switcher = {
            list: lambda l: l,
            dict: lambda d: [d]
        }
        return rule_switcher.get(type(category_rule_collection),
                                 lambda x: error("Category rules must be a  list or dict: ", x)
                                 )(category_rule_collection)

    def parse_category_list(self, category_rule_collection):
        """Creates the actual category and reference definition objects and stores them
        into a category array or ref_dict, resp., by parsing the JSON input with the given rules

        :param category_rule_collection: JSON array with the categories and their rules to be parsed
        :return: an array of category objects with their parsed rules as operator expressions
            Additionally, all reference (named subexpressions) definitions are stored into ref_dict
        """
        res = []
        for source in category_rule_collection:
            cat_or_ref = self.category_or_refdef_parser.parse(source)
            if isinstance(cat_or_ref, Category):
                res.append(cat_or_ref)
            else:
                self.ref_dict.set_ref(cat_or_ref)
        return res

    def parse(self,  category_catalog_source, debug=False):
        """The main parser method to be called from outside

        :param  category_catalog_source: JSON structure as a dictionary or a string as a file path
        :param debug: set to True for verbose output
        :return: a CategoryCatalog object
        """
        category_catalog = category_catalog_source
        if isinstance(category_catalog_source, str):
            with open(category_catalog_source) as f:
                category_catalog = json.load(f)
        if not self.validate(category_catalog):
            error("It is not a valid CategoryRuleCollection: ", category_catalog)
        return CategoryCatalog(self.parse_category_list(self.__get_category_rules(category_catalog)),
                               self.get_properties(category_catalog), debug)
