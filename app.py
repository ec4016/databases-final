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


# -- CUSTOMER --
#Define route for login
@app.route('/customer_login')
def login_customer():
    return render_template('customer_login.html')

#Authenticates the login
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


@app.route('/customer_home')
def customer_home():
    username = session['username']
    cursor = conn.cursor();
    customer = 'SELECT first_name from customer where email=%s'
    cursor.execute(customer, (username))
    customerData = cursor.fetchone()
    fname = customerData['first_name']

    query = 'SELECT ticket_id, airline_name, flight_num, departure_date, departure_time, arrival_date, arrival_time, status, ' \
            'airplane_id, departure_airport, arrival_airport, sold_price, first_name, last_name' \
            ' FROM flight NATURAL JOIN ticket NATURAL JOIN purchase' \
            ' WHERE email=%s'
    
    cursor.execute(query, username)
    data = cursor.fetchall()
    cursor.close()
    return render_template('customer_home.html', username=fname, flights=data)


@app.route('/cust_add_num', methods=['POST'])
def cust_add_num():
    username = session['username']
    number = request.form['phonenumber']
    cursor = conn.cursor()

    customer = 'SELECT first_name from customer where email=%s'
    cursor.execute(customer, (username))
    customerData = cursor.fetchone()
    fname = customerData['first_name']

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
        return render_template('customer_home.html', phone_error=phone_error, username=fname, flights=flightdata)
    else:
        ins = "INSERT INTO customer_phone_numbers (email, phone_number) VALUES (%s, %s)"
        cursor.execute(ins, (username, number))
        conn.commit()
        cursor.close()
        return render_template('customer_home.html', username=fname, flights=flightdata)
    
@app.route('/cancel_flight', methods=['POST'])
def cancel_flight():
    username = session['username']
    ticket_id = request.form['ticket_id']
    cursor = conn.cursor()

    customer = 'SELECT first_name from customer where email=%s'
    cursor.execute(customer, (username))
    customerData = cursor.fetchone()
    fname = customerData['first_name']

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
        return render_template('customer_home.html', cancel_error=cancel_error, username=fname, flights=flightdata)


@app.route('/flight_search')
def flight_search():
    username = session['username']
    cursor = conn.cursor()
    customer = 'SELECT first_name from customer where email=%s'
    cursor.execute(customer, (username))
    customerData = cursor.fetchone()
    fname = customerData['first_name']
    return render_template('flight_search.html', username=fname)

@app.route('/flightSearch', methods=['GET', 'POST'])
def flightSearch():
    username = session['username']
    cursor = conn.cursor()
    params = request.form
    error = None
    flightType = 'Future'

    customer = 'SELECT first_name from customer where email=%s'
    cursor.execute(customer, (username))
    customerData = cursor.fetchone()
    fname = customerData['first_name']

    query = 'SELECT F.*, departureAirport.city AS departure_city, departureAirport.name AS departure_airport_name, arrivalAirport.city AS arrival_city, arrivalAirport.name AS arrival_airport_name FROM Flight F JOIN Airport departureAirport ON F.departure_airport = departureAirport.code JOIN Airport arrivalAirport ON F.arrival_airport = arrivalAirport.code WHERE (F.departure_date > CURRENT_DATE OR (F.departure_date = CURRENT_DATE AND F.departure_time > CURRENT_TIME)) AND F.status <> \'Cancelled\'' 

    queries = []

    if 'departure_city' in params and params['departure_city']:
        query += ' AND departureAirport.city = %s'
        queries.append(params['departure_city'])
    if 'arrival_city' in params and params['arrival_city']:
        query += ' AND arrivalAirport.city = %s'
        queries.append(params['arrival_city'])
    if 'departure_airport' in params and params['departure_airport']:
        query += ' AND departureAirport.code = %s'
        queries.append(params['departure_airport'])
    if 'arrival_airport' in params and params['arrival_airport']:
        query += ' AND arrivalAirport.code = %s'
        queries.append(params['arrival_airport'])
    if 'departure_date' in params and params['departure_date']:
        query += ' AND F.departure_date = %s'
        queries.append(params['departure_date'])

    cursor.execute(query, queries)
    data = cursor.fetchall()

    if not data:
        error = "There are no flights matching these parameters. Please try again!"
        return render_template('flight_search.html', username=fname, flightType=flightType, error=error)
        
    cursor.close()
    return render_template('flight_search.html', username=fname, flightType=flightType, error=error, results=data)

