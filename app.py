from hashlib import new
import random
from winreg import REG_QWORD
from flask import Flask, redirect, render_template, request, url_for
from flask import session as STORE
from sqlalchemy import delete
import db
from sqlalchemy.orm import sessionmaker
from datetime import datetime

import smtplib, ssl


Session = sessionmaker(bind=db.engine)
session = Session()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///Database.sqlite'
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_password():

    if request.method != "POST":
        return render_template('reset_password.html')

    sender = ("Airline Reservation System", 'noreplyairlinereservation@gmail.com') 
    receiver = request.form['email']

    pincode = random.randint(100000, 999999)

    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "noreplyairlinereservation@gmail.com"  # Enter your address
    receiver_email = receiver  # Enter receiver address
    password = "ndfsqyjiauirttid"
 
    message = """\
    Airline Reservation System

    Your password reset pin is : .""" + str(pincode)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)

    return render_template('new_password.html', original_pincode = pincode, email=receiver_email)

@app.route('/complete_reset_password', methods=['GET', 'POST'])
def complete_reset_password():

    if request.method != 'POST':
        return redirect(url_for('reset_password'))

    original_pincode = request.form['originalpincode']
    pincode = request.form['pincode']
    new_password = request.form['newpassword']
    confirm_password = request.form['confirmpassword']
    email = request.form['email']

    if original_pincode != pincode:
        return render_template('message.html', message = "Incorrect Pin Code", prev_url = "passenger_signin", dashboard = '/')
    
    if new_password != confirm_password:
        return render_template('message.html', message = "Password do not match!", prev_url = "passenger_signin", dashboard = '/')

    if session.query(db.Admin).filter(db.Admin.EmailAddress == email).count() != 0:

        session.query(db.Admin).filter(db.Admin.EmailAddress == email).update({'Password': new_password})
        session.commit()
        return render_template('message.html', message = "Password Updated!", prev_url = "passenger_signin", dashboard = '/')

    elif session.query(db.Passenger).filter(db.Passenger.EmailAddress == email).count() != 0: 
        
            session.query(db.Passenger).filter(db.Passenger.EmailAddress == email).update({'Password': new_password})
            session.commit()
            return render_template('message.html', message = "Password Updated!", prev_url = "passenger_signin", dashboard = '/')

    else:
        
        return render_template('message.html', message = "No such user!", prev_url = "passenger_signin", dashboard = '')

def add_passenger_to_database(FirstName, LastName, EmailAddress, Password, Gender, PhoneNumber, DateOfBirth, National_ID, Passport):

    #returns true if added successfully, false otherwise

    ret = session.query(db.Passenger).filter(db.Passenger.EmailAddress == EmailAddress)

    if ret.count() == 0:

        tr = db.Passenger(FirstName, LastName, EmailAddress, Password, Gender, DateOfBirth, Passport, National_ID, PhoneNumber)
        session.add(tr)

        session.commit()

        return True
    
    return False

def add_admin_to_database(FirstName, LastName, EmailAddress, Password, Gender, PhoneNumber, DateOfBirth, National_ID, EmployeeID):

    #returns true if added successfully, false otherwise

    ret = session.query(db.Admin).filter(db.Admin.EmployeeID == EmployeeID)

    if ret.count() == 0:

        tr = db.Admin(FirstName, LastName, EmailAddress, Password, Gender, DateOfBirth, EmployeeID, National_ID, PhoneNumber)
        session.add(tr)

        session.commit()

        return True
    
    return False

def add_flight_to_database(Flight_ID, Aiirline_ID, Airline_Name, From_Location, To_Location, Departure_Date, Arrival_Date, Departure_Time, Arrival_Time, Duration, Total_Seats, Booked_Seats):

    #returns true if added successfully, false otherwise

    ret = session.query(db.Flight).filter(db.Flight.Flight_ID == Flight_ID)

    if ret.count() == 0:

        tr = db.Flight(Flight_ID, Aiirline_ID, Airline_Name, From_Location, To_Location, Departure_Date, Arrival_Date, Departure_Time, Arrival_Time, Duration, Total_Seats, Booked_Seats)
        session.add(tr)

        session.commit()

        return True
    
    return False

