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
                    description,
                    created_by
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
                        description,
                        created_by,
                        created_date,
                        updated_by,
                        updated_date
                    ) VALUES (
                        %s,
                        %s,
                        %s,
                        SYSDATE(),
                        %s,
                        SYSDATE());
                    """

                data = json.loads(event["body"])
                params = (
                    data.get("setName",""),
                    data.get("description",""),
                    mysql_connector.get_username(event),
                    mysql_connector.get_username(event)
                )
                return mysql_connector.execute(sql, params)
            except:
                return mysql_connector.client_error("Invalid POST data")
        elif httpMethod == "PUT":
            try:
                sql = """
                    UPDATE value_sets
                    SET set_name = %s,
                        description = %s,
                        updated_by = %s,
                        updated_date = SYSDATE()
                    WHERE set_id = %s
                    """

                data = json.loads(event["body"])
                params = (
                    data.get("setName",""),
                    data.get("description",""),
                    mysql_connector.get_username(event),
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
            return mysql_connector.client_error("Invalid HTTP Method")
    except:
        return mysql_connector.server_error("Unknown server error")
        