@app.route('/returnFlightSearch', methods=['GET', 'POST'])
def returnFlightSearch():
    username = session['username']
    cursor = conn.cursor()
    params = request.form
    error = None
    returnError = None
    flightType = 'Future'

    customer = 'SELECT first_name from customer where email=%s'
    cursor.execute(customer, (username))
    customerData = cursor.fetchone()
    fname = customerData['first_name']

    query = 'SELECT F.*, departureAirport.city AS departure_city, departureAirport.name AS departure_airport_name, arrivalAirport.city AS arrival_city, arrivalAirport.name AS arrival_airport_name FROM Flight F JOIN Airport departureAirport ON F.departure_airport = departureAirport.code JOIN Airport arrivalAirport ON F.arrival_airport = arrivalAirport.code WHERE (F.departure_date > CURRENT_DATE OR (F.departure_date = CURRENT_DATE AND F.departure_time > CURRENT_TIME)) AND F.status <> \'Cancelled\'' 

    queries = []

    if 'departure_city' in params and params['departure_city']:
        query += ' AND departureAirport.city = %s'
        queries.append(params['departure_city'])
    if 'arrival_city' in params and params['arrival_city']:
        query += ' AND arrivalAirport.city = %s'
        queries.append(params['arrival_city'])
    if 'departure_airport' in params and params['departure_airport']:
        query += ' AND departureAirport.code = %s'
        queries.append(params['departure_airport'])
    if 'arrival_airport' in params and params['arrival_airport']:
        query += ' AND arrivalAirport.code = %s'
        queries.append(params['arrival_airport'])
    if 'departure_date' in params and params['departure_date']:
        query += ' AND F.departure_date = %s'
        queries.append(params['departure_date'])
    if 'return_date' in params and params['return_date']:
        flightType = 'Return'
        query += ' AND F.departure_date = %s'
        queries.append(params['return_date'])

    cursor.execute(query, queries)
    data = cursor.fetchall()

    if not data:
        returnError = "There are no return flights matching these parameters. Please try again!"
        flightType = 'Future'
        return render_template('flight_search.html', username=fname, flightType=flightType, returnError=returnError)
        
    cursor.close()
    return render_template('flight_search.html', username=fname, flightType=flightType, error=error, results=data)

# @app.route('/get_purchase', methods=['POST'])
# def get_purchase():
#     username = session['username']
#     airline = request.form['airline']
#     flight_num = request.form['flight_num']
#     departure_date = request.form['departure_date']
#     departure_time = request.form['departure_time']
#     query = "SELECT * FROM flight WHERE airline_name=%s AND flight_num=%s AND departure_date=%s " \
#             "AND TIME_FORMAT(departure_time, '%%H') = TIME_FORMAT(%s, '%%H')"
#     cursor = conn.cursor()
#     cursor.execute(query, (airline, flight_num, departure_date, departure_time))
#     exist = cursor.fetchone()
#     cursor.close()
#     flight_error = None
#     if (exist):
#         if (datetime.strptime(departure_date, '%Y-%m-%d') < datetime.today()):
#             flight_error = "The Flight is a Past Flight"
#             return render_template('flight_search.html', flight_error=flight_error)
#         else:
#             #print(exist)
#             exist['departure_time'] = int(exist['departure_time'].total_seconds())
#             exist['arrival_time'] = int(exist['arrival_time'].total_seconds())
#             session['flight'] = exist
#             return render_template('purchase.html',flight=exist)
#     else:
#         flight_error = "The Flight Does Not Exist"
#         return render_template('flight_search.html', flight_error=flight_error)

