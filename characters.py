import mysql_connector
import json

ev = dict()

def get_char(char_id=None):
    q = """ 
        select
            ch.char_id,
            ch.char_name,
            ch.lvl,
            ch.str,
            ch.dex,
            ch.con,
            ch.intel,
            ch.wis,
            ch.cha,
            ch.armor_class,
            IFNULL(ra2.race_id, ra.race_id) race_id,
            IFNULL(ra2.race_name, ra.race_name) race_name,
            IFNULL(ra2.speed, ra.speed) speed,
            ra.race_id subrace_id,
            ra.race_name subrace_name,
            IFNULL(cl2.class_id, cl.class_id) class_id,
            IFNULL(cl2.class_name, cl.class_name) class_name,
            IFNULL(cl2.hit_die, cl.hit_die) hit_die,
            cl.class_id subclass_id,
            cl.class_name subclass_name,
            ba.value_id background_id,
            ba.set_value background_name,
            ba.value_desc background_desc,
            IF(ch.caster, 'true', 'false') caster,
            ch.created_by
        from characters ch,
			 classes cl
             LEFT OUTER JOIN classes cl2
             ON cl.parent_id = cl2.class_id,
             races ra
             LEFT OUTER JOIN races ra2
             ON ra.parent_id = ra2.race_id,
             set_values ba
             {}
        where ch.class_id = cl.class_id
		and	  ch.race_id = ra.race_id
        and   ch.background_id = ba.value_id
        """
        
    params = ev["queryStringParameters"]
    if char_id != None:
        q = q.format("")
        q = q + " and ch.char_id = %s"
        params = char_id
        char = mysql_connector.single_query_json(q, params)
        char["race_traits"] = get_race_traits(char["race_id"])
        char["class_traits"] = get_class_traits(char["class_id"])
        char["armor"] = get_char_armor(char_id)
        char["spells"] = get_char_spells(char_id)
        char["weapons"] = get_char_weapons(char_id)
        return char
    elif params != None and "camp_id" in params:
        q = q.format(", campaign_chars cc ")
        q = q + "and ch.char_id = cc.char_id and cc.camp_id = %s"
        params = params["camp_id"]
        chars = [get_char(c["char_id"]) for c in mysql_connector.query_json(q, params)]
        return chars
    else:
        q = q.format("")
        q = q + " and ch.created_by = %s"
        params = mysql_connector.get_username(ev)
        chars = [get_char(c["char_id"]) for c in mysql_connector.query_json(q, params)]
        return chars
def get_race_traits(race_id):
    q = """ 
        select
            rt.trait_id,
            rt.race_id,
            rt.trait_name,
            rt.trait_desc,
            rt.created_by
        from race_traits rt,
            races r
        where r.race_id = %s
        and (rt.race_id = r.race_id or rt.race_id = r.parent_id)
        order by 3
        """
    params = race_id
    return mysql_connector.query_json(q, params)
def get_class_traits(class_id):
    q = """ 
        select
            ct.trait_id,
            ct.class_id,
            ct.trait_name,
            ct.trait_desc,
            ct.char_level,
            ct.created_by
        from class_traits ct,
                classes c
        where c.class_id = %s
        and (ct.class_id = c.class_id or ct.class_id = c.parent_id)
        order by 5, 3
        """
    params = class_id
    return mysql_connector.query_json(q, params)
def get_char_armor(char_id):
    q = """ 
        select
            a.armor_id,
            a.armor_name,
            a.armor_desc,
            a.armor_type,
            a.cost,
            a.armor_class,
			a.strength,
            IF(a.stealth_dis, 'true', 'false') stealth_dis,
            a.weight,
            a.created_by
        from armor a,
			 char_assets ca
		where ca.asset_id = a.armor_id
        and asset_type = 'Armor'
        and ca.char_id = %s
        """
    params = char_id
    return mysql_connector.query_json(q, params)
def get_char_spells(char_id):
    q = """ 
        select
            s.spell_id,
            s.spell_name,
            s.spell_desc,
            s.spell_level,
            s.higher_level,
            s.spell_range,
            s.components,
            IF(s.ritual, 'true', 'false') ritual,
            s.duration,
            s.casting_time,
            s.spell_school,
            s.created_by
        from spells s,
			 char_assets ca
		where ca.asset_id = s.spell_id
        and asset_type = 'Spells'
        and ca.char_id = %s
        """
    params = char_id
    return mysql_connector.query_json(q, params)
def get_char_weapons(char_id):
    q = """ 
        select
            w.weapon_id,
            w.weapon_name,
            w.weapon_desc,
            w.weapon_type,
            w.cost,
            w.damage,
            w.weight,
            w.weapon_props,
            w.created_by
        from weapons w,
			 char_assets ca
		where ca.asset_id = w.weapon_id
        and asset_type = 'Weapons'
        and ca.char_id = %s
        """
    params = char_id
    return mysql_connector.query_json(q, params)

