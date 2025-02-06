
from ast import Str
from sqlite3 import Time
from sqlalchemy import Float, create_engine
from sqlalchemy import Column, String, Integer, DateTime, Date, Time
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///Database.sqlite', echo=True, connect_args={'check_same_thread': False})
base = declarative_base()

class Passenger(base):

    __tablename__ = "Passenger"

    FirstName = Column(String) 
    LastName = Column(String)
    EmailAddress = Column(String, primary_key =True)
    Password = Column(String)
    Gender = Column(String)

    #date is useful, so keep the correct type
    DateOfBirth = Column(Date)
    
    #No need to keep these as integers as we do not need to perform maths operations
    Passport = Column(String)
    NationalID = Column(String)
    ContactNumber = Column(String)


    def __init__(self, FirstName, LastName, EmailAddress, Password, Gender, DateOfBirth, Passport, NationalID, ContactNumber):
        
        self.FirstName = FirstName
        self.LastName = LastName
        self.EmailAddress = EmailAddress
        self.Password = Password
        self.Gender = Gender
        self.DateOfBirth = DateOfBirth
        self.Passport = Passport
        self.NationalID = NationalID
        self. ContactNumber = ContactNumber

class Admin(base):

    __tablename__ = "Admin"

    FirstName = Column(String) 
    LastName = Column(String)
    EmailAddress = Column(String, primary_key =True)
    Password = Column(String)
    Gender = Column(String)

    #date is useful, so keep the correct type
    DateOfBirth = Column(Date)
    
    #No need to keep these as integers as we do not need to perform maths operations
    EmployeeID = Column(String)
    NationalID = Column(String)
    ContactNumber = Column(String)


    def __init__(self, FirstName, LastName, EmailAddress, Password, Gender, DateOfBirth, EmployeeID, NationalID, ContactNumber):
        
        self.FirstName = FirstName
        self.LastName = LastName
        self.EmailAddress = EmailAddress
        self.Password = Password
        self.Gender = Gender
        self.DateOfBirth = DateOfBirth
        self.EmployeeID = EmployeeID
        self.NationalID = NationalID
        self. ContactNumber = ContactNumber


class Flight(base):

    __tablename__ = "Flights"

    Flight_ID = Column(Integer, primary_key=True) 
    Airline_ID = Column(Integer)
    AirlineName = Column(String)
    From_location = Column(String)
    To_location = Column(String)
    Departure_date = Column(Date)
    Arrival_date = Column(Date)
    Departure_time = Column(Time)
    Arrival_time = Column(Time)
    Duration = Column(String)
    Total_seats = Column(Integer)
    Booked_seats = Column(Integer)
    Status = Column(String)

    def __init__(self, Flight_ID, Airline_ID, AirlineName, From_location, To_location, Departure_date, Arrival_date, Departure_time, Arrival_time, Duration, Total_seats, Booked_Seats):
        
        self.Flight_ID = Flight_ID
        self.Airline_ID = Airline_ID 
        self.AirlineName = AirlineName
        self.From_location = From_location
        self.To_location = To_location
        self.Departure_time = Departure_time
        self.Arrival_time = Arrival_time
        self.Departure_date = Departure_date
        self.Arrival_date = Arrival_date
        self.Duration = Duration
        self.Total_seats = Total_seats
        self.Booked_seats = Booked_Seats
        self.Status = "Active" #flight is active by default, can be canceled by admin


class Booking(base):

    __tablename__ = "Bookings"

    Booking_ID = Column(Integer, primary_key=True)
    Passenger_Email = Column(String)
    Flight_ID = Column(Integer)
    Booking_Date = Column(String)
    Ticket_ID = Column(Integer) 
    Ticket_Price = Column(Float) 
    Payment_ID = Column(Integer)

    def __init__(self, Passenger_Email, Flight_ID, Booking_Date, Ticket_ID, Ticket_Price, Payment_ID):
        
        #self.Booking_ID = Booking_ID 
        self.Passenger_Email = Passenger_Email
        self.Flight_ID = Flight_ID
        self.Booking_Date = Booking_Date
        self.Ticket_ID = Ticket_ID 
        self.Ticket_Price = Ticket_Price 
        self.Payment_ID = Payment_ID


base.metadata.create_all(engine)
