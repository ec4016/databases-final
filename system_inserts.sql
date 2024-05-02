/* a. One Airline name "Jet Blue" */
INSERT INTO airline (name) values ('Jet Blue'), ('British Airways'), ('Emirates'), ('American Airlines');

/* b. At least two airports named "JFK" in NYC and "PVG" in Shanghai */
insert into airport (code, name, city, country, num_terminals, type) values ('JFK', 'John F. Kennedy International Airport', 'New York', 'United States', 5, 'international'), ('PVG', 'Shanghai Pudong International Airport', 'Shanghai', 'China', 2, 'International'), ('LGW', 'London Gatwick Airport', 'London', 'United Kingdom', 2, 'International'), ('CMN', 'Casablanca Mohammed V International Airport', 'Casablanca', 'Morocco', 3, 'International');

/* c. Insert at least three customers with appropriate names and other attributes */
INSERT INTO customer (email, first_name, last_name, password, building_num, street, apartment_num, city, state, zip_code, primary_phone_number, passport_number, passport_expiration_date, passport_country, date_of_birth) values ('ec4016@nyu.edu', 'Emil', 'Cheung', 'abc123', 2, 'Jay Street', 13, 'Brooklyn', 'NY', 11201, '123-456-7890', 1234567890, '2030-01-11', 'United States', '2001-1-11'), 
('yz9020@nyu.edu', 'Yuyu', 'Zhou', 'cdef112', 2, 'Jay Street', 13, 'Brooklyn', 'NY', 11201, '231-456-7891', 345678901, '2030-02-12', 'United States', '2001-2-12'), 
('yf2266@nyu.edu', 'Yinyi', 'Feng', 'dasdsakd123', 2, 'Jay Street', 13, 'Brooklyn', 'NY', 11201, '221-456-7792', 456789012, '2030-03-14', 'United States', '2001-3-14')
('jchen2000@gmail.com', 'Josh', 'Chen', 'jjahjsdga123', '15', 'Wall Street', '22', 'Manhattan', 'NY', 10004, '327-215-6386', 241133426, '2030-06-30', 'United States', '2000-09-03'),
('knguyen1998@gmail.com', 'Kevin', 'Nguyen', 'dagasd2q123', '13', '69 North Road', '69', 'London', 'Greater London', 'N89 2YP', '318-890-7788', 436086038, '2035-2-01', 'United Kingdom', '1998-07-13'),
('ejames1992@gmail.com', 'Ethan', 'James', 'sagasdsad123', '24', '79 Old York Street', '79', 'Massapequa', 'NY', '11758', '997-476-6172 ', 040523661, '2027-02-13', 'United States', '1992-04-12');

/* d. Insert at least three airplanes */
INSERT INTO airplane (airline_name, airplane_id, num_seats, manufacturer, model_number, manufacturing_date, age) VALUES 
('British Airways', 747, 416, 'The Boeing Company', 'Boeing 747', '1970-01-01', 54), 
('Emirates', 456, 380, 'Airbus', 'Airbus A380', '2007-02-01', 17), 
('American Airlines', '737', 215, 'The Boeing Company', 'Boeing 737', '1960-11-01', 84),
('Jet Blue', 123, 320, 'The Boeing Company', 'Airbus 320','1980-05-02', 64);

/* e. Insert at least one airline staff working for Jet Blue */
INSERT INTO staff (username, airline_name, password, first_name, last_name, date_of_birth, primary_email) VALUES
('crolland', 'Jet Blue','Crolland01320','Chris', 'Rolland', '2001-3-20', 'cr123@jetblue.com');

/* f. Insert several flights with on-time, and delayed statuses */
INSERT INTO flight (airline_name, flight_num, departure_date, departure_time, arrival_date, arrival_time, base_price, status, airplane_id, departure_airport, arrival_airport) VALUES 
('Jet Blue', '1', '2024-03-30', '13:13:00' , '2024-03-30', '20:13:00', 300, 'delayed', 123, 'JFK', 'PVG'),
('British Airways', '2', '2024-05-13', '08:15:00' , '2024-05-13', '14:10:00', 650, 'on-time', 747, 'JFK', 'LGW'),
('Emirates', '3', '2024-06-28', '11:58:00', '2024-06-29', '23:55:00', 1000, 'cancelled', 456, 'JFK', 'CMN'), 
('American Airlines', '4', '2024-06-28', '11:58:00', '2024-06-29', '23:55:00', 1000, 'on-time', 215, 'JFK', 'LGW')
('Jet Blue', '5', '2025-05-30', '15:15:00' , '2025-05-30', '20:15:00', 300, 'on-time', 123, 'LGW', 'JFK');

/* g. Insert some tickets for corresponding flights and insert some purchase records (customers bought some tickets) */
INSERT INTO ticket (ticket_id, flight_num, sold_price, first_name, last_name, date_of_birth, airline_name, departure_date, departure_time) VALUES 
(123451, 1, 300, 'Josh', 'Chen', '2000-09-03', 'Jet Blue', '2024-03-30', '13:13:00'),
(234112, 2, 650, 'Kevin', 'Nguyen', '1998-07-13', 'British Airways', '2024-05-13', '08:15:00'),
(324323, 3, 1000, 'Ethan', 'James', '1992-04-12', 'Emirates', '2024-06-28', '11:58:00'),
(213445, 4, 1000, 'Ethan', 'James', '1992-04-12', 'American Airlines', '2024-06-28', '11:58:00'),
(215545, 5, 300, 'Test', 'Case1', '1993-03-13', 'Jet Blue', '2025-05-30', '15:15:00')
(123213, 1, 100, 'Test', 'Case1', '1993-03-13', 'Jet Blue', '2024-03-30', '13:13:00');

INSERT INTO purchase (email, ticket_id, card_type, card_num, expiration_date, purchase_date, purchase_time) VALUES 
('jchen2000@gmail.com', 123451, 'credit', '854519844301460', '2027-09-25', '2024-02-29', '12:15:03'),
('knguyen1998@gmail.com', 234112, 'credit', '3658520643474707', '2029-10-12', '2024-03-11', '15:21:23'),
('ejames1992@gmail.com', 324323, 'credit', '8775669174370915', '2026-2-04', '2024-04-29', '20:13:22'),
('test1@gmail.com', 215545, 'credit', '8775655555370915', '2026-2-04', '2024-05-29', '20:15:22'),
('test1@gmail.com', 123213, 'credit', '8775655555370915', '2026-2-04', '2024-02-29', '12:13:11');

-- INSERT INTO Flight_Taken (email, airline_name, flight_num, departure_date, departure_time, rating, comment) VALUES
-- ();

