import mysql_connector
import json

def handler(event, context):
    q = """ 
        select
            weapon_id,
            weapon_name,
            weapon_desc,
            weapon_type,
            cost,
            damage,
            weight,
            weapon_props,
            created_by
        from weapons
        where 1=1 
        """

    try:
        httpMethod = event["httpMethod"]

        if httpMethod == "GET":
            params = event["queryStringParameters"]
            if params != None and "weapon_id" in params:
                q += " and weapon_id = %s"
                params = (params["weapon_id"])
                return mysql_connector.single_query(q, params)
            else:
                return mysql_connector.query(q, params)
        elif httpMethod == "POST":
            try:
                sql = """
                    INSERT INTO weapons (
                        weapon_name,
                        weapon_desc,
                        weapon_type,
                        cost,
                        damage,
                        weight,
                        weapon_props,
                        created_by,
                        created_date,
                        updated_by,
                        updated_date
                    ) VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
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
                    data.get("weapon_name",""),
                    data.get("weapon_desc",""),
                    data.get("weapon_type",""),
                    data.get("cost",""),
                    data.get("damage",""),
                    data.get("weight",""),
                    data.get("weapon_props",""),
                    mysql_connector.get_username(event),
                    mysql_connector.get_username(event)
                )
                mysql_connector.execute(sql, params)

                q += """ and weapon_id = LAST_INSERT_ID()"""
                return mysql_connector.single_query(q)
            except:
                return mysql_connector.client_error("Invalid POST data")
        elif httpMethod == "PUT":
            try:
                sql = """
                    UPDATE weapons
                    SET weapon_name = %s,
                        weapon_desc = %s,
                        weapon_type = %s,
                        cost = %s,
                        damage = %s,
                        weight = %s,
                        weapon_props = %s,
                        updated_by = %s,
                        updated_date = SYSDATE()
                    WHERE weapon_id = %s
                    """

                data = json.loads(event["body"])
                params = (
                    data.get("weapon_name",""),
                    data.get("weapon_desc",""),
                    data.get("weapon_type",""),
                    data.get("cost",""),
                    data.get("damage",""),
                    data.get("weight",""),
                    data.get("weapon_props",""),
                    mysql_connector.get_username(event),
                    data.get("weapon_id","")
                )
                mysql_connector.execute(sql, params)

                params = (
                    data.get("weapon_id","")
                )
                q += """ and weapon_id = %s"""
                return mysql_connector.single_query(q, params)
            except:
                return mysql_connector.client_error("Invalid PUT data")
        elif httpMethod == "DELETE":
            try:
                sql = """
                    DELETE FROM weapons
                    WHERE weapon_id = %s
                    """

                params = event["queryStringParameters"]
                params = (params["weapon_id"])
                return mysql_connector.execute(sql, params)
            except:
                return mysql_connector.client_error("Invalid DELETE data")
        else:
            return mysql_connector.client_error("Invalid HTTP Method")
    except:
        return mysql_connector.server_error("Unknown server error")
        