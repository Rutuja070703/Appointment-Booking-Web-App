from flask import Flask, request, jsonify, render_template, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///appointments.db'
app.secret_key = 'Lol'
db = SQLAlchemy(app)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    lesson_date = db.Column(db.DateTime, nullable=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/book_appointment', methods=['GET', 'POST'])
def book_appointment():
    if request.method == 'POST':
        if request.headers.get('Content-Type') == 'application/json':
            return chatbot_response()
        
        details = request.form
        name = details['name']
        email = details['email']
        phone = details['phone']
        lesson_date = details['lesson_date']
        lesson_date = datetime.strptime(lesson_date, '%Y-%m-%dT%H:%M')
        appointment = Appointment(name=name, email=email, phone=phone, lesson_date=lesson_date)
        db.session.add(appointment)
        db.session.commit()
        flash(f"An appointment has been booked for {name} on {lesson_date.strftime('%Y-%m-%d %H:%M')} with your appointment id {appointment.id}")
        return redirect(url_for('index'))
    return render_template('book_appointment.html')


@app.route('/cancel_appointment', methods=['GET', 'POST'])
def cancel_appointment():
    if request.method == 'POST':
        if request.headers.get('Content-Type') == 'application/json':
            return chatbot_response()

        appointment_id = request.form.get('id')

        # Check if the appointment ID is provided
        if not appointment_id:
            flash("Please provide the appointment ID.")
            return redirect(url_for('cancel_appointment'))

        # Check if the appointment exists
        appointment = Appointment.query.get(appointment_id)
        if appointment:
            db.session.delete(appointment)
            db.session.commit()
            flash(f"Appointment with ID {appointment_id} has been canceled.")
        else:
            flash(f"No appointment found with ID {appointment_id}.")

        return redirect(url_for('index'))

    return render_template('cancel_appointment.html')


@app.route('/chatbot', methods=['POST'])
def chatbot_response():
    data = request.json
    message = data.get('message')
    response = {}

    if "schedule" in message.lower() or "appointment" in message.lower():
        response['message'] = "Sure, let's schedule an appointment. Please fill out the form."
        response['redirect'] = url_for('book_appointment')
    if "delete" in message.lower() or "cancel" in message.lower():
        response['message'] = " Please fill out the id to cancel appointment."
        response['redirect'] = url_for('cancel_appointment')

    elif message.lower() in ["hii", "hi", "hey", "hello", "hiya", "good morning"]:
        response['message'] = "Hey there! How can I help you today?"
    else:
        response['message'] = "I'm sorry, I didn't understand that. Please choose from the available options."

    return jsonify(response)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
