import unittest
from openlostcat.category import Category
from openlostcat.categorycatalog import CategoryCatalog
from openlostcat.operators.abstract_bool_operator import AbstractBoolOperator
from openlostcat.operators.bool_operators import BoolREF, BoolConst
from openlostcat.operators.filter_operators import FilterREF, FilterConst
from openlostcat.parsers.opexpressionparser import OpExpressionParser
from openlostcat.parsers.categoryorrefdefparser import CategoryOrRefDefParser
from openlostcat.parsers.categorycatalogparser import CategoryCatalogParser
from openlostcat.parsers.refdict import RefDict

from unittest.mock import patch


class TestParserProcess(unittest.TestCase):

    @staticmethod
    def __uniform_output(out):
        return out.replace(" ", "").replace("\n", "")

    def test_simplify_operator(self):
        """Test the singleton operator simplification functionality:
        If a bool AND or OR contains only 1 operator then it will be optimized (left out) by the parser
        """
        operator_json = {"__OR_": [{"__AND_": {"__OR_": [{"__AND_": {"__ANY_test": True}}]}}]}
        op_parser = OpExpressionParser()
        self.assertEqual("ANY[test](const(True))",
                         TestParserProcess.__uniform_output(str(op_parser.parse(operator_json))))
        operator_json2 = {"__OR_": [{"__AND_": {"__OR_": [{"__AND_": {"__CONST_": True}}]}}]}
        self.assertEqual("const(True)",
                         TestParserProcess.__uniform_output(str(op_parser.parse(operator_json2))))

    @patch('openlostcat.parsers.opexpressionparser.ANY.get_name')
    @patch('openlostcat.parsers.opexpressionparser.ALL.get_name')
    def test_nested_operator(self, get_name_mock_any, get_name_mock_all):
        """Test a nested operator example with more depth levels.
        Cases included:
            * filter->bool conversion in multiple levels (quantifier wrapping)
                * the last operand for the global [] is a bool const
                    -> other elements are translated to bool ops by quantifier wrapping
                * a bool-level operator (__ALL_) under IMPL_1 causes all operands of IMPL_1 to be wrapped as bool ops
                * because IMPL_1 becomes a bool op, all other operands of the first AND become bool-level ops (wrapped)
        Remark: uppercase operators are bool-level operators, lowercase operators are filter-level operators
        """

        get_name_mock_any.return_value = '__ANY_test'
        get_name_mock_all.return_value = '__ALL_test'
        operator_json = [
            {
                "__IMPL_1": [
                    {
                        "__NOT_": [
                            {"access": "private"},
                            {"motor_vehicle": True},
                            {
                                "__OR_": [
                                    {"__CONST_test": True,
                                     "landuse": "residential"},
                                    {"__CONST_test": False}
                                ],
                                "landuse": "residential"
                            }
                        ]
                    },
                    {"__ALL_": {"landuse": "residential"}},
                    {"landuse": "residential"}
                ],
                "__IMPL_2": [
                    {"landuse": 42}, {"landuse": None}, {"landuse": ["residential", None]}
                ],
                "landuse": "residential"

            },
            {"landuse": "residential"},
            {"__CONST_test": False,
             "__CONST_test2": False,
             "__CONST_test3": False,
             "__CONST_test4": True},
            True
        ]
        op_parser = OpExpressionParser()
        operator_validation_output = "OR[ \
                AND( \
                    IMPL( \
                        ANY[test]( \
                            not( \
                                or[ \
                                    {access : {'private'}}, is_optional_key = False \
                                    {motor_vehicle : {'yes'}}, is_optional_key = False \
                                    and( \
                                        or[ \
                                            and( \
                                                const(True) \
                                                {landuse : {'residential'}}, is_optional_key = False \
                                            ) \
                                            const(False) \
                                        ] \
                                        {landuse : {'residential'}}, is_optional_key = False \
                                    ) \
                                ] \
                            ) \
                        ) \
                        => \
                        ALL[test]( \
                            {landuse : {'residential'}}, is_optional_key = False \
                        ) \
                        => \
                        ANY[test]( \
                            {landuse : {'residential'}}, is_optional_key = False \
                        ) \
                    ) \
                    ALL[test]( \
                        impl( \
                            {landuse : {'42'}}, is_optional_key = False \
                            => \
                            {landuse : set()}, is_optional_key = True \
                            => \
                            {landuse : {'residential'}}, is_optional_key = True \
                        ) \
                    ) \
                    ANY[test]( \
                        {landuse : {'residential'}}, is_optional_key = False \
                    ) \
                ) \
                ANY[test]( \
                    {landuse : {'residential'}}, is_optional_key = False \
                ) \
                ANY[test]( \
                    and( \
                        const(False) \
                        const(False) \
                        const(False) \
                        const(True) \
                    ) \
                ) \
                CONST(True) \
            ]"
        self.assertEqual(TestParserProcess.__uniform_output(operator_validation_output),
                         TestParserProcess.__uniform_output(str(op_parser.parse(operator_json))))

    def test_parser_error(self):
        """Test if an exception is raised on a parser error - wrong constructs / nesting of elements
        """
        op_parser = OpExpressionParser()
        wrong_jsons = [{"__OR_": {"__CONST_": True}},
                       {"__AND_": [{"__CONST_": True}]},
                       {"__NOT_": "#wrong"},
                       {"__REF_": {"__CONST_": True}},
                       {"__IMPL_": {"__CONST_": True}},
                       {"__IMPL_": [True]},
                       {"__IMPL_": [{"__CONST_": True}]},
                       {"__CONST_": "#wrong"},
                       {"key": {"__CONST_": True}},
                       "wrong",
                       {"__ANY_": {"__ANY_2": True}},
                       {"__ALL_": {"__ALL_2": True}}]
        for wrong_json in wrong_jsons:
            with self.subTest(wrong_json=wrong_json):
                with self.assertRaises(SyntaxError):
                    op_parser.parse(wrong_json)

    def test_operator_equal_creation(self):
        """Test of some operators that can be created in multiple ways
        """
        op_parser = OpExpressionParser(RefDict({"#test": FilterREF("#test", FilterConst(True))},
                                               {"##test": BoolREF("#test", BoolConst(True))}))
        same_operators = [
            ({"__AND_": {"__CONST_": True, "__CONST_2": True}},
             {"__CONST_": True, "__CONST_2": True}),
            ({"__OR_": [True, True]},
             [True, True]),
            ({"__CONST_": True}, True),
            ({"__REF_": "#test"}, "#test"),
            ({"__REF_": "##test"}, "##test")
        ]
        for same_operator in same_operators:
            with self.subTest(same_operator=same_operator):
                self.assertEqual(type(op_parser.parse(same_operator[0])), type(op_parser.parse(same_operator[1])))

    def test_operator_filter_bool_variation(self):
        """Test if the parser creates the appropriate filter or bool variant of an operator
        """
        op_parser = OpExpressionParser(RefDict({"#test": FilterREF("#test", FilterConst(True))},
                                               {"##test": BoolREF("#test", BoolConst(True))}))
        bool_filter_operator_pairs = [
            ({"__CONST_": True, "__ANY_test": True}, {"__CONST_": True, "__CONST_2": True}),
            ([True, True, {"__ANY_test": True}], [True, True]),
            ({"__NOT_": {"__ANY_test": True}}, {"__NOT_": True}),
            ("##test", "#test"),
            ({"__IMPL_": [True, True, {"__ANY_test": True}]},
             {"__IMPL_": [True, True]})
        ]
        for bool_filter_operator_pair in bool_filter_operator_pairs:
            with self.subTest(bool_filter_operator_pair=bool_filter_operator_pair):
                self.assertTrue(AbstractBoolOperator.is_bool_op(op_parser.parse(bool_filter_operator_pair[0])))
                self.assertFalse(AbstractBoolOperator.is_bool_op(op_parser.parse(bool_filter_operator_pair[1])))

    @patch('openlostcat.parsers.opexpressionparser.ANY.get_name')
    @patch('openlostcat.parsers.opexpressionparser.ALL.get_name')
    def test_category_wrapper_quantifier(self, get_name_mock_any, get_name_mock_all):
        """Test the parsing of a category. Additionally tests quantifier wrapping inheritance.
        """
        get_name_mock_any.return_value = '__ANY_test'
        get_name_mock_all.return_value = '__ALL_test'
        category_json = {
            "test_category": [
                {
                    "__IMPL_1": [
                        {"landuse": "residential"}, {"landuse": "residential"}, {"landuse": "residential"}
                    ],
                    "__IMPL_2": [
                        {"landuse": "residential"}, {"landuse": "residential"}, {"landuse": "residential"}
                    ],
                    "landuse": "residential"

                },
                {"landuse": "residential"},
                {"__IMPL_1": [
                    {"landuse": "residential"}, {"landuse": "residential"}, {"landuse": "residential"}
                ]}
            ]
        }
        category_validation_output = "Category name: test_category \
                                    rules: [ \
                                        OR[ \
                                            ANY[test]( \
                                                and( \
                                                    impl( \
                                                            {landuse : {'residential'}}, is_optional_key = False \
                                                            => \
                                                            {landuse : {'residential'}}, is_optional_key = False \
                                                            => \
                                                            {landuse : {'residential'}}, is_optional_key = False \
                                                        ) \
                                                    impl( \
                                                            {landuse : {'residential'}}, is_optional_key = False \
                                                            => \
                                                            {landuse : {'residential'}}, is_optional_key = False \
                                                            => \
                                                            {landuse : {'residential'}}, is_optional_key = False \
                                                        ) \
                                                            {landuse : {'residential'}}, is_optional_key = False \
                                                ) \
                                            ) \
                                            ANY[test]( \
                                                {landuse : {'residential'}}, is_optional_key = False \
                                            ) \
                                            ALL[test]( \
                                                impl( \
                                                    {landuse : {'residential'}}, is_optional_key = False \
                                                    => \
                                                    {landuse : {'residential'}}, is_optional_key = False \
                                                    => \
                                                    {landuse : {'residential'}}, is_optional_key = False \
                                                ) \
                                            ) \
                                        ] \
                                    ]"

        category_ref_parser = CategoryOrRefDefParser()
        category = category_ref_parser.parse(category_json)
        self.assertTrue(isinstance(category, Category))
        self.assertEqual(TestParserProcess.__uniform_output(category_validation_output),
                         TestParserProcess.__uniform_output(str(category)))

    @patch('openlostcat.parsers.opexpressionparser.ANY.get_name')
    @patch('openlostcat.parsers.opexpressionparser.ALL.get_name')
    def test_ref_parser(self, get_name_mock_any, get_name_mock_all):
        """Test the parsing of references
        """
        get_name_mock_any.return_value = '__ANY_test'
        get_name_mock_all.return_value = '__ALL_test'
        ref_json = {
            "##test_ref": [
                {
                    "__IMPL_1": [
                        {"landuse": "residential"}, {"landuse": "residential"}, {"landuse": "residential"}
                    ],
                    "__IMPL_2": [
                        {"landuse": "residential"}, {"landuse": "residential"}, {"landuse": "residential"}
                    ],
                    "landuse": "residential"

                },
                {"landuse": "residential"},
                {"__IMPL_1": [
                    {"landuse": "residential"}, {"landuse": "residential"}, {"landuse": "residential"}
                ]}
            ]
        }
        ref_validation_output = "REF ##test_ref( \
                    ALL[test]( \
                            or[ \
                                and( \
                                    impl( \
                                        {landuse : {'residential'}}, is_optional_key = False \
                                        => \
                                        {landuse : {'residential'}}, is_optional_key = False \
                                        => \
                                        {landuse : {'residential'}}, is_optional_key = False \
                                    ) \
                                impl( \
                                    {landuse : {'residential'}}, is_optional_key = False \
                                    => \
                                    {landuse : {'residential'}}, is_optional_key = False \
                                    => \
                                    {landuse : {'residential'}}, is_optional_key = False \
                                ) \
                                {landuse : {'residential'}}, is_optional_key = False \
                                ) \
                                {landuse : {'residential'}}, is_optional_key = False \
                                impl( \
                                    {landuse : {'residential'}}, is_optional_key = False \
                                => \
                                {landuse : {'residential'}}, is_optional_key = False \
                                => \
                                {landuse : {'residential'}}, is_optional_key = False \
                                ) \
                            ] \
                    ) \
            )"

        category_ref_parser = CategoryOrRefDefParser()
        ref = category_ref_parser.parse(ref_json)
        self.assertTrue(isinstance(ref, BoolREF))
        self.assertEqual(TestParserProcess.__uniform_output(ref_validation_output),
                         TestParserProcess.__uniform_output(str(ref)))

    def test_category_cat_error(self):
        """Test if an exception is raised if the top-level structure of the input json is wrong (tests validation)
        """
        bad_json1 = {
            "type": "Wrong type",
            "properties": {
                "evaluationStrategy": "all"
            },
            "categoryRules": [
                {
                    "water_nearby": {"waterway": "river"}
                }
            ]
        }
        bad_json2 = {
            "type": "CategoryRuleCollection",
            "properties": {
                "evaluationStrategy": "all"
            },
            "wrong rules label": [
                {
                    "water_nearby": {"waterway": "river"}
                }
            ]
        }
        cat_cat_parser = CategoryCatalogParser()
        with self.assertRaises(SyntaxError):
            cat_cat_parser.parse(bad_json1)
        with self.assertRaises(SyntaxError):
            cat_cat_parser.parse(bad_json2)

    @patch('openlostcat.parsers.opexpressionparser.ANY.get_name')
    @patch('openlostcat.parsers.opexpressionparser.ALL.get_name')
    def test_category_cat_parser(self, get_name_mock_any, get_name_mock_all):
        """Test the category catalog parser (without references)
        """
        get_name_mock_any.return_value = '__ANY_test'
        get_name_mock_all.return_value = '__ALL_test'
        cat_cat_json = {
            "type": "CategoryRuleCollection",
            "properties": {
                "evaluationStrategy": "all"
            },
            "categoryRules": [
                {
                    "water_nearby": {"waterway": "river"}
                },
                {
                    "calm_streets": {
                        "__ALL_not_road": {
                            "__NOT_road": {"highway": "primary"}
                        }
                    }
                }
            ]
        }
        cat_cat_validation_output = "CategoryCatalog: \
                category rule collection: [ \
                        Category name: water_nearby \
                            rules: [ \
                                ANY[test]( \
                                    {waterway : {'river'}}, is_optional_key = False \
                                ) \
                            ] \
                        Category name: calm_streets \
                        rules: [ \
                            ALL[test]( \
                                not( \
                                    {highway : {'primary'}}, is_optional_key = False \
                                ) \
                            ) \
                        ] \
                ]"
        cat_cat_parser = CategoryCatalogParser()
        cat_cat = cat_cat_parser.parse(cat_cat_json)
        self.assertTrue(isinstance(cat_cat, CategoryCatalog))
        self.assertEqual(cat_cat.evaluationStrategy, "all")
        self.assertEqual(len(cat_cat.categories), 2)
        self.assertEqual(TestParserProcess.__uniform_output(cat_cat_validation_output),
                         TestParserProcess.__uniform_output(str(cat_cat)))

    @patch('openlostcat.parsers.opexpressionparser.ANY.get_name')
    @patch('openlostcat.parsers.opexpressionparser.ALL.get_name')
    def test_category_cat_with_ref_parser(self, get_name_mock_any, get_name_mock_all):
        """Test category catalog parser for references
        """
        get_name_mock_any.return_value = '__ANY_test'
        get_name_mock_all.return_value = '__ALL_test'
        cat_cat_ref_json = {
            "type": "CategoryRuleCollection",
            "categoryRules": [
                {
                    "#test": {"__FIELDCONST_": True}
                },
                {
                    "#test2": {"__FIELDCONST_": False}
                },
                {
                    "##test": True
                },
                {
                    "#test3": False
                },
                {
                    "first": ["#test", "##test", "#test2"]
                },
                {
                    "second": {"__OR_": ["#test", "##test"], "__REF_:": "#test3"}
                },
                {
                    "third": {"__IMPL_": ["#test", {"__NOT_": ["##test"]}, "#test3"]}
                },
            ]
        }
        cat_cat_validation_output = "CategoryCatalog: \
            category rule collection: [ \
                    Category name: first \
                    rules: [ \
                        OR[ \
                            ANY[test]( \
                                ref #test( \
                                    {__FIELDCONST_ : {'yes'}}, is_optional_key = False \
                                ) \
                            ) \
                            REF ##test( \
                                CONST(True) \
                            ) \
                            ANY[test]( \
                                ref #test2( \
                                    {__FIELDCONST_ : {'no'}}, is_optional_key = False \
                                 ) \
                            ) \
                        ] \
                    ] \
                    Category name: second \
                    rules: [ \
                        AND( \
                            OR[ \
                                ANY[test]( \
                                    ref #test( \
                                        {__FIELDCONST_ : {'yes'}}, is_optional_key = False \
                                    ) \
                                ) \
                                REF ##test( \
                                    CONST(True) \
                                ) \
                            ] \
                            REF {#}#test3( \
                                CONST(False) \
                            ) \
                        ) \
                    ] \
                    Category name: third \
                    rules: [ \
                        IMPL( \
                            ANY[test]( \
                                ref #test( \
                                    {__FIELDCONST_ : {'yes'}}, is_optional_key = False \
                                ) \
                            ) \
                            => \
                            NOT( \
                                REF ##test( \
                                    CONST(True) \
                                ) \
                            ) \
                            => \
                            REF {#}#test3( \
                                CONST(False) \
                            ) \
                        ) \
                    ] \
            ]"
        cat_cat_parser = CategoryCatalogParser()
        cat_cat = cat_cat_parser.parse(cat_cat_ref_json)
        self.assertTrue(isinstance(cat_cat, CategoryCatalog))
        self.assertEqual(len(cat_cat.categories), 3)
        self.assertEqual(TestParserProcess.__uniform_output(cat_cat_validation_output),
                         TestParserProcess.__uniform_output(str(cat_cat)))


if __name__ == '__main__':
    unittest.main()
