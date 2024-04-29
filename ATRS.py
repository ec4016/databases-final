# Import Flask Library
import hashlib

from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors

# Initialize the app from Flask
app = Flask(__name__)

# Configure MySQL
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
                       db='air ticket reservation system',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login_customer')
def login_customer():
    return render_template('login_customer.html')


@app.route('/cust_loginAuth', methods=['POST'])
def cust_loginAuth():
    username = request.form['username']
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
        return redirect(url_for('home_customer'))
    else:
        error = 'Invalid login or username'
        return render_template('login_customer.html', error=error)


@app.route('/login_staff')
def login_staff():
    return render_template('login_staff.html')


@app.route('/staff_loginAuth', methods=['POST'])
def staff_loginAuth():
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
        return redirect(url_for('home_staff'))
    else:
        error = 'Invalid login or username'
        return render_template('login_staff.html', error=error)


@app.route('/register_customer')
def register_customer():
    return render_template('register_customer.html')


@app.route('/cust_registerAuth', methods=['POST'])
def cust_registerAuth():
    username = request.form['username']
    cursor = conn.cursor()
    query = 'SELECT * FROM customer WHERE email = %s'
    cursor.execute(query, (username))
    data = cursor.fetchone()
    error = None
    if (data):
        error = "This user already exists"
        return render_template('register_customer.html', error=error)
    else:
        ins = """INSERT INTO customer (email, first_name, last_name, password, building_num, 
                                 street, apartment_num, city, state, zip_code, primary_phone_number, passport_number, 
                                 passport_expiration_date, passport_country, date_of_birth)
                                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        hashed_password = hashlib.md5(request.form['password'].encode()).hexdigest()
        cursor.execute(ins, (request.form['username'], request.form['first_name'], request.form['last_name'],
                             hashed_password, request.form['building_num'], request.form['street'],
                             request.form['apartment_num'], request.form['city'], request.form['state'],
                             request.form['zip_code'], request.form['primary_phone_number'],
                             request.form['passport_number'], request.form['passport_expiration_date'],
                             request.form['passport_country'], request.form['date_of_birth']))
        conn.commit()
        ins2='INSERT INTO customer_phone_numbers (email, phone_number) VALUES (%s,%s)'
        cursor.execute(ins2,(request.form['username'],request.form['primary_phone_number']))
        conn.commit()
        cursor.close()
        return render_template('index.html')


@app.route('/register_staff')
def register_staff():
    return render_template('register_staff.html')


@app.route('/staff_registerAuth', methods=['POST'])
def staff_registerAuth():
    username = request.form['username']
    cursor = conn.cursor()
    query = 'SELECT * FROM staff WHERE username = %s'
    cursor.execute(query, (username))
    data = cursor.fetchone()
    error = None
    if (data):
        error = "This user already exists"
        return render_template('register_staff.html', error=error)
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

@app.route('/home_customer')
def home_customer():
    username = session['username']
    return render_template('home_customer.html', username=username)

@app.route('/cust_add_num',methods=['POST'])
def cust_add_num():
    username = session['username']
    number = request.form['phonenumber']
    cursor = conn.cursor();
    query = 'SELECT * FROM customer_phone_numbers WHERE email=%s AND phone_number=%s'
    cursor.execute(query, (username,number))
    data = cursor.fetchone()
    error = None
    if(data):
        error = "This number already exists"
        return render_template('home_customer.html', error=error)
    else:
        ins="INSERT INTO customer_phone_numbers (email, phone_number) VALUES (%s, %s)"
        cursor.execute(ins, (username,number))
        conn.commit()
        cursor.close()
        return render_template('home_customer.html')

@app.route('/customer_flights')
def customer_flights():
    username=session['username']
    cursor = conn.cursor();
    query='SELECT airline_name, flight_num, departure_date, departure_time, arrival_date, arrival_time, status, ' \
          'airplane_id, departure_airport, arrival_airport, sold_price, first_name, last_name'\
          ' FROM flight NATURAL JOIN ticket NATURAL JOIN purchase' \
          ' WHERE email=%s'
    cursor.execute(query, username)
    data = cursor.fetchall()
    cursor.close()
    return render_template('customer_flights.html',flights=data)


@app.route('/staff_view_flights')
def staff_view_flights():
    username = session['username']
    cursor = conn.cursor()
    query='SELECT flight_num, departure_date, departure_time, arrival_date, arrival_time, status, ' \
          'airplane_id, departure_airport, arrival_airport'\
          ' FROM flight NATURAL JOIN ticket NATURAL JOIN purchase' \
          ' WHERE airline_name=%s'
    cursor.execute(query, username)
    data = cursor.fetchall()
    cursor.close()
    return render_template('staff_flights.html',flights=data)

@app.route('/staff_create_flights', methods=['POST'])
def staff_create_flights():
    print(request.form)
    airline_name = request.form.get('airline_name')
    flight_num = request.form.get('flight_num')
    departure_date = request.form.get('departure_date')
    departure_time = request.form.get('departure_time')
    arrival_date = request.form.get('arrival_date')
    arrival_time = request.form.get('arrival_time')
    base_price = request.form.get('base_price')
    status = request.form.get('status')
    ariplane_id = request.form.get('airplane_id')
    departure_airport = request.form.get('departure_airport')
    arrival_airport = request.form.get('arrival_airport')

    data = {
        'airline_name': airline_name,
        'flight_num' : flight_num,
        'departure_date': departure_date,
        'departure_time': departure_time,
        'arrival_date': arrival_date,
        'arrival_time': arrival_time,
        'base_price': base_price,
        'status': status,
        'airplane_id': airline_id,
        'departure_airport': departure_airport,
        'arrival_airport': arrival_airport
    }
    
    username = session['username']
    cursor = conn.cursor()

    error = None
    if(data):
        error = "This number already exists"
        return render_template('home_customer.html', error=error)
    else:
        ins="INSERT INTO customer_phone_numbers (email, phone_number) VALUES (%s, %s)"
        //cursor.execute(ins, (username,number))
        conn.commit()
        cursor.close()
        return render_template('staff_flights.html',flights=data)

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
