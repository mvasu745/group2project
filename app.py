from flask import Flask, render_template, request
import boto3
from pymysql import connections
import os
import random
import argparse

app = Flask(__name__)


DBHOST = os.environ.get("DBHOST") or "localhost"
DBUSER = os.environ.get("DBUSER") or "root"
DBPWD = os.environ.get("DBPWD") or "password"
DATABASE = os.environ.get("DATABASE") or "employees"
DBPORT = int(os.environ.get("DBPORT")) or "3306"
AWS_BUCKET_NAME = os.environ.get("AWS_BUCKET_NAME") or "group2-project"
IMAGE_NAME = os.environ.get("IMAGE_NAME") or "project.jpg"
GROUP_NAME = os.environ.get("GROUP_NAME") or "Group2"
GROUP_SLOGAN = os.environ.get("GROUP_SLOGAN") or "Keep Trying Until You Succeed"

# Create a connection to the MySQL database
db_conn = connections.Connection(
    host= DBHOST,
    port=DBPORT,
    user= DBUSER,
    password= DBPWD, 
    db= DATABASE
    
)
output = {}
table = 'employee';

def download_image(bucket, image):
    if not os.path.exists('static'):
        os.makedirs('static')
    output_file = 'static/background.jpg'
    print(bucket, image)
    s3 = boto3.resource('s3')
    s3.Bucket(bucket).download_file(image, output_file)
    return output_file

@app.route("/download_image", methods=['GET', 'POST'])
def download_image_route():
    image_path = download_image(AWS_BUCKET_NAME, IMAGE_NAME)
    return image_path

# Route to render the homepage
@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('addemp.html', background_image=bg, group_name=GROUP_NAME, group_slogan=GROUP_SLOGAN)

# Route to render the about page
@app.route("/about", methods=['GET','POST'])
def about():
    return render_template('about.html', background_image=bg)

# Route to render the AddEmp page
@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    primary_skill = request.form['primary_skill']
    location = request.form['location']

  
    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:
        
        cursor.execute(insert_sql,(emp_id, first_name, last_name, primary_skill, location))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('addempoutput.html', name=emp_name, background_image=bg)

# Route to render the GetEmp page
@app.route("/getemp", methods=['GET', 'POST'])
def GetEmp():
    return render_template("getemp.html", background_image=bg)

# Route to render the FetchData page
@app.route("/fetchdata", methods=['GET','POST'])
def FetchData():
    emp_id = request.form['emp_id']

    output = {}
    select_sql = "SELECT emp_id, first_name, last_name, primary_skill, location from employee where emp_id=%s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql,(emp_id))
        result = cursor.fetchone()
        
        # Add No Employee found form
        output["emp_id"] = result[0]
        output["first_name"] = result[1]
        output["last_name"] = result[2]
        output["primary_skills"] = result[3]
        output["location"] = result[4]
        
    except Exception as e:
        print(e)

    finally:
        cursor.close()

    return render_template("getempoutput.html", id=output["emp_id"], fname=output["first_name"],
                           lname=output["last_name"], interest=output["primary_skills"], location=output["location"], background_image=bg)

if __name__ == '__main__':
    bg = download_image(AWS_BUCKET_NAME, IMAGE_NAME)
    print(bg)
    app.run(host='0.0.0.0', port=8080, debug=True)
