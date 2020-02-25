import mysql_connector
import json

def handler(event, context):
    try:
        httpMethod = event["httpMethod"]

        if httpMethod == "GET":
            q = """ 
                select 
                    set_id,
                    set_name,
                    display_name,
                    description
                from value_sets
                """

            params = event["queryStringParameters"]
            if params != None and "setName" in params:
                q += " where set_name = %s"
                params = (params["setName"])

            return mysql_connector.query(q, params)
        elif httpMethod == "POST":
            try:
                sql = """
                    INSERT INTO value_sets (
                        set_name,
                        display_name,
                        description
                    ) VALUES (
                        %s,
                        %s,
                        %s);
                    """

                data = json.loads(event["body"])
                params = (
                    data.get("setName",""),
                    data.get("displayName",""),
                    data.get("description","")
                )
                return mysql_connector.execute(sql, params)
            except:
                return mysql_connector.client_error("Invalid POST data")
        elif httpMethod == "PUT":
            try:
                sql = """
                    UPDATE value_sets
                    SET set_name = %s,
                        display_name = %s,
                        description = %s
                    WHERE set_id = %s
                    """

                data = json.loads(event["body"])
                params = (
                    data.get("setName",""),
                    data.get("displayName",""),
                    data.get("description",""),
                    data.get("setId","")
                )
                return mysql_connector.execute(sql, params)
            except:
                return mysql_connector.client_error("Invalid PUT data")
        elif httpMethod == "DELETE":
            try:
                sql = """
                    DELETE FROM value_sets
                    WHERE set_id = %s
                    """

                data = json.loads(event["body"])
                params = (
                    data.get("setId","")
                )
                return mysql_connector.execute(sql, params)
            except:
                return mysql_connector.client_error("Invalid DELETE data")
        else:
            mappings = dict()

            return mysql_connector.upsert("value_sets", mappings)
    except:
        return mysql_connector.server_error("Unknown server error")
        