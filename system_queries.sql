/* Show all the future flights in the system */
/* (British Airways, 2, 2024-05-13, 08:15:00, 2024-05-13, 14:10:00, 650.00, on-time, 747, JFK, LGW)
(Emirates, 3, 2024-06-28, 11:58:00, 2024-06-29, 23:55:00, 1000.00, cancelled, 456, JFK, CMN) */
select * from flight where CURRENT_DATE < departure_date and CURRENT_TIME < departure_time;

/* b. Show all of the delayed flights in the system */
/* (Jet Blue, 1, 2024-03-30, 13:13:00, 2024-03-30, 20:13:00, 300.00, delayed, 123, JFK, PVG,) */
select * from flight where status = 'delayed';

/* c. Show the customer names who bought the tickets */
/* (Ethan, James)
   (Josh, Chen)
   (Kevin, Nguyen) */
select distinct first_name, last_name from customer natural join purchase;

/* d. Show all the airplanes owned by the airline Jet Blue */
/* (Jet Blue, 123, 320, The Boeing Company, Airbus, 320, 1980-05-02, 64) */
select * from airplane where airline_name = 'Jet Blue';