# @app.route('/purchase', methods=['GET', 'POST'])
# def purchase():
#     username = session['username']
#     flight = session['flight']
#     flight_num = flight['flight_num']
#     airline_name = flight['airline_name']
#     departure_date = datetime.strptime(flight['departure_date'], "%a, %d %b %Y %H:%M:%S %Z")
#     departure_date=departure_date.strftime("%Y-%m-%d")
#     departure_time = timedelta(seconds=flight['departure_time'])
#     airplane_id = flight['airplane_id']
#     first = request.form['first']
#     last = request.form['last']
#     birthday = request.form['birthday']
#     type = request.form['type']
#     card_fname = request.form['card_fname']
#     card_lname = request.form['card_lname']
#     card_num = request.form['card_num']
#     expiration = request.form['expiration']
#     cursor = conn.cursor()
#     find_ticket = 'SELECT ticket_id ' \
#                   'FROM ticket WHERE airline_name = %s ' \
#                   'AND flight_num = %s AND departure_date = %s ' \
#                   'AND departure_time = %s ' \
#                   'AND sold_price IS NULL ' \
#                   'AND first_name IS NULL ' \
#                   'AND last_name IS NULL ' \
#                   'AND date_of_birth IS NULL ' \
#                   'LIMIT 1'
#     cursor.execute(find_ticket, (airline_name, flight_num, departure_date, departure_time))
#     data = cursor.fetchone()
#     ticket_id = data['ticket_id']
#     ins = 'INSERT INTO purchase(email,ticket_id,card_type,card_num, ' \
#           'card_fname, card_lname, expiration_date, purchase_date, purchase_time)' \
#           'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)'
#     purchase_date = datetime.today()
#     time = current_time = datetime.now().time()
#     purchase_time = current_time.strftime('%H:%M:%S')
#     cursor.execute(ins, (username, ticket_id, type, card_num, card_fname, card_lname, expiration, purchase_date, purchase_time))
#     conn.commit()
#     price = 'SELECT base_price FROM flight WHERE airline_name = %s ' \
#             'AND flight_num = %s AND departure_date =%s AND departure_time = %s'
#     cursor.execute(price, (airline_name, flight_num, departure_date, departure_time))
#     data = cursor.fetchone()
#     base_price = data['base_price']
#     capacity = 'SELECT num_seats FROM airplane WHERE airline_name=%s AND airplane_id=%s'
#     cursor.execute(capacity, (airline_name, airplane_id))
#     data = cursor.fetchone()
#     max_passenger = data['num_seats']
#     seats_filled = 'SELECT COUNT(ticket_id) AS total_tickets ' \
#                    'FROM ticket WHERE sold_price IS NOT NULL AND first_name IS NOT NULL ' \
#                    'AND last_name IS NOT NULL AND date_of_birth IS NOT NULL AND airline_name IS NOT NULL ' \
#                    'AND departure_date IS NOT NULL AND departure_time IS NOT NULL'
#     cursor.execute(seats_filled)
#     data = cursor.fetchone()
#     passengers = data['total_tickets']
#     sold_price = base_price
#     if (passengers / max_passenger >= 0.8):
#         sold_price *= 1.25
#     update = 'UPDATE Ticket SET sold_price = %s, first_name = %s, last_name = %s,date_of_birth = %s ' \
#              'WHERE ticket_id = %s AND airline_name = %s AND flight_num = %s ' \
#              'AND departure_date = %s AND departure_time = %s'
#     cursor.execute(update, (
#         sold_price, first, last, birthday, ticket_id, airline_name, flight_num, departure_date, departure_time))
#     conn.commit()
#     return redirect(url_for('customer_home'))


