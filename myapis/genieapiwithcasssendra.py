from flask import Flask,request,jsonify
from flask_redis import FlaskRedis
from flask_restful import Resource, Api
from flask_mysqldb import MySQL
from passlib.hash import bcrypt
import logging
from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster, BatchStatement
from cassandra.query import SimpleStatement
import jwt,datetime
import redis

from cassandra.auth import PlainTextAuthProvider


app = Flask(__name__)
api = Api(app)

# REDIS_URL = "redis://:password@127.0.0.1:6379/0"
app.config['SECRET_KEY']="SecretykeytoGetStarted"
# redis_client = FlaskRedis(app)



rediscon = redis.StrictRedis(host='127.0.0.1', port=6379, db=0, password='password', socket_timeout=None, connection_pool=None, charset='utf-8', errors='strict', unix_socket_path=None)

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
        response=None
        if not result:
            response=jsonify({"message":"User Doesnt Exist"})
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

                print(userName)
                token=JWTHandling.encode_auth_token(userName)
                dec=token.decode('utf-8')
                response=jsonify(token=dec)
                rediscon.__setitem__(userName,token)
                # redis_client.__setitem__(userName,token)


            else:
                response = jsonify({"message":"Invalid Credentials"})
        return response

    def delete(self):
        jsonvalue = request.json
        userName = jsonvalue.get("username")
        password = jsonvalue.get("password")
        result = DB.readData("select password from mydb.login_details where username='" + userName + "';")
        response = None
        if not result:
            response = jsonify({"message": "User Doesnt Exist"})
        else:
            hashed_password = ""
            for row in result:
                hashed_password = row.password

            for row in result:
                hashed_password = row[0]
            login_success = False
            print(bcrypt.verify(password, hashed_password))
            if bcrypt.verify(password, hashed_password):
                login_success = True
            if (login_success):
                result = DB.readData("delete from mydb.login_details where username='" + userName + "';")

                response = jsonify({"message": "Successfully Deleted"})
                rediscon.__delitem__(userName)

            else:
                response = jsonify({"message": "Invalid Credentials"})
        return response

class ApiJWTAuth(Resource):

    def get(self):

        headersvalue = request.headers
        if 'jwt-token' in headersvalue:
            token = headersvalue.get("jwt-token")
            jwtAuth=JWTHandling.decode_auth_token(token)

            if jwtAuth.find("expired") >= 0 or jwtAuth.find("Invalid") >= 0 :
                return jsonify({"message":"Invalid JWT"})
            elif rediscon.exists(jwtAuth):
                return jsonify({"message":"Valid JWT","username":jwtAuth})
            else:
                return jsonify({"Message":"Please Create new JWT Token"})
        else:
            return jsonify({"message": "JWT Token is Required"})


class JWTHandling:

    @classmethod
    def decode_auth_token(cls,auth_token):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        print(auth_token)
        try:
            payload = jwt.decode(auth_token, app.config['SECRET_KEY'])
            return payload['username']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'

    @classmethod
    def encode_auth_token(self, user_id):
        """
        Generates the Auth Token
        :return: string
        """
        print("ins"+user_id)
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta( minutes=5),

                'username': user_id
            }
            return jwt.encode(
                payload,
                app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e

    def delete(self):
        jsonvalue = request.json
        userName = jsonvalue.get("username")
        password = jsonvalue.get("password")
        result= DB.readData("select password from mydb.login_details where username='"+userName+"'")

        if not result:
            response = jsonify({"message":"User Doesnt Exist"})
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
                    response= jsonify({"message":"Account Deletion is successful"})
                else:
                    response= jsonify({"message":"Error deleting Account"})
            else:
                response= jsonify({"message":"Please Enter Valid Credentials"})
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
                response = jsonify({"message":"Account Creation is successful"})
            else:
                response =  jsonify({"message":"Error in Account Creation "})

        except Exception as e:
            print(e)
            response = jsonify({"message":"Error in Account Creation "})
        return response


api.add_resource(SignUp, '/signup')
api.add_resource(Login, '/login','/delete')
api.add_resource(ApiJWTAuth, '/validatejwt')

if __name__ == '__main__':
    DB.setConnection("mydb")
    app.run(debug=True)

