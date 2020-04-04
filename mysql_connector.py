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
    return success_response(json.dumps(jsonData))

def single_query(sql, params=None):
    with conn.cursor() as cur:
        cur.execute(sql, params)
        jsonData = []
        rowHeaders = [x[0] for x in cur.description]
        for row in cur:
            jsonData.append(dict(zip(rowHeaders,row)))
    return success_response(json.dumps(next(iter(jsonData), None)))

def execute(sql, params=None):
    with conn.cursor() as cur:
        cur.execute(sql, params)
    conn.commit()
    return success_response(json.dumps({
            "result": "Success"
        }))

def success_response(json):
    response =  {
        "statusCode": 200,
        "headers": {},
        "body": json
    }
    return response

def client_error(error):
    response =  {
        "statusCode": 400,
        "headers": {},
        "body": json.dumps({
            "message": error
        })
    }
    return response

def server_error(error):
    response =  {
        "statusCode": 500,
        "headers": {},
        "body": json.dumps({
            "message": error
        })
    }
    return response

def get_username(event):
    try:
        return event["headers"]["DndUser"]
    except:
        return "(Guest)"
    #return event["requestContext"]["authorizer"]["claims"]["preferred_username"]