def search_passenger_password(EmailAddress, Password):

    #returns a tuple with status and message

    ret = session.query(db.Passenger).filter(db.Passenger.EmailAddress == EmailAddress)
    
    if ret.count() > 0:

        if ret.one().Password == Password:
            return (1, "You have successfully signed in!", ret.one()) #also returns the object retrieved
        else:
            return (-1, "Invalid Password!")

    return (-2, "Email not registered!")

def search_admin_password(EmployeeID, Password):

    #returns a tuple with status and message

    ret = session.query(db.Admin).filter(db.Admin.EmployeeID == EmployeeID)
    
    if ret.count() > 0:

        if ret.one().Password == Password:
            return (1, "You have successfully signed in!", ret.one()) #also returns the object retrieved
        else:
            return (-1, "Invalid Password!")

    return (-2, "Admin not registered!")

@app.route('/')
def index():

    return render_template('index.html', msg = "Welcome Home")

@app.route('/login')
def login():

    return render_template('login.html')

@app.route('/passenger_signup')
def passenger_signup():

    return render_template('passenger_signup.html')

@app.route('/admin_signup')
def admin_signup():

    return render_template('admin_signup.html')


@app.route('/passenger_signin')
def passenger_signin():

    return render_template('passenger_signin.html')

@app.route('/admin_signin')
def admin_signin():

    return render_template('admin_signin.html')

@app.route('/passenger_dashboard',  methods=['GET', 'POST'])
def passenger_dashboard():

    if request.method == 'POST':
        
        username = request.form['username']

    return render_template('passenger_dashboard.html', user = STORE['passenger'])

@app.route('/admin_dashboard',  methods=['GET', 'POST'])
def admin_dashboard():

    if request.method == 'POST':
        
        username = request.form['username']

    return render_template('admin_dashboard.html', user = STORE['admin'])

@app.route('/profile')
def passenger_profile():

    return render_template('passenger_profile.html')

@app.route('/compelete_passenger_signup', methods=['GET', 'POST'])
def compelete_passenger_signup():

    if request.method == 'POST':
        
        FirstName = request.form['firstname']
        LastName = request.form['lastname']
        EmailAddress = request.form['emailaddress']
        password = request.form['password']
        ConfirmPassword = request.form['confirmpassword']
        Gender = request.form['gender']
        PhoneNumber = request.form['phonenumber']
        DateOfBirth = request.form['dob']
        Passport = request.form['passport']
        National_ID = request.form['nic']

        #fix the date
        DateOfBirth = datetime.strptime(DateOfBirth,'%Y-%m-%d').date()

        #failed prompt
        fp = "Oh no! Looks like you had issues with your password!\n\nHere are the requirements you failed:\n"

        #success prompt
        sp = "Your password passed all the requirements!\n"

        #constraint prompts
        c1 = "You did not use an uppercase character.\n"
        c2 = "You did not use a lowercase character.\n"
        c3 = "You did not end your username with a number.\n"
        c4 = "Password length is less than 8 characters.\n"
        c5 = "The passwords entered do not match.\n"

        #check for constraints
        ul = []

        res = any(ele.isupper() for ele in password)
        
        if res == False:
            ul.append(c1)

        res = any(ele.islower() for ele in password)

        if res == False:
            ul.append(c2)

        if not password[-1].isdigit():        
            ul.append(c3)

        if len(password) < 8:
            ul.append(c4)

        if password != ConfirmPassword:
            ul.append(c5)

        finalmsg = ''

        if len(ul) == 0:
            finalmsg = sp
        else:
            finalmsg = fp

        if len(ul) > 0:
            return render_template('passenger_signup.html', color = "red-text", errors=ul)
        else:

            #record in the database
            added = add_passenger_to_database(FirstName, LastName, EmailAddress, password, Gender, PhoneNumber, DateOfBirth, National_ID, Passport)

            if added:
                ul = ["Registration Complete!"]
                return render_template('passenger_signup.html', color = "green-text", errors= ul)
            else:
                ul = ["Email already registered!"]
                return render_template('passenger_signup.html', color = "red-text", errors= ul)

    else:
        
        return redirect(url_for('passenger_signup'))

