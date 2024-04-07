from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from werkzeug.utils import secure_filename
import bcrypt  # Added for password hashing
import os

app = Flask(__name__)

app.secret_key = 'your_secret_key'  # Replace with a randomly generated secret key

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Pt47nol3@'
app.config['MYSQL_DB'] = 'Codement'

mysql = MySQL(app)

app.config['UPLOAD_FOLDER'] = 'static/images'

# Function to hash passwords
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def save_upload(uploaded_file, current_user):
  """
  This function saves the uploaded file with a user-specific folder.

  Args:
      uploaded_file: The uploaded file object from the form submission.
      current_user: The current user object (assuming you have user authentication).

  Returns:
      The filepath where the file is saved (or None if there's an error).
  """

  if uploaded_file.filename != '':
    # Secure the filename
    filename = secure_filename(uploaded_file.filename)

    # Get the upload folder path from config
    upload_folder = app.config['UPLOAD_FOLDER']

    # Create user-specific folder path
    user_folder = os.path.join(upload_folder, str(current_user))

    # Create the user folder if it doesn't exist
    if not os.path.exists(user_folder):
      os.makedirs(user_folder)

    # Build the complete filepath
    filepath = os.path.join(user_folder, filename)

    # Save the uploaded file
    uploaded_file.save(filepath)

    return filepath
  else:
    return None

@app.route('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        hashed_password = hash_password(password)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM patient WHERE email = %s', (email,))
        account = cursor.fetchone()
        if account and bcrypt.checkpw(password.encode('utf-8'), account['password'].encode('utf-8')):
            session['loggedin'] = True
            session['id'] = account['id']
            session['email'] = account['email']
            msg = 'Logged in successfully!'
            return render_template('pd2.html', msg=msg)
        else:
            msg = 'Incorrect username / password!'
    return render_template('index.html', msg=msg)


@app.route('/login2', methods=['GET', 'POST'])
def logi():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
       username = request.form['username']
       password = request.form['password']
       cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
       cursor.execute('SELECT * FROM doctors WHERE username = % s AND password = % s', (username, password, ))
       account = cursor.fetchone()
       if account :
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg = 'Logged in successfully!'
            return render_template('db4.html', msg=msg)
       else:
            msg = 'Incorrect username / password!'
    return render_template('index.html', msg=msg)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('email', None)
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'fullname' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['fullname']
        password = request.form['password']
        email = request.form['email']
        dob = request.form['dob']
        selected_value = request.form.get('gender')
        phone = request.form['phone']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM patient WHERE email = %s', (email,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            hashed_password = hash_password(password)
            cursor.execute('INSERT INTO patient VALUES (NULL, %s, %s, %s,%s,%s)', (username, hashed_password, email, selected_value, phone,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        uploaded_file = request.files['image']
        date = request.form.get('date')  # Get comment from form (if present)
        disease = request.form.get('disease')
       
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        current_user=cursor.execute('SELECT * FROM patient WHERE email = %s', (session['email']  ,) )
        filename=save_upload(uploaded_file, current_user)
        
           # new_image = Image(NULL, filename=filename, comment=comment)  # Store comment
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO images VALUES (NULL,  % s, % s , %s)', ( filename, date,disease ))
        mysql.connection.commit()
           # db.session.add(new_image)
           # db.session.commit()

        return redirect(url_for('show_images'))

    return render_template('upload.html')


@app.route('/images')
def show_images():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM images")
    images = cursor.fetchall()  # Fetch all images
    return render_template('images.html', images=images)