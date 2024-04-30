# Import Flask Library
import hashlib
from datetime import datetime, timedelta
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors

# Initialize the app from Flask
app = Flask(__name__)

# Configure MySQL
conn = pymysql.connect(host='localhost',
					   user='root',
					   password='',
					   db='air_ticket_reservation_system',
					   charset='utf8mb4',
					   cursorclass=pymysql.cursors.DictCursor)


@app.route('/')
def index():
	return render_template('index.html')


@app.route('/customer_login')
def login_customer():
	return render_template('customer_login.html')


@app.route('/customerLoginAuth', methods=['POST'])
def cust_loginAuth():
	username = request.form['email']
	password = request.form['password']
	hashed_password = hashlib.md5(password.encode()).hexdigest()
	cursor = conn.cursor()
	query = "SELECT * FROM customer WHERE email = %s AND password = %s"
	cursor.execute(query, (username, hashed_password))
	data = cursor.fetchone()
	error = None
	cursor.close()
	if (data):
		session['username'] = username
		return redirect(url_for('customer_home'))
	else:
		error = 'Invalid login or username'
		return render_template('customer_login.html', error=error)


# -- STAFF --
#Define route for login
@app.route('/staff_login')
def staff_login():
	return render_template('staff_login.html')

#Authenticates the login
@app.route('/staffLoginAuth', methods=['POST'])
def staffLoginAuth():
	username = request.form['username']
	password = request.form['password']
	hashed_password = hashlib.md5(password.encode()).hexdigest()
	cursor = conn.cursor()
	query = "SELECT * FROM staff WHERE username = %s AND password = %s"
	cursor.execute(query, (username, hashed_password))
	data = cursor.fetchone()
	cursor.close()
	error = None
	if (data):
		session['username'] = username
		return render_template('home_staff.html', error=error)
	else:
		error = 'Invalid login or username'
		return render_template('staff_login.html', error=error)


#Define route for register
@app.route('/staff_register')
def staff_register():
	return render_template('staff_register.html')




@app.route('/register_customer')
def register_customer():
	return render_template('register_customer.html')


#Define route for register
@app.route('/customer_register')
def customer_register():
	return render_template('customer_register.html')

#Authenticates the register
@app.route('/customerRegisterAuth', methods=['POST'])
def custRegisterAuth():
	username = request.form['email']
	password = request.form['password']

	# checks that password reaches required length
	if len(password) < 8:
		return render_template('customer_register.html', error="Password must be at least 8 characters long.")
	
	cursor = conn.cursor()
	query = 'SELECT * FROM customer WHERE email = %s'
	cursor.execute(query, (username))
	data = cursor.fetchone()
	error = None
	if (data):
		error = "This user already exists"
		return render_template('customer_register.html', error=error)
	else:
		ins = "INSERT INTO customer (email, first_name, last_name, password, building_num, street, apartment_num, city, state, zip_code, primary_phone_number, passport_number, passport_expiration_date, passport_country, date_of_birth) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
		hashed_password = hashlib.md5(request.form['password'].encode()).hexdigest()
		cursor.execute(ins, (request.form['email'], request.form['first_name'], request.form['last_name'],
							 hashed_password, request.form['building_num'], request.form['street'],
							 request.form['apartment_num'], request.form['city'], request.form['state'],
							 request.form['zip_code'], request.form['primary_phone_number'],
							 request.form['passport_number'], request.form['passport_expiration_date'],
							 request.form['passport_country'], request.form['date_of_birth']))
		conn.commit()
		ins2='INSERT INTO customer_phone_numbers (email, phone_number) VALUES (%s,%s)'
		cursor.execute(ins2,(request.form['email'],request.form['primary_phone_number']))
		conn.commit()
		cursor.close()
		return render_template('index.html')


#Authenticates the register
@app.route('/staffRegisterAuth', methods=['POST'])