@app.route('/edit_admin_profile')
def edit_admin_profile():

    if 'admin' in STORE:

        EmployeeID = STORE['admin']

        found = session.query(db.Admin).filter(db.Admin.EmployeeID == EmployeeID).count()

        if found == 0:
            return render_template('message.html', message = "Admin Does Not Exist!", prev_url = "edit_admin_profile", dashboard = 'admin_dashboard')

        admin = session.query(db.Admin).filter(db.Admin.EmployeeID == EmployeeID).one()

        return render_template('edit_admin_profile.html', admin = admin)

    else:

        return redirect(url_for('index'))

@app.route('/edit_passenger_profile')
def edit_passenger_profile():

    if 'passenger' in STORE:

        EmailAddress = STORE['passenger']

        found = session.query(db.Passenger).filter(db.Passenger.EmailAddress == EmailAddress).count()

        if found == 0:
            return render_template('message.html', message = "User Does Not Exist!", prev_url = "edit_passenger_profile", dashboard = 'passenger_dashboard')

        passenger = session.query(db.Passenger).filter(db.Passenger.EmailAddress == EmailAddress).one()

        return render_template('edit_passenger_profile.html', passenger = passenger)

    else:

        return redirect(url_for('index'))



@app.route('/compelete_admin_signup', methods=['GET', 'POST'])
def compelete_admin_signup():

    if request.method == 'POST':
        
        FirstName = request.form['firstname']
        LastName = request.form['lastname']
        EmailAddress = request.form['emailaddress']
        password = request.form['password']
        ConfirmPassword = request.form['confirmpassword']
        Gender = request.form['gender']
        PhoneNumber = request.form['phonenumber']
        DateOfBirth = request.form['dob']
        EmployeeID = request.form['employeeid']
        National_ID = request.form['nic']

        DateOfBirth = datetime.strptime(DateOfBirth,'%Y-%m-%d').date()

        #constraint prompts
        c1 = "You did not use an uppercase character.\n"
        c2 = "You did not use a lowercase character.\n"
        c3 = "You did not end your password with a number.\n"
        c4 = "Password length is less than 8 characters.\n"
        c5 = "The passwords entered do not match.\n"

        #check for constraints
        ul = []

        res = any(ele.isupper() for ele in password)
        
        if res == False:
            ul.append(c1)

        res = any(ele.islower() for ele in password)

        if res == False:
            ul.append(c2)

        if not password[-1].isdigit():        
            ul.append(c3)

        if len(password) < 8:
            ul.append(c4)

        if password != ConfirmPassword:
            ul.append(c5)


        if len(ul) > 0:
            return render_template('admin_signup.html', color = "red-text", errors=ul)
        else:

            #record in the database
            added = add_admin_to_database(FirstName, LastName, EmailAddress, password, Gender, PhoneNumber, DateOfBirth, National_ID, EmployeeID)

            if added:
                ul = ["Registration Complete!"]
                return render_template('admin_signup.html', color = "green-text", errors= ul)
            else:
                ul = ["Email already registered!"]
                return render_template('admin_signup.html', color = "red-text", errors= ul)
    else:
        
        return redirect(url_for('admin_signup'))

