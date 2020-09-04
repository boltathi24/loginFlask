from flask import jsonify
import jwt
import datetime
from myapis.rediscon import redisconnection




class ApiJWTAuthentication():
    secretKey='TempSecret'


    @classmethod
    def validateJwt(cls,headersvalue):
        if 'jwt-token' in headersvalue:
            token = headersvalue.get("jwt-token")
            jwtAuth=ApiJWTAuthentication.decode_auth_token(token)

            if jwtAuth.find("expired") >= 0 or jwtAuth.find("Invalid") >= 0 :
                return jsonify({"message":"Invalid JWT"})
            elif redisconnection.isKeyExist(jwtAuth):
                return jsonify({"message":"Valid JWT","username":jwtAuth})
            else:
                return jsonify({"Message":"Please Create new JWT Token"})
        else:
            return jsonify({"message": "JWT Token is Required"})

    @classmethod
    def decode_auth_token(cls, auth_token):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, ApiJWTAuthentication.secretKey)
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
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=5),
                'username': user_id
            }
            return jwt.encode(
                payload,
                ApiJWTAuthentication.secretKey,
                algorithm='HS256'
            )
        except Exception as e:
            return e