def staffRegisterAuth():
	username = request.form['username']
	airline_name = request.form['airline_name']
	password = request.form['password']

	# checks that password reaches required length
	if len(password) < 8:
		return render_template('staff_register.html', error="Password must be at least 8 characters long.")

	cursor = conn.cursor()

	# checks if airline exists in database
	airlineCheck = 'SELECT * FROM airline WHERE name = %s'
	cursor.execute(airlineCheck, (airline_name))
	exists = cursor.fetchall()

	if (not exists):
		error = "The airline you have entered does not exist"
		return render_template('staff_register.html', error=error)
	
	query = 'SELECT * FROM staff WHERE username = %s'
	cursor.execute(query, (username))
	data = cursor.fetchone()
	error = None
	if (data):
		error = "This user already exists"
		return render_template('staff_register.html', error=error)
	else:
		ins = "INSERT INTO staff (username, password, first_name, last_name, date_of_birth, primary_email, airline_name) VALUES (%s, %s, %s, %s, %s, %s, %s)"
		hashed_password = hashlib.md5(request.form['password'].encode()).hexdigest()
		cursor.execute(ins, (request.form['username'], hashed_password, request.form['first_name'],
							 request.form['last_name'], request.form['date_of_birth'],
							 request.form['primary_email'], request.form['airline_name']))
		conn.commit()
		cursor.close()
		return render_template('index.html')
	
# -- GUEST -- 
@app.route('/guest')
def guest():
	return render_template('guest.html')

@app.route('/guestView', methods=['GET', 'POST'])
def guestView():
	cursor = conn.cursor()
	params = request.form
	error = None

	query = 'SELECT f.airline_name, f.flight_num, f.departure_date, f.departure_time, f.arrival_date, f.arrival_time, f.status, f.departure_airport, f.arrival_airport, dep.city as departure_city, arr.city as arrival_city FROM Flight f JOIN Airport dep ON f.departure_airport = dep.code JOIN Airport arr ON f.arrival_airport = arr.code where status != \'cancelled\' AND ( departure_date > current_date OR ( departure_date = current_date AND departure_time > current_time ) )' 

	queries = []

	if 'source_city' in params and params['source_city']:
		query += ' AND dep.city = %s'
		queries.append(params['source_city'])
	if 'destination_city' in params and params['destination_city']:
		query += ' AND arr.city = %s'
		queries.append(params['destination_city'])
	if 'source_airport' in params and params['source_airport']:
		query += ' AND f.departure_airport = %s'
		queries.append(params['source_airport'])
	if 'destination_airport' in params and params['destination_airport']:
		query += ' AND f.arrival_airport = %s'
		queries.append(params['destination_airport'])
	if 'departure_date' in params and params['departure_date']:
		query += ' AND f.departure_date = %s'
		queries.append(params['departure_date'])

	cursor.execute(query, queries)
	data = cursor.fetchall()

	if not data:
		error = "There are no flights matching these parameters. Please try again"
		return render_template('guest.html', error=error)

	return_data = None

	if 'return_date' in params:
		return_query = 'SELECT f.airline_name, f.flight_num, f.departure_date, f.departure_time, f.arrival_date, f.arrival_time, f.status, f.departure_airport, f.arrival_airport, dep.city as departure_city, arr.city as arrival_city FROM Flight f JOIN Airport dep ON f.departure_airport = dep.code JOIN Airport arr ON f.arrival_airport = arr.code where status != \'cancelled\' AND ( departure_date > current_date OR ( departure_date = current_date AND departure_time > current_time ) )' 

		return_queries = []

		if 'source_city' in params and params['source_city']:
			return_query += ' AND arr.city = %s'
			return_queries.append(params['source_city'])
		if 'destination_city' in params and params['destination_city']:
			return_query += ' AND dep.city = %s'
			return_queries.append(params['destination_city'])
		if 'source_airport' in params and params['source_airport']:
			return_query += ' AND f.arrival_airport = %s'
			return_queries.append(params['source_airport'])
		if 'destination_airport' in params and params['destination_airport']:
			return_query += ' AND f.departure_airport = %s'
			return_queries.append(params['destination_airport'])
		
		# condition for return flight
		return_query += ' AND f.departure_date = %s'
		return_queries.append(params['return_date'])

		cursor.execute(return_query, return_queries)
		return_data = cursor.fetchall()
		print(return_query, return_data)
	cursor.close()
	return render_template('guest.html', results=data, ret=return_data)


