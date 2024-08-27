from flask import Flask, render_template, request
import csv
from datetime import datetime, timedelta
import logging
import os

logging.basicConfig(filename='flask_errors.log', level=logging.ERROR)

template = "./template"
appointments_csv = "./appointments.csv"
app = Flask(__name__, template_folder=template)

# Function to create or get doctor's CSV file path
def get_doctor_csv_path(doctor):
    doctor_csv_path = f"./doctors/{doctor}_appointments.csv"
    if not os.path.exists(doctor_csv_path):
        with open(doctor_csv_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Date', 'Time', 'Name'])  # Header for the CSV
    return doctor_csv_path

# Function to save appointment to doctor's CSV file
def save_to_doctor_csv(doctor, date, time, name):
    doctor_csv_path = get_doctor_csv_path(doctor)
    with open(doctor_csv_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([date, time, name])

def save_to_csv(name, date, time):
    try:
        print(f"Before writing to CSV: {appointments_csv}")
        print(f"Name: {name}, Date: {date}, Time: {time}")

        with open(appointments_csv, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([name, date, time,])

        print("Successfully wrote to CSV")
    except FileNotFoundError:
        print(f"Error: CSV file not found at path: {appointments_csv}")
    except PermissionError:
        print(f"Error: Permission issue. Check if the script has write access to the CSV file.")
    except Exception as e:
        print(f"Error writing to CSV: {e}")

def save_to_csv2(name, date, time):
    try:
        print(f"Before writing to CSV: contact_csv")
        print(f"Name: {name}, Date: {date}, Time: {time}")

        with open('contact_csv.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([name, date, time,])

        print("Successfully wrote to CSV")
    except FileNotFoundError:
        print(f"Error: CSV file not found at path: {appointments_csv}")
    except PermissionError:
        print(f"Error: Permission issue. Check if the script has write access to the CSV file.")
    except Exception as e:
        print(f"Error writing to CSV: {e}")

def check_time_conflict(new_time, existing_time):
    new_start, new_end = parse_time_interval(new_time)
    existing_start, existing_end = parse_time_interval(existing_time)
    print(f"New start: {new_start}, New end: {new_end}")
    return new_start < existing_end and new_end > existing_start

def parse_time_interval(time_string):
    start_time = datetime.strptime(time_string, '%Y-%m-%d %H:%M')
    end_time = start_time + timedelta(hours=1)
    return start_time, end_time

def save_to_txt(name, date, medical_history, current_problems):
    file = open(f"MedicalHistory\\{name}", 'a')
    file.write(f"\nDate: {date}\nMedical History:\n {medical_history}\nCurrent Problems:\n{current_problems}")
    file.close()

@app.route('/', methods=['GET', 'POST'])
def book_appointment():
    try:
        if request.method == 'POST':
            name = request.form['name']
            date = request.form['date']
            time = request.form['time']
            doctor = request.form['doctor']  # Added line to get the selected doctor
            medical_history = request.form['medical_history']
            current_problems = request.form['current_problems']

            # Check if the selected date is not in the past
            current_date = datetime.now()
            selected_date = datetime.strptime(date, '%Y-%m-%d')

            if selected_date < current_date:
                return "Please select a future date."

            # Check for time conflicts
            with open(appointments_csv, mode='r') as file:
                reader = csv.reader(file)
                print(f"Checking for time conflicts for {date} {time}")
                for row in reader:
                    existing_date_time = f"{row[1]} {row[2]}"
                    print(f"Checking against: {existing_date_time}")
                    if check_time_conflict(f"{date} {time}", existing_date_time):
                        print("Time conflict found")
                        return "Error: Two appointments cannot coincide within one hour."
                    else:
                        print("No time conflicts found")

            # Save to CSV if all checks pass
            print("Saving to CSV")
            save_to_txt(name.lower(), date, medical_history, current_problems)
            save_to_csv(name.lower(), date, time)

            # Save to doctor's CSV
            save_to_doctor_csv(doctor, date, time, name)

            return "Appointment booked successfully!"

        # Move the render_template line inside the conditional block for the GET request
        return render_template('newappoi.html')

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return f"An error occurred: {e}", 500

@app.route('/home')
def wow():
    return render_template('landing2.html')

@app.route('/faculty')
def fac():
    return render_template('faculty.html')

@app.route('/contactus', methods=['GET', 'POST'])
def con():
    if request.method == 'POST':
        try:
            name = request.form['name']
            email = request.form['email']
            message = request.form['message']

            # Save contact form submission to the existing CSV file
            data_to_save_contact = [name, email, message]
            save_to_csv2(name, email, message)

            return "Form submitted successfully!"
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return f"An error occurred: {e}", 500

    return render_template('contactus.html')

if __name__ == '__main__':
    app.run(debug=True, port=8001)
