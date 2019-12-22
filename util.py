import mysql.connector
from time import strftime
import traceback
import sys
import threading

sql = 0
db = 0

def getTime(format="%d.%m.%Y %H:%M:%S"):
    try:
        return strftime(format)
    except Exception as e:
        handleException(e)
        return getTime(format)

def getSqlConfig():
    host = ""
    user = ""
    password = ""
    database = ""
    try:
        with open("sql.con") as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith("host"):
                    host = line.replace("host=", "").replace("\n", "")
                if line.startswith("user"):
                    user = line.replace("user=", "").replace("\n", "")
                if line.startswith("password"):
                    password = line.replace("password=", "").replace("\n", "")
                if line.startswith("database"):
                    database = line.replace("database=", "").replace("\n", "")
    except Exception as e:
        p("ERROR", "something went wrong with the sql.con")
        print(e)
        p("ERROR", "exiting...")
        sys.exit()
    return host, user, password, database

def connectToSQL(h, u, p, d):
    global sql
    global db
    try:
        db = mysql.connector.connect(host=h, user=u, passwd=p, database=d)
        sql = db.cursor()
        p("MySQL", "connected to database: " + h + ", " + u + ", " + p + ", " + d)
    except Exception as e:
        p("ERROR", "something went wrong with the sql connection: " + h + ", " + u + ", " + p + ", " + d)
        print(e)
        p("ERROR", "exiting...")
        sys.exit()
    return sql

def disconnectFromSQL():
    util.sql.close()
    p("MySQL", "dissconnected from database")

def executeSQL(cmd):
    global sql
    global db
    sql.execute(cmd)
    #p("MySQL", "command executed: " + cmd)
    if "select" in cmd or "SELECT" in cmd or "show" in cmd or "SHOW" in cmd:
        return sql.fetchall()
    else:
        db.commit()

def executeSQLMulti(cmd):
    global sql
    global db
    sql.execute(cmd, multi=True)
    db.commit()
    #p("MySQL", "command executed: " + cmd)
    if "select" in cmd or "SELECT" in cmd or "show" in cmd or "SHOW" in cmd:
        return sql.fetchall()