@app.route('/complete_add_flight', methods=['GET', 'POST'])
def complete_add_flight():

    if request.method == 'POST':

        Flight_ID = request.form['flightid']
        Aiirline_ID = request.form['airlineid']
        Airline_Name = request.form['airlinename']
        From_Location = request.form['fromlocation']
        To_Location = request.form['tolocation']
        Departure_Date = request.form['departuredate']
        Arrival_Date = request.form['arrivaldate']
        Departure_Time = request.form['departuretime']
        Arrival_Time = request.form['arrivaltime']
        Duration = request.form['duration']
        Total_Seats = request.form['totalseats']
        Booked_Seats = 0

        Departure_Date = datetime.strptime(Departure_Date,'%Y-%m-%d').date()
        Arrival_Date = datetime.strptime(Arrival_Date,'%Y-%m-%d').date()

        Departure_Time = datetime.strptime(Departure_Time,'%H:%M').time()
        Arrival_Time = datetime.strptime(Arrival_Time, '%H:%M').time()

        #check for constraints
        ul = []

        if len(ul) > 0:
            return render_template('admin_signup.html', color = "red-text", errors=ul)
        else:

            #record in the database
            added = add_flight_to_database(Flight_ID, Aiirline_ID, Airline_Name, From_Location, To_Location, Departure_Date, Arrival_Date, Departure_Time, Arrival_Time, Duration, Total_Seats, Booked_Seats)

            if added > 0:
                return render_template('message.html', message = "Added Flight with ID: " + (str(Flight_ID)), prev_url='add_flight', dashboard = 'admin_dashboard')
            else:
                return render_template('message.html', message = "Flight Already Exists!", prev_url='add_flight', dashboard = 'admin_dashboard')
    else:
        
        return redirect(url_for('add_flight'))

@app.route('/complete_update_flight', methods=['GET', 'POST'])
def complete_update_flight():

    if request.method == 'POST':

        Flight_ID = request.form['flightid']

        session.query(db.Flight).filter(db.Flight.Flight_ID == Flight_ID).delete() #delete the previous details and add new

        Aiirline_ID = request.form['airlineid']
        Airline_Name = request.form['airlinename']
        From_Location = request.form['fromlocation']
        To_Location = request.form['tolocation']
        Departure_Date = request.form['departuredate']
        Arrival_Date = request.form['arrivaldate']
        Departure_Time = request.form['departuretime']
        Arrival_Time = request.form['arrivaltime']
        Duration = request.form['duration']
        Total_Seats = request.form['totalseats']
        Booked_Seats = 0

        Departure_Date = datetime.strptime(Departure_Date,'%Y-%m-%d').date()
        Arrival_Date = datetime.strptime(Arrival_Date,'%Y-%m-%d').date()

        Departure_Time = datetime.strptime(Departure_Time,'%H:%M').time()
        Arrival_Time = datetime.strptime(Arrival_Time, '%H:%M').time()

        #check for constraints
        ul = []

        if len(ul) > 0:
                return render_template('message.html', message = "Error in one or more details!", prev_url='add_flight', dashboard = 'admin_dashboard')
        else:

            #record in the database
            added = add_flight_to_database(Flight_ID, Aiirline_ID, Airline_Name, From_Location, To_Location, Departure_Date, Arrival_Date, Departure_Time, Arrival_Time, Duration, Total_Seats, Booked_Seats)

            if added > 0:
                return render_template('message.html', message = "Updated Flight with ID: " + (str(Flight_ID)), prev_url='update_flight', dashboard = 'admin_dashboard')
            else:
                return render_template('message.html', message = "Unable to Update!", prev_url='add_flight', dashboard = 'admin_dashboard')
    else:
        
        return redirect(url_for('update_flight'))

