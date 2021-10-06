import json

import requests
import datetime
from rejson import Client, Path
from rest_framework import status, serializers

from backend import settings
from backend.settings import REDIS_HOST, REDIS_PORT, WEATHER_API_KEY

import types
from botocore.client import Config
import ibm_boto3


class ReJsonWeather:
    WEATHER_48HOUR = '48hour'
    WEATHER_2DAY = '2day'
    WEATHER_WEEK = '7day'
    WEATHER_MONTH = '1month'
    WEATHER_YEAR = '1year'

    rj = None
    weather_48hour_api = 'https://api.weather.com/v1/geocode/{}/{}/forecast/hourly/48hour.json?units=m&language=mn&apiKey=' + WEATHER_API_KEY
    weather_weekly_api = 'https://api.weather.com/v1/geocode/{}/{}/forecast/intraday/7day.json?units=m&language=mn&apiKey=' + WEATHER_API_KEY

    weather_2day_api = 'https://api.weather.com/v3/wx/forecast/hourly/2day?geocode={},{}&format=json&units=m&language=mn&apiKey=' + WEATHER_API_KEY

    def __init__(self):
        self.rj = Client(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

    def __iter__(self):
        return 0

    def _set_weather(self, params, data):
        self.rj.jsonset("{}-{}-{},{}".format(params['type'], params['date'], params['lat'], params['lon']),
                        Path.rootPath(), data)

    def get_weather(self, params):
        data = self.rj.jsonget("{}-{}-{},{}".format(params['type'], params['date'], params['lat'], params['lon']),
                               no_escape=True)
        if params['type'] == self.WEATHER_2DAY:
            return data if data else self._get_weather_data(params)
        if params['type'] == self.WEATHER_48HOUR:
            return self._get_trim_24hour_data(data) if data else self._get_trim_24hour_data(
                self._get_weather_data(params))
        if params['type'] == self.WEATHER_WEEK:
            return data if data else self._get_weather_data(params)
        # else ibm cloud data

        return self._ibm_cloud_data(params)

    def get_notification_weather_data(self, lat_lon):
        lat, lon = lat_lon.split(",")
        params = {
            "lat": lat,
            "lon": lon,
            "type": self.WEATHER_2DAY,
            "date": str(datetime.datetime.now().date())
        }
        return self.get_weather(params)

    def _get_weather_data(self, params):
        url = self.weather_48hour_api
        if params['type'] == self.WEATHER_2DAY:
            url = self.weather_2day_api
        if params['type'] == self.WEATHER_WEEK:
            url = self.weather_weekly_api
        response = requests.get(url.format(params['lat'], params['lon']))
        if response.status_code == status.HTTP_200_OK:
            json_res = response.json()
            self._set_weather(params, json_res)
            return json_res
        else:
            raise serializers.ValidationError("weather data api not working")

    @staticmethod
    def _get_trim_24hour_data(forecasts):
        date_now = datetime.datetime.now()
        time = str(date_now.time()).split('.')[0]
        norm_time = '{}T{}:00:00+0800'.format(date_now.date(), time.split(":")[0])
        sel_ind = 0
        for ind in range(len(forecasts['forecasts'])):
            if forecasts['forecasts'][ind]['fcst_valid_local'] == norm_time:
                sel_ind = ind
                break
        return forecasts['forecasts'][sel_ind:sel_ind + 24]

    @staticmethod
    def _ibm_client():
        try:
            return ibm_boto3.client(service_name='s3',
                                    ibm_api_key_id=settings.IBM_API_KEY_ID,
                                    ibm_auth_endpoint=settings.IBM_AUTH_ENDPOINT,
                                    config=Config(signature_version='oauth'),
                                    endpoint_url=settings.IBM_ENDPOINT)
        except ValueError as ex:
            raise serializers.ValidationError(str(ex))

    def _ibm_cloud_data(self, params):
        filename = 'output_json/{},{}.json'.format(params['lat'], params['lon'])
        ibm_client = self._ibm_client()

        streaming_body_1 = ibm_client.get_object(Bucket=settings.IBM_CLOUD_BUCKET,
                                                 Key=filename)['Body']
        # add missing __iter__ method, so pandas accepts body as file-like object
        if not hasattr(streaming_body_1, "__iter__"): streaming_body_1.__iter__ = types.MethodType(self.__iter__,
                                                                                                   streaming_body_1)
        raw_data = streaming_body_1.read()
        json_data = json.loads(raw_data)
        now_date = datetime.datetime.now().date()
        month_data = []
        year_data = []
        for data in json_data:
            start_date = datetime.datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            if now_date <= start_date:
                year_data.append(data)
                if len(month_data) < 4:
                    month_data.append(data)
        if params['type'] == self.WEATHER_MONTH:
            self._set_weather(params, month_data)
            return month_data
        self._set_weather(params, year_data)
        return year_data
