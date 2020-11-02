from flask import Flask
from flask_restplus import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify
from flask import request
import requests

flask_app = Flask(__name__)
flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
flask_app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://postgres:ratestask@127.0.0.1:5432/postgres"
db = SQLAlchemy(flask_app)


app = Api(app=flask_app, version="1.0", title="Rates task", description="Rates task for xeneta company by Ognjen Bulut")

name_space = app.namespace('/', description='Main APIs')


@name_space.route("/rates")
class MainClass(Resource):
	@app.doc(responses={200: 'OK', 400: 'Invalid Argument', 500: 'Mapping Key Error'}, params={'date_from': 'Enter date from', 'date_to': 'Enter date', 'origin': 'Enter origin where from to go', 'destination': 'Enter destination where to go'})
	def get(self):

		date_from = request.args.get('date_from')
		date_to = request.args.get('date_to')
		origin = request.args.get('origin')
		destination = request.args.get('destination')

		try:
			sql = ("select day, ROUND(avg(price), 2) as average_price"
				   " from prices"
				   " where day>='{0}' and day<='{1}'"
				   " and (orig_code='{2}' or orig_code in (select orig_code from prices, ports where ports.parent_slug = '{2}' and orig_code=ports.code))"
				   " and (dest_code='{3}' or dest_code in (select dest_code from prices, ports where ports.parent_slug = '{3}' and dest_code=ports.code))"
				   " group by day"
				   " ORDER BY day ASC").format(date_from, date_to, origin, destination)
			result = db.session.execute(sql)
			return jsonify({'result': [dict(row) for row in result]})

		except KeyError as e:
			name_space.abort(500, e.__doc__, status="Could not retrieve information", statusCode="500")
		except Exception as e:
			name_space.abort(400, e.__doc__, status="Could not retrieve information", statusCode="400")

	@app.doc(responses={200: 'OK', 400: 'Invalid Argument', 500: 'Mapping Key Error'},
			 params={'date': 'Enter date from', 'origin': 'Enter origin where from to go',
					 'destination': 'Enter destination where to go', 'price': 'Enter price', 'currency': 'Enter currency of price'})
	def post(self):
		date = request.args.get('date')
		origin = request.args.get('origin')
		destination = request.args.get('destination')
		price = request.args.get('price')
		currency = request.args.get('currency')

		response = requests.get("https://api.currencyfreaks.com/latest?apikey=9dd4dfce30c84f679528e8ac4529da8c")

		currency_value = 1.0
		if response.status_code == 200:
			currencies = response.json()
			currency_value = currencies['rates'][currency]

		print(type(currency_value))
		print(type(price))
		if currency == 'USD' or '':
			new_price = price
		else:
			new_price = int(float(currency_value)*float(price))

		try:
			sql_insert = ("INSERT INTO prices (orig_code, dest_code, day, price)"
				   " VALUES ('{0}', '{1}', '{2}', '{3}')").format(origin, destination, date, new_price)
			print(sql_insert)
			sql_show = ("select * from prices"
						  " where day='{0}' and orig_code='{1}' and dest_code='{2}' and price='{3}'").format(date, origin, destination, new_price)
			print(sql_show)
			db.engine.execute(sql_insert)
			result = db.session.execute(sql_show)

			return jsonify({'result': [dict(row) for row in result]})

		except KeyError as e:
			name_space.abort(500, e.__doc__, status="Could not retrieve information", statusCode="500")
		except Exception as e:
			name_space.abort(400, e.__doc__, status="Could not retrieve information", statusCode="400")

	@name_space.route("/rates_null")
	class NextClass(Resource):
		@app.doc(responses={200: 'OK', 400: 'Invalid Argument', 500: 'Mapping Key Error'},
				 params={'date_from': 'Enter date from', 'date_to': 'Enter date',
						 'origin': 'Enter origin where from to go', 'destination': 'Enter destination where to go'})
		def get(self):
			print("here1")

			date_from = request.args.get('date_from')
			date_to = request.args.get('date_to')
			origin = request.args.get('origin')
			destination = request.args.get('destination')

			print("here2")

			try:
				sql = ("select day,"
					   " CASE WHEN count(price)<3 THEN null"
					   " ELSE round(avg(price), 2)"
					   " END"
					   " from prices"
					   " where day>='{0}' and day<='{1}'"
					   " and (orig_code='{2}' or orig_code in (select orig_code from prices, ports where ports.parent_slug = '{2}' and orig_code=ports.code))"
					   " and (dest_code='{3}' or dest_code in (select dest_code from prices, ports where ports.parent_slug = '{3}' and dest_code=ports.code))"
					   " group by day"
					   " ORDER BY day ASC").format(date_from, date_to, origin, destination)
				print(sql)
				result = db.session.execute(sql)
				return jsonify({'result': [dict(row) for row in result]})

			except KeyError as e:
				name_space.abort(500, e.__doc__, status="Could not retrieve information", statusCode="500")
			except Exception as e:
				name_space.abort(400, e.__doc__, status="Could not retrieve information", statusCode="400")