#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import abstractmethod
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
    required: bool = False
    nullable: bool = True
    field_name = ""

    def __init__(self, required=False, nullable=True):
        self.required = required
        self.nullable = nullable

    def validate(self, value):
        if self.required and value is None:
            raise ValueError(f"{self.field_name} - This field is required")

        if not self.nullable and not value:
            raise ValueError(f"{self.field_name} - This field can not be empty")


class CharField(Field):
    def validate(self, value):
        super().validate(value=value)

        if not isinstance(value, str):
            raise ValueError(f"{self.field_name} - This field must be string")


class ArgumentsField(Field):
    def validate(self, value):
        super().validate(value=value)

        if not isinstance(value, dict):
            raise ValueError(f"{self.field_name} - This field must be dict")


class EmailField(CharField):
    field_name: str = "Email"

    def validate(self, value):
        super().validate(value=value)

        if "@" not in value:
            raise ValueError(f"{self.field_name} must contain @")


class PhoneField(Field):
    field_name: str = "Phone"

    def validate(self, value):
        super().validate(value=value)

        if not isinstance(value, str) and not isinstance(value, int):
            raise ValueError(f"{self.field_name} - This field must be string or int")

        if len(value) < 11:
            raise ValueError(f"{self.field_name} must contain 11 symbols")

        if str(value[0]) != "7":
            raise ValueError(f"{self.field_name} must starts with 7")


class DateField(CharField):
    field_name: str = "Date"

    def validate(self, value):
        super().validate(value=value)

        if not re.match(r"\d{2}\.\d{2}.\d{4}", value):
            raise ValueError(f"{self.field_name} must be in DD.MM.YYYY format")


class BirthDayField(DateField):
    field_name: str = "Birthday"

    def validate(self, value):
        super().validate(value=value)

        max_allowed_age = 70
        date_to_compare = datetime.datetime.now()
        date_to_compare = date_to_compare.replace(
            year=date_to_compare.year - max_allowed_age
        )

        if date_to_compare > datetime.datetime.strptime(value, "%d.%m.%Y"):
            raise ValueError(f"{self.field_name} is not valid. Must be under 70")


class GenderField(Field):
    field_name: str = "Gender"

    def validate(self, value):
        super().validate(value=value)

        if not isinstance(value, int):
            raise ValueError(f"{self.field_name} - This field must be int")

        if value not in GENDERS.keys():
            raise ValueError(f"{self.field_name} - This field must be one of 0, 1, 2")


class ClientIDsField(Field):
    field_name: str = "ClientIDs"

    def validate(self, value):
        super().validate(value=value)

        for v in value:
            if not isinstance(v, int):
                raise ValueError(f"{self.field_name} - This field must array of int")


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
            field.validate(passed_field)
            setattr(self, name, passed_field)

        self.validate()

    @abstractmethod
    def validate(self):
        pass


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

        if not (
            self.phone
            and self.email
            or self.first_name
            and self.last_name
            or self.gender
            and self.birthday
        ):
            raise ValueError(
                "Request should contain one of pairs: Phone + Email, First Name + Last Name or Gender + Birthday"
            )


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
            bytes(datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT, "utf-8")
        ).hexdigest()
    else:
        digest = hashlib.sha512(
            bytes(request.account + request.login + SALT, "utf-8")
        ).hexdigest()
    if digest == request.token:
        return True
    return False


def online_score(request_method, args, ctx, store):
    online_score = OnlineScoreRequest(args)

    online_score.validate()

    if request_method.is_admin:
        return {"score": 42}, OK

    return (
        scoring.get_score(
            store,
            online_score.phone,
            online_score.email,
            online_score.birthday,
            online_score.gender,
            online_score.first_name,
            online_score.last_name,
        ),
        OK,
    )


def clients_interests(request_method, args, ctx, store):
    clients_interests = ClientsInterestsRequest(args)
    cids = clients_interests.client_ids

    ctx["nclients"] = len(cids)

    response = {}
    for cid in cids:
        response[cid] = scoring.get_interests(store, cid)

    return response, OK


def method_handler(request, ctx, store):
    methods = {"online_score": online_score, "clients_interests": clients_interests}

    request_method = MethodRequest(request.get("body"))

    if not check_auth(request_method):
        return "Forbidden", FORBIDDEN

    args = request_method.arguments

    if request_method.method in methods.keys():
        try:
            response, code = methods[request_method.method](
                request_method, args, ctx, store
            )
        except ValueError as e:
            return str(e), INVALID_REQUEST

    else:
        return "Unknown method", INVALID_REQUEST

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
            data_string = data_string.decode("utf-8")
            request = json.loads(data_string)
        except Exception as e:
            logging.exception("Bad request: %s" % e)
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
