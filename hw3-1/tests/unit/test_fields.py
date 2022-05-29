import unittest

from ..utils import cases
from api import (
    Field,
    ValidationError,
    CharField,
    ArgumentsField,
    EmailField,
    PhoneField,
)


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
        field = CharField(args.get("init_values"))
        self.assertIsNone(field.validate(args.get("value")))

    @cases(
        [
            {"init_values": {"required": True, "nullable": False}, "value": None},
            {
                "init_values": {"required": True, "nullable": True},
            },
            {"value": 123},
            {"value": ["array"]},
            {"value": bytes("bytes", "utf-8")},
        ]
    )
    def test_validation_failed(self, args):
        field = CharField(args.get("init_values"))

        with self.assertRaises(ValidationError):
            field.validate(args.get("value"))


class TestArgumentsField(unittest.TestCase):
    @cases(
        [
            {
                "init_values": {"required": True, "nullable": False},
                "value": {"a": 4, "b": "some string"},
            },
            {"init_values": {"required": True, "nullable": True}, "value": ""},
            {"value": {}},
        ]
    )
    def test_validation_passed(self, args):
        field = ArgumentsField(args.get("init_values"))
        self.assertIsNone(field.validate(args.get("value")))

    @cases(
        [
            {"init_values": {"required": True, "nullable": False}, "value": None},
            {
                "init_values": {"required": True, "nullable": True},
            },
            {"value": 123},
            {"value": ["array"]},
            {"value": bytes("bytes", "utf-8")},
        ]
    )
    def test_validation_failed(self, args):
        field = ArgumentsField(args.get("init_values"))

        with self.assertRaises(ValidationError):
            field.validate(args.get("value"))


class TestEmailField(unittest.TestCase):
    @cases(
        [
            {
                "init_values": {"required": True, "nullable": False},
                "value": "goodemail@example.com",
            },
            {
                "init_values": {"required": True, "nullable": True},
                "value": "aaaa@example.com",
            },
        ]
    )
    def test_validation_passed(self, args):
        field = EmailField(args.get("init_values"))
        self.assertIsNone(field.validate(args.get("value")))

    @cases(
        [
            {"init_values": {"required": True, "nullable": False}, "value": None},
            {
                "init_values": {"required": True, "nullable": True},
            },
            {"value": 123},
            {"value": ["array"]},
            {"value": bytes("bytes", "utf-8")},
            {"value": "aaaexample"},
        ]
    )
    def test_validation_failed(self, args):
        field = EmailField(args.get("init_values"))

        with self.assertRaises(ValidationError):
            field.validate(args.get("value"))


class TestPhoneField(unittest.TestCase):
    @cases(
        [
            {
                "init_values": {"required": True, "nullable": False},
                "value": "71231232323",
            },
            {
                "init_values": {"required": True, "nullable": True},
                "value": 77777777777,
            },
        ]
    )
    def test_validation_passed(self, args):
        field = PhoneField(args.get("init_values"))
        self.assertIsNone(field.validate(args.get("value")))

    @cases(
        [
            {"init_values": {"required": True, "nullable": False}, "value": None},
            {
                "init_values": {"required": True, "nullable": True},
            },
            {"value": 123},
            {"value": ["array"]},
            {"value": bytes("bytes", "utf-8")},
            {"value": "aaaexample"},
            {"value": "77777"},
            {"value": 12345},
            {"value": 10101010101},
            {"value": "12345678901"},
        ]
    )
    def test_validation_failed(self, args):
        field = PhoneField(args.get("init_values"))

        with self.assertRaises(ValidationError):
            field.validate(args.get("value"))


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
