from flask_restplus import reqparse
from validators import valid_date, valid_currency


class Parsers:

    rates_get = reqparse.RequestParser()
    rates_get.add_argument("date_from", type=valid_date, required=True)
    rates_get.add_argument("date_to", type=valid_date, required=True)
    rates_get.add_argument("origin", type=str, required=True)
    rates_get.add_argument("destination", type=str, required=True)

    rates_post = reqparse.RequestParser()
    rates_post.add_argument("date", type=valid_date, required=True)
    rates_post.add_argument("origin", type=str, required=True)
    rates_post.add_argument("destination", type=str, required=True)
    rates_post.add_argument("price", type=int, required=True)
    rates_post.add_argument("currency", type=valid_currency, required=False)