@app.route('/rating', methods=['GET'])
def rating():
    username = session['username']
    cursor = conn.cursor()

    customer = 'SELECT first_name from customer where email=%s'
    cursor.execute(customer, (username))
    customerData = cursor.fetchone()
    fname = customerData['first_name']

    # flights the customer has taken
    query = 'SELECT F.airline_name, F.flight_num, F.departure_date, F.departure_time FROM Flight F JOIN Ticket T ON F.airline_name = T.airline_name AND F.flight_num = T.flight_num JOIN Purchase P ON T.ticket_id = P.ticket_id JOIN Customer C ON P.email = C.email WHERE C.email = %s AND (F.departure_date < CURRENT_DATE OR (F.departure_date = CURRENT_DATE AND F.departure_time < CURRENT_TIME))'
    
    cursor.execute(query, username)
    flights = cursor.fetchall()

    # flights that customer has taken and has been recorded in flight_taken table
    check_query = 'SELECT FT.airline_name, FT.flight_num, FT.departure_date, FT.departure_time FROM Flight_Taken FT JOIN Ticket T ON FT.airline_name = T.airline_name AND FT.flight_num = T.flight_num AND FT.departure_date = T.departure_date AND FT.departure_time = T.departure_time WHERE FT.email = %s'
    cursor.execute(check_query, (username))
    existing_flights = cursor.fetchall()

    for flight in flights:
        # Check if the flight is already in Flight_Taken
        if flight not in existing_flights:
            # If not, insert the flight into Flight_Taken
            insert_query = "INSERT INTO Flight_Taken (email, airline_name, flight_num, departure_date, departure_time, rating, comment) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(insert_query, (username, flight['airline_name'], flight['flight_num'], flight['departure_date'], flight['departure_time'], 'N/A', 'N/A'))
            conn.commit()

    printQuery = 'SELECT * FROM flight_taken WHERE email=%s'
    cursor.execute(printQuery, (username))
    flightTaken = cursor.fetchall()

    cursor.close()
    flight_error = None
    if (flightTaken):
        return render_template('rating.html', username=fname, flights=flightTaken)
    else:
        flight_error = "You Have Not Taken Any Flights"
        return render_template('rating.html', username=fname, flights=flights, flight_error=flight_error)


