import mysql_connector
import json

def get_class(class_id=None):
    q = """ 
        select
            class_id,
            class_name,
            hit_die,
            IF(str, 'true', 'false') str,
            IF(dex, 'true', 'false') dex,
            IF(con, 'true', 'false') con,
            IF(intel, 'true', 'false') intel,
            IF(wis, 'true', 'false') wis,
            IF(cha, 'true', 'false') cha,
            IF(caster, 'true', 'false') caster,
            parent_id,
            created_by
        from classes
        where 1=1
        """
        
    if class_id != None:
        qclass = q + " and class_id = %s"
        params = class_id
        c = mysql_connector.single_query_json(qclass, params)
        qSub = q + " and parent_id = %s"
        c['subclasses'] = [get_class(c["class_id"]) for c in mysql_connector.query_json(qSub, params)]
        c['class_traits'] = get_class_traits(class_id)
        return c
    else:
        q += " and parent_id < 1"
        classes = [get_class(c["class_id"]) for c in mysql_connector.query_json(q)]
        return classes

def get_class_traits(class_id):
    q = """ 
        select
            trait_id,
            class_id,
            trait_name,
            trait_desc,
            char_level,
            created_by
        from class_traits
        where class_id = %s
        order by 3
        """
        
    params = class_id
    return mysql_connector.query_json(q, params)

def create_class(event, data):
    sql = """
        INSERT INTO classes (
            class_name,
            hit_die,
            str,
            dex,
            con,
            intel,
            wis,
            cha,
            caster,
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
            %s,
            SYSDATE(),
            %s,
            SYSDATE());
        """

    params = (
        data.get("class_name",""),
        data.get("hit_die",""),
        (1 if str(data.get("str","")).lower() == "true" else 0),
        (1 if str(data.get("dex","")).lower() == "true" else 0),
        (1 if str(data.get("con","")).lower() == "true" else 0),
        (1 if str(data.get("intel","")).lower() == "true" else 0),
        (1 if str(data.get("wis","")).lower() == "true" else 0),
        (1 if str(data.get("cha","")).lower() == "true" else 0),
        (1 if str(data.get("caster","")).lower() == "true" else 0),
        data.get("parent_id",""),
        mysql_connector.get_username(event),
        mysql_connector.get_username(event)
    )
    mysql_connector.execute_no_return(sql, params)
    class_id = mysql_connector.get_last_insert_id()

    for sub in data.get("subclasses", list()):
        sub["parent_id"] = class_id
        create_class(event, sub)

    for trait in data.get("class_traits", list()):
        trait["class_id"] = class_id
        create_class_trait(event, trait)

    return class_id

def create_class_trait(event, data):
    sql = """
        INSERT INTO class_traits (
            class_id,
            trait_name,
            trait_desc,
            char_level,
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
            SYSDATE(),
            %s,
            SYSDATE());
        """

    params = (
        data.get("class_id",""),
        data.get("trait_name",""),
        data.get("trait_desc",""),
        data.get("char_level",""),
        mysql_connector.get_username(event),
        mysql_connector.get_username(event)
    )
    mysql_connector.execute_no_return(sql, params)

def update_class(event, data):
    sql = """
        UPDATE classes
        SET class_name = %s,
            hit_die = %s,
            str = %s,
            dex = %s,
            con = %s,
            intel = %s,
            wis = %s,
            cha = %s,
            caster = %s,
            updated_by = %s,
            updated_date = SYSDATE()
        WHERE class_id = %s
        """

    params = (
        data.get("class_name",""),
        data.get("hit_die",""),
        (1 if str(data.get("str","")).lower() == "true" else 0),
        (1 if str(data.get("dex","")).lower() == "true" else 0),
        (1 if str(data.get("con","")).lower() == "true" else 0),
        (1 if str(data.get("intel","")).lower() == "true" else 0),
        (1 if str(data.get("wis","")).lower() == "true" else 0),
        (1 if str(data.get("cha","")).lower() == "true" else 0),
        (1 if str(data.get("caster","")).lower() == "true" else 0),
        mysql_connector.get_username(event),
        data.get("class_id","")
    )
    mysql_connector.execute_no_return(sql, params)

    for sub in data.get("subclasses", list()):
        if sub.get("delete", False) == True:
            delete_class(sub["class_id"])
        elif sub.get("class_id", None) != None:
            sub["parent_id"] = data["class_id"]
            update_class(event, sub)
        else:
            sub["parent_id"] = data["class_id"]
            create_class(event, sub)

    for trait in data.get("class_traits", list()):
        if trait.get("delete", False) == True:
            delete_class_trait(trait["trait_id"])
        elif trait.get("trait_id", None) != None:
            trait["class_id"] = data["class_id"]
            update_class_trait(event, trait)
        else:
            trait["class_id"] = data["class_id"]
            create_class_trait(event, trait)
        
def update_class_trait(event, data):
    sql = """
        UPDATE class_traits
        SET trait_name = %s,
            trait_desc = %s,
            char_level = %s,
            updated_by = %s,
            updated_date = SYSDATE()
        WHERE trait_id = %s
        """

    params = (
        data.get("trait_name",""),
        data.get("trait_desc",""),
        data.get("char_level",""),
        mysql_connector.get_username(event),
        data.get("trait_id","")
    )
    mysql_connector.execute_no_return(sql, params)

def delete_class(class_id):
    sql = """
        DELETE FROM classes
        WHERE 1=1 
        """
    params = class_id

    sqlSub = sql + """ and parent_id = %s"""
    mysql_connector.execute_no_return(sqlSub, params)

    sqlclass = sql + """ and class_id = %s"""
    mysql_connector.execute_no_return(sqlclass, params)

def delete_class_trait(trait_id):
    sql = """
        DELETE FROM class_traits
        WHERE trait_id = %s
        """
    params = trait_id
    mysql_connector.execute_no_return(sql, params)

def handler(event, context):
    try:
        httpMethod = event["httpMethod"]

        if httpMethod == "GET":
            params = event["queryStringParameters"]
            if params != None and "class_id" in params:
                return mysql_connector.success_response(json.dumps(get_class(params["class_id"])))
            else:
                return mysql_connector.success_response(json.dumps(get_class()))
        elif httpMethod == "POST":
            try:
                data = json.loads(event["body"])
                class_id = create_class(event, data)
                return mysql_connector.success_response(json.dumps(get_class(class_id)))
            except Exception as e:
                return mysql_connector.client_error("Invalid POST data" + str(e))
        elif httpMethod == "PUT":
            try:
                data = json.loads(event["body"])
                update_class(event, data)
                return mysql_connector.success_response(json.dumps(get_class(data["class_id"])))
            except Exception as e:
                return mysql_connector.client_error("Invalid PUT data" + str(e))
        elif httpMethod == "DELETE":
            try:
                params = event["queryStringParameters"]
                delete_class(params["class_id"])
                return mysql_connector.success_response_string()
            except:
                return mysql_connector.client_error("Invalid DELETE data")
        else:
            return mysql_connector.client_error("Invalid HTTP Method")
    except:
        return mysql_connector.server_error("Unknown server error")
        