@app.route('/customer_home')
def customer_home():
	username = session['username']
	cursor = conn.cursor();
	customer = 'SELECT first_name from customer where email=%s'
	cursor.execute(customer, (username))
	customerData = cursor.fetchone()
	query = 'SELECT ticket_id, airline_name, flight_num, departure_date, departure_time, arrival_date, arrival_time, status, ' \
			'airplane_id, departure_airport, arrival_airport, sold_price, first_name, last_name' \
			' FROM flight NATURAL JOIN ticket NATURAL JOIN purchase' \
			' WHERE email=%s'
	cursor.execute(query, username)
	data = cursor.fetchall()
	cursor.close()
	return render_template('customer_home.html', username=customerData['first_name'], flights=data)

@app.route('/home_staff')
def home_staff():
	username = session['username']
	cursor = conn.cursor();
	query = 'SELECT first_name from staff where username = %s'
	cursor.execute(query, username)
	data = cursor.fetchall()
	cursor.close()
	return render_template('customer_home.html', username=username, flights=data)


@app.route('/cust_add_num', methods=['POST'])
def cust_add_num():
	username = session['username']
	number = request.form['phonenumber']
	cursor = conn.cursor()
	query = 'SELECT * FROM customer_phone_numbers WHERE email=%s AND phone_number=%s'
	cursor.execute(query, (username, number))
	data = cursor.fetchone()
	phone_error = None
	flights = 'SELECT ticket_id, airline_name, flight_num, departure_date, departure_time, arrival_date, arrival_time, status, ' \
			  'airplane_id, departure_airport, arrival_airport, sold_price, first_name, last_name' \
			  ' FROM flight NATURAL JOIN ticket NATURAL JOIN purchase' \
			  ' WHERE email=%s'
	cursor.execute(flights, username)
	flightdata = cursor.fetchall()
	if (data):
		phone_error = "This number already exists"
		return render_template('customer_home.html', phone_error=phone_error, username=username, flights=flightdata)
	else:
		ins = "INSERT INTO customer_phone_numbers (email, phone_number) VALUES (%s, %s)"
		cursor.execute(ins, (username, number))
		conn.commit()
		cursor.close()
		return render_template('customer_home.html', username=username, flights=flightdata)


@app.route('/cancel_flight', methods=['POST'])
def cancel_flight():
	username = session['username']
	ticket_id = request.form['ticket_id']
	cursor = conn.cursor()
	query = 'SELECT email FROM purchase WHERE email=%s AND ticket_id=%s'
	cursor.execute(query, (username, ticket_id))
	data = cursor.fetchone()
	cancel_error = None
	flights = 'SELECT ticket_id, airline_name, flight_num, departure_date, departure_time, arrival_date, arrival_time, status, ' \
			  'airplane_id, departure_airport, arrival_airport, sold_price, first_name, last_name' \
			  ' FROM flight NATURAL JOIN ticket NATURAL JOIN purchase' \
			  ' WHERE email=%s ORDER BY departure_date DESC'
	cursor.execute(flights, username)
	flightdata = cursor.fetchall()
	if (data):
		time_query = 'SELECT departure_date, departure_time FROM ticket WHERE ticket_id=%s'
		cursor.execute(time_query, ticket_id)
		timedata = cursor.fetchone()
		date = timedata['departure_date']
		time = (datetime.min + timedata['departure_time']).time()

		print(type(date), type(time))
		print(time)
		departure_date_time = datetime.combine(date, time)
		now = datetime.now()
		if ((departure_date_time - now) > timedelta(hours=24)):
			update = "UPDATE Ticket SET sold_price = NULL, first_name = NULL,last_name = NULL, date_of_birth = NULL" \
					 "WHERE ticket_id=%s"
			cursor.execute(update, ticket_id)
			conn.commit()
			cursor.close()
		else:
			cancel_error = "Flight is Within 24 Hours, Cannot be Canceled"
			return render_template('customer_home.html', cancel_error=cancel_error, username=username,
								   flights=flightdata)
	else:
		cancel_error = "Ticket Does Not Exist or You do Not Own This Ticket"
		return render_template('customer_home.html', cancel_error=cancel_error, username=username, flights=flightdata)


