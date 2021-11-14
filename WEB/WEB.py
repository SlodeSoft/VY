import os.path
import re
from datetime import timedelta
from flask import Flask, render_template, request, session, redirect, url_for
from lib import WEBTOMYSQL as CONNEC
from lib import SECRET as SCRT
# from netmiko import ConnectHandler

# BEGIN Configuration and Web display
__STATIC_DIR = os.path.abspath('./static')
__TEMPLATE_DIR = os.path.abspath('./templates')

app = Flask(__name__, static_folder=__STATIC_DIR, template_folder=__TEMPLATE_DIR)
title = "VyOS Manager"
app.secret_key = ';VQE\3@5v5o03BKvd%[}j5@chul(z"8]ZG`=}#?uY&NhE)Sob-'


class CONNECTION:
    def __init__(self):
        bddconn = CONNEC.CONNECT_TO_BDD()
        self.cursor = bddconn.connection.cursor()


"""class VYOS_GET:
    def get(self, host, user, pwd, port, cmd):
        __vyos_router__ = {
            'device-type': "vyos",
            'host': host,
            'username': user,
            'password': pwd,
            'port': port
        }
        __net_connect__ = ConnectHandler(**__vyos_router__)
        __config_commands__ = [cmd]
        # launch command
        output = __net_connect__.send_command(__config_commands__)
        print(output)
        # commit configuration"""


bddcon = CONNECTION()
set_key = SCRT.__quatre__.__entry__.password
set_iv = SCRT.__cinq__.__entry__.password


# LOGIN / REGISTRY / LOGOUT - Manage Connection Users

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html',
                               stylelogin="./static/stylelogin.css",
                               title=title)
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL

        sql = 'CALL `SELECT_CRYPT_USER_INFO`(%s, %s, %s, %s)'
        values = (set_key,
                  set_iv,
                  username,
                  password)
        bddcon.cursor.execute(sql, values)
        # Fetch one record and return result
        account = bddcon.cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            # Redirect to Home Page
            app.permanent_session_lifetime = timedelta(minutes=30)
            return redirect(url_for('main'))
        else:
            msg = 'Incorrect username/password'
    return render_template('login.html',
                           stylelogin="./static/stylelogin.css",
                           title=title, msg=msg)


@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirect to login page
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form \
            and 'password' in request.form \
            and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        # Check if account exists using MySQL
        sql = "CALL `SELECT_REGISTRY_USER`(%s, %s, %s)"
        values = (set_key,
                  set_iv,
                  username)
        bddcon.cursor.execute(sql, values)
        account = bddcon.cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            print(account[0])
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            sql = "CALL `INSERT_CRYPT_USER_INFO`(%s, %s, %s, %s, %s)"
            values = (set_key,
                      set_iv,
                      username,
                      password,
                      email)
            bddcon.cursor.execute(sql, values)
            bddcon.cursor.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html',
                           stylelogin="./static/stylelogin.css",
                           msg=msg)


# Main display and function Configuration Routers
@app.route('/main', methods=['GET', 'POST'])
def main():
    # if 'loggedin' in session:
    bddcon.cursor.execute('SELECT host FROM `VY-RT-INFO`;')
    row = bddcon.cursor.fetchall()
    return render_template('main.html',
                           stylesbuttoninput='./static/styles-button-input.css',
                           title=title,
                           row=row)
    # else:
    #   return redirect(url_for('login'))


@app.route('/add-vy', methods=['GET', 'POST'])
def addvy():
    msg = ''
    if request.method == 'POST':
        host = request.form['host']
        user = request.form['username']
        paswd = request.form['password']
        port = request.form['port']
        # Check if account exists using MySQL
        sql = 'SELECT host FROM `VY-RT-INFO` WHERE host = %s'
        bddcon.cursor.execute(sql, host)
        submit = bddcon.cursor.fetchone()
        """sql = "CALL `SELECT_REGISTRY_VY`(%s, %s, %s)"
        values = (set_key,
                  set_iv,
                  host)
        bddcon.cursor.execute(sql, values)
        submit = bddcon.cursor.fetchone()
        # If account exists show error and validation checks"""
        if submit:
            print(submit[0])
            msg = 'Device already exists !'
            return msg
        elif not re.match(r'^([0-9]{1,3}\.){3}[0-9]{1,3}$', host):
            msg = 'Invalid ip address, must be e.g 1.2.3.4 !'
        elif not re.match(r'[0-9]+', port):
            msg = "Invalid Port, must be integer e.g 22 !"
        elif not user or not paswd or not port or not host:
            msg = "Not Valid form, check informations's device !"
        else:
            """sql = "CALL `INSERT_NEW_VY`(%s, %s, %s)"
            values = (set_key,
                      set_iv,
                      host)
            bddcon.cursor.execute(sql, values)
            submit = bddcon.cursor.fetchone()
            # If account exists show error and validation checks"""
            # Device doesnt exists and the form data is valid, now insert new account into accounts table
            msg = "VyOS Device Added !"
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form !'
    return render_template('add-vy.html',
                           stylesbuttoninput='./static/styles-button-input.css',
                           title=title,
                           msg=msg)


@app.route('/config', methods=['GET', 'POST'])
def config():
    msg = ''
    gethost = request.args.get('hst', type=str)
    if request.method == 'POST':
        shconfig = request.form.get('shconfig')
        return "?"
    if request.method == 'GET':
        return render_template('config.html',
                               stylesbuttoninput='./static/styles-button-input.css',
                               title=title,
                               msg=msg)


"""# Config Flask Specific, page error & config
@app.errorhandler(404)
def page_not_found():
    return render_template('404.html',
                           stylesgeneral="./static/stylesgeneral.css",
                           styles404="./static/styles404.css",
                           title=title), 404


@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=5)"""


if __name__ == "__main__":
    app.run(debug=True, port=80)