@app.route('/complete_passenger_signin', methods=['GET', 'POST'])
def complete_passenger_signin():

    if request.method == 'POST':
        
        EmailAddress = request.form['email']
        password = request.form['password']

        #constraint prompts
        c1 = "You did not use an uppercase character in Password.\n"
        c2 = "You did not use a lowercase character in Password.\n"
        c3 = "You did not end your Password with a number.\n"
        c4 = "Password length is less than 8 characters.\n"
        c5 = "The passwords entered do not match.\n"

        #check for constraints
        ul = []

        res = any(ele.isupper() for ele in password)
        
        if res == False:
            ul.append(c1)

        res = any(ele.islower() for ele in password)

        if res == False:
            ul.append(c2)

        if not password[-1].isdigit():        
            ul.append(c3)

        if len(password) < 8:
            ul.append(c4)

        if len(ul) > 0:
            return render_template('passenger_signin.html', color = "red-text", errors=ul)
        else:

            #record in the database
            retrieved = search_passenger_password(EmailAddress, password)

            if retrieved[0] == 1:
                
                username = retrieved[2].FirstName
                
                if not STORE.get('passenger'):
                    STORE['passenger'] = EmailAddress
                
                #store session
                
                return redirect(url_for('passenger_dashboard'))

            else:
                ul = [retrieved[1]]
                return render_template('passenger_signin.html', color = "red-text", errors=ul)


@app.route('/complete_admin_signin', methods=['GET', 'POST'])
def complete_admin_signin():

    if request.method == 'POST':
        
        EmployeeID = request.form['employeeid']
        password = request.form['password']

        #constraint prompts
        c1 = "You did not use an uppercase character.\n"
        c2 = "You did not use a lowercase character.\n"
        c3 = "You did not end your username with a number.\n"
        c4 = "Password length is less than 8 characters.\n"
        c5 = "The passwords entered do not match.\n"

        #check for constraints
        ul = []

        res = any(ele.isupper() for ele in password)
        
        if res == False:
            ul.append(c1)

        res = any(ele.islower() for ele in password)

        if res == False:
            ul.append(c2)

        if not password[-1].isdigit():        
            ul.append(c3)

        if len(password) < 8:
            ul.append(c4)

        if len(ul) > 0:
            return render_template('admin_signin.html', color = "red-text", errors=ul)
        else:

            #record in the database
            retrieved = search_admin_password(EmployeeID, password)

            if retrieved[0] == 1:
                
                username = retrieved[2].FirstName

                STORE["admin"] = request.form['employeeid']

                return redirect(url_for('admin_dashboard'))

            else:
                ul = [retrieved[1]]
                return render_template('admin_signin.html', color = "red-text", errors=ul)

@app.route('/add_flight')
def add_flight():

    return render_template('add_flight.html')

@app.route('/view_flights')
def view_flights():

    ret = session.query(db.Flight).all()

    print("VALUES ARE: ")
    
    for each in ret:
        print(each.Airline_ID)

    return render_template('view_flights.html', values = ret)

@app.route('/view_flights_passenger')
def view_flights_passenger():

    ret = session.query(db.Flight).all()

    print("VALUES ARE: ")
    
    for each in ret:
        print(each.Airline_ID)

    return render_template('view_flights_passenger.html', values = ret)

@app.route('/view_flights2')
def view_flights2():

    ret = session.query(db.Flight).all()

    print("VALUES ARE: ")
    
    for each in ret:
        print(each.Airline_ID)

    return render_template('view_flights2.html', values = ret)


@app.route('/search_flight')
def search_flight():

    return render_template('search_flight.html')

@app.route('/search_results', methods=['GET', 'POST'])
def search_results():

    if request.method != "POST":
        return redirect(url_for('passenger_dashboard'))

    fromdest = request.form['fromdest']
    todest = request.form['todest']
    date = request.form['date']

    date = datetime.strptime(date,'%Y-%m-%d').date()

    count = session.query(db.Flight).filter(db.Flight.From_location == fromdest, db.Flight.To_location == todest, db.Flight.Departure_date == date, db.Flight.Status == "Active").count()
    ret = session.query(db.Flight).filter(db.Flight.From_location == fromdest, db.Flight.To_location == todest, db.Flight.Departure_date == date).all()

    message = ""

    if count == 0:
        message = "No matching flights! date: " + str(date)

    return render_template('search_results.html', values = ret, message = message)

