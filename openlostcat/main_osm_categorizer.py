from openlostcat.utils import to_tag_bundle_set, get_tags_from_osm_elements
from openlostcat.parsers.categorycatalogparser import CategoryCatalogParser


class MainOsmCategorizer:
    """The main entry point for OpenLostCat:
    sets up a category catalog and categorizes locations by their tag bundle sets

    """

    def __init__(self, category_catalog_source, debug=False, category_catalog_parser=CategoryCatalogParser()):
        """Initializes the categorizer by setting up the category catalog

        :param category_catalog_source: a JSON structure as python dictionary or a file path string
        :param debug: Boolean, set to true for more detailed output
        :param category_catalog_parser: parse using the given parser
        """
        self.category_cat = category_catalog_parser.parse(category_catalog_source, debug=debug)

    def categorize(self, osm_json_dict):
        """Categorizes a location by the osm tag bundle set of the objects located there/nearby

        :param osm_json_dict: tag bundle set of the osm objects at/near the location
        :return: categories matching the location by the given strategy
        """
        tag_bundle_set = to_tag_bundle_set(get_tags_from_osm_elements(osm_json_dict))
        return self.category_cat.apply(tag_bundle_set)

    def get_categories_enumerated_key_map(self):
        """Retrieves the categories parsed by __init__

        :return: categories
        """
        return self.category_cat.get_categories_enumerated_key_map()

    def __str__(self):
        return str(self.category_cat)
