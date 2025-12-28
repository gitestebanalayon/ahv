from ninja      import Schema

class SucessSchema(Schema):
    message: str

class ErrorSchema(Schema):
    message: str