import datetime
import decimal
import json


class DecimalEncoder(json.JSONEncoder):
    def _iterencode(self, o, markers=None):
        if isinstance(o, decimal.Decimal):
            return (str(o) for o in [o])
        return super(DecimalEncoder, self)._iterencode(o, markers)


class DateTimeEncoder(json.JSONEncoder):
    def _iterencode(self, o, markers=None):
        if isinstance(o, datetime.datetime):
            return str(o)
        return super(DateTimeEncoder, self)._iterencode(o, markers)
