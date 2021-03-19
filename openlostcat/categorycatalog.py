from openlostcat.utils import error, indent, base_indent_num


class CategoryCatalog:
    """Represents a catalog of place categories, with their rules included,
    so that it can categorize a location by matching its osm tag bundle set according to a given strategy

    """

    evaluationStrategy = "firstMatching"
    """evaluationStrategy  """

    str_template = "CategoryCatalog:\ncategory rule collection: [\n{categories}\n]"

    def update_properties(self, prop):
        """Updates properties

        :param prop: a dict of properties, currently only "evaluationStrategy": "firstMatching" or "all"
        """
        if 'evaluationStrategy' in prop:
            self.evaluationStrategy = prop['evaluationStrategy']

    def __init__(self, category_list, properties=None, debug=False):
        """Initializes the catalog

        :param category_list: Category objects
        :param properties: directives for the category evaluation, see update_properties
        :param debug: Boolean for detailed output
        """
        if properties is None:
            properties = {}
        self.debug = debug
        self.update_properties(properties)
        self.categories = category_list

    def get_categories_enumerated_key_map(self):
        """Retrieves the categories with their rules

        :return: a dictionary of categories
        """
        return dict(enumerate([c.name for c in self.categories]))

    def apply_fm_evaluation(self, tag_bundle_set):
        """Categorizes a location (by its tag bundle set) with the first-matching category strategy (single output)

        :param tag_bundle_set: set of dicts of tags of osm objects at the location to be categorized
        :return: list of matching categories
        """
        for num, category in enumerate(self.categories):
            (is_matching_category, op_result_meta_info) = category.apply(tag_bundle_set)
            if is_matching_category:
                return (num, category.name, op_result_meta_info) if self.debug else (num, category.name)
        return (-1, None, []) if self.debug else (-1, None)

    def apply_all_evaluation(self, tag_bundle_set):
        """Categorizes a location (by its tag bundle set) with the all-matching category strategy
        (possible multiple output)

        :param tag_bundle_set: set of dicts of tags of osm objects at the location to be categorized
        :return: list of matching categories
        """
        categories_list = []
        for num, category in enumerate(self.categories):
            (is_matching_category, op_result_meta_info) = category.apply(tag_bundle_set)
            if is_matching_category:
                categories_list.append(
                    (num, category.name, op_result_meta_info) if self.debug else (num, category.name))
        return categories_list if categories_list else [(-1, None, []) if self.debug else (-1, None)]

    def apply(self, tag_bundle_set):
        """Categorizes a location (by its tag bundle set) according to the given strategy (stored in the catalog)
        
        :param tag_bundle_set: set of dicts of tags of osm objects at the location to be categorized
        :return: list of matching categories
        """
        evaluation_switcher = {
            "firstMatching": self.apply_fm_evaluation,
            "all": self.apply_all_evaluation
        }
        return evaluation_switcher.get(self.evaluationStrategy,
                                       lambda x: error("Unsupported evaluation strategy: ", self.evaluationStrategy))(
            tag_bundle_set)

    def __str__(self):
        return self.str_template.format(categories=indent(
            '\n'.join([str(category) for category in self.categories]),
            base_indent_num))
