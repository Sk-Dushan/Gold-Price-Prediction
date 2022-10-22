from flask import request, Flask, render_template, redirect, session
import mysql.connector
import pandas as pd 
import numpy as np
import pickle
import os
from sklearn.ensemble import RandomForestRegressor

app = Flask(__name__)
app.secret_key=os.urandom(24)

conn=mysql.connector.connect(host="localhost",user="root",password="",database="gold")
cursor=conn.cursor()

model1 = pickle.load(open('RF_regressor.pkl', 'rb'))

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/home')
def home():
    if 'id' in session:
      return render_template('home.html')
    else:
      return redirect('/')

@app.route('/login_validation', methods=['POST'])
def login_validation():
    name=request.form.get('name')
    password=request.form.get('password')

    cursor.execute("""SELECT * FROM `user` WHERE `name` LIKE '{}' AND `password` LIKE '{}'"""
    .format(name,password))
    users=cursor.fetchall()

    if len(users)>0:
      session['id']=users[0][0]
      return redirect('/home')
    else:
      return render_template("login.html")

@app.route('/sing_up', methods=['POST'])
def sing_up():
    name=request.form.get('username')
    email=request.form.get('useremail')
    password=request.form.get('password')
    location=request.form.get('location')
    number=request.form.get('number')

    cursor.execute("""INSERT INTO `user` (`id`,`name`,`email`,`password`,`location`,`number`) VALUES(NULL,'{}','{}','{}','{}','{}')""".format(name,email,password,location,number))
    conn.commit()

    cursor.execute("""SELECT * FROM `user` WHERE `name` LIKE '{}'""".format(name))
    myuser=cursor.fetchall()
    session['id']=myuser[0][0]
    return redirect('/home')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/predict',methods=['POST'])
def predict():
    features = request.form
    print(features)
    Silver_Price_gram = features['Silver_Price_gram']
    USD_rate = features['USD_rate']
    Crude_oil = features['Crude_oil']
    

    user_input = {'Silver_Price_gram':[Silver_Price_gram],'USD_rate':[USD_rate],'Crude_oil':[Crude_oil]}
    test_df = pd.DataFrame(user_input)


    test_df = pd.concat([test_df],axis=1) 


    print(test_df)


    prediction = model1.predict(test_df)

    output = float(np.round(prediction[0], 2))

    print(output)

    return render_template('index.html', prediction_text='Predicted Price of Gold (1 Gram) is Rs. {}'.format(output))


if __name__ == "__main__":
    app.run(debug=True)