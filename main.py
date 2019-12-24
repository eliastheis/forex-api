import util

# connect to SQL
host, user, password, database = util.getSqlConfig()
util.connectToSQL(host, user, password, database)

