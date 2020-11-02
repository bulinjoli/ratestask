from flask import Flask
from flask_restplus import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify
import requests
from parsers import Parsers


flask_app = Flask(__name__)
flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
flask_app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgres://postgres:ratestask@127.0.0.1:5432/postgres"
db = SQLAlchemy(flask_app)

app = Api(
    app=flask_app,
    version="1.0",
    title="Rates task",
    description="Rates task for xeneta company by Ognjen Bulut",
)

name_space = app.namespace("/", description="Main APIs")

Parser = Parsers()

@name_space.route("/rates")
class RatesClass(Resource):
    @app.doc(
        responses={200: "OK", 400: "Invalid Argument", 500: "Mapping Key Error"},
        params={
            "date_from": "Enter date from in format yyyy-mm-dd; example: 2016-01-01",
            "date_to": "Enter date in format yyyy-mm-dd; example: 2016-01-10",
            "origin": "Enter origin code or slug from where to go; example: CNGGZ or china_south_main",
            "destination": "Enter destination code or slug where to go; example: EETLL or baltic_main",
        },
    )
    @app.expect(Parser.rates_get)
    def get(self):

        args = Parser.rates_get.parse_args()
        date_from = args.get("date_from")
        date_to = args.get("date_to")
        origin = args.get("origin")
        destination = args.get("destination")

        try:
            sql = (
                "select day, ROUND(avg(price), 2) as average_price"
                " from prices"
                " where day>='{0}' and day<='{1}'"
                " and (orig_code='{2}' or orig_code in (select orig_code from prices, ports where ports.parent_slug = '{2}' and orig_code=ports.code))"
                " and (dest_code='{3}' or dest_code in (select dest_code from prices, ports where ports.parent_slug = '{3}' and dest_code=ports.code))"
                " group by day"
                " ORDER BY day ASC"
            ).format(date_from, date_to, origin, destination)
            result = db.session.execute(sql)
            return jsonify({"result": [dict(row) for row in result]})

        except KeyError as e:
            name_space.abort(
                500,
                e.__doc__,
                status="Could not retrieve information",
                statusCode="500",
            )
        except Exception as e:
            name_space.abort(
                400,
                e.__doc__,
                status="Could not retrieve information",
                statusCode="400",
            )

    @app.doc(
        responses={200: "OK", 400: "Invalid Argument", 500: "Mapping Key Error"},
        params={
            "date": "Enter date from in format yyyy-mm-dd; example: 2016-01-01",
            "origin": "Enter origin code where from to go; example: CNGGZ",
            "destination": "Enter destination code where to go; EETLL",
            "price": "Enter price; example: 12000",
            "currency": "Enter currency of price and this will be converted to USD; example: EUR",
        },
    )
    @app.expect(Parser.rates_post)
    def post(self):

        args = Parser.rates_post.parse_args()
        date = args.get("date")
        origin = args.get("origin")
        destination = args.get("destination")
        price = args.get("price")
        currency = args.get("currency")

        if currency is None or currency == "USD":
            new_price = price
        else:
            currency = currency.upper()
            try:
                response = requests.get(
                    "https://api.currencyfreaks.com/latest?apikey=9dd4dfce30c84f679528e8ac4529da8c"
                )
            except requests.exceptions.RequestException as e:
                name_space.abort(
                    500,
                    e.__doc__,
                    status="Could not retrieve information",
                    statusCode="500",
                )

            if response.status_code == 200:
                currencies = response.json()["rates"]
                if currencies.get(currency):
                    currency_value = currencies.get(currency)
                else:
                    name_space.abort(
                        400,
                        "Your currency doesnt exist",
                        status="Could not retrieve information",
                        statusCode="400",
                    )
            else:
                name_space.abort(
                    response.status_code,
                    "Currency freaks api doesnt work properly",
                    status="Could not retrieve information",
                    statusCode=response.status_code,
                )
            new_price = int(float(price)/float(currency_value))

        try:
            sql_insert = (
                "INSERT INTO prices (orig_code, dest_code, day, price)"
                " VALUES ('{0}', '{1}', '{2}', '{3}')"
            ).format(origin, destination, date, new_price)
            sql_show = (
                "select * from prices"
                " where day='{0}' and orig_code='{1}' and dest_code='{2}' and price='{3}'"
            ).format(date, origin, destination, new_price)
            db.engine.execute(sql_insert)
            result = db.session.execute(sql_show)

            return jsonify({"result": [dict(row) for row in result]})

        except KeyError as e:
            name_space.abort(
                500,
                e.__doc__,
                status="Could not retrieve information",
                statusCode="500",
            )
        except Exception as e:
            name_space.abort(
                400,
                e.__doc__,
                status="Could not retrieve information",
                statusCode="400",
            )

    @name_space.route("/rates_null")
    class RatesNullClass(Resource):
        @app.doc(
            responses={200: "OK", 400: "Invalid Argument", 500: "Mapping Key Error"},
            params={
                "date_from": "Enter date from in format yyyy-mm-dd; example: 2016-01-01",
                "date_to": "Enter date in format yyyy-mm-dd; example: 2016-01-01",
                "origin": "Enter origin code or slug from where to go; example: CNGGZ or china_south_main",
                "destination": "Enter destination code or slug where to go; example: EETLL or baltic_main",
            },
        )
        @app.expect(Parser.rates_get)
        def get(self):
            args = Parser.rates_get.parse_args()
            date_from = args.get("date_from")
            date_to = args.get("date_to")
            origin = args.get("origin")
            destination = args.get("destination")

            try:
                sql = (
                    "select day,"
                    " CASE WHEN count(price)<3 THEN null"
                    " ELSE round(avg(price), 2)"
                    " END"
                    " from prices"
                    " where day>='{0}' and day<='{1}'"
                    " and (orig_code='{2}' or orig_code in (select orig_code from prices, ports where ports.parent_slug = '{2}' and orig_code=ports.code))"
                    " and (dest_code='{3}' or dest_code in (select dest_code from prices, ports where ports.parent_slug = '{3}' and dest_code=ports.code))"
                    " group by day"
                    " ORDER BY day ASC"
                ).format(date_from, date_to, origin, destination)
                result = db.session.execute(sql)
                return jsonify({"result": [dict(row) for row in result]})

            except KeyError as e:
                name_space.abort(
                    500,
                    e.__doc__,
                    status="Could not retrieve information",
                    statusCode="500",
                )
            except Exception as e:
                name_space.abort(
                    400,
                    e.__doc__,
                    status="Could not retrieve information",
                    statusCode="400",
                )
