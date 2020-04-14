import mysql_connector
import json

def get_race(race_id=None):
    q = """ 
        select
            race_id,
            race_name,
            str,
            dex,
            con,
            intel,
            wis,
            cha,
            speed,
            parent_id,
            created_by
        from races
        where 1=1
        """
        
    if race_id != None:
        qRace = q + " and race_id = %s"
        params = race_id
        race = mysql_connector.single_query_json(qRace, params)
        qSub = q + " and parent_id = %s"
        race['subraces'] = [get_race(race["race_id"]) for race in mysql_connector.query_json(qSub, params)]
        race['race_traits'] = get_race_traits(race_id)
        return race
    else:
        q += " and (parent_id IS NULL OR parent_id < 1)"
        races = [get_race(race["race_id"]) for race in mysql_connector.query_json(q)]
        return races

def get_race_traits(race_id):
    q = """ 
        select
            trait_id,
            race_id,
            trait_name,
            trait_desc,
            created_by
        from race_traits
        where race_id = %s
        order by 3
        """
        
    params = race_id
    return mysql_connector.query_json(q, params)

def create_race(event, data):
    sql = """
        INSERT INTO races (
            race_name,
            str,
            dex,
            con,
            intel,
            wis,
            cha,
            speed,
            parent_id,
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
            SYSDATE(),
            %s,
            SYSDATE());
        """

    params = (
        data.get("race_name",""),
        data.get("str",""),
        data.get("dex",""),
        data.get("con",""),
        data.get("intel",""),
        data.get("wis",""),
        data.get("cha",""),
        data.get("speed",""),
        data.get("parent_id",""),
        mysql_connector.get_username(event),
        mysql_connector.get_username(event)
    )
    mysql_connector.execute_no_return(sql, params)
    race_id = mysql_connector.get_last_insert_id()

    for sub in data.get("subraces", list()):
        sub["parent_id"] = race_id
        create_race(event, sub)

    for trait in data.get("race_traits", list()):
        trait["race_id"] = race_id
        create_race_trait(event, trait)

    return race_id

def create_race_trait(event, data):
    sql = """
        INSERT INTO race_traits (
            race_id,
            trait_name,
            trait_desc,
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

    params = (
        data.get("race_id",""),
        data.get("trait_name",""),
        data.get("trait_desc",""),
        mysql_connector.get_username(event),
        mysql_connector.get_username(event)
    )
    mysql_connector.execute_no_return(sql, params)

def update_race(event, data):
    sql = """
        UPDATE races
        SET race_name = %s,
            str = %s,
            dex = %s,
            con = %s,
            intel = %s,
            wis = %s,
            cha = %s,
            speed = %s,
            updated_by = %s,
            updated_date = SYSDATE()
        WHERE race_id = %s
        """

    params = (
        data.get("race_name",""),
        data.get("str",""),
        data.get("dex",""),
        data.get("con",""),
        data.get("intel",""),
        data.get("wis",""),
        data.get("cha",""),
        data.get("speed",""),
        mysql_connector.get_username(event),
        data.get("race_id","")
    )
    mysql_connector.execute_no_return(sql, params)

    for sub in data.get("subraces", list()):
        if sub.get("delete", False) == True:
            delete_race(sub["race_id"])
        elif sub.get("race_id", None) != None:
            sub["parent_id"] = data["race_id"]
            update_race(event, sub)
        else:
            sub["parent_id"] = data["race_id"]
            create_race(event, sub)

    for trait in data.get("race_traits", list()):
        if trait.get("delete", False) == True:
            delete_race_trait(trait["trait_id"])
        elif trait.get("trait_id", None) != None:
            trait["race_id"] = data["race_id"]
            update_race_trait(event, trait)
        else:
            trait["race_id"] = data["race_id"]
            create_race_trait(event, trait)
        
def update_race_trait(event, data):
    sql = """
        UPDATE race_traits
        SET race_id = %s,
            trait_name = %s,
            trait_desc = %s,
            updated_by = %s,
            updated_date = SYSDATE()
        WHERE trait_id = %s
        """

    params = (
        data.get("race_id",""),
        data.get("trait_name",""),
        data.get("trait_desc",""),
        mysql_connector.get_username(event),
        data.get("trait_id","")
    )
    mysql_connector.execute_no_return(sql, params)

def delete_race(race_id):
    sql = """
        DELETE FROM races
        WHERE 1=1 
        """
    params = race_id

    sqlSub = sql + """ and parent_id = %s"""
    mysql_connector.execute_no_return(sqlSub, params)

    sqlRace = sql + """ and race_id = %s"""
    mysql_connector.execute_no_return(sqlRace, params)

def delete_race_trait(trait_id):
    sql = """
        DELETE FROM race_traits
        WHERE trait_id = %s
        """
    params = trait_id
    mysql_connector.execute_no_return(sql, params)

def handler(event, context):
    try:
        httpMethod = event["httpMethod"]

        if httpMethod == "GET":
            params = event["queryStringParameters"]
            if params != None and "race_id" in params:
                return mysql_connector.success_response(json.dumps(get_race(params["race_id"])))
            else:
                return mysql_connector.success_response(json.dumps(get_race()))
        elif httpMethod == "POST":
            try:
                data = json.loads(event["body"])
                race_id = create_race(event, data)
                return mysql_connector.success_response(json.dumps(get_race(race_id)))
            except Exception as e:
                return mysql_connector.client_error("Invalid POST data" + str(e))
        elif httpMethod == "PUT":
            try:
                data = json.loads(event["body"])
                update_race(event, data)
                return mysql_connector.success_response(json.dumps(get_race(data["race_id"])))
            except Exception as e:
                return mysql_connector.client_error("Invalid PUT data" + str(e))
        elif httpMethod == "DELETE":
            try:
                params = event["queryStringParameters"]
                delete_race(params["race_id"])
                return mysql_connector.success_response_string()
            except:
                return mysql_connector.client_error("Invalid DELETE data")
        else:
            return mysql_connector.client_error("Invalid HTTP Method")
    except:
        return mysql_connector.server_error("Unknown server error")
        