from pymysqlreplication import BinLogStreamReader
from pymysqlreplication import row_event
import configparser
import pymysqlreplication

# MySQL 연결 정보 가져옴
parser = configparser.ConfigParser()
parser.read('pipeline.conf')
hostname = parser.get('mysql_config', 'hostname')
port = parser.get('mysql_config', 'port')
usernamer = parser.get('mysql_config', 'username')
password = parser.get('mysql_config', 'password')
