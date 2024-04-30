Create table airline ( 
name varchar(30),
primary key (name)
);

Create table airplane (
airline_name varchar(30),
airplane_id int,
num_seats int not null,
manufacturer varchar(30),
model_number varchar(30),
manufacturing_date DATE,
age int default 0,
primary key (airline_name, airplane_id),
Foreign key (airline_name) references airline (name)
);

Create table staff (
username varchar(30) not null,
airline_name varchar(30),
password varchar(32),
first_name varchar(30) not null,
last_name varchar(30) not null,
date_of_birth date not null,
primary_email varchar(30) not null,
primary key (username),
Foreign key (airline_name) references airline (name)
);

Create table staff_email (
username 	varchar(30),
email 		varchar(30),
Primary key (username, email),
Foreign key (username) references staff (username)
);

Create table staff_phone_numbers (
username 		varchar(30),
phone_number 	varchar(30),
Primary key (username, phone_number),
Foreign key (username) references staff (username)
);

Create table airport ( 
code VARCHAR(30), 
name varchar(30), 
city varchar(30), 
country varchar(30), 
num_terminals int, 
type varchar(30), 
Primary key (code) 
);

CREATE TABLE Flight (
airline_name VARCHAR(30),
flight_num int,
departure_date DATE,
departure_time TIME,
arrival_date DATE,
arrival_time TIME,
base_price numeric(9,2),
status VARCHAR(30),
airplane_id INT,
departure_airport VARCHAR(30),
arrival_airport VARCHAR(30),
PRIMARY KEY(airline_name, flight_num, departure_date, departure_time),
FOREIGN KEY (airline_name) REFERENCES Airline(name)
);

CREATE TABLE Customer (
email VARCHAR(30),
first_name VARCHAR(30),
last_name VARCHAR(30),
password VARCHAR(32),
building_num INT,
street VARCHAR(30),
apartment_num VARCHAR(30),
city VARCHAR(30),
state VARCHAR(30),
zip_code INT,
primary_phone_number varchar(30),
passport_number INT,
passport_expiration_date date,
passport_country VARCHAR(30),
date_of_birth DATE,
PRIMARY KEY(email)
);

CREATE TABLE Flight_Taken (
email VARCHAR(30),
airline_name VARCHAR(30),
flight_num int,
departure_date DATE,
departure_time TIME,
rating numeric(2,1),
comment VARCHAR(100),
PRIMARY KEY(email, airline_name, flight_num, departure_date,  departure_time),
FOREIGN KEY(email) REFERENCES Customer(email),
FOREIGN KEY(airline_name, flight_num, departure_date,  departure_time) REFERENCES Flight(airline_name, flight_num, departure_date,  departure_time)
);

CREATE TABLE Ticket (
ticket_id INT,
flight_num int,
sold_price INT,
first_name VARCHAR(30),
last_name VARCHAR(30),
date_of_birth DATE,
airline_name varchar(30),
departure_date date,
departure_time time,
PRIMARY KEY(ticket_id),
FOREIGN KEY(airline_name, flight_num, departure_date, departure_time) REFERENCES Flight(airline_name, flight_num, departure_date, departure_time)
);

CREATE TABLE Purchase(
email VARCHAR(30),
ticket_id INT,
card_type VARCHAR(30),
card_num bigint,
expiration_date DATE,
purchase_date DATE,
purchase_time TIME,
PRIMARY KEY(email, ticket_id),
FOREIGN KEY(email) REFERENCES Customer(email),
FOREIGN KEY(ticket_id) REFERENCES Ticket(ticket_id)
);

CREATE TABLE Customer_Phone_Numbers (
email VARCHAR(30),
Phone_number VARCHAR(30),
PRIMARY KEY(email, phone_number),
FOREIGN KEY(email) REFERENCES Customer(email)
);

CREATE TABLE Maintenance (
airline_name VARCHAR(30),
airplane_id int,
start_date DATE,
start_time TIME,
end_date DATE,
end_time TIME,
PRIMARY KEY(airline_name, airplane_id, start_date, start_time, end_date, end_time),
FOREIGN KEY(airline_name, airplane_id) REFERENCES Airplane(airline_name, airplane_id)
);