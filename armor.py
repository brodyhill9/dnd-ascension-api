import mysql_connector
import json

def handler(event, context):
    q = """ 
        select
            armor_id,
            armor_name,
            armor_desc,
            armor_type,
            cost,
            armor_class,
            strength,
            IF(stealth_dis, 'true', 'false') stealth_dis,
            weight,
            created_by
        from armor
        where 1=1 
        """

    try:
        httpMethod = event["httpMethod"]

        if httpMethod == "GET":
            params = event["queryStringParameters"]
            if params != None and "armor_id" in params:
                q += " and armor_id = %s"
                params = (params["armor_id"])
                return mysql_connector.single_query(q, params)
            else:
                return mysql_connector.query(q, params)
        elif httpMethod == "POST":
            try:
                sql = """
                    INSERT INTO armor (
                        armor_name,
                        armor_desc,
                        armor_type,
                        cost,
                        armor_class,
                        strength,
                        stealth_dis,
                        weight,
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
                        %s,
                        SYSDATE(),
                        %s,
                        SYSDATE());
                    """

                data = json.loads(event["body"])
                params = (
                    data.get("armor_name",""),
                    data.get("armor_desc",""),
                    data.get("armor_type",""),
                    data.get("cost",""),
                    data.get("armor_class",""),
                    data.get("strength",""),
                    (1 if str(data.get("stealth_dis","")).lower() == "true" else 0),
                    data.get("weight",""),
                    mysql_connector.get_username(event),
                    mysql_connector.get_username(event)
                )
                mysql_connector.execute(sql, params)

                q += """ and armor_id = LAST_INSERT_ID()"""
                return mysql_connector.single_query(q)
            except:
                return mysql_connector.client_error("Invalid POST data")
        elif httpMethod == "PUT":
            try:
                sql = """
                    UPDATE armor
                    SET armor_name = %s,
                        armor_desc = %s,
                        armor_type = %s,
                        cost = %s,
                        armor_class = %s,
                        strength = %s,
                        stealth_dis = %s,
                        weight = %s,
                        updated_by = %s,
                        updated_date = SYSDATE()
                    WHERE armor_id = %s
                    """

                data = json.loads(event["body"])
                params = (
                    data.get("armor_name",""),
                    data.get("armor_desc",""),
                    data.get("armor_type",""),
                    data.get("cost",""),
                    data.get("armor_class",""),
                    data.get("strength",""),
                    (1 if str(data.get("stealth_dis","")).lower() == "true" else 0),
                    data.get("weight",""),
                    mysql_connector.get_username(event),
                    data.get("armor_id","")
                )
                mysql_connector.execute(sql, params)

                params = (
                    data.get("armor_id","")
                )
                q += """ and armor_id = %s"""
                return mysql_connector.single_query(q, params)
            except:
                return mysql_connector.client_error("Invalid PUT data")
        elif httpMethod == "DELETE":
            try:
                sql = """
                    DELETE FROM armor
                    WHERE armor_id = %s
                    """

                params = event["queryStringParameters"]
                params = (params["armor_id"])
                return mysql_connector.execute(sql, params)
            except:
                return mysql_connector.client_error("Invalid DELETE data")
        else:
            return mysql_connector.client_error("Invalid HTTP Method")
    except:
        return mysql_connector.server_error("Unknown server error")
        