def create_char(event, data):
    sql = """
        INSERT INTO characters (
            class_id,
            race_id,
            background_id,
            char_name,
            lvl,
            str,
            dex,
            con,
            intel,
            wis,
            cha,
            armor_class,
            caster,
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
            %s,
            %s,
            SYSDATE(),
            %s,
            SYSDATE());
        """

    params = (
        data.get("class_id",""),
        data.get("race_id",""),
        data.get("background_id",""),
        data.get("char_name",""),
        data.get("lvl",""),
        data.get("str",""),
        data.get("dex",""),
        data.get("con",""),
        data.get("intel",""),
        data.get("wis",""),
        data.get("cha",""),
        data.get("armor_class",""),
        (1 if str(data.get("caster","")).lower() == "true" else 0),
        mysql_connector.get_username(event),
        mysql_connector.get_username(event)
    )
    mysql_connector.execute_no_return(sql, params)
    char_id = mysql_connector.get_last_insert_id()

    return char_id

def update_char(event, data):
    sql = """
        UPDATE characters
        SET char_name = %s,
            lvl = %s,
            str = %s,
            dex = %s,
            con = %s,
            intel = %s,
            wis = %s,
            cha = %s,
            armor_class = %s,
            caster = %s,
            updated_by = %s,
            updated_date = SYSDATE()
        WHERE char_id = %s
        """

    params = (
        data.get("char_name",""),
        data.get("lvl",""),
        data.get("str",""),
        data.get("dex",""),
        data.get("con",""),
        data.get("intel",""),
        data.get("wis",""),
        data.get("cha",""),
        data.get("armor_class",""),
        (1 if str(data.get("caster","")).lower() == "true" else 0),
        mysql_connector.get_username(event),
        data.get("char_id","")
    )
    mysql_connector.execute_no_return(sql, params)

def delete_char(char_id):
    sql = """
        DELETE FROM characters
        WHERE char_id = %s
        """
    params = char_id
    mysql_connector.execute_no_return(sql, params)

def add_asset(event, data):
    sql = """
        INSERT INTO char_assets (
            char_id,
            asset_id,
            asset_type,
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
        data.get("char_id",""),
        data.get("asset_id",""),
        data.get("asset_type",""),
        mysql_connector.get_username(event),
        mysql_connector.get_username(event)
    )
    return mysql_connector.execute(sql, params)
def remove_asset(data):
    sql = """
        DELETE FROM char_assets
        WHERE char_id = %s
        and asset_id = %s
        and asset_type = %s
        LIMIT 1;
        """
    params = (
        data.get("char_id",""),
        data.get("asset_id",""),
        data.get("asset_type","")
    )
    return mysql_connector.execute(sql, params)

def add_campaign(event, data):
    sql = """
        INSERT IGNORE INTO campaign_chars (
            camp_id,
            char_id,
            created_by,
            created_date,
            updated_by,
            updated_date
        ) VALUES (
            %s,
            %s,
            %s,
            SYSDATE(),
            %s,
            SYSDATE());
        """

    params = (
        data.get("camp_id",""),
        data.get("char_id",""),
        mysql_connector.get_username(event),
        mysql_connector.get_username(event)
    )
    return mysql_connector.execute(sql, params)
def remove_campaign(data):
    sql = """
        DELETE FROM campaign_chars
        WHERE camp_id = %s
        and char_id = %s
        """
    params = (
        data.get("camp_id",""),
        data.get("char_id","")
    )
    return mysql_connector.execute(sql, params)

def handler(event, context):
    try:
        global ev
        ev = event
        httpMethod = event["httpMethod"]

        if httpMethod == "GET":
            params = event["queryStringParameters"]
            if params != None and "char_id" in params:
                return mysql_connector.success_response(json.dumps(get_char(params["char_id"])))
            else:
                return mysql_connector.success_response(json.dumps(get_char()))
        elif httpMethod == "POST":
            try:
                data = json.loads(event["body"])
                if 'asset_id' in data:
                    return add_asset(event, data)
                elif 'camp_id' in data:
                    return add_campaign(event, data)
                else:
                    char_id = create_char(event, data)
                    return mysql_connector.success_response(json.dumps(get_char(char_id)))
            except Exception as e:
                return mysql_connector.client_error("Invalid POST data" + str(e))
        elif httpMethod == "PUT":
            try:
                data = json.loads(event["body"])
                update_char(event, data)
                return mysql_connector.success_response(json.dumps(get_char(data["char_id"])))
            except Exception as e:
                return mysql_connector.client_error("Invalid PUT data" + str(e))
        elif httpMethod == "DELETE":
            try:
                params = event["queryStringParameters"]
                if 'asset_id' in params:
                    return remove_asset(params)
                elif 'camp_id' in params:
                    return remove_campaign(params)
                else:
                    delete_char(params["char_id"])
                    return mysql_connector.success_response_string()
            except:
                return mysql_connector.client_error("Invalid DELETE data")
        else:
            return mysql_connector.client_error("Invalid HTTP Method")
    except Exception as e:
        return mysql_connector.server_error("Unknown server error: " + str(e))
        