@app.route('/rate', methods=['POST'])
def rate():
    username = session['username']
    cursor = conn.cursor()

    customer = 'SELECT first_name from customer where email=%s'
    cursor.execute(customer, (username))
    customerData = cursor.fetchone()
    fname = customerData['first_name']

    airline = request.form['airline_name']
    flight_num = request.form['flight_num']
    date = request.form['departure_date']
    time = request.form['departure_time']
    rating = request.form['rating']
    comment = request.form['comment']

    find = "SELECT * FROM flight_taken WHERE airline_name=%s AND flight_num=%s " \
           "AND departure_date=%s AND TIME_FORMAT(departure_time, '%%H') = TIME_FORMAT(%s, '%%H') AND email=%s"
    cursor.execute(find, (airline, flight_num, date, time, username))
    exist = cursor.fetchall()

    rating_error = None
    msg = None

    if (exist):
        update = "UPDATE Flight_Taken SET rating = %s, comment = %s " \
                 "WHERE email = %s AND airline_name = %s " \
                 "AND flight_num = %s AND departure_date = %s " \
                 "AND TIME_FORMAT(departure_time, '%%H') = TIME_FORMAT(%s, '%%H')"
        cursor.execute(update, (rating, comment, username, airline, flight_num, date, time))

        query = 'SELECT * FROM flight_taken WHERE email=%s'
        cursor = conn.cursor()
        cursor.execute(query, username)
        flights = cursor.fetchall()

        msg="You've successfully updated the rating!"
        conn.commit()
        
    else:
        rating_error = "The Flight Does Not Exist or You Have Not Taken it"

    cursor.close()    
    return render_template('rating.html', username=fname, flights=flights, msg=msg, rating_error=rating_error)



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
        return render_template('staff_home.html', error=error)
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
    flightType = 'Future'

    query = 'SELECT F.*, departureAirport.city AS departure_city, departureAirport.name AS departure_airport_name, arrivalAirport.city AS arrival_city, arrivalAirport.name AS arrival_airport_name FROM Flight F JOIN Airport departureAirport ON F.departure_airport = departureAirport.code JOIN Airport arrivalAirport ON F.arrival_airport = arrivalAirport.code WHERE (F.departure_date > CURRENT_DATE OR (F.departure_date = CURRENT_DATE AND F.departure_time > CURRENT_TIME)) AND F.status <> \'Cancelled\'' 

    queries = []

    if 'departure_city' in params and params['departure_city']:
        query += ' AND departureAirport.city = %s'
        queries.append(params['departure_city'])
    if 'arrival_city' in params and params['arrival_city']:
        query += ' AND arrivalAirport.city = %s'
        queries.append(params['arrival_city'])
    if 'departure_airport' in params and params['departure_airport']:
        query += ' AND departureAirport.code = %s'
        queries.append(params['departure_airport'])
    if 'arrival_airport' in params and params['arrival_airport']:
        query += ' AND arrivalAirport.code = %s'
        queries.append(params['arrival_airport'])
    if 'departure_date' in params and params['departure_date']:
        query += ' AND F.departure_date = %s'
        queries.append(params['departure_date'])

    cursor.execute(query, queries)
    data = cursor.fetchall()

    if not data:
        error = "There are no flights matching these parameters. Please try again!"
        return render_template('guest.html', flightType=flightType, error=error)
        
    cursor.close()
    return render_template('guest.html', flightType=flightType, error=error, results=data)

@app.route('/guestReturnFlight', methods=['GET', 'POST'])
def guestReturnFlight():
    cursor = conn.cursor()
    params = request.form
    error = None
    returnError = None
    flightType = 'Future'

    query = 'SELECT F.*, departureAirport.city AS departure_city, departureAirport.name AS departure_airport_name, arrivalAirport.city AS arrival_city, arrivalAirport.name AS arrival_airport_name FROM Flight F JOIN Airport departureAirport ON F.departure_airport = departureAirport.code JOIN Airport arrivalAirport ON F.arrival_airport = arrivalAirport.code WHERE (F.departure_date > CURRENT_DATE OR (F.departure_date = CURRENT_DATE AND F.departure_time > CURRENT_TIME)) AND F.status <> \'Cancelled\'' 

    queries = []

    if 'departure_city' in params and params['departure_city']:
        query += ' AND departureAirport.city = %s'
        queries.append(params['departure_city'])
    if 'arrival_city' in params and params['arrival_city']:
        query += ' AND arrivalAirport.city = %s'
        queries.append(params['arrival_city'])
    if 'departure_airport' in params and params['departure_airport']:
        query += ' AND departureAirport.code = %s'
        queries.append(params['departure_airport'])
    if 'arrival_airport' in params and params['arrival_airport']:
        query += ' AND arrivalAirport.code = %s'
        queries.append(params['arrival_airport'])
    if 'departure_date' in params and params['departure_date']:
        query += ' AND F.departure_date = %s'
        queries.append(params['departure_date'])
    if 'return_date' in params and params['return_date']:
        flightType = 'Return'
        query += ' AND F.departure_date = %s'
        queries.append(params['return_date'])

    cursor.execute(query, queries)
    data = cursor.fetchall()

    if not data:
        returnError = "There are no return flights matching these parameters. Please try again!"
        flightType = 'Future'
        return render_template('guest.html', flightType=flightType, returnError=returnError)

    cursor.close()
    return render_template('guest.html', flightType=flightType, error=error, results=data)