@app.route('/flight_results', methods=['GET', 'POST'])
def flight_results():

    if request.method != "POST":
        return redirect(url_for('passenger_dashboard'))

    flight_ID = request.form['flightid']

    count = session.query(db.Flight).filter(db.Flight.Flight_ID == flight_ID).count()
    ret = session.query(db.Flight).filter(db.Flight.Flight_ID == flight_ID).all()

    message = ""

    if count == 0:
        message = "No matching flights!"

    return render_template('search_results.html', values = ret, message = message)

@app.route('/cancel_flight')
def cancel_flight():

    return render_template('cancel_flight.html')

@app.route('/book_ticket', methods=['GET', 'POST'])
def book_ticket():

    if request.method != "POST":
        return render_template("book_new_ticket.html")

    flight_ID = request.form['flightid']
    email_Address = STORE['passenger']

    count = session.query(db.Flight).filter(db.Flight.Flight_ID == flight_ID).count()

    if count < 1:
        return render_template('message.html', message = "Error!\nNo such flight: " + str(flight_ID), prev_url = "book_ticket", dashboard = 'passenger_dashboard')
        

    flight = session.query(db.Flight).filter(db.Flight.Flight_ID == flight_ID).one()
    passenger = session.query(db.Passenger).filter(db.Passenger.EmailAddress == email_Address).one()

    current_time = datetime.now()
    ticket_id = random.randint(100000, 999999)
    price = random.randint(500, 4000)
    payment_ID = random.randint(100000, 999999)

    booked_seats = flight.Booked_seats

    session.query(db.Flight).filter(db.Flight.Flight_ID == flight_ID).update({'Booked_seats': booked_seats+1})
    session.commit()

    return render_template('booking_details.html', flight = flight, passenger = passenger, ticket_id = ticket_id, price = price, payment_id = payment_ID)

@app.route("/confirm_booking", methods=['GET', 'POST'])
def confirm_booking():

    if request.method != "POST":
        return "Error!"

    email_Address = request.form['emailaddress']
    flight_ID = request.form['flightid']
    current_time = datetime.now()
    ticket_id = request.form['ticket_id']
    price = request.form['price']
    payment_ID = request.form['payment_id']
    paymentmethod = request.form['paymentmethod']

    if paymentmethod == "creditcard":

        price = float(price) - ((float(price)/100) * 20)
        price = str(price)

    elif paymentmethod == "ibft":

        price = float(price) - ((float(price)/100) * 15)
        price = str(price)

    tr = db.Booking(email_Address, flight_ID, current_time, ticket_id, price, payment_ID)
    session.add(tr)

    session.commit()

    #send email
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "noreplyairlinereservation@gmail.com"  # Enter your address
    receiver_email = email_Address
    password = "ndfsqyjiauirttid"
 
    message = """\

    Dear Customer, 
    Your ticket has been booked for flight number: """ + str(flight_ID) + " with booking ID: " + str(ticket_id)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)

    return render_template('message.html', message = "Success!\nBooking complete for flight: " + str(flight_ID), prev_url = "book_ticket", dashboard = 'passenger_dashboard')

@app.route('/remove_flight')
def remove_flight():

    return render_template('remove_flight.html')

@app.route('/update_flight')
def update_flight():

    return render_template('update_flight.html')


@app.route('/update_flight_details', methods=['GET', 'POST'])
def update_flight_details():

    if request.method == 'POST':

        flight_ID = request.form['flightid']

        found = session.query(db.Flight).filter(db.Flight.Flight_ID == flight_ID).count()

        if found == 0:
            return render_template('message.html', message = "Flight Does Not Exist!", prev_url = "update_flight", dashboard = 'admin_dashboard')

        flight = session.query(db.Flight).filter(db.Flight.Flight_ID == flight_ID).one()

        return render_template('update_flight_details.html', flight = flight)

    else:

        return redirect(url_for('update_flight'))


@app.route('/logout')
def logout():

    STORE.clear()
    return redirect(url_for('index'))

