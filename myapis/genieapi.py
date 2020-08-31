from flask import Flask,request
from flask_restful import Resource, Api
from flask_mysqldb import MySQL
from passlib.hash import bcrypt

app = Flask(__name__)
api = Api(app)
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'ZohoTest@24'
app.config['MYSQL_DB'] = 'login'
app.config['MYSQL_PORT'] = 3306




mysql = MySQL(app)


#Handles DB Operation
class DB:

    result=None

    @classmethod
    def getConnection(cls):
        return mysql.connection.cursor()

    @classmethod
    def readData(cls,query):
        print(query)
        updateMsg="False"
        try:
            cursor=DB.getConnection()
            cursor.execute(query)
            DB.result=cursor.fetchall()

        except Exception as e:
            updateMsg="Exception"+str(e)

        if updateMsg.find("Exception") >= 0:
            DB.result =()

        return DB.result

    @classmethod
    def updateData(cls, query):
        updateMsg='False'

        try:
            DB.getConnection().execute(query)
            mysql.connection.commit()
            updateMsg='Successful'
        except Exception as e:
            updateMsg=str(e)
        return updateMsg

#Handles Login Operation
class Login(Resource):
    def post(self):

        jsonvalue = request.json
        userName = jsonvalue.get("username")
        password = jsonvalue.get("password")
        result= DB.readData("select password from login_details where username='"+userName+"'")

        if (len(result))==0:
            response="User Doesnt Exist"
        else:
            for row in result:
              hashed_password= row[0]
            login_success=False
            print(bcrypt.verify(password, hashed_password))
            if bcrypt.verify(password, hashed_password):
                login_success=True
            if(login_success):
                response="Login_Success"
            else:
                response = "Invalid Crendentials"
        return response

#Handle Sign up Operation
class SignUp(Resource):

    def post(self):
        jsonvalue = request.json
        userName = jsonvalue.get("username")

        password = jsonvalue.get("password")
        password = bcrypt.hash(password)

        response = ""
        try:
            query = "INSERT INTO login_details (username, password) VALUES ('"+userName+"' , '"+password+"')"
            responseOfUpdate=DB.updateData(query)
            if responseOfUpdate.find("Successful") >= 0:
                response ="Successfully Created"
            else:
                response = "Error Creating Account"

        except Exception as e:
            print(e)
            response = "Error Creating Account"
        return response


api.add_resource(SignUp, '/signup')
api.add_resource(Login, '/login')

if __name__ == '__main__':
    app.run(debug=True)
