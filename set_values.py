import mysql_connector
import json

def handler(event, context):
    q = """ 
        select 
            sv.value_id,
            sv.set_value,
            sv.value_desc,
            sv.created_by,
            vs.set_id,
            vs.set_name
        from set_values sv,
                value_sets vs
        where 
            sv.set_id = vs.set_id 
        """

    try:
        httpMethod = event["httpMethod"]

        if httpMethod == "GET":
            params = event["queryStringParameters"]
            if params != None and "set_name" in params:
                q += " and vs.set_name = %s"
                params = (params["set_name"])

            return mysql_connector.query(q, params)
        elif httpMethod == "POST":
            try:
                sql = """
                    INSERT INTO set_values (
                        set_value,
                        set_id,
                        value_desc,
                        created_by,
                        created_date,
                        updated_by,
                        updated_date
                    ) VALUES (
                        %s,
                        (SELECT vs.set_id FROM value_sets vs WHERE vs.set_name = %s),
                        %s,
                        %s,
                        SYSDATE(),
                        %s,
                        SYSDATE());
                    """
                data = json.loads(event["body"])
                params = (
                    data.get("set_value",""),
                    data.get("set_name",""),
                    data.get("value_desc",""),
                    mysql_connector.get_username(event),
                    mysql_connector.get_username(event)
                )
                mysql_connector.execute(sql, params)

                q += """ and sv.value_id = LAST_INSERT_ID()"""
                return mysql_connector.single_query(q)
            except Exception as e:
                return mysql_connector.client_error("Invalid POST data" + str(e))
        elif httpMethod == "PUT":
            try:
                sql = """
                    UPDATE set_values
                    SET set_value = %s,
                        value_desc = %s,
                        updated_by = %s,
                        updated_date = SYSDATE()
                    WHERE value_id = %s
                    """

                data = json.loads(event["body"])
                params = (
                    data.get("set_value",""),
                    data.get("value_desc",""),
                    mysql_connector.get_username(event),
                    data.get("value_id","")
                )
                mysql_connector.execute(sql, params)

                params = (
                    data.get("value_id","")
                )
                q += """ and sv.value_id = %s"""
                return mysql_connector.single_query(q, params)
            except:
                return mysql_connector.client_error("Invalid PUT data")
        elif httpMethod == "DELETE":
            try:
                sql = """
                    DELETE FROM set_values
                    WHERE value_id = %s
                    """

                params = event["queryStringParameters"]
                params = (params["value_id"])
                return mysql_connector.execute(sql, params)
            except:
                return mysql_connector.client_error("Invalid DELETE data")
        else:
            return mysql_connector.client_error("Invalid HTTP Method")
    except:
        return mysql_connector.server_error("Unknown server error")
        