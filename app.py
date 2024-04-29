#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
import hashlib

#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='localhost',
					   user='root',
					   password='',
					   db='air_ticket_reservation_system', # database name
					   charset='utf8mb4',
					   cursorclass=pymysql.cursors.DictCursor)

#Define a route to hello function
@app.route('/')
def hello():
	return render_template('index.html')


# -- CUSTOMER --
#Define route for login
@app.route('/customer_login')
def customer_login():
	return render_template('customer_login.html')

#Authenticates the login
@app.route('/customerLoginAuth', methods=['POST'])
def custLoginAuth():
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
		return render_template('customer.html', error=error)
	else:
		error = 'Invalid login or username'
		return render_template('customer_login.html', error=error)


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
		ins = """INSERT INTO customer (email, first_name, last_name, password, building_num, 
								 street, apartment_num, city, state, zip_code, primary_phone_number, passport_number, 
								 passport_expiration_date, passport_country, date_of_birth)
								 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
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
		return render_template('staff.html', error=error)
	else:
		error = 'Invalid login or username'
		return render_template('staff_login.html', error=error)


#Define route for register
@app.route('/staff_register')
def staff_register():
	return render_template('staff_register.html')

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
		ins = """INSERT INTO staff (username, password, first_name, last_name, date_of_birth, 
						 primary_email, airline_name)
						 VALUES (%s, %s, %s, %s, %s, %s, %s)"""
		hashed_password = hashlib.md5(request.form['password'].encode()).hexdigest()
		cursor.execute(ins, (request.form['username'], hashed_password, request.form['first_name'],
							 request.form['last_name'], request.form['date_of_birth'],
							 request.form['primary_email'], request.form['airline_name']))
		conn.commit()
		cursor.close()
		return render_template('index.html')
	

# -- GUEST --
#Define route for guest
@app.route('/guest')
def guest():
	return render_template('guest.html')



@app.route('/home')
def home():
	
	username = session['username']
	cursor = conn.cursor();
	query = 'SELECT ts, blog_post FROM blog WHERE username = %s ORDER BY ts DESC'
	cursor.execute(query, (username))
	data1 = cursor.fetchall() 
	for each in data1:
		print(each['blog_post'])
	cursor.close()
	return render_template('home.html', username=username, posts=data1)

		

@app.route('/logout')
def logout():
	session.pop('username')
	return redirect('/')
		
app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)
