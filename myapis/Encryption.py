from cryptography.fernet import Fernet

class EncryptionAlg:
    f=None
    @classmethod
    def initEncrypt(cls):
        cls.f = Fernet(cls.getKey())

    @classmethod
    def generate_key(cls):
        """
        Generates a key and save it into a file
        """
        key = Fernet.generate_key()
        with open("security.properties", "wb") as key_file:
            key_file.write(key)

    @classmethod
    def getKey(cls):
        """
        return a key
        """
        return open("security.properties", "rb").read()


    @classmethod
    def getEncryptedMsg(cls,message):
        # message = message.encode()
        # # f = Fernet(cls.getKey())
        # encrypted_message = cls.f.encrypt(message).decode('utf-8')

        return cls.f.encrypt(message.encode('utf-8')).decode('utf-8')

    @classmethod
    def getDecryptedMsg(cls, message):
        # print("into")
        # print(cls.getKey())
        # f = Fernet(cls.getKey())

        # print(cls.f.decrypt(message ))

        decrypted_message = cls.f.decrypt(message.encode() ).decode()

        return decrypted_message

