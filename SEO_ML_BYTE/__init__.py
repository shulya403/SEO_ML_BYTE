# import os
# print(os.environ)
# print(os.environ.get('MYSQLCLIENT_CONNECTOR'))
#os.environ['MYSQLCLIENT_CONNECTOR'] = 'C:\Program Files\MariaDB\Mar
import pymysql

pymysql.install_as_MySQLdb()