@app.route('/complete_remove_flight', methods=['GET', 'POST'])
def complete_remove_flight():

    if request.method == 'POST':

        Flight_ID = request.form['flightid']

        #record in the database
        deleted = session.query(db.Flight).filter(db.Flight.Flight_ID == Flight_ID).delete()
        session.commit()

        if deleted > 0:
            return render_template('message.html', message = "Deleted Flight with ID: " + (str(Flight_ID)), prev_url = "remove_flight", dashboard = 'admin_dashboard')
        else:
            return render_template('message.html', message = "Flight does not exist!", prev_url = "remove_flight", dashboard = 'admin_dashboard')
    else:
        return redirect(url_for('remove_flight'))


@app.route('/complete_cancel_flight', methods=['GET', 'POST'])
def complete_cancel_flight():

    if request.method == 'POST':

        Flight_ID = request.form['flightid']

        #record in the database
        updated = session.query(db.Flight).filter(db.Flight.Flight_ID == Flight_ID).update({'Status': "Canceled"})
        session.commit()

        if updated > 0:
            return render_template('message.html', message = "Canceled Flight with ID: " + (str(Flight_ID)), prev_url='/cancel_flight', dashboard = 'admin_dashboard')
        else:
            return render_template('message.html', message = "Flight does not exist!", prev_url='/cancel_flight', dashboard = 'admin_dashboard')

    else:

        return redirect(url_for("cancel_flight"))

@app.route('/complete_edit_profile', methods=['GET', 'POST'])
def complete_edit_profile():

    if request.method == 'POST':

        EmployeeID = request.form['employeeid']
        Password = (session.query(db.Admin).filter(db.Admin.EmployeeID == EmployeeID).one()).Password

        session.query(db.Admin).filter(db.Admin.EmployeeID == EmployeeID).delete() #delete the previous details and add new

        FirstName = request.form['firstname']
        LastName = request.form['lastname']
        EmailAddress = request.form['emailaddress']
        Gender = request.form['gender']
        DateOfBirth = request.form['dob']
        National_ID = request.form['nic']
        PhoneNumber = request.form['phonenumber']

        DateOfBirth = datetime.strptime(DateOfBirth,'%Y-%m-%d').date()

        #check for constraints
        ul = []

        if len(ul) > 0:
                return render_template('message.html', message = "Error in one or more details!", prev_url='edit_admin_profile', dashboard = 'admin_dashboard')
        else:

            #record in the database
            added = add_admin_to_database(FirstName, LastName, EmailAddress, Password, Gender, PhoneNumber, DateOfBirth, National_ID, EmployeeID)

            if added > 0:
                return render_template('message.html', message = "Updated Admin with ID: " + (str(EmployeeID)), prev_url='edit_admin_profile', dashboard = 'admin_dashboard')
            else:
                return render_template('message.html', message = "Unable to Update!", prev_url='edit_admin_profile', dashboard = 'admin_dashboard')
    else:
        
        return redirect(url_for('edit_admin_profile'))

@app.route('/complete_edit_passenger_profile', methods=['GET', 'POST'])
def complete_edit_passenger_profile():

    if request.method == 'POST':

        EmailAddress = request.form['emailaddress']
        Password = (session.query(db.Passenger).filter(db.Passenger.EmailAddress == EmailAddress).one()).Password

        session.query(db.Passenger).filter(db.Passenger.EmailAddress == EmailAddress).delete() #delete the previous details and add new

        FirstName = request.form['firstname']
        LastName = request.form['lastname']
        Passport = request.form['passport']
        Gender = request.form['gender']
        DateOfBirth = request.form['dob']
        National_ID = request.form['nic']
        PhoneNumber = request.form['phonenumber']

        DateOfBirth = datetime.strptime(DateOfBirth,'%Y-%m-%d').date()

        #check for constraints
        ul = []

        if len(ul) > 0:
                return render_template('message.html', message = "Error in one or more details!", prev_url='edit_admin_profile', dashboard = 'admin_dashboard')
        else:

            #record in the database
            added = add_passenger_to_database(FirstName, LastName, EmailAddress, Password, Gender, PhoneNumber, DateOfBirth, National_ID, Passport)

            if added > 0:
                return render_template('message.html', message = "Updated Passenger with Email: " + (str(EmailAddress)), prev_url='edit_passenger_profile', dashboard = 'passenger_dashboard')
            else:
                return render_template('message.html', message = "Unable to Update!", prev_url='edit_passenger_profile', dashboard = 'passenger_dashboard')
    else:
        
        return redirect(url_for('edit_passenger_profile'))


