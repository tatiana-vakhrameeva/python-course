#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from array import array
import json
import datetime
import logging
import hashlib
import re
import uuid
from optparse import OptionParser
from http.server import BaseHTTPRequestHandler, HTTPServer
import scoring

SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}
UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}


class Field(object):
    value: any
    required: bool = False
    nullable: bool = True
    field_name = ""
    errors = []

    def __init__(self, required=False, nullable=True):
        self.required = required
        self.nullable = nullable

    def validate(self):
        if self.required and self.value is None:
            self.errors.append(f"{self.field_name} - This field is required")

        if not self.nullable and not self.value:
            self.errors.append(f"{self.field_name} - This field can not be empty")


class CharField(Field):
    value: str

    def validate(self):
        super().validate(self)

        if not isinstance(self.value, str):
            self.errors.append(f"{self.field_name} - This field must be string")


class ArgumentsField(Field):
    value: dict

    def validate(self):
        super().validate(self)

        if not isinstance(self.value, dict):
            self.errors.append(f"{self.field_name} - This field must be dict")


class EmailField(CharField):
    field_name: str = "Email"

    def validate(self):
        super().validate(self)

        if "@" not in self.value:
            self.errors.append(f"{self.field_name} must contain @")


class PhoneField(Field):
    field_name: str = "Phone"
    value: str | int

    def validate(self):
        super().validate(self)

        if not isinstance(self.value, str) and not isinstance(self.value, int):
            self.errors.append(f"{self.field_name} - This field must be string or int")

        if len(self.value) < 11:
            self.errors.append(f"{self.field_name} must contain 11 symbols")

        if str(self.value[0]) != "7":
            self.errors.append(f"{self.field_name} must starts with 7")


class DateField(CharField):
    field_name: str = "Date"

    def validate(self):
        super().validate(self)

        if not re.match(r"\d{2}\.\d{2}.\d{4}", self.value):
            self.errors.append(f"{self.field_name} must be in DD.MM.YYYY format")


class BirthDayField(DateField):
    field_name: str = "Birthday"

    def validate(self):
        super().validate(self)

        max_allowed_age = 70
        date_to_compare = datetime.datetime.now()
        date_to_compare.replace(year=date_to_compare.year - max_allowed_age)

        if date_to_compare > datetime.datetime.strptime(self.value, "%d.%m.%Y"):
            self.errors.append(f"{self.field_name} is not valid. Must be under 70")


class GenderField(Field):
    field_name: str = "Gender"
    value: int

    def validate(self):
        super().validate(self.value)

        if not isinstance(self.value, int):
            self.errors.append(f"{self.field_name} - This field must be int")

        if self.value not in GENDERS.keys():
            self.errors.append(f"{self.field_name} - This field must be one of 0, 1, 2")


class ClientIDsField(Field):
    field_name: str = "ClientIDs"
    value: array

    def validate(self):
        super().validate(self)

        for v in self.value:
            if not isinstance(v, int):
                self.errors.append(f"{self.field_name} - This field must array of int")


class RequestMetaclass(type):
    def __new__(cls, clsname, bases, attrs):
        fields_attrs = {}
        for attr, v in attrs.items():
            if isinstance(v, Field):
                fields_attrs[attr] = v

        attrs["fields"] = fields_attrs

        return super(RequestMetaclass, cls).__new__(cls, clsname, bases, attrs)


class BaseRequest(object, metaclass=RequestMetaclass):
    def __init__(self, request_params):
        # pass value and validate every field
        for name, field in self.fields.items():
            passed_field = request_params.get(name, None)
            # todo: validate
            setattr(self, name, passed_field)

    def validate(self):
        # validate all fileds
        for name, field in self.fields.items():
            field.validate()


class ClientsInterestsRequest(BaseRequest):
    client_ids = ClientIDsField(required=True, nullable=False)
    date = DateField(required=False, nullable=True)

    def validate(self):
        super().validate()

        # check pairs


class OnlineScoreRequest(BaseRequest):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    def validate(self):
        super().validate()

        # check pairs


class MethodRequest(BaseRequest):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN


def check_auth(request):
    if request.is_admin:
        digest = hashlib.sha512(
            datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT
        ).hexdigest()
    else:
        digest = hashlib.sha512(request.account + request.login + SALT).hexdigest()
    if digest == request.token:
        return True
    return False


def online_score(args):
    online_score = OnlineScoreRequest(args)
    print(online_score)
    # return scoring.get_score(store, phone, email, birthday=None, gender=None, first_name=None, last_name=None)


def clients_interests(args):
    clients_interests = ClientsInterestsRequest(args)
    print(clients_interests)


def method_handler(request, ctx, store):
    methods = {"online_score": online_score, "clients_interests": clients_interests}

    request_method = MethodRequest(request.get("body"))

    args = request_method.arguments

    if request_method.method in methods.keys():
        methods[request_method.method](args)
    else:
        return "Unknown method", INVALID_REQUEST

    response, code = None, OK

    return response, code


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {"method": method_handler}
    store = None

    def get_request_id(self, headers):
        return headers.get("HTTP_X_REQUEST_ID", uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers["Content-Length"]))
            request = json.loads(data_string)
        except Exception as e:
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s" % (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path](
                        {"body": request, "headers": self.headers}, context, self.store
                    )
                except Exception as e:
                    logging.exception("Unexpected error: %s" % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(code, "Unknown Error"), "code": code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r).encode())
        return


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(
        filename=opts.log,
        level=logging.INFO,
        format="[%(asctime)s] %(levelname).1s %(message)s",
        datefmt="%Y.%m.%d %H:%M:%S",
    )
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
