from time import sleep

import pandas as pd
import json
import os
import sys
import pymysql
from pymysql import Error
import time, datetime
import requests

'''
for remote access - add HOSTNAME=localhost to env  
ssh -L 8676:127.0.0.1:3306 ialerner@cse191.ucsd.edu
'''
class dbClass:

    def __init__(self, type="JSON"):
        self.outType = type
        # AMAZON CLOUD - AWS DB Cluster
        print("connect to main DB")
        self.servername = "127.0.0.1"
        self.username = "root"
        self.password = "iotiot"
        self.dbname = "cse191"
        self.port = 3306

        if os.getenv('HOSTNAME') == "localpc":
            print("connect local ssh tunnel")
            self.port = 8676

        self.reconnect()

    def check_conn(self):

        # test connection
        try:
            if self.db.cursor().execute("SELECT now()") == 0:
                return self.reconnect()
            else:
                print("DB connection OK\n")
                return True
        except:
            print("Unexpected exception occurred: ", sys.exc_info())
            return self.reconnect()

    def reconnect(self):

        # try to connect 5 times
        retry = 5
        while retry > 0:
            try:
                print("connecting to DB...")
                self.db = pymysql.connect(
                    host=self.servername,
                    user=self.username,
                    password=self.password,
                    database=self.dbname,
                    port=self.port
                )
                retry = 0
                return True
            except:
                print("Unexpected exception occurred: ", sys.exc_info())
                retry -= 1
                if retry > 0:
                    print("retry\n")
                    sleep(2)
                else:
                    exit(-1)

        print("Success\n")

    def postWeather(self):
        if self.check_conn():
            zip = "92093"
            weatherData = requests.get(f'http://api.openweathermap.org/data/2.5/weather?zip={zip},us&appid=0354c29c5e773c46d37727c8a0455d58')
            weatherData = json.loads(weatherData.text)
            timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

            sqlstr = f"INSERT INTO cse191.forecast (temperature,  humidity, min_temp, max_temp, forecast_ts, groupname, sunrise, sunset, zipcode)\
                        VALUES (\"{weatherData['main']['temp']}\",\
                            \"{weatherData['main']['humidity']}\",\
                            \"{weatherData['main']['temp_min']}\",\
                            \"{weatherData['main']['temp_max']}\",\
                            \"{timestamp}\",\
                            \"The Boyz\",\
                            \"{datetime.datetime.fromtimestamp(weatherData['sys']['sunrise']).strftime('%Y-%m-%d %H:%M:%S')}\",\
                            \"{datetime.datetime.fromtimestamp(weatherData['sys']['sunset']).strftime('%Y-%m-%d %H:%M:%S')}\",\
                            \"{zip}\");"

            cursor = self.db.cursor()
            try:
                cursor.execute(sqlstr)
                cursor.execute("COMMIT;")
                return True
            except Error as e:
                print(e)
        return False