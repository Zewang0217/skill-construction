import unittest
import collector

class TestCollector(unittest.TestCase):
    def test_parse_urlencoded(self):
        raw = b"name=Alice&age=30"
        result = collector.parse_input(raw)
        self.assertEqual(result, {"name": "Alice", "age": "30"})

    def test_parse_json(self):
        raw = b'{"name": "Bob", "age": 25}'
        result = collector.parse_input(raw, "application/json")
        self.assertEqual(result, {"name": "Bob", "age": 25})

    def test_validate_required(self):
        data = {"age": "20"}
        rules = {"name": {"required": True}}
        errors = collector.validate(data, rules)
        self.assertEqual(len(errors), 1)

    def test_mapping(self):
        data = {"first": "A", "last": "B", "age": 20}
        mappings = {"full": "f'{first} {last}'"}
        result = collector.apply_mappings(data, mappings)
        self.assertEqual(result["full"], "A B")

if __name__ == "__main__":
    unittest.main()