import mysql_connector
import json

def handler(event, context):
    try:
        httpMethod = event["httpMethod"]

        if httpMethod == "GET":
            q = """ 
                select
                    spell_id,
                    spell_name,
                    spell_desc,
                    spell_level,
                    higher_level,
                    spell_range,
                    components,
                    material,
                    ritual,
                    duration,
                    casting_time,
                    spell_school,
                    created_by
                from spells
                """

            params = event["queryStringParameters"]
            if params != None and "spellId" in params:
                q += " where spell_id = %s"
                params = (params["spellId"])

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
                        material,
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
                        %s,
                        SYSDATE(),
                        %s,
                        SYSDATE());
                    """

                data = json.loads(event["body"])
                params = (
                    data.get("spellName",""),
                    data.get("spellDesc",""),
                    data.get("spellLevel",""),
                    data.get("higherLevel",""),
                    data.get("spellRange",""),
                    data.get("components",""),
                    data.get("material",""),
                    data.get("ritual",""),
                    data.get("duration",""),
                    data.get("castingTime",""),
                    data.get("spellSchool",""),
                    mysql_connector.get_username(event),
                    mysql_connector.get_username(event)
                )
                return mysql_connector.execute(sql, params)
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
                        material = %s,
                        ritual = %s,
                        duration = %s,
                        casting_time = %s,
                        spell_school = %s,
                        updated_by = %s,
                        updated_date = SYSDATE()
                    WHERE set_id = %s
                    """

                data = json.loads(event["body"])
                params = (
                    data.get("spellName",""),
                    data.get("spellDesc",""),
                    data.get("spellLevel",""),
                    data.get("higherLevel",""),
                    data.get("spellRange",""),
                    data.get("components",""),
                    data.get("material",""),
                    data.get("ritual",""),
                    data.get("duration",""),
                    data.get("castingTime",""),
                    data.get("spellSchool",""),
                    mysql_connector.get_username(event),
                    data.get("setId","")
                )
                return mysql_connector.execute(sql, params)
            except:
                return mysql_connector.client_error("Invalid PUT data")
        elif httpMethod == "DELETE":
            try:
                sql = """
                    DELETE FROM spells
                    WHERE spell_id = %s
                    """

                data = json.loads(event["body"])
                params = (
                    data.get("spellId","")
                )
                return mysql_connector.execute(sql, params)
            except:
                return mysql_connector.client_error("Invalid DELETE data")
        else:
            return mysql_connector.client_error("Invalid HTTP Method")
    except:
        return mysql_connector.server_error("Unknown server error")
        