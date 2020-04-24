import mysql_connector
import json

ev = dict()

def get_campaign(camp_id=None):
    q = """ 
        select
            c.camp_id,
            c.camp_name,
            c.created_by,
            if (c.created_by = %s, 'true', 'false') is_owner
        from campaigns c
	    where 1=1 
        """
        
    if camp_id != None:
        q = q + " and c.camp_id = %s"
        params = (
            mysql_connector.get_username(ev),
            camp_id
        )
        camp = mysql_connector.single_query_json(q, params)
        return camp
    else:
        q = q + """ and c.created_by = %s
                    or exists (select 1 
                                from campaign_invites ci
                                where c.camp_id = ci.camp_id
                                and ci.user = %s
                                and ci.accepted = 1)"""
        params = (
            mysql_connector.get_username(ev),
            mysql_connector.get_username(ev),
            mysql_connector.get_username(ev)
        )
        camps = mysql_connector.query_json(q, params)
        return camps

def create_campaign(data):
    sql = """
        INSERT INTO campaigns (
            camp_name,
            created_by,
            created_date,
            updated_by,
            updated_date
        ) VALUES (
            %s,
            %s,
            SYSDATE(),
            %s,
            SYSDATE());
        """

    params = (
        data.get("camp_name",""),
        mysql_connector.get_username(ev),
        mysql_connector.get_username(ev)
    )
    mysql_connector.execute_no_return(sql, params)
    camp_id = mysql_connector.get_last_insert_id()
    return camp_id

def update_campaign(data):
    sql = """
        UPDATE campaigns
        SET camp_name = %s,
            updated_by = %s,
            updated_date = SYSDATE()
        WHERE camp_id = %s
        """

    params = (
        data.get("camp_name",""),
        mysql_connector.get_username(ev),
        data.get("camp_id","")
    )
    mysql_connector.execute_no_return(sql, params)   

def delete_campaign(camp_id):
    sql = """
        DELETE FROM campaigns
        WHERE camp_id = %s
        """
    params = camp_id
    mysql_connector.execute_no_return(sql, params)

def handler(event, context):
    try:
        global ev
        ev = event
        httpMethod = event["httpMethod"]

        if httpMethod == "GET":
            params = event["queryStringParameters"]
            if params != None and "camp_id" in params:
                return mysql_connector.success_response(json.dumps(get_campaign(params["camp_id"])))
            else:
                return mysql_connector.success_response(json.dumps(get_campaign()))
        elif httpMethod == "POST":
            try:
                data = json.loads(event["body"])
                campaign_id = create_campaign(data)
                return mysql_connector.success_response(json.dumps(get_campaign(campaign_id)))
            except Exception as e:
                return mysql_connector.client_error("Invalid POST data" + str(e))
        elif httpMethod == "PUT":
            try:
                data = json.loads(event["body"])
                update_campaign(data)
                return mysql_connector.success_response(json.dumps(get_campaign(data["camp_id"])))
            except Exception as e:
                return mysql_connector.client_error("Invalid PUT data" + str(e))
        elif httpMethod == "DELETE":
            try:
                params = event["queryStringParameters"]
                delete_campaign(params["camp_id"])
                return mysql_connector.success_response_string()
            except:
                return mysql_connector.client_error("Invalid DELETE data")
        else:
            return mysql_connector.client_error("Invalid HTTP Method")
    except Exception as e:
        return mysql_connector.server_error("Unknown server error " + str(e))
        