@app.route('/spending', methods=['GET', 'POST'])
def spending():
	username = session['username']
	query = "SELECT SUM(sold_price) AS total_spending FROM purchase NATURAL JOIN ticket " \
			"WHERE email = %s AND purchase_date BETWEEN DATE_FORMAT(CURDATE() - INTERVAL 5 MONTH, '%%Y-%%m-01') AND CURDATE()"
	cursor = conn.cursor()
	cursor.execute(query, username)
	data = cursor.fetchone()
	monthly = "SELECT DATE_FORMAT(purchase_date, '%%Y-%%m') AS month, SUM(sold_price) AS month_spending " \
			  "FROM purchase NATURAL JOIN ticket " \
			  "WHERE email = %s AND purchase_date " \
			  "BETWEEN DATE_FORMAT(CURDATE() - INTERVAL 5 MONTH, '%%Y-%%m-01') AND CURDATE() " \
			  "GROUP BY month ORDER BY month ASC"
	cursor.execute(monthly, username)
	monthlydata = cursor.fetchall()
	cursor.close()
	months = [(datetime.today().replace(day=1) - timedelta(days=30 * i)).strftime('%Y-%m') for i in range(6)][::-1]
	spending_data = {d['month']: d['month_spending'] for d in monthlydata}
	results = [{'month': month, 'month_spending': spending_data.get(month, 0)} for month in months]
	if (data['total_spending'] != None):
		return render_template('spending.html', total_spending=data['total_spending'], monthly=results)
	else:
		return render_template('spending.html', total_spending=0, monthly=results)


@app.route('/specific_spending', methods=['GET', 'POST'])
def specific_spending():
	username = session['username']
	start=request.form['start']
	end=request.form['end']
	specific = None
	query = "SELECT SUM(sold_price) AS total_spending FROM purchase NATURAL JOIN ticket " \
			"WHERE email = %s AND purchase_date BETWEEN %s AND %s"
	cursor = conn.cursor()
	cursor.execute(query, (username,start,end))
	data = cursor.fetchone()
	monthly = "SELECT DATE_FORMAT(purchase_date, '%%Y-%%m') AS month, SUM(sold_price) AS month_spending " \
			  "FROM purchase NATURAL JOIN ticket " \
			  "WHERE email = %s AND purchase_date " \
			  "BETWEEN %s AND %s " \
			  "GROUP BY month ORDER BY month ASC"
	cursor.execute(monthly, (username, start, end))
	monthlydata = cursor.fetchall()
	cursor.close()
	start_date = datetime.strptime(start, '%Y-%m-%d')
	end_date = datetime.strptime(end, '%Y-%m-%d')
	error=None
	if(end_date<start_date):
		error="Invalid Start and End Date"
		return render_template('spending.html', error=error)
	num_months = (end_date.year - start_date.year) * 12 + end_date.month - start_date.month + 1
	months = [(start_date + timedelta(days=30 * i)).strftime('%Y-%m') for i in range(num_months)]
	spending_data = {d['month']: d['month_spending'] for d in monthlydata}
	results = [{'month': month, 'month_spending': spending_data.get(month, 0)} for month in months]
	if start is None and end is None:
		specific = False
	else:
		specific = True
	if (data['total_spending'] != None):
		return render_template('spending.html',total_spending=data['total_spending'],start=start,end=end,monthly=results, error=error, specific=specific)
	else:
		return render_template('spending.html',total_spending=0,start=start,end=end,monthly=results, error=error, specific=specific)


@app.route('/logout')
def logout():
	session.pop('username')
	return redirect('/')


app.secret_key = 'some key that you will never guess'
# Run the app on localhost port 5000
# debug = True -> you don't have to restart flask
# for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug=True)