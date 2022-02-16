from multiprocessing import synchronize
import pyupbit
from MySQLdb import _mysql
import json
import os

def connectMySQL(password) : 
    return _mysql.connect(host="localhost",user="guest",passwd=password,db="muhan_db") # connect with MySQL
    
def account_sync(db) : 
    # querying needed data
    db.query("""
            SELECT * FROM trade_history
            """)
    r=db.store_result()
    return r.fetch_row()
    

if __name__ == "__main__" : 
    
    # get secret key from json file
    secrets = json.loads(open('mysite/secret.json').read())
    password = secrets["PASSWORD"]

    db = connectMySQL(password)
    print(account_sync(db))