@app.route("/change_passenger_password")
def change_passenger_password():

    if 'passenger' not in STORE:

        return render_template('message.html', message = "Error in session!", prev_url = '/')

    else:
        
        return render_template('change_passenger_password.html', color = "red-text", errors=[])

@app.route("/complete_change_passenger_password", methods=["GET", "POST"])
def complete_change_passenger_password():

    if request.method != "POST":
        return redirect(url_for('passenger_dashboard'))

    if 'passenger' in STORE:

        EmailAddress = STORE['passenger']
        print("EMAIL ADDR: ", EmailAddress)

        found = session.query(db.Passenger).filter(db.Passenger.EmailAddress == EmailAddress).count()

        if found == 0:
            return render_template('message.html', message = "User Does Not Exist!", prev_url = "change_passenger_password", dashboard = 'passenger_dashboard')

        passenger = session.query(db.Passenger).filter(db.Passenger.EmailAddress == EmailAddress).one()

        correct_password = passenger.Password

        current_password = request.form['currentpassword']
        new_password = request.form['newpassword']
        confirm_password = request.form['confirmpassword']

        if correct_password == current_password:

            if new_password != confirm_password:
                
                error = "Entered Passwords do not match!"
                return render_template('change_passenger_password.html', color = "red-text", errors=[error])

            else:
                
                updated = session.query(db.Passenger).filter(db.Passenger.EmailAddress == EmailAddress).update({'Password': new_password})
                session.commit()
                if updated > 0:
                    success = "Password changed!"
                else:
                    success = "Failure!"

                return render_template('change_passenger_password.html', color = "green-text", errors=[success])
                
        else:

            error = "Password Entered is Incorrect!"
            return render_template('change_passenger_password.html', color = "red-text", errors=[error])

@app.route('/guest_view')
def guest_view():

    ret = session.query(db.Flight).all()

    return render_template('guest_view.html', values=ret)

@app.route('/cancel_ticket')
def cancel_ticket():

    if "passenger" not in STORE:

        return render_template('message.html', message = "Please login first!", prev_url = "/", dashboard = 'passenger_dashboard')

    Email_Address = STORE['passenger']


    count = session.query(db.Booking).filter(db.Booking.Passenger_Email == Email_Address).count()
    bookings = session.query(db.Booking).filter(db.Booking.Passenger_Email == Email_Address).all()

    message = ""

    if count == 0:
        message = "No booked flights!"

    return render_template('cancel_ticket.html', bookings=bookings, message=message)

@app.route('/complete_ticket_cancelation', methods=["POST", "GET"])
def complete_ticket_cancelation():

    if request.method != "POST":
        return render_template('message.html', message = "Error! Make sure you log in!", prev_url = "/", dashboard = 'passenger_dashboard')
        
    booking_id = request.form['bookingid']

    flight_ID = session.query(db.Booking).filter(db.Booking.Booking_ID == booking_id).one()
    flight_ID = flight_ID.Flight_ID

    removed = session.query(db.Booking).filter(db.Booking.Booking_ID == booking_id).delete()
    session.commit()


    flight = session.query(db.Flight).filter(db.Flight.Flight_ID == flight_ID).one()
    booked_seats = flight.Booked_seats

    session.query(db.Flight).filter(db.Flight.Flight_ID == flight_ID).update({'Booked_seats': booked_seats-1})
    session.commit()

    return render_template('message.html', message = "Canceled Booking with ID: " + str(booking_id), prev_url = "cancel_ticket", dashboard = 'passenger_dashboard')


if __name__ == "__main__":

    app.run(debug=True)