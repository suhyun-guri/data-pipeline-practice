from pymysqlreplication import BinLogStreamReader
from pymysqlreplication import row_event
import configparser
import pymysqlreplication
import csv, boto3
import pymysql

# MySQL 연결 정보 가져옴
parser = configparser.ConfigParser()
parser.read('pipeline.conf')
hostname = parser.get('mysql_config', 'hostname')
port = parser.get('mysql_config', 'port')
username = parser.get('mysql_config', 'username')
password = parser.get('mysql_config', 'password')
database = parser.get('mysql_config', 'database')

mysql_settings = {
    "host" : hostname,
    "port" : int(port),
    "user" : username,
    "passwd" : password
}

# #쿼리 날리기
# conn = pymysql.connect(host = hostname, user=username, passwd = password,
#                     db=database, port=int(port), use_unicode=True,charset ='utf8',
#                     cursorclass=pymysql.cursors.DictCursor)
# cursor = conn.cursor()
# query = """INSERT INTO Orders
# 	      Values(5, 'Shipped', '2022-09-22 09:20:00');"""

# cursor.execute(query)
# conn.commit()
# conn.close()

b_stream = BinLogStreamReader(
    connection_settings = mysql_settings,
    server_id=1383646513,
    only_events=[row_event.DeleteRowsEvent,
                 row_event.WriteRowsEvent,
                 row_event.UpdateRowsEvent]    
)
order_events = []

for binlogevent in b_stream:
  print("binlog", binlogevent)
  for row in binlogevent.rows:
    if binlogevent.table == 'Orders':
      event = {}
      if isinstance(
            binlogevent,row_event.DeleteRowsEvent
        ):
        event["action"] = "delete"
        event.update(row["values"].items())
      elif isinstance(
            binlogevent,row_event.UpdateRowsEvent
        ):
        event["action"] = "update"
        print(row)
        event.update(row["after_values"].items())
      elif isinstance(
            binlogevent,row_event.WriteRowsEvent
        ):
        event["action"] = "insert"
        event.update(row["values"].items())
        print(row)
      print(event)
      order_events.append(event)

b_stream.close()

keys = order_events[0].keys()
local_filename = 'orders_extract.csv'
with open(
        local_filename,
        'w',
        newline='') as output_file:
    dict_writer = csv.DictWriter(
                output_file, keys,delimiter='|')
    dict_writer.writerows(order_events)

# load the aws_boto_credentials values
parser = configparser.ConfigParser()
parser.read("pipeline.conf")
access_key = parser.get(
                "aws_boto_credentials",
                "access_key")
secret_key = parser.get(
                "aws_boto_credentials",
                "secret_key")
bucket_name = parser.get(
                "aws_boto_credentials",
                "bucket_name")

s3 = boto3.client(
    's3',
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key)

s3_file = local_filename

s3.upload_file(
    local_filename,
    bucket_name,
    s3_file)
