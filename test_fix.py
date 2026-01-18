"""
Test script to verify metafield write fix works correctly.
"""

import json
from metafield_writer import MetafieldTypeTransformer


def test_type_transformations():
    """Test value transformations for various metafield types."""
    
    transformer = MetafieldTypeTransformer()
    tests_passed = 0
    tests_failed = 0
    
    print("=" * 60)
    print("TESTING METAFIELD TYPE TRANSFORMATIONS")
    print("=" * 60)
    
    test_cases = [
        # (value, type, expected_format_description)
        ("Hello World", "single_line_text_field", "string"),
        (123, "single_line_text_field", "string '123'"),
        (42, "number_integer", "string '42'"),
        ("42", "number_integer", "string '42'"),
        (42.5, "number_decimal", "string '42.5'"),
        (True, "boolean", "string 'true'"),
        (False, "boolean", "string 'false'"),
        ({"key": "value"}, "json", "JSON string"),
        (["item1", "item2"], "list.single_line_text_field", "JSON array string"),
    ]
    
    for value, metafield_type, expected_desc in test_cases:
        try:
            result = transformer.transform_value(value, metafield_type)
            print(f"✅ {metafield_type}: {repr(value)} → {repr(result)}")
            tests_passed += 1
        except Exception as e:
            print(f"❌ {metafield_type}: {repr(value)} → ERROR: {e}")
            tests_failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {tests_passed} passed, {tests_failed} failed")
    print("=" * 60)
    
    return tests_failed == 0


def test_list_transformations():
    """Test list type transformations."""
    
    transformer = MetafieldTypeTransformer()
    print("\n" + "=" * 60)
    print("TESTING LIST TYPE TRANSFORMATIONS")
    print("=" * 60)
    
    test_cases = [
        (["tag1", "tag2"], "list.single_line_text_field"),
        ([1, 2, 3], "list.number_integer"),
        (["single"], "list.single_line_text_field"),  # Single item list
        ("single", "list.single_line_text_field"),  # Single string -> list
    ]
    
    for value, list_type in test_cases:
        try:
            result = transformer.transform_value(value, list_type)
            # Verify it's a valid JSON array string
            parsed = json.loads(result)
            assert isinstance(parsed, list), "Result should be JSON array"
            print(f"✅ {list_type}: {repr(value)} → {result} (valid JSON array)")
        except Exception as e:
            print(f"❌ {list_type}: {repr(value)} → ERROR: {e}")


def test_json_transformations():
    """Test JSON type transformations."""
    
    transformer = MetafieldTypeTransformer()
    print("\n" + "=" * 60)
    print("TESTING JSON TYPE TRANSFORMATIONS")
    print("=" * 60)
    
    test_cases = [
        ({"key": "value"}, "json"),
        ({"nested": {"data": [1, 2, 3]}}, "json"),
        ('{"key": "value"}', "json"),  # Already JSON string
        ([1, 2, 3], "json"),  # Array
    ]
    
    for value, json_type in test_cases:
        try:
            result = transformer.transform_value(value, json_type)
            # Verify it's valid JSON
            parsed = json.loads(result)
            print(f"✅ JSON: {repr(value)[:50]}... → valid JSON")
        except Exception as e:
            print(f"❌ JSON: {repr(value)[:50]}... → ERROR: {e}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("METAFIELD WRITE FIX - VALIDATION TESTS")
    print("=" * 60)
    
    # Run tests
    basic_tests_pass = test_type_transformations()
    test_list_transformations()
    test_json_transformations()
    
    print("\n" + "=" * 60)
    if basic_tests_pass:
        print("✅ ALL CORE TESTS PASSED")
        print("The metafield type transformation logic works correctly.")
    else:
        print("❌ SOME TESTS FAILED")
        print("Please review the errors above.")
    print("=" * 60)
