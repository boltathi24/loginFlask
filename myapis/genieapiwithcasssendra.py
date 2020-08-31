from flask import Flask,request
from flask_restful import Resource, Api
from flask_mysqldb import MySQL
from passlib.hash import bcrypt
import logging
from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster, BatchStatement
from cassandra.query import SimpleStatement
from cassandra.auth import PlainTextAuthProvider


app = Flask(__name__)
api = Api(app)



#Handles DB Operation
class DB:

    def __init__(cls):
        cls.cluster = None
        cls.session = None
        cls.result=None


    @classmethod
    def setConnection(cls,keyspace):
        ap = PlainTextAuthProvider(username='cassandra', password='cassandra')
        cls.cluster = Cluster(['127.0.0.1'],port=9042,auth_provider=ap)
        cls.session = cls.cluster.connect(keyspace)


    @classmethod
    def readData(cls,query):
        print(query)
        updateMsg="False"
        try:
            cls.result = cls.session.execute(query)
            updateMsg="Successful"
        except Exception as e:
            cls.result=()
        return cls.result


    @classmethod
    def updateData(cls, query):
        updateMsg=""
        try:
            insert_sql = cls.session.prepare(query)
            batch = BatchStatement()
            batch.add(query)
            cls.session.execute(batch)
            updateMsg="Successful"
        except Exception as e:
            updateMsg="Exception"+str(e)

        return updateMsg

#Handles Login Operation
class Login(Resource):
    def post(self):
        jsonvalue = request.json
        userName = jsonvalue.get("username")
        password = jsonvalue.get("password")
        result= DB.readData("select password from mydb.login_details where username='"+userName+"';")

        if not result:
            response="User Doesnt Exist"
        else:
            hashed_password=""
            for row in result:
                hashed_password=row.password


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

    def delete(self):
        jsonvalue = request.json
        userName = jsonvalue.get("username")
        password = jsonvalue.get("password")
        result= DB.readData("select password from mydb.login_details where username='"+userName+"'")

        if not result:
            response = "User Doesnt Exist"
        else:
            for row in result:
              hashed_password=row.password
            login_success=False
            print(bcrypt.verify(password, hashed_password))
            if bcrypt.verify(password, hashed_password):
                login_success=True
            if(login_success):
                updateMsg = DB.updateData("Delete from mydb.login_details where username='" + userName + "';")
                if updateMsg.find("Successful") >= 0:
                    response="Account Got Deleted Successfully"
                else:
                    response="Error Deleting Account"
            else:
                response="Please Enter valid credentials"
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
            query = "INSERT INTO mydb.login_details (username, password,user_id) VALUES ('"+userName+"' , '"+password+"',1);"

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
api.add_resource(Login, '/login','/delete')

if __name__ == '__main__':
    DB.setConnection("mydb")
    app.run(debug=True)


# class PythonCassandraExample:
#     def __init__(self):
#         self.cluster = None
#         self.session = None
#         self.keyspace = None
#         self.log = None
#     def __del__(self):
#         self.cluster.shutdown()
#     def createsession(self):
#         self.cluster = Cluster(['localhost'])
#         self.session = self.cluster.connect(self.keyspace)
#     def getsession(self):
#         return self.session
#     # How about Adding some log info to see what went wrong
#     def setlogger(self):
#         log = logging.getLogger()
#         log.setLevel('INFO')
#         handler = logging.StreamHandler()
#         handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
#         log.addHandler(handler)
#         self.log = log
#     # Create Keyspace based on Given Name
#
#
#     # lets do some batch insert
#     def insert_data(self,query):
#         insert_sql = self.session.prepare(query)
#         batch = BatchStatement()
#         batch.add(query)
#
#         self.session.execute(batch)
#         self.log.info('Batch Insert Completed')
#
#     def select_data(self,query):
#         rows = self.session.execute(query)
#         return rows
#
#
# if __name__ == '__main__':
#     example1 = PythonCassandraExample()
#     example1.createsession()
#     example1.setlogger()
#     example1.insert_data()
#     example1.select_data()
