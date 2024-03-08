from datetime import date
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, session
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from GymDb import GymDb

USER = "root"
PASSWORD = "2004"
engine = create_engine(f"mysql+mysqlconnector://{USER}:{PASSWORD}@localhost")
db = GymDb(engine.connect())

app = Flask(__name__)
app.secret_key = '2004'


@app.route('/')
def index():
    return render_template('homePage.html')


@app.route('/adminPage')
def adminPage():
    return render_template('admins.html')


@app.route('/trainerPage')
def trainerPage():
    if 'email' in session:
        email = session['email']
        query = f"Select * From Trainers where email = '{email}'; "
        result = db.executeStatement(query)
        trainers = result.all()
        print(trainers)
    return render_template('trainers.html', trainers_data=trainers, members_data=[""])


@app.route('/memberPage')
def memberPage():
    if 'email' in session:
        username = session['email']
        query = f"Select * From Members where email = '{username}'; "
        result = db.executeStatement(query)
        members = result.all()
        print(members)

        query = f"Select * From payments where member_email = '{username}'"
        result = db.executeStatement(query)
        payments = result.all()
        print(payments)

        query = f"Select * From trainers;"
        result = db.executeStatement(query)
        trainers_data = result.all()
        print(trainers_data)

        query = f"Select * From trainers where member_email = '{username}';"
        result = db.executeStatement(query)
        selectTrainer_data = result.all()
        print(selectTrainer_data)

    return render_template('members.html', members_data=members, payments_data=payments,trainers_data = trainers_data,selectTrainer_data = selectTrainer_data)


@app.route('/insert_payment', methods=['POST'])
def insert_payment():
    if request.method == 'POST':
        member_email = session['email']
        amount = request.form['amount']
        payment_date = request.form['payment_date']
    try:
        sql = f"INSERT INTO Payments (member_email,amount,payment_date) VALUES ('{member_email}', {amount}, '{payment_date}');"
        db.executeStatement(sql, commit=True)
        return redirect(url_for('memberPage'))
    except SQLAlchemyError as error:
        return redirect(url_for('memberPage'))


@app.route('/update_trainer_members', methods=['POST'])
def update_trainer():
    if request.method == 'POST':
        member_email = session['email']
        name = request.form['trainer']
    try:
        sql = f" update trainers set member_email = '{member_email}' where name = '{name}';"
        db.executeStatement(sql, commit=True)
        return redirect(url_for('memberPage'))
    except SQLAlchemyError as error:
        return redirect(url_for('memberPage'))


@app.route('/addUser', methods=['POST'])
def addUser():
    if request.method != 'POST': return
    actionType = request.form["type"]
    userType = request.form["userType"]
    userName = request.form['userName']
    userEmail = request.form['userEmail']
    userPassword = request.form['userPassword']

    if actionType == "Create":
        if userType == "Member":
            db.insertMember(userName, userEmail, userPassword, date.today())
        else:
            db.insertTrainers(userName, userEmail, userPassword, date.today())
    elif actionType == "Login":
        for userType in ("Admins", "Members", "Trainers"):
            query = f"Select * From {userType} Where email='{userEmail}' and password='{userPassword}';"
            result = db.executeStatement(query)
            if result is not None:
                userData = result.all()
                if len(userData) > 0:
                    session['email'] = userEmail
                    break
        else:
            return render_template(
                'homePage.html',
                errorTitle="Can't find User",
                errorMessage=rf"Invalid User({userEmail}) in database! Create the user."
            )
        if userType == "Admins":
            return redirect(url_for('adminPage'))
        elif userType == "Trainers":
            return redirect(url_for('trainerPage'))
        elif userType == "Members":
            return redirect(url_for('memberPage', var_name=userEmail))
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
