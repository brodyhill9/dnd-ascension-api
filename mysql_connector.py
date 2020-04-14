import sys
import rds_config
import pymysql
import json
import logging

rds_host  = rds_config.db_endpoint
name = rds_config.db_username
password = rds_config.db_password
db_name = rds_config.db_name
timeout = rds_config.db_timeout

logger = logging.getLogger()
logger.setLevel(logging.INFO)

try:
    conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=timeout)
except:
    logger.error("ERROR: Could not connect to MySQL.")
    sys.exit()
logger.info("SUCCESS: Connected to MySQL successfully")

def query(sql, params=None):
    with conn.cursor() as cur:
        cur.execute(sql, params)
        jsonData = []
        rowHeaders = [x[0] for x in cur.description]
        for row in cur:
            jsonData.append(dict(zip(rowHeaders,row)))
    return success_response(json.dumps(query_json(sql, params)))

def query_json(sql, params=None):
    with conn.cursor() as cur:
        cur.execute(sql, params)
        jsonData = []
        rowHeaders = [x[0] for x in cur.description]
        for row in cur:
            jsonData.append(dict(zip(rowHeaders,row)))
    return jsonData

def single_query(sql, params=None):
    return success_response(json.dumps(single_query_json(sql, params)))

def single_query_json(sql, params=None):
    with conn.cursor() as cur:
        cur.execute(sql, params)
        jsonData = []
        rowHeaders = [x[0] for x in cur.description]
        for row in cur:
            jsonData.append(dict(zip(rowHeaders,row)))
    return next(iter(jsonData), None)

def get_last_insert_id():
    with conn.cursor() as cur:
        cur.execute("select LAST_INSERT_ID() id from dual")
        jsonData = []
        rowHeaders = [x[0] for x in cur.description]
        for row in cur:
            jsonData.append(dict(zip(rowHeaders,row)))
    return next(iter(jsonData), None)["id"]

def execute(sql, params=None):
    with conn.cursor() as cur:
        cur.execute(sql, params)
    return success_response_string()

def execute_no_return(sql, params=None):
    with conn.cursor() as cur:
        cur.execute(sql, params)

def success_response(jsonString):
    response =  {
        "statusCode": 200,
        "headers": {},
        "body": jsonString
    }
    conn.commit()
    return response

def success_response_string(message="Success"):
    return success_response(json.dumps({"result": message}))

def client_error(error):
    response =  {
        "statusCode": 400,
        "headers": {},
        "body": json.dumps({
            "message": error
        })
    }
    conn.rollback()
    return response

def server_error(error):
    response =  {
        "statusCode": 500,
        "headers": {},
        "body": json.dumps({
            "message": error
        })
    }
    conn.rollback()
    return response

def get_username(event):
    try:
        return event["headers"]["DndUser"]
    except:
        return "(Guest)"
    #return event["requestContext"]["authorizer"]["claims"]["preferred_username"]
