import mysql_connector
import json

ev = dict()

def get_users(camp_id):
    q = """
        select distinct c.created_by user 
        from characters c
        where 1=1 
        and c.created_by <> %s 
        and not exists (select 1 
                            from campaign_invites ci
                            where ci.user = c.created_by
                            and ci.accepted = 1
                            and ci.camp_id = %s)"""   
    
    params = (
        mysql_connector.get_username(ev),
        camp_id
    )
    users = mysql_connector.query_json(q, params)
    users = [user["user"] for user in users]
    return users

def get_invites():
    q = """ 
        select
            camp_id,
            user,
            IF(accepted, 'true', 'false') accepted,
            created_by
        from campaign_invites
        where 1=1
        """
        
    q = q + " and user = %s"
    params = mysql_connector.get_username(ev)
    invites = mysql_connector.query_json(q, params)
    return invites

def create_invite(data):
    sql = """
        INSERT IGNORE INTO campaign_invites (
            camp_id,
            user,
            accepted,
            created_by,
            created_date,
            updated_by,
            updated_date
        ) VALUES (
            %s,
            %s,
            1,
            %s,
            SYSDATE(),
            %s,
            SYSDATE());
        """

    params = (
        data.get("camp_id",""),
        data.get("user",""),
        mysql_connector.get_username(ev),
        mysql_connector.get_username(ev)
    )
    mysql_connector.execute_no_return(sql, params)

def update_invite(data):
    sql = """
        UPDATE campaign_invites
        SET accepted = 1,
            updated_by = %s,
            updated_date = SYSDATE()
        WHERE camp_id = %s
        and user = %s
        """

    params = (
        mysql_connector.get_username(ev),
        data.get("camp_id",""),
        mysql_connector.get_username(ev)
    )
    mysql_connector.execute_no_return(sql, params)   

def delete_invite(camp_id):
    sql = """
        DELETE FROM campaign_invites
        WHERE camp_id = %s
        and user = %s
        """
    params = (
        camp_id,
        mysql_connector.get_username(ev)
    )
    mysql_connector.execute_no_return(sql, params)
    delete_camp_chars(camp_id)

def delete_camp_chars(camp_id):
    sql = """
        DELETE FROM campaign_chars
        WHERE camp_id = %s
        and created_by = %s
        """
    params = (
        camp_id,
        mysql_connector.get_username(ev)
    )
    mysql_connector.execute_no_return(sql, params)

def handler(event, context):
    try:
        global ev
        ev = event
        httpMethod = event["httpMethod"]

        if httpMethod == "GET":
            params = event["queryStringParameters"]
            if params != None and "camp_id" in params:
                camp_id = params["camp_id"]
                return mysql_connector.success_response(json.dumps(get_users(camp_id)))
            else:
                return mysql_connector.success_response(json.dumps(get_invites()))
        elif httpMethod == "POST":
            try:
                data = json.loads(event["body"])
                create_invite(data)
                return mysql_connector.success_response_string()
            except Exception as e:
                return mysql_connector.client_error("Invalid POST data" + str(e))
        elif httpMethod == "PUT":
            try:
                data = json.loads(event["body"])
                update_invite(data)
                return mysql_connector.success_response_string()
            except Exception as e:
                return mysql_connector.client_error("Invalid PUT data" + str(e))
        elif httpMethod == "DELETE":
            try:
                params = event["queryStringParameters"]
                delete_invite(params["camp_id"])
                return mysql_connector.success_response_string()
            except:
                return mysql_connector.client_error("Invalid DELETE data")
        else:
            return mysql_connector.client_error("Invalid HTTP Method")
    except Exception as e:
        return mysql_connector.server_error("Unknown server error " + str(e))
        