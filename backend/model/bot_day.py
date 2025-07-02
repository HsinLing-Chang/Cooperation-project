import requests
from .api_response_handler import get_weather_by_city
from backend.model.db_connector import mysql_pool


class Bot_daily():
    def __init__(self, url):
        self.url = url

    def __get_radar_data(self):
        try:
            con = mysql_pool.get_connection()
            cursor = con.cursor(dictionary=True)
            cursor.execute(
                "SELECT radar_img_url FROM radar_data ORDER BY radar_time DESC LIMIT 1")
            data = cursor.fetchone()
            if data:
                return data.get("radar_img_url")
            print("找不到rader data")
        except Exception as e:
            print(e)
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()

    def __get_detail(self, value):
        data = value.split("。")
        obj = {
            "天氣現象": data[0],
            "降雨機率": data[1][-2:],
            "舒適度": data[3],
            "濕度": data[5][-3:]
        }
        return obj

    def __build_embed(self, city, obj):
        img_url = self.__get_radar_data()
        return {
            "title": f"當前天氣預報--{city}",
            "url": "http://18.180.198.102:8001/",
            "description": f"天氣現象: {obj.get("天氣現象")}\n降雨機率: {obj.get('降雨機率')}\n舒適度: {obj.get('舒適度')}\n濕度: {obj.get('濕度')}\n最高溫度: {obj.get('最高溫度')}°C\n最低溫度: {obj.get('最低溫度')}°C",
            # "thumbnail": {"url": "https://www.cwa.gov.tw/Data/radar/CV1_3600_202504301410.png"},
            "image": {"url": img_url},
            "color": 16753920,
            "footer": {
                "text": f"資料來源：中央情報局 👨‍💻"
            }
        }

    def __build_data(self, city, obj):
        embed = self.__build_embed(city, obj)
        data = {
            "username": "瑞克雷達",
            "avatar_url": "https://image-cdn.hypb.st/https%3A%2F%2Fhk.hypebeast.com%2Ffiles%2F2021%2F08%2Fnever-gonna-give-you-up-passes-one-billion-views-01.jpg?w=960&cbr=1&q=90&fit=max",
            "embeds": [embed]
        }
        return data

    def get_current_weather_data(self, city):
        try:
            weather_data = get_weather_by_city(
                city, ["最高溫度", "最低溫度", "天氣預報綜合描述"])
            weathers = weather_data.get("weather")
            obj = {}
            for weather in weathers:
                element_type = weather.get("elementType")
                element_value = weather.get("elementValue")
                values = element_value[0].get("values")
                key, value = list(values.items())[0]
                if element_type == "天氣預報綜合描述":
                    weather_detail = self.__get_detail(value)
                    obj = {**weather_detail, **obj}
                else:
                    obj[element_type] = value
            weather_data = self.__build_data(city, obj)
            response = requests.post(self.url, json=weather_data)
            if response.status_code == 204:
                print(f"✅ 訊息發送成功")
        except Exception as e:
            print(e)
