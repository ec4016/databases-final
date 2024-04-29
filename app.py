#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
from hashlib import md5

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

#Define route for login
#customer login
@app.route('/customer_login')
def customer_login():
	return render_template('customer_login.html')

#Define route for register
@app.route('/customer_register')
def customer_register():
	return render_template('customer_register.html')

#Define route for login
#staff login
@app.route('/staff_login')
def staff_login():
	return render_template('staff_login.html')

#Define route for register
@app.route('/staff_register')
def staff_register():
	return render_template('staff_register.html')

@app.route('/guest')
def guest():
	return render_template('guest.html')

# -- CUSTOMER --
#Authenticates the login
@app.route('/loginCustomerAuth', methods=['GET', 'POST'])
def loginAuth():
	#grabs information from the forms
	email = request.form['email']
	password = request.form['password']
	hashed_password = md5(password.encode()).hexdigest()

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM customer WHERE email = %s and password = %s'
	cursor.execute(query, (email, hashed_password))
	#stores the results in a variable
	print(hashed_password)
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	error = None
	if(data):
		#creates a session for the the user
		#session is a built in
		session['email'] = email
		return redirect(url_for('customer'))
	else:
		#returns an error message to the html page
		error = 'Invalid login or username'
		return render_template('customer_login.html', error=error)

#Authenticates the register
@app.route('/registerCustomerAuth', methods=['GET', 'POST'])
def registerAuth():
	#grabs information from the forms
	email = request.form['email']
	fname = request.form['fname']
	lname = request.form['lname']

	password = request.form['password']
	hashed_password = md5(password.encode()).hexdigest()

	building_num = request.form['building_num']
	street = request.form['street']
	apartment_num = request.form['apartment_num']
	city = request.form["city"]
	state = request.form["state"]
	zip_code = request.form["zip_code"]
	primary_phone_number = request.form["primary_phone_number"]
	passport_number = request.form["passport_number"]
	passport_expiration_date = request.form["passport_expiration_date"]
	passport_country = request.form["passport_country"]
	date_of_birth = request.form["date_of_birth"]

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM customer WHERE email = %s'
	cursor.execute(query, (email))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	error = None
	if(data):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('customer_register.html', error = error)
	else:
		ins = 'INSERT INTO user customer VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
		cursor.execute(ins, (email, fname, lname, hashed_password, building_num, street, apartment_num, city, state, zip_code, primary_phone_number, passport_number, passport_expiration_date, passport_country, date_of_birth))
		conn.commit()
		cursor.close()
		return render_template('index.html')
	
# -- STAFF --
#Authenticates the login
@app.route('/loginStaffAuth', methods=['GET', 'POST'])
def loginAuth():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']
	hashed_password = md5(password.encode()).hexdigest()

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM staff WHERE username = %s and password = %s'
	cursor.execute(query, (username, hashed_password))
	#stores the results in a variable
	print(hashed_password)
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	error = None
	if(data):
		#creates a session for the the user
		#session is a built in
		session['username'] = username
		return redirect(url_for('staff'))
	else:
		#returns an error message to the html page
		error = 'Invalid login or username'
		return render_template('staff_login.html', error=error)

#Authenticates the register
@app.route('/registerStaffAuth', methods=['GET', 'POST'])
def registerAuth():
	#grabs information from the forms
	username = request.form['username']
	airline_name = request.form['airline_name']

	password = request.form['password']
	hashed_password = md5(password.encode()).hexdigest()

	first_name = request.form['first_name']
	last_name = request.form['strelast_nameet']
	apartment_num = request.form['apartment_num']
	date_of_birth = request.form["date_of_birth"]
	primary_email = request.form["primary_email"]

	#cursor used to send queries
	cursor = conn.cursor()

	# checks to see if airline exists in the database
	airlineCheck = 'SELECT * FROM airline WHERE name = %s'
	cursor.execute(airlineCheck, (airline_name))
	exists = cursor.fetchall()

	if not exists:
		error = "The airline you have entered does not exist"
		return render_template('staff_register.html', error=error)

	#executes query
	query = 'SELECT * FROM staff WHERE email = %s'
	cursor.execute(query, (username))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	error = None
	if(data):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('staff_register.html', error = error)
	else:
		ins = 'INSERT INTO user customer VALUES(%s, %s, %s, %s, %s, %s, %s)'
		cursor.execute(ins, (username, airline_name, password, hashed_password, first_name, last_name, date_of_birth, primary_email))
		conn.commit()
		cursor.close()
		return render_template('index.html')

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

		
@app.route('/post', methods=['GET', 'POST'])
def post():
	username = session['username']
	cursor = conn.cursor();
	blog = request.form['blog']
	query = 'INSERT INTO blog (blog_post, username) VALUES(%s, %s)'
	cursor.execute(query, (blog, username))
	conn.commit()
	cursor.close()
	return redirect(url_for('home'))

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
