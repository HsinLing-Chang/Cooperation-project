from backend.model.db_connector import mysql_pool
from datetime import date
from fastapi import HTTPException


def search_user_with_email(email, cursor):
    cursor.execute(
        "SELECT email, webhook_url, city, notify_time FROM webhook WHERE email=%s", (email,))
    email = cursor.fetchone()
    return email


def create_webhook_data(email, webhook_url: str, city: str, notify_time: str):
    try:
        today = date.today()
        con = mysql_pool.get_connection()
        cursor = con.cursor(dictionary=True)
        user_email = search_user_with_email(email, cursor)
        if user_email:
            return {"error": True, "message": "此信箱已被註冊"}
        query = "INSERT INTO webhook (email, webhook_url, city, notify_time)" \
            "VALUES(%s, %s, %s, %s)"
        params = (email, webhook_url, city, notify_time)
        cursor.execute(query, params)
        con.commit()
        return {"ok": True}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="伺服器錯誤，請重新嘗試")
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()


def update_webhook_data(email, webhook_url: str = None, city: str = None, notify_time: str = None):
    try:
        con = mysql_pool.get_connection()
        cursor = con.cursor(dictionary=True)
        user_email = search_user_with_email(email, cursor)
        if not user_email:
            return {"error": True, "message": "未找到用戶，請註冊後再嘗試"}
        webhook_url = webhook_url if webhook_url else user_email.get(
            "webhook_url")
        city = city if city else user_email.get("city")
        notify_time = notify_time if notify_time else user_email.get(
            "notify_time")
        query = "UPDATE webhook SET webhook_url = %s, city = %s, notify_time= %s WHERE email = %s"
        params = (webhook_url, city, notify_time, email)
        cursor.execute(query, params)
        con.commit()
        return {"ok": True}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="伺服器錯誤，請重新嘗試")
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()


def get_all_webhook_data(hour):
    try:
        con = mysql_pool.get_connection()
        cursor = con.cursor(dictionary=True)
        query = "SELECT city, webhook_url FROM webhook WHERE notify_time=%s"
        param = hour
        cursor.execute(query, (param,))
        all_data = cursor.fetchall()
        return all_data
    except Exception as e:
        print(e)
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()
