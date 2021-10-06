import json
from numpy import average, around
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from users.models import MobileUser, Role
from farmers.models import Farmer

from api.weather_utils import ReJsonWeather
from users.models import Notifications


class Command(BaseCommand):
    help = 'Api Broadcast'

    # def add_arguments(self, parser):
    #     parser.add_argument('')

    def handle(self, *args, **options):
        mobile_users = MobileUser.objects.exclude(fcm_id=None, role__user_type=Role.FARMER)
        locations = []
        target_users = {}
        for mobile_user in mobile_users:
            farmer_sum = mobile_user.role.farmer_sum
            if farmer_sum:
                loc = "{},{}".format(farmer_sum.lat, farmer_sum.lon)
                locations.append(loc)
                if not target_users.get(loc, None):
                    target_users[loc] = []
                target_users[loc].append(mobile_user.role.user)
        locations = list(dict.fromkeys(locations))
        # self.stdout.write(self.style.SUCCESS('Target users "%s"' % str(json.dumps(list(target_users)))))
        rejson = ReJsonWeather()
        for location in locations:
            data = rejson.get_notification_weather_data(location)

            weather_data = {
                "max_temp": max(data['temperature'][:19]),
                "min_temp": min(data['temperature'][:19]),
                "mean_rain": around(average(data['precipChance'][:19]), decimals=1),
                "mean_wind": around(average(data['windSpeed'][:19]) / 3.6, decimals=1),
                "mean_humid": around(average(data['relativeHumidity'][:19]), decimals=1),

            }

            payload = {
                "title": "Өнөөдөр цаг агаар {}° {}° дундаж бороо орох магадлал {}% дундаж салхи {} м/c дундаж чийгшэл {}%  ".format(
                    weather_data['min_temp'],
                    weather_data['max_temp'],
                    weather_data['mean_rain'],
                    weather_data['mean_wind'],
                    weather_data['mean_humid'],
                ),
                "not_styled_title": "Өнөөдөр цаг агаар {}° {}° дундаж бороо орох магадлал {}% дундаж салхи {} м/c дундаж чийгшэл {}%  ".format(
                    weather_data['min_temp'],
                    weather_data['max_temp'],
                    weather_data['mean_rain'],
                    weather_data['mean_wind'],
                    weather_data['mean_humid'],
                ),
                "route": "WeatherSummary",
                "params": {
                },
                "type": Notifications.MOBILE
            }
            for user in target_users[location]:
                Notifications.objects.create(user_id=user.id, **payload)

                self.stdout.write(self.style.SUCCESS('Successfully send locations weather data "%s"' % str(location)))
