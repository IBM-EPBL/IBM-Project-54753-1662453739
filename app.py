from flask import Flask, flash, redirect, render_template, request, session, url_for

from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import pickle
import cv2
from skimage import feature
import os.path

import sqlite3


app=Flask(__name__)


app.secret_key="#@universityflaskapp@#"

# email verification

app.config.from_pyfile('config.cfg')

mail=Mail(app)

s = URLSafeTimedSerializer(app.config['SECRET_KEY']) 


# database creation
con=sqlite3.connect("database.db")
print("Opened database successfully")
con.execute("create table if not exists customer(pid integer primary key, name text, email text, password text,status BOOLEAN)")
print("Table created successfully")
con.close()



@app.route('/signup',methods=['GET','POST'])
def signup():
  if request.method == 'POST':
        try:
            name=request.form['name']
            email=request.form['email']
            password=request.form['password']
            con=sqlite3.connect("database.db")
            cur=con.cursor()
            cur.execute("INSERT INTO customer(name,email,password) VALUES (?,?,?)",(name,email,password))
            con.commit()
            flash("Registered successfully","success")
        except:
            con.rollback()  
            flash("Problem in Registration, Please try again","danger")
        finally:
            return redirect(url_for("index"))
            con.close()
  else:
        return render_template('signup.html')

@app.route('/login',methods=['POST','GET'])
def login():
  if request.method =='POST':
        email = request.form['email']
        password = request.form['password']
        con=sqlite3.connect("database.db")
        con.row_factory=sqlite3.Row
        cur=con.cursor()
        cur.execute("SELECT * FROM customer where email=? and password=?",(email,password))
        data=cur.fetchone()

        if data:
            session["email"]=data["email"]
            print("sent to home")
            return redirect(url_for("home"))
                      
        else:
            flash("Username or Password is incorrect","danger")
            print("not sent to home")
  return redirect(url_for("home"))
  
@app.route('/')
def index():
  return render_template("index.html")

@app.route('/home')
def home():
  return render_template("homepage.html")

@app.route('/prediction')
def prediction():
  return render_template("prediction.html")

@app.route('/images')
def images():
  return render_template("image.html")

@app.route('/contact')
def contact():
  return render_template("contact.html")

@app.route('/explore')
def explore():
  return render_template("explore.html")

@app.route('/logout')
def logout():
    session.clear()
    return render_template('index.html')


@app.route('/healthy')
def healthy():
    return render_template('healthy.html')

@app.route('/parkinson')
def parkinson():
    return render_template('parkinson.html')

@app.route('/check')
def check():
    email = session["email"]
    con=sqlite3.connect("database.db")
    cur=con.cursor()
    cur.execute("SELECT status FROM customer where email=?",[email])
    data=cur.fetchone()
    con.commit()
    print(data)
    if data[0]==1:
        return render_template('prediction.html')
    else:
        return render_template('verify.html')

@app.route('/verify')
def verify():
    email = session["email"]

    token = s.dumps(email, salt='email-confirm')

    msg=Message('Confirm Email', sender='ibmproject2023@gmail.com.', recipients=[email])

    link=url_for('confirm_email', token=token, _external=True)

    msg.body= 'Please click the link to verify your account to continue  : {} '.format(link)

    mail.send(msg)
    return render_template("homepage.html")

@app.route('/confirm_email/<token>')
def confirm_email(token):
  try:
    email=s.loads(token, salt='email-confirm' , max_age=3600*5)
  except SignatureExpired:
    return render_template("verify.html")
  con=sqlite3.connect("database.db")
  con.row_factory=sqlite3.Row
  cur=con.cursor()
  cur.execute("UPDATE customer SET status = 1 WHERE email = ?",(email,))
  con.commit()
  con.close()
  return redirect(url_for("prediction"))



@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        f = request.files['file2']  # requesting the file
        #filename_secure = secure_filename(f.filename)
        basepath = os.path.dirname(
            '__file__')  # storing the file directory
        # storing the file in uploads folder
        filepath = os.path.join(basepath, "uploads", f.filename)
        f.save(filepath)  # saving the file

        # Loading the saved model
        print("[INFO] loading model...")
        model = pickle.loads(open('parkinson.pkl', "rb").read())
        ''' local_filename = "./uploads/"
        local_filename += filename_secure
        print(local_filename)'''

        # Pre-process the image in the same manner we did earlier
        image = cv2.imread(filepath)
        output = image.copy()

        # Load the input image, convert it to grayscale, and resize
        output = cv2.resize(output, (128, 128))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = cv2.resize(image, (200, 200))
        image = cv2.threshold(image, 0, 255,
                              cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

        # Quantify the image and make predictions based on the extracted features using the last trained Random Forest
        features = feature.hog(image, orientations=9,
                               pixels_per_cell=(10, 10), cells_per_block=(2, 2),
                               transform_sqrt=True, block_norm="L1")
        preds = model.predict([features])
        print(preds)
        ls = ["healthy", "parkinson"]
        result = ls[preds[0]]
        '''color = (0, 255, 0) if result == "healthy" else (0, 0, 255)
        cv2.putText(output, result, (3, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        cv2.imshow("Output", output)
        cv2.waitKey(0)'''
        if result =="healthy":
          return redirect("healthy")
        else:
          return redirect("parkinson")
          
    return None
if __name__=='__main__':
  app.run(Debug=True)