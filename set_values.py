import mysql_connector
import json

def handler(event, context):
    try:
        httpMethod = event["httpMethod"]

        if httpMethod == "GET":
            q = """ 
                select 
                    sv.value_id,
                    sv.set_value,
                    sv.description,
                    sv.created_by,
                    vs.set_id,
                    vs.set_name
                from set_values sv,
                     value_sets vs
                where 
                    sv.set_id = vs.set_id
                """

            params = event["queryStringParameters"]
            if params != None and "setName" in params:
                q += " and vs.set_name = %s"
                params = (params["setName"])

            return mysql_connector.query(q, params)
        elif httpMethod == "POST":
            try:
                sql = """
                    INSERT INTO set_values (
                        set_value,
                        set_id,
                        description,
                        created_by,
                        created_date,
                        updated_by,
                        updated_date
                    ) VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        SYSDATE(),
                        %s,
                        SYSDATE());
                    """
                data = json.loads(event["body"])
                params = (
                    data.get("setValue",""),
                    data.get("setId",""),
                    data.get("description",""),
                    mysql_connector.get_username(event),
                    mysql_connector.get_username(event)
                )
                return mysql_connector.execute(sql, params)
            except Exception as e:
                return mysql_connector.client_error("Invalid POST data" + str(e))
        elif httpMethod == "PUT":
            try:
                sql = """
                    UPDATE set_values
                    SET set_value = %s,
                        description = %s,
                        updated_by = %s,
                        updated_date = SYSDATE()
                    WHERE value_id = %s
                    """

                data = json.loads(event["body"])
                params = (
                    data.get("value",""),
                    data.get("description",""),
                    mysql_connector.get_username(event),
                    data.get("valueId","")
                )
                return mysql_connector.execute(sql, params)
            except:
                return mysql_connector.client_error("Invalid PUT data")
        elif httpMethod == "DELETE":
            try:
                sql = """
                    DELETE FROM set_values
                    WHERE value_id = %s
                    """

                data = json.loads(event["body"])
                params = (
                    data.get("valueId","")
                )
                return mysql_connector.execute(sql, params)
            except:
                return mysql_connector.client_error("Invalid DELETE data")
        else:
            return mysql_connector.client_error("Invalid HTTP Method")
    except:
        return mysql_connector.server_error("Unknown server error")
        