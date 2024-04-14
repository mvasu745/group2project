from flask import Flask, render_template, request, send_file, Response
from pymysql import connections
import os
import boto3
import random
import argparse
from io import BytesIO

app = Flask(__name__)

DBHOST = os.environ.get("DBHOST") or "localhost"
DBUSER = os.environ.get("DBUSER") or "root"
DBPWD = os.environ.get("DBPWD") or "password"
DATABASE = os.environ.get("DATABASE") or "employees"
BUCKETNAME = os.environ.get("BUCKETNAME") or "clo800projectbucket"
GROUPNAME = os.environ.get("GROUPNAME") or "Group2"
DBPORT = int(os.environ.get("DBPORT", "3306"))

# Create a connection to the MySQL database
db_conn = connections.Connection(
    host=DBHOST,
    port=DBPORT,
    user=DBUSER,
    password=DBPWD,
    db=DATABASE
)

default_image = "image1.jpg"
default_bucket = 'clo800projectbucket'

@app.route("/download", methods=['GET', 'POST'])
def download(bucket=default_bucket, imageName=default_image):
    try:
        s3 = boto3.client('s3')
        image_object = s3.get_object(Bucket=bucket, Key=imageName)
        image_stream = BytesIO(image_object['Body'].read())  # Convert to BytesIO object

        # Set the appropriate content type
        content_type = image_object['ContentType']

        return image_stream, content_type  # Return image stream and content type

    except Exception as error:
        print("Error occurred while fetching the image!", error)
        return str(error), 500  # Return an error message with status code 500 if there's an error

@app.route("/", methods=['GET', 'POST'])
def home():
    image_stream, content_type = download(BUCKETNAME, default_image)
    return render_template('addemp.html', image_stream=image_stream, content_type=content_type, group_name=GROUPNAME)



@app.route("/about", methods=['GET', 'POST'])
def about():
    image_stream, content_type = download(BUCKETNAME, default_image)
    return render_template('about.html', image_stream=image_stream, content_type=content_type, group_name=GROUPNAME)


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
        cursor.execute(insert_sql, (emp_id, first_name, last_name, primary_skill, location))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name

    finally:
        cursor.close()

    print("all modifications done...")
    return render_template('addempoutput.html', name=emp_name, group_name=GROUPNAME)


@app.route("/getemp", methods=['GET', 'POST'])
def GetEmp():
    return render_template("getemp.html", group_name=GROUPNAME)


@app.route("/fetchdata", methods=['GET', 'POST'])
def FetchData():
    emp_id = request.form['emp_id']

    output = {}
    select_sql = "SELECT emp_id, first_name, last_name, primary_skill, location from employee where emp_id=%s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql, (emp_id,))
        result = cursor.fetchone()

        output["emp_id"] = result[0]
        output["first_name"] = result[1]
        output["last_name"] = result[2]
        output["primary_skills"] = result[3]
        output["location"] = result[4]

    except Exception as error:
        print(error)

    finally:
        cursor.close()

    return render_template("getempoutput.html", id=output["emp_id"], fname=output["first_name"], lname=output["last_name"], interest=output["primary_skills"], location=output["location"],group_name=GROUPNAME)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)