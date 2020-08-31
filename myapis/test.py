from passlib.hash import bcrypt

# print(bcrypt.verify("heybuddy", '$2b$12$QKxfcVBhOpPCZ3E.jOB9XuKc38owaELbudDBLyyHAjDdWCBh0T9KS'))
class DB:
    global sqlconnection

    def getConnection(self):
        print(sqlconnection)

a=DB()
print(a.getConnection())
# userName='boltathi'
# hashed_password= "select password from login_details where username='"+userName+"'"
# print(hashed_password)