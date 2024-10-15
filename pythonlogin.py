# use these steps to free-up a port number
# lsof -i: port_number
# kill -9 ID of process
# mysql case sensitive use COLLATE utf8mb3_bin
# ==================================================
# pip install flask-debugtoolbar to debug
# initiate the virtual environment
# Uses .venv python 3.12.3
# 1. » source .venv/bin/activate
# 2. » sudo ./rungunicordpythonlogin.sh
# 3 Add a breakpoint in pythonlogin.py
# 4. » click arrow on left side "Run and Debug"


import os
import re
import hashlib
from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from dotenv import load_dotenv
import hashlib

from flask import current_app

load_dotenv()


def before_first_request():
    print("Debug Mode:", current_app.debug)

print("FLASK_DEBUG:", os.getenv("FLASK_DEBUG"))
print("FLASK_APP:", os.getenv("FLASK_APP"))

def validate_and_register(username, password, email):

    # Create variables for easy access
    # Check if account exists using MySQL
    """
    Validate and register a new account.

    :param username: The username to check for availability and to register.
    :type username: str
    :param password: The password to hash and store with the new account.
    :type password: str
    :param email: The email address to check for validity and to store with the new account.
    :type email: str
    :return: A string containing either an error message or a success message.
    :rtype: str
    """

    result = ""
    msg = ""
    try:
        qry = f"SELECT * FROM accounts a WHERE a.username = '{username}'"
        with db.cursor() as cursor:
            cursor.execute(qry)
            result = cursor.fetchone()
            print(f"validate_and_register: cursor.rowcount is {cursor.rowcount}")
            # # Close the cursor and the connection
            # cursor.close()
            # db.close()
    except Exception as err:
        print("Error:", err)

    read_username = ""
    read_email = ""

    if result:
        read_username = result[1]
        read_email = result[3]

    # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # cursor.execute(qry, username)

    # account = cursor.fetchone()

    # If account exists show error and validation checks
    if read_username == username:
        msg = "Account already exists!"
    elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        msg = "Invalid email address!"
    elif not re.match(r"[A-Za-z0-9]+", username):
        msg = "Username must contain only characters and numbers!"
    elif not username or not password or not email:
        msg = "Please fill out the form!"
    else:
        # Hash the password
        hash = password + app.secret_key
        hash = hashlib.sha1(hash.encode())
        password = hash.hexdigest()
        # Account doesn't exist, and the form data is valid, so insert the new account into the accounts table
        # Check if account exists using MySQL
        # cursor.execute(
        #     'INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
        # mysql.connection.commit()
        try:
            qry = f'INSERT INTO accounts VALUES (NULL, "{username}", "{password}", "{email}")'
            with db.cursor() as cursor:
                cursor.execute(qry)
                db.commit()
                msg = "You have successfully registered!"
        except Exception as err:
            print("Error:", err)

    return msg


# Establish a database connection
db_config = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_DBNAME"),
}

db = mysql.connector.connect(**db_config)
# try:
#     db.cursor().execute('SELECT 1')
# finally:
#     db.close()


cursor = db.cursor()


# Set the secret key
app = Flask(__name__)
secret_key = os.getenv("SECRET_KEY")
app.secret_key = secret_key

# http://localhost:5000/pythonlogin/profile - this will be the profile page, only accessible for logged in users

#
#  url_for( PROFILE )
#


@app.route("/pythonlogin/profile", endpoint="profile")
def profile():
    # Check if the user is logged in
    # fetchone() returns a tuple. In this case,
    # account
    # 0:1
    # 1:'test'
    # 2:'7288edd0fc3ffcbe93a0cf06e3568e28521687bc'
    # 3:'test@test.com'
    # len():4
    #
    result = ""
    if "logged_in" in session:
        # We need all the account info for the user so we can display it on the profile page
        # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        try:
            qry = f'SElECT * FROM accounts where id = {session["id"]}'
            with db.cursor() as cursor:
                cursor.execute(qry)
                result = cursor.fetchone()
                print(f"profile: cursor.rowcount is {cursor.rowcount}")
        except Exception as err:
            print("Error:", err)

        # Show the profile page with account info
        return render_template("profile.html", account=result)
    # User is not logged in redirect to login page
    return redirect(url_for("login"))


#
#  url_for( HOME )
#


@app.route("/pythonlogin/home", endpoint="home")
def home():
    # Check if the user is logged in
    if "logged_in" in session:
        # User is logged-in show them the home page
        return render_template("home.html", username=session["username"])
    else:
        # User is not logged-in redirect to login page
        return redirect(url_for("login"))


# http://ip:port/pythonlogin/register - this will be the registration page, we need to use both GET and POST requests

#
#  url_for( REGISTER )
#


@app.route("/pythonlogin/register/", methods=["GET", "POST"], endpoint="register")
def register():
    # Output message if something goes wrong...
    msg = ""
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if (
        request.method == "POST"
        and "username" in request.form
        and "password" in request.form
        and "email" in request.form
    ):
        # Create variables for easy access
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]
        msg = validate_and_register(username, password, email)
    elif request.method == "POST":
        # Form is empty... (no POST data)
        msg = "Please fill out the form!"
    # Show registration form with message (if any)
    return render_template("register.html", msg=msg)


# http://192.168.1.9:3200/pythonlogin/logout - this will be the logout page

#
#  url_for( LOGOUT )
#


@app.route("/pythonlogin/logout/", endpoint="logout")
def logout():
    # Remove session data, this will log the user out
    session.pop("logged_in", None)
    session.pop("id", None)
    session.pop("username", None)
    # Redirect to login page
    return redirect(url_for("login"))


#
#  url_for( LOGIN )
#


@app.route("/", methods=["GET", "POST"], endpoint="login")
def login():

    # Output a message if something goes wrong...
    msg = ""
    result = ""
    # Check if "username" and "password" POST requests exist (user submitted form)
    if (
        request.method == "POST"
        and "username" in request.form
        and "password" in request.form
    ):
        # Create variables for easy access
        username = request.form["username"]
        password = request.form["password"]
        # Retrieve the hashed password
        hash = password + app.secret_key
        hash = hashlib.sha1(hash.encode())
        password = hash.hexdigest()

        # Check if account exists using MySQL for username and password fields
        # qry = 'SELECT * FROM accounts WHERE username = %s AND password = %s', (
        #     username, password,)
        try:
            qry = f'SELECT * FROM accounts a WHERE a.username = "{username}" and a.password = "{password}"'
            with db.cursor() as cursor:
                cursor.execute(qry)
                result = cursor.fetchone()
                print(f"login: cursor.rowcount is {cursor.rowcount}")
        except Exception as err:
            print("Error:", err)

        read_session_id = 0
        read_username = ""
        read_email = ""

        if result:
            read_session_id = result[0]
            read_username = result[1]
            read_email = result[3]

        # If account exists in accounts table in out database
        if read_username == username:
            # Create session data, we can access this data in other routes
            session["logged_in"] = True
            session["id"] = result[0]
            session["username"] = result[1]

            # Redirect to home page
            # return 'Logged in successfully!'
            return redirect(url_for("home"))
        else:
            # Account doesn't exist or username/password incorrect
            msg = "Incorrect username/password!"
    # Show the login form with message (if any)
    return render_template("index.html", msg=msg)


if __name__ == "__main__":
    app.run(host="192.168.1.176", port=3100, debug=True)
