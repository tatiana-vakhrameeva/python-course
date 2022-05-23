import unittest

from ..utils import cases
from api import Field, ValidationError


class TestField(unittest.TestCase):
    @cases(
        [
            {
                "init_values": {"required": True, "nullable": False},
                "value": "somevalue",
            },
            {"init_values": {"required": True, "nullable": True}, "value": ""},
            {"value": "somevalue"},
        ]
    )
    def test_validation_passed(self, args):
        field = Field(args.get("init_values"))
        self.assertIsNone(field.validate(args.get("value")))

    @cases(
        [
            {"init_values": {"required": True, "nullable": False}, "value": None},
            {
                "init_values": {"required": True, "nullable": True},
            },
        ]
    )
    def test_validation_failed(self, args):
        field = Field(args.get("init_values"))

        with self.assertRaises(ValidationError):
            field.validate(args.get("value"))


class TestCharField(unittest.TestCase):
    pass


class TestArgumentsField(unittest.TestCase):
    pass


class TestEmailField(unittest.TestCase):
    pass


class TestPhoneField(unittest.TestCase):
    pass


class TestDateField(unittest.TestCase):
    pass


class TestBirthDayField(unittest.TestCase):
    pass


class TestGenderField(unittest.TestCase):
    pass


class TestClientIDsField(unittest.TestCase):
    pass


if __name__ == "__main__":
    unittest.main()
