@app.route('/guestView', methods=['GET', 'POST'])
def guestView():
	cursor = conn.cursor()
	params = request.form
	error = None

	query = 'SELECT airline_name, flight_num, dep_timestamp, arr_timestamp, ' + \
			'status, dep_airport, dep_city, arr_airport, arr_city FROM flight NATURAL JOIN ' + \
			'(SELECT name as arr_airport, city as arr_city FROM airport) as arrival NATURAL JOIN ' + \
			'(SELECT name as dep_airport, city as dep_city FROM airport) as departure WHERE ' + \
			'status <> \'canceled\' and dep_timestamp > current_timestamp and' 

	queries = ()
	if params['source city']:
		query += ' dep_city = %s and'
		queries += (params['source city'],)
	if params['destination city']:
		query += ' arr_city = %s and'
		queries += (params['destination city'],)
	if params['source airport']:
		query += ' dep_airport = %s and'
		queries += (params['source airport'],)
	if params['destination airport']:
		query += ' arr_airport = %s and'
		queries += (params['destination airport'],)
	if params['departure date']:
		query += ' DATE(dep_timestamp) = %s and'
		queries += (params['departure date'],)
	if query[-4:] == ' and':
		query = query[:-4]  # cut the trailing ' and'
	# print(query)
	cursor.execute(query, queries)
	data = cursor.fetchall()

	if not data:
		error = "There are no flights matching these parameters. Please try again"
		return render_template('guest.html', error=error)

	ret_data = None

	if params['return date']:  # I assume a return date means the user wants to come back to the airport from which they departed
		return_query = 'SELECT airline_name, flight_num, dep_timestamp, arr_timestamp, ' + \
			'status, dep_airport, dep_city, arr_airport, arr_city FROM flight NATURAL JOIN ' + \
			'(SELECT name as arr_airport, city as arr_city FROM airport) as arrival NATURAL JOIN ' + \
			'(SELECT name as dep_airport, city as dep_city FROM airport) as departure WHERE ' + \
			'status <> \'canceled\' and dep_timestamp > current_timestamp and' 
		ret_queries = ()
		if params['source city']:
			return_query += ' arr_city = %s and'
			ret_queries += (params['source city'],)
		if params['destination city']:
			return_query += ' dep_city = %s and'
			ret_queries += (params['destination city'],)
		if params['source airport']:
			return_query += ' arr_airport = %s and'
			ret_queries += (params['source airport'],)
		if params['destination airport']:
			return_query += ' dep_airport = %s and'
			ret_queries += (params['destination airport'],)
		return_query += ' DATE(dep_timestamp) = %s'
		ret_queries += (params['return date'],)
		cursor.execute(return_query, ret_queries)
		ret_data = cursor.fetchall()
		print(return_query, ret_data)

	cursor.close()
	# print(data)
	return render_template('guest.html', results=data, ret=ret_data)
