# Import Flask Library
import hashlib, random
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
    cursor = conn.cursor()
    past="SELECT airline_name,flight_num,departure_date,departure_time " \
          "FROM ticket NATURAL JOIN purchase " \
          "WHERE email=%s AND departure_date<CURDATE()"
    cursor.execute(past, username)
    taken=cursor.fetchall()
    for line in taken:
        ins='INSERT IGNORE INTO flight_taken(email,airline_name,flight_num,departure_date,departure_time, rating, comment)' \
            'VALUES(%s,%s,%s,%s,%s,NULL,NULL)'
        airline=line['airline_name']
        flight_num=line['flight_num']
        departure_date = line['departure_date']
        departure_time = line['departure_time']
        cursor.execute(ins, (username,airline,flight_num,departure_date,departure_time))
        conn.commit()
    query = 'SELECT * FROM flight_taken WHERE email=%s'

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
    username = session['username']
    cursor = conn.cursor()
    customer = 'SELECT first_name from customer where email=%s'
    cursor.execute(customer, (username))
    customerData = cursor.fetchone()
    fname = customerData['first_name']
    return render_template('flight_search.html', username=fname)


@app.route('/flight_search', methods=['GET', 'POST'])
def flight_search():
    username = session['username']
    cursor = conn.cursor()
    params = request.form
    error = None

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
    if 'destination_airport' in params and params['destination_airport']:
        query += ' AND arrivalAirport.code = %s'
        queries.append(params['destination_airport'])
    if 'departure_date' in params and params['departure_date']:
        query += ' AND F.departure_date = %s'
        queries.append(params['departure_date'])

    cursor.execute(query, queries)
    data = cursor.fetchall()

    if not data:
        error = "There are no flights matching these parameters. Please try again"
        return render_template('flight_search.html', error=error)

    return_data = None

    if 'return_date' in params:
        return_query = 'SELECT F.*, departureAirport.city AS departure_city, departureAirport.name AS departure_airport_name, arrivalAirport.city AS arrival_city, arrivalAirport.name AS arrival_airport_name FROM Flight F JOIN Airport departureAirport ON F.departure_airport = departureAirport.code JOIN Airport arrivalAirport ON F.arrival_airport = arrivalAirport.code WHERE (F.departure_date > CURRENT_DATE OR (F.departure_date = CURRENT_DATE AND F.departure_time > CURRENT_TIME)) AND F.status <> \'Cancelled\''

        return_queries = []

        if 'departure_city' in params and params['departure_city']:
            return_query += ' AND arrivalAirport.city = %s'
            return_queries.append(params['departure_city'])
        if 'arrival_city' in params and params['arrival_city']:
            return_query += ' AND departureAirport.city = %s'
            return_queries.append(params['arrival_city'])
        if 'departure_airport' in params and params['departure_airport']:
            return_query += ' AND arrivalAirport.code = %s'
            return_queries.append(params['departure_airport'])
        if 'destination_airport' in params and params['destination_airport']:
            return_query += ' AND departureAirport.code = %s'
            return_queries.append(params['destination_airport'])

        # condition for return flight
        return_query += ' AND F.departure_date = %s'
        return_queries.append(params['return_date'])

        # condition for return flight
        return_query += ' AND f.departure_date = %s'
        return_queries.append(params['return_date'])

        cursor.execute(return_query, return_queries)
        return_data = cursor.fetchall()
        print(return_query, return_data)
    cursor.close()
    return render_template('flight_search.html', username=fname, results=data, ret=return_data)


@app.route('/get_purchase', methods=['POST'])
def get_purchase():
    username = session['username']
    airline = request.form['airline']
    flight_num = request.form['flight_num']
    departure_date = request.form['departure_date']
    departure_time = request.form['departure_time']
    query = "SELECT * FROM flight WHERE airline_name=%s AND flight_num=%s AND departure_date=%s " \
            "AND TIME_FORMAT(departure_time, '%%H') = TIME_FORMAT(%s, '%%H')"
    cursor = conn.cursor()
    cursor.execute(query, (airline, flight_num, departure_date, departure_time))
    exist = cursor.fetchone()
    cursor.close()
    flight_error = None
    if (exist):
        if (datetime.strptime(departure_date, '%Y-%m-%d') < datetime.today()):
            flight_error = "The Flight is a Past Flight"
            return render_template('flight_search.html', flight_error=flight_error)
        else:
            #print(exist)
            exist['departure_time'] = int(exist['departure_time'].total_seconds())
            exist['arrival_time'] = int(exist['arrival_time'].total_seconds())
            session['flight'] = exist
            return render_template('purchase.html',flight=exist)
    else:
        flight_error = "The Flight Does Not Exist"
        return render_template('flight_search.html', flight_error=flight_error)

@app.route('/purchase', methods=['GET', 'POST'])
def purchase():
    username = session['username']
    flight = session['flight']
    flight_num = flight['flight_num']
    airline_name = flight['airline_name']
    departure_date = datetime.strptime(flight['departure_date'], "%a, %d %b %Y %H:%M:%S %Z")
    departure_date=departure_date.strftime("%Y-%m-%d")
    departure_time = timedelta(seconds=flight['departure_time'])
    airplane_id = flight['airplane_id']
    first = request.form['first']
    last = request.form['last']
    birthday = request.form['birthday']
    type = request.form['type']
    card_fname = request.form['card_fname']
    card_lname = request.form['card_lname']
    card_num = request.form['card_num']
    expiration = request.form['expiration']
    cursor = conn.cursor()
    find_ticket = 'SELECT ticket_id ' \
                  'FROM ticket WHERE airline_name = %s ' \
                  'AND flight_num = %s AND departure_date = %s ' \
                  'AND departure_time = %s ' \
                  'AND sold_price IS NULL ' \
                  'AND first_name IS NULL ' \
                  'AND last_name IS NULL ' \
                  'AND date_of_birth IS NULL ' \
                  'LIMIT 1'
    cursor.execute(find_ticket, (airline_name, flight_num, departure_date, departure_time))
    data = cursor.fetchone()
    ticket_id = data['ticket_id']
    ins = 'INSERT INTO purchase(email,ticket_id,card_type,card_num, ' \
          'card_fname, card_lname, expiration_date, purchase_date, purchase_time)' \
          'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    purchase_date = datetime.today()
    time = current_time = datetime.now().time()
    purchase_time = current_time.strftime('%H:%M:%S')
    cursor.execute(ins, (username, ticket_id, type, card_num, card_fname, card_lname, expiration, purchase_date, purchase_time))
    conn.commit()
    price = 'SELECT base_price FROM flight WHERE airline_name = %s ' \
            'AND flight_num = %s AND departure_date =%s AND departure_time = %s'
    cursor.execute(price, (airline_name, flight_num, departure_date, departure_time))
    data = cursor.fetchone()
    base_price = data['base_price']
    capacity = 'SELECT num_seats FROM airplane WHERE airline_name=%s AND airplane_id=%s'
    cursor.execute(capacity, (airline_name, airplane_id))
    data = cursor.fetchone()
    max_passenger = data['num_seats']
    seats_filled = 'SELECT COUNT(ticket_id) AS total_tickets ' \
                   'FROM ticket WHERE sold_price IS NOT NULL AND first_name IS NOT NULL ' \
                   'AND last_name IS NOT NULL AND date_of_birth IS NOT NULL AND airline_name IS NOT NULL ' \
                   'AND departure_date IS NOT NULL AND departure_time IS NOT NULL'
    cursor.execute(seats_filled)
    data = cursor.fetchone()
    passengers = data['total_tickets']
    sold_price = base_price
    if (passengers / max_passenger >= 0.8):
        sold_price *= 1.25
    update = 'UPDATE Ticket SET sold_price = %s, first_name = %s, last_name = %s,date_of_birth = %s ' \
             'WHERE ticket_id = %s AND airline_name = %s AND flight_num = %s ' \
             'AND departure_date = %s AND departure_time = %s'
    cursor.execute(update, (
        sold_price, first, last, birthday, ticket_id, airline_name, flight_num, departure_date, departure_time))
    conn.commit()
    return redirect(url_for('home_customer'))

@app.route('/staff_view_flights')

def generate_tickets(capacity, airline_name, flight_num, departure_time):
    cursor = conn.cursor
    for i in range(capacity):
        ticket_id = random.randint(0, 1000000)
        ins="INSERT into Ticket (ticket_id, airline_name, flight_num, departure_date, sold_price, first_name, last_name, date_of_birth)"
        cursor.execute(ins, (ticket_id, airline_name, flight_num, departure_time, None, None, None, None, None))
        conn.commit()
    cursor.close()


