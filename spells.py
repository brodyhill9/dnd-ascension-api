import mysql_connector
import json

def handler(event, context):
    q = """ 
        select
            spell_id,
            spell_name,
            spell_desc,
            spell_level,
            higher_level,
            spell_range,
            components,
            IF(ritual, 'true', 'false') ritual,
            duration,
            casting_time,
            spell_school,
            created_by
        from spells
        where 1=1 
        """

    try:
        httpMethod = event["httpMethod"]

        if httpMethod == "GET":
            params = event["queryStringParameters"]
            if params != None and "spell_id" in params:
                q += " and spell_id = %s"
                params = (params["spell_id"])
                return mysql_connector.single_query(q, params)
            else:
                return mysql_connector.query(q, params)
        elif httpMethod == "POST":
            try:
                sql = """
                    INSERT INTO spells (
                        spell_name,
                        spell_desc,
                        spell_level,
                        higher_level,
                        spell_range,
                        components,
                        ritual,
                        duration,
                        casting_time,
                        spell_school,
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
                        %s,
                        %s,
                        SYSDATE(),
                        %s,
                        SYSDATE());
                    """

                data = json.loads(event["body"])
                params = (
                    data.get("spell_name",""),
                    data.get("spell_desc",""),
                    data.get("spell_level",""),
                    data.get("higher_level",""),
                    data.get("spell_range",""),
                    data.get("components",""),
                    data.get("ritual",""),
                    data.get("duration",""),
                    data.get("casting_time",""),
                    data.get("spell_school",""),
                    mysql_connector.get_username(event),
                    mysql_connector.get_username(event)
                )
                mysql_connector.execute(sql, params)

                q += """ and spell_id = LAST_INSERT_ID()"""
                return mysql_connector.single_query(q)
            except Exception as e:
                return mysql_connector.client_error("Invalid POST data" + str(e))
        elif httpMethod == "PUT":
            try:
                sql = """
                    UPDATE spells
                    SET spell_name = %s,
                        spell_desc = %s,
                        spell_level = %s,
                        higher_level = %s,
                        spell_range = %s,
                        components = %s,
                        ritual = %s,
                        duration = %s,
                        casting_time = %s,
                        spell_school = %s,
                        updated_by = %s,
                        updated_date = SYSDATE()
                    WHERE spell_id = %s
                    """

                data = json.loads(event["body"])
                params = (
                    data.get("spell_name",""),
                    data.get("spell_desc",""),
                    data.get("spell_level",""),
                    data.get("higher_level",""),
                    data.get("spell_range",""),
                    data.get("components",""),
                    data.get("ritual",""),
                    data.get("duration",""),
                    data.get("casting_time",""),
                    data.get("spell_school",""),
                    mysql_connector.get_username(event),
                    data.get("spell_id","")
                )
                mysql_connector.execute(sql, params)

                params = (
                    data.get("spell_id","")
                )
                q += """ and spell_id = %s"""
                return mysql_connector.single_query(q)
            except:
                return mysql_connector.client_error("Invalid PUT data")
        elif httpMethod == "DELETE":
            try:
                sql = """
                    DELETE FROM spells
                    WHERE spell_id = %s
                    """

                params = event["queryStringParameters"]
                params = (params["spell_id"])
                return mysql_connector.execute(sql, params)
            except:
                return mysql_connector.client_error("Invalid DELETE data")
        else:
            return mysql_connector.client_error("Invalid HTTP Method")
    except:
        return mysql_connector.server_error("Unknown server error")
        