@app.route('/flight_status')
def flight_status():
    return render_template('flight_status.html')

@app.route('/flightStatus', methods=['GET', 'POST'])
def flightStatus():
    cursor = conn.cursor()
    params = request.form
    error = None

    query = 'SELECT F.*, departureAirport.city AS departure_city, departureAirport.name AS departure_airport_name, arrivalAirport.city AS arrival_city, arrivalAirport.name AS arrival_airport_name FROM Flight F JOIN Airline flightAirline ON F.airline_name = flightAirline.name JOIN Airport departureAirport ON F.departure_airport = departureAirport.code JOIN Airport arrivalAirport ON F.arrival_airport = arrivalAirport.code WHERE (F.departure_date > CURRENT_DATE OR (F.departure_date = CURRENT_DATE AND F.departure_time > CURRENT_TIME)) AND F.status <> \'Cancelled\'' 

    queries = []

    if 'airline_name' in params and params['airline_name']:
        query += ' AND F.airline_name = %s'
        queries.append(params['airline_name'])
    if 'flight_num' in params and params['flight_num']:
        query += ' AND F.flight_num = %s'
        queries.append(params['flight_num'])
    if 'arrival_date' in params and params['arrival_date']:
        query += ' AND F.arrival_date = %s'
        queries.append(params['arrival_date'])
    if 'departure_date' in params and params['departure_date']:
        query += ' AND F.departure_date = %s'
        queries.append(params['departure_date'])

    cursor.execute(query, queries)
    data = cursor.fetchall()

    if not data:
        error = "There are no flights matching these parameters. Please try again!"
        return render_template('flight_status.html', error=error)
        
    cursor.close()
    return render_template('flight_status.html', error=error, results=data)


@app.route('/home_staff')
def home_staff():
    username = session['username']
    cursor = conn.cursor();
    query = 'SELECT first_name from staff where username = %s'
    cursor.execute(query, username)
    data = cursor.fetchall()
    cursor.close()
    return render_template('customer_home.html', username=username, flights=data)



@app.route('/staffView', methods=['GET', 'POST'])
def stafftView():
	cursor = conn.cursor()
	params = request.form
	error = None
	flightType = 'Future'

	query = """SELECT F.*, departureAirport.city AS departure_city, departureAirport.name AS departure_airport_name, arrivalAirport.city AS arrival_city, arrivalAirport.name AS arrival_airport_name
			FROM Flight
				F JOIN Airport departureAirport
				ON F.departure_airport = departureAirport.code
				JOIN Airport arrivalAirport
				ON F.arrival_airport = arrivalAirport.code
			WHERE (F.departure_date > CURRENT_DATE 
			OR (F.departure_date = CURRENT_DATE AND F.departure_time > CURRENT_TIME)) 
			AND F.status <> \'Cancelled\'"""

	queries = []

	if 'departure_city' in params and params['departure_city']:
		query += ' AND departureAirport.city = %s'
		queries.append(params['departure_city'])
	if 'arrival_city' in params and params['arrival_city']:
		query += ' AND arrivalAirport.city = %s'
		queries.append(params['arrival_city'])
	if 'departure_airport' in params and params['departure_airport']:
		query += ' AND departureAirport.code = %s'
		queries.append(params['departure_airport'])
	if 'arrival_airport' in params and params['arrival_airport']:
		query += ' AND arrivalAirport.code = %s'
		queries.append(params['arrival_airport'])
	if 'departure_date' in params and params['departure_date']:
		query += ' AND F.departure_date = %s'
		queries.append(params['departure_date'])

	cursor.execute(query, queries)
	data = cursor.fetchall()

	if not data:
		error = "There are no flights matching these parameters. Please try again!"
		return render_template('guest.html', flightType=flightType, error=error)
		
	cursor.close()
	return render_template('guest.html', flightType=flightType, error=error, results=data)




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