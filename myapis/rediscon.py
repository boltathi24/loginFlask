import redis
class redisconnection:

    def __init__(self):
        self.rediscon = None

    @classmethod
    def setcon(self):

        self.rediscon = redis.StrictRedis(host='127.0.0.1', port=6379, db=0, password='password',
                                              socket_timeout=None, connection_pool=None, charset='utf-8',
                                              errors='strict', unix_socket_path=None,decode_responses=True)

    @classmethod
    def getcon(self):
        return self.rediscon

    @classmethod
    def setRedisValue(self,key,value):
        self.getcon().__setitem__(key  ,value)

    @classmethod
    def getRedisValue(self,key):
        try:
            return self.getcon().__getitem__(key)
        except Exception as e:
            return str(e)

    @classmethod
    def delRedisValue(self,key):
        self.getcon().__delitem__(key)
        try:
            self.getcon().__delitem__(key)
        except Exception as e:
            pass

    @classmethod
    def isKeyExist(self,key):
        return self.getcon().exists(key)