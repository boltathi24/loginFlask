from flask import jsonify
import jwt
import datetime
import json
from myapis.rediscon import redisconnection




class ApiJWTAuthentication():
    secretKey_Refresh='TempSecretRefresh'
    secretKey_access='accessToken'
    expirationTime_Refresh=5
    expirationTime_Access = 1

    @classmethod
    def getAccessTokenWithRefreshToken(cls, headervalue):
        print(headervalue)
        if 'jwt-token' in headervalue:
            refreshToken=headervalue.get('jwt-token')
            refreshTokenDecodeResponse = json.loads(cls.decodeRefreshTokenForUserName(refreshToken))
            if refreshTokenDecodeResponse.get('message').find("success") >= 0:
                redisDbToken = redisconnection.getRedisValue(refreshTokenDecodeResponse.get('username'))
                if redisDbToken.find(refreshToken) >=0:
                    return json.loads(cls.getAccessToken(refreshToken))
                else:
                    return jsonify({"message":"Invalid Refresh Token"})
            else:
                return jsonify(refreshTokenDecodeResponse)
        else:
            return jsonify({"message": "Please Provide Refresh Token"})



    @classmethod
    def validateAccessToken(cls,headersvalue):
        """
                   Validates the Access Token
                   :return: JSON wrapped by Response Object
                   """
        if 'jwt-token' in headersvalue:
            try:
                token = headersvalue.get("jwt-token")

                accessTokenDecodeResponse=json.loads(cls.decodeAccesshTokenForRefreshToken(token)) #Getting refresh Token From Token
                print(accessTokenDecodeResponse)
                if accessTokenDecodeResponse.get('message').find("success") >= 0 :
                    refreshTokenDecodeResponse=json.loads(cls.decodeRefreshTokenForUserName(accessTokenDecodeResponse.get('refreshToken')))
                    if refreshTokenDecodeResponse.get('message').find("success") >=0:
                        redisDbToken=redisconnection.getRedisValue(refreshTokenDecodeResponse.get('username')) #Checking the Refresh Token in Redis
                        if redisDbToken.find(accessTokenDecodeResponse.get('refreshToken')) >=0:
                            return jsonify({"message":"success","username":refreshTokenDecodeResponse.get('username')})
                        else:
                            return jsonify({"message":"invalid Refresh Token"}) #Session Terminated
                    else:
                         return jsonify(refreshTokenDecodeResponse)

                else:
                    return jsonify(accessTokenDecodeResponse) #When Access Token Is Invalid
            except Exception as e:
                return jsonify({"message":str(e)})
        else:
            return jsonify({"message": "Please Provide JWT Token"})



    @classmethod
    def decodeRefreshTokenForUserName(cls, refreshToken):
        """
        Decodes the auth token
        :param refreshToken:
        :return: integer|string
        """
        try:
            payload = jwt.decode(refreshToken, cls.secretKey_Refresh)
            return json.dumps({"message": "success","username":payload['username']})
        except jwt.ExpiredSignatureError:
            return json.dumps({"message": "Expired Refresh Token"})
        except jwt.InvalidTokenError:
            return json.dumps({"message": "Invalid Refresh Token"})

    @classmethod
    def decodeAccesshTokenForRefreshToken(cls, accessToken):
        """
        Decodes the access token
        :param accessToken:
        :return: integer|string
        """
        try:
            payload = jwt.decode(accessToken, cls.secretKey_access)
            return json.dumps({"message": "success","refreshToken": payload['refreshToken']})
        except jwt.ExpiredSignatureError:
            return json.dumps({"message": "Expired Access Token"})
        except jwt.InvalidTokenError:
            return json.dumps({"message": "Invalid access Token"})



    @classmethod
    def getAccessToken(cls, refreshToken):
            """
            Generates the Access Token
            :return: string
            """
            print(refreshToken)
            try:
                payload = {
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=cls.expirationTime_Access),
                    'refreshToken': refreshToken
                }
                jwttoken= jwt.encode(
                    payload,
                    ApiJWTAuthentication.secretKey_access,
                    algorithm='HS256'
                )
                token=jwttoken.decode('utf-8')
                return json.dumps({"message": "success", "jwt": token})
            except Exception as e:
                return json.dumps({"message": "exception","Exception": str(e)})

    @classmethod
    def getRefreshToken(cls, username):
            """
            Generates the Refresh Token
            :return: string
            """
            try:
                payload = {
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=cls.expirationTime_Refresh),
                    'username': username
                }
                jwtToken=jwt.encode(
                    payload,
                    ApiJWTAuthentication.secretKey_Refresh,
                    algorithm='HS256'
                );
                token=jwtToken.decode('utf-8')
                return json.dumps({"message": "success", "jwt": token})
            except Exception as e:
                return json.dumps({"message": "exception","Exception": str(e)})

    # @classmethod
    # def encode_auth_token(self, user_id):
    #     """
    #     Generates the Auth Token
    #     :return: string
    #     """
    #     try:
    #         payload = {
    #             'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=5),
    #             'username': user_id
    #         }
    #         jwttoken= jwt.encode(
    #             payload,
    #             ApiJWTAuthentication.secretKey,
    #             algorithm='HS256'
    #         )
    #         return jsonify({"message": "success"},{"jwt": jwttoken})
    #     except Exception as e:
    #         return jsonify({"message": "exception"},{"Exception": str(e)})




        #     if jwtAuth.find("expired") >= 0 or jwtAuth.find("Invalid") >= 0 :
        #         return jsonify({"message":"Invalid JWT"})
        #     elif redisconnection.isKeyExist(jwtAuth):
        #         return jsonify({"message":"Valid JWT","username":jwtAuth})
        #     else:
        #         return jsonify({"Message":"Please Create new JWT Token"})
        # else:
        #     return jsonify({"message": "JWT Token is Required"})

    # @classmethod
    # def decode_auth_token(cls, auth_token):
    #     """
    #     Decodes the auth token
    #     :param auth_token:
    #     :return: integer|string
    #     """
    #     try:
    #         payload = jwt.decode(auth_token, ApiJWTAuthentication.secretKey)
    #         return payload['username']
    #     except jwt.ExpiredSignatureError:
    #         return 'Signature expired. Please log in again.'
    #     except jwt.InvalidTokenError:
    #         return 'Invalid token. Please log in again.'