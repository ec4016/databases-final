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
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        building = request.form['building_num']
        street = request.form['street']
        apartment = request.form['apartment_num']
        city = request.form['city']
        state = request.form['state']
        zipcode = request.form['zip_code']
        phonenumber = request.form['primary_phone_number']
        passport_num = request.form['passport_number']
        passport_date = request.form['passport_expiration_date']
        passport_country = request.form['passport_country']
        birthday = request.form['date_of_birth']
        cursor.execute(ins, (username, first_name, last_name, hashed_password, building, street, apartment, city, state,
                             zipcode, phonenumber, passport_num, passport_date, passport_country, birthday))
        conn.commit()
        ins2 = 'INSERT INTO customer_phone_numbers (email, phone_number) VALUES (%s,%s)'
        cursor.execute(ins2, (username, phonenumber))
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
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        birthday = request.form['date_of_birth']
        email = request.form['primary_email']
        airline = request.form['airline_name']
        hashed_password = hashlib.md5(request.form['password'].encode()).hexdigest()
        cursor.execute(ins, (username, hashed_password, first_name, last_name, birthday, email, airline))
        conn.commit()
        ins2 = "INSERT INTO staff_email (username, email) VALUES(%s,%s)"
        cursor.execute(ins2, username, email)
        conn.commit()
        cursor.close()
        return render_template('index.html')


@app.route('/home_customer')
def home_customer():
    username = session['username']
    cursor = conn.cursor();
    query = 'SELECT ticket_id, airline_name, flight_num, departure_date, departure_time, arrival_date, arrival_time, status, ' \
            'airplane_id, departure_airport, arrival_airport, sold_price, first_name, last_name' \
            ' FROM flight NATURAL JOIN ticket NATURAL JOIN purchase' \
            ' WHERE email=%s'
    cursor.execute(query, username)
    data = cursor.fetchall()
    cursor.close()
    return render_template('home_customer.html', username=username, flights=data)


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
        return render_template('home_customer.html', phone_error=phone_error, username=username, flights=flightdata)
    else:
        ins = "INSERT INTO customer_phone_numbers (email, phone_number) VALUES (%s, %s)"
        cursor.execute(ins, (username, number))
        conn.commit()
        cursor.close()
        return render_template('home_customer.html', username=username, flights=flightdata)


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
            return render_template('home_customer.html', cancel_error=cancel_error, username=username,
                                   flights=flightdata)
    else:
        cancel_error = "Ticket Does Not Exist or You do Not Own This Ticket"
        return render_template('home_customer.html', cancel_error=cancel_error, username=username, flights=flightdata)


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
    start = request.form['start']
    end = request.form['end']
    query = "SELECT SUM(sold_price) AS total_spending FROM purchase NATURAL JOIN ticket " \
            "WHERE email = %s AND purchase_date BETWEEN %s AND %s"
    cursor = conn.cursor()
    cursor.execute(query, (username, start, end))
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
    error = None
    if (end_date < start_date):
        error = "Invalid Start and End Date"
        return render_template('specific_spending.html', error=error)
    num_months = (end_date.year - start_date.year) * 12 + end_date.month - start_date.month + 1
    months = [(start_date + timedelta(days=30 * i)).strftime('%Y-%m') for i in range(num_months)]
    spending_data = {d['month']: d['month_spending'] for d in monthlydata}
    results = [{'month': month, 'month_spending': spending_data.get(month, 0)} for month in months]
    if (data['total_spending'] != None):
        return render_template('specific_spending.html', total_spending=data['total_spending'], start=start, end=end,
                               monthly=results)
    else:
        return render_template('specific_spending.html', total_spending=0, start=start, end=end, monthly=results)


@app.route('/rating', methods=['GET'])
def rating():
    username = session['username']
    query = 'SELECT * FROM flight_taken WHERE email=%s'
    cursor = conn.cursor()
    cursor.execute(query, username)
    flights = cursor.fetchall()
    cursor.close()
    flight_error = None
    if (flights):
        return render_template('rating.html', flights=flights)
    else:
        flight_error = "You Have Not Taken Any Flights"
        return render_template('rating.html', flight_error=flight_error)


@app.route('/rate', methods=['POST'])
def rate():
    username = session['username']
    cursor = conn.cursor()
    airline = request.form['airline_name']
    flight_num = request.form['flight_num']
    date = request.form['departure_date']
    time = request.form['departure_time']
    print(time)
    rating = request.form['rating']
    comment = request.form['comment']
    find = "SELECT * FROM flight_taken WHERE airline_name=%s AND flight_num=%s " \
           "AND departure_date=%s AND TIME_FORMAT(departure_time, '%%H') = TIME_FORMAT(%s, '%%H') AND email=%s"
    cursor.execute(find, (airline, flight_num, date, time, username))
    exist = cursor.fetchone()
    print(exist)
    rating_error = None
    query = 'SELECT * FROM flight_taken WHERE email=%s'
    cursor = conn.cursor()
    cursor.execute(query, username)
    flights = cursor.fetchall()
    if (exist):
        update = "UPDATE Flight_Taken SET rating = %s, comment = %s " \
                 "WHERE email = %s AND airline_name = %s " \
                 "AND flight_num = %s AND departure_date = %s " \
                 "AND TIME_FORMAT(departure_time, '%%H') = TIME_FORMAT(%s, '%%H')"
        cursor.execute(update, (rating, comment, username, airline, flight_num, date, time))
        conn.commit()
        cursor.close()
        return redirect(url_for('rating'))
    else:
        cursor.close()
        rating_error = "The Flight Does Not Exist or You Have Not Taken it"
        return render_template('rating.html', flights=flights, rating_error=rating_error)


@app.route('/search')
def search():
    return render_template('flight_search.html')


@app.route('/flight_search', methods=['GET', 'POST'])
def flight_search():
    cursor = conn.cursor()
    params = request.form
    error = None

    query = 'SELECT f.airline_name, f.flight_num, f.departure_date, f.departure_time, ' \
            'f.arrival_date, f.arrival_time, f.status, f.departure_airport, f.arrival_airport, ' \
            'dep.city as departure_city, arr.city as arrival_city ' \
            'FROM Flight f JOIN Airport dep ON f.departure_airport = dep.code ' \
            'JOIN Airport arr ON f.arrival_airport = arr.code where status != \'cancelled\' ' \
            'AND ( departure_date > current_date OR ( departure_date = current_date AND departure_time > current_time ) )'

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
    # print(query)
    cursor.execute(query, queries)
    data = cursor.fetchall()

    if not data:
        error = "There are no flights matching these parameters. Please try again"
    return render_template('flight_search.html', error=error)

    return_data = None

    if 'return_date' in params:  # I assume a return date means the user wants to come back to the airport from which they departed
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

    # Add condition for return date
    return_query += ' AND f.departure_date = %s'
    return_queries.append(params['return_date'])

    # Execute the return query with parameters
    cursor.execute(return_query, return_queries)
    return_data = cursor.fetchall()
    print(return_query, return_data)
    cursor.close()
    # print(data)
    return render_template('flight_search.html', results=data, ret=return_data)


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
