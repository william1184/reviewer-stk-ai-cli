import unittest
from unittest import TestCase

from src.utils.validate_helper import get_required_properties


class TestValidateHelper(TestCase):

    def test_get_required_properties_int(self):
        args = {"prop": 42}
        property_name = "prop"
        result = get_required_properties(args, property_name)
        self.assertEqual(result, 42)

    def test_get_required_properties_str(self):
        args = {"prop": "value"}
        property_name = "prop"
        result = get_required_properties(args, property_name)
        self.assertEqual(result, "value")

    def test_get_required_properties_empty_str(self):
        args = {"prop": ""}
        property_name = "prop"
        with self.assertRaises(EnvironmentError) as context:
            get_required_properties(args, property_name)
        self.assertEqual(str(context.exception), "The property prop is required")

    def test_get_required_properties_whitespace_str(self):
        args = {"prop": "   "}
        property_name = "prop"
        with self.assertRaises(EnvironmentError) as context:
            get_required_properties(args, property_name)
        self.assertEqual(str(context.exception), "The property prop is required")

    def test_get_required_properties_missing_property(self):
        args = {}
        property_name = "prop"
        with self.assertRaises(EnvironmentError) as context:
            get_required_properties(args, property_name)
        self.assertEqual(str(context.exception), "The property prop is required")

    def test_get_required_properties_none_property(self):
        args = {"prop": None}
        property_name = "prop"
        with self.assertRaises(EnvironmentError) as context:
            get_required_properties(args, property_name)
        self.assertEqual(str(context.exception), "The property prop is required")


if __name__ == "__main__":
    unittest.main()