@app.route('/staff_new_flight', methods=['POST'])
def staff_new_flight():
    print(request.form)
    airline_name = request.form.get('airline_name')
    flight_num = request.form.get('flight_num')
    departure_date = request.form.get('departure_date')
    departure_time = request.form.get('departure_time')
    arrival_date = request.form.get('arrival_date')
    arrival_time = request.form.get('arrival_time')
    base_price = request.form.get('base_price')
    status = request.form.get('status')
    airplane_id = request.form.get('airplane_id')
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
        'airplane_id': airplane_id,
        'departure_airport': departure_airport,
        'arrival_airport': arrival_airport
    }
    
    username = session['username']
    cursor = conn.cursor()

    error = None
    if(data):
        check1 = """SELECT country FROM Airport WHERE code = %(departure_airport)s"""
        check2 = """SELECT country FROM Airport WHERE code = %(arrival_airport)s"""
        cursor.execute(check1)
        result1 = cursor.fetchone()
        cursor.execute(check2)
        result2 = cursor.fetchone()

        if (result1["country"] == result2["country"]):
            ins="INSERT INTO flight (airline_name, flight_num, departure_date, departure_time, arrival_date, arrival_time, base_price, status, airplane_id, departure_airport, arrival_airport) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(ins, (airline_name, flight_num, departure_date, departure_time, arrival_date, arrival_time, base_price, status, airplane_id, departure_airport, arrival_airport))
            conn.commit()
            cursor.close()

            seats_query = """SELECT num_seats FROM Airplane WHERE airplane_id = %s"""
            cursor.execute(seats_query)
            seats_data = cursor.fetchone()
            num_seats = data["num_seats"]
            generate_tickets(num_seats)
    
    else:
        error = "Data inputted incorrectly."
        return render_template('staff_new_flight.html', error=error)


@app.route('/change_flight_status', methods=['GET'])
def change_flight_status():
    print(request.args)
    status = request.args.get('status')

    username = session['username']
    airline_name = request.form['airline_num']
    flight_num = request.form['flight_num']
    #departure_date = request.form['departure_date']
    #departure_time = request.form['departure_time']

    cursor = conn.cursor()
    query = 'SELECT flight_num FROM flight WHERE flight_num=%s'
    cursor.execute(query, (username, flight_num))
    data = cursor.fetchone()
    change_error = None
    
    #cursor.execute(flights, username)
    flightdata = cursor.fetchall()
    if (data):
        time_query = 'SELECT * FROM flight WHERE airline_name = %s AND flight_number = %s AND departure_date_time = %s'
        cursor.execute(time_query, flight_num)
        timedata = cursor.fetchone()
        date = timedata['departure_date']
        time = (datetime.min + timedata['departure_time']).time()

        print(type(date), type(time))
        print(time)
        departure_date_time = datetime.combine(date, time)
        now = datetime.now()
        if ((departure_date_time - now) > timedelta(hours=0)):
            update = """UPDATE Flight SET status=%s
                    WHERE flight_num=%s
                    AND flight_nim = %s
                    AND departure_date = %s
                    AND departure_time = %s"""
            cursor.execute(update, flight_num)
            conn.commit()
            cursor.close()
        else:
            change_error = "Flight has already taken off"
            return render_template('change_status.html', change_error=change_error, username=username,
                                   flights=flightdata)
    else:
        change_error = "Missing Field"
        return render_template('change_status.html', change_error=change_error, username=username, flights=flightdata)

@app.route('/staff_new_airplane', methods=['POST'])
def staff_new_airplane():
    print(request.form)
    airline_name = request.form.get('airline_name')
    airplane_id = request.form.get('airplane_id')
    num_seats = request.form.get('num_seats')
    manufacturer = request.form.get('manufacturer')
    model_number = request.form.get('model_number')
    manufacturing_date = request.form.get('manufacturing_date')
    age = request.form.get('age')

    data = {
        'airline_name': airline_name,
        'airplane_id': airplane_id,
        'num_seats': num_seats,
        'manufacturer': manufacturer,
        'model_number': model_number,
        'manufacturing_date': manufacturing_date,
        'age': age
    }

    username = session['username']
    cursor = conn.cursor()

    error = None
    if(data):
        ins="INSERT INTO Airplane (airline_name, airplane_id, num_seats, manufacturer, model_number, manufacturing_date, age) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(ins, (airline_name, airplane_id, num_seats, manufacturer, model_number, manufacturing_date, age))
        conn.commit()
        cursor.close()
    
    else:
        error = "Data inputted incorrectly."
        return render_template('staff_new_airplane.html', error=error)

@app.route('/staff_new_airport', methods=['POST'])
def staff_new_airport():
    print(request.form)
    code = request.form.get('code')
    name = request.form.get('name')
    city = request.form.get('city')
    country = request.form.get('country')
    num_terminals = request.form.get('num_terminals')
    type = request.form.get('type')

    data = {
        'code': code,
        'name': name,
        'city': city,
        'country': country,
        'num_terminals': num_terminals,
        'type': type
    }

    username = session['username']
    cursor = conn.cursor()

    error = None
    if(data):
        ins="INSERT INTO Airport (code, name, city, country, num_terminals, type) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(ins, (code, name, city, country, num_terminals, type))
        conn.commit()
        cursor.close()
    
    else:
        error = "Data inputted incorrectly."
        return render_template('staff_new_airport.html', error=error)

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
