# Contains all classes (just Weather)

import math
import random


class Weather:
    FREEZING_POINT = 32
    PRECIP_TARGET = 0.33
    WIND_TARGET = 15
    HUMIDITY_TARGET = 0.2

    def __init__(
        self,
        precip,
        temp,
        wind,
        gust,
        wind_dir,
        humidity,
        days=2,
    ):
        self.precip = precip
        self.temp = temp
        self.wind = wind
        self.gust = gust
        self.wind_dir = wind_dir
        self.humidity = humidity
        self.days = days

        self.weather_name = self.get_weather_name()

    def __str__(self):
        return (
            "{}% precipitation\n"
            "{}F temperature\n"
            "{}mph wind\n"
            "{}mph gust\n"
            "{} wind direction\n"
            "{}% humidity\n"
            "{}\n"
        ).format(
            round(self.precip * 100, 2),
            int(self.temp),
            int(self.wind),
            int(self.gust),
            int(self.wind_dir),
            round(self.humidity * 100, 2),
            self.weather_name,
        )

    def get_weather_name(self):
        is_freezing = self.temp < self.FREEZING_POINT

        if self.humidity > 0.5:
            if self.precip > 0.4:
                if self.wind > 43:
                    return "Blizzard" if is_freezing else "Hurricane"

                if self.wind > 25:
                    return "Snowstorm" if is_freezing else "Storm"

                return "Snow" if is_freezing else "Rain"

            if self.precip > 0.25:
                return "Sleet" if is_freezing else "Drizzle"

            if self.humidity > 0.8:
                return "Overcast"

            if self.humidity > 0.65:
                return "Cloudy"

            return "Partly cloudy"

        if self.precip > 0.4:
            return "Snow" if is_freezing else "Rain"

        if self.precip > 0.2:
            return "Sleet" if is_freezing else "Drizzle"

        if self.humidity < 0.1:
            return "Sunny"

        if self.humidity < 0.2:
            return "Partly sunny"

        return "Clear"

    def mutate(self, steps=1):
        for _ in range(steps):
            self._mutate_precipitation()
            self._mutate_wind()
            self._mutate_temperature()
            self._mutate_humidity()

            self.gust = self.wind * random.randint(210, 260) * 0.01
            self.days += 1

        self.weather_name = self.get_weather_name()

    def _mutate_precipitation(self):
        difference = self.PRECIP_TARGET - self.precip

        movement = random.randint(-100, 100) / 400.0
        movement += (
            random.randint(0, int(100 * abs(difference))) / 200.0
        ) * self._direction(difference)

        self.precip = self._clamp(
            self.precip + movement,
            0,
            1,
        )

    def _mutate_wind(self):
        self.wind_dir = (
            self.wind_dir + random.randint(-3, 3)
        ) % 8

        difference = self.WIND_TARGET - self.wind

        movement = random.randint(-100, 100) / 13.0
        movement += (
            random.randint(0, int(abs(difference))) / 3.0
        ) * self._direction(difference)

        self.wind = max(0, self.wind + movement)

    def _mutate_temperature(self):
        adjusted_days = self.days - 282

        target = (
            40
            * (
                math.sin(
                    (2 * math.pi * adjusted_days) / 365
                    - math.pi / 3
                )
                + 1
            )
            + 20
        )

        difference = target - self.temp

        movement = random.randint(-100, 100) / 20.0
        movement += (
            random.randint(0, int(abs(difference))) / 5.0
        ) * self._direction(difference)

        self.temp = max(0, self.temp + movement)

    def _mutate_humidity(self):
        difference = self.HUMIDITY_TARGET - self.humidity

        movement = random.randint(-100, 100) / 500.0
        movement += (
            random.randint(0, int(100 * abs(difference))) / 200.0
        ) * self._direction(difference)

        self.humidity = self._clamp(
            self.humidity + movement,
            0,
            1,
        )

    @staticmethod
    def _direction(value):
        if value < 0:
            return -1

        return 1

    @staticmethod
    def _clamp(value, minimum, maximum):
        return min(maximum, max(minimum, value))


# 22.10.2009: Cloudy, precip 20%, temp 43, wind dir 6, 13 (25)
# 23.10.2009: Sunny, precip 4%, temp 52, wind dir 7, 12 (25)
# 24.10.2009: Partly sunny, precip 7%, temp 48, wind dir 1, 8 (20)
known_weathers = (
    Weather(0.203, 43, 13, 25, 6, 0.66),
    Weather(0.04, 52, 12, 25, 7, 0.1),
    Weather(0.07, 48, 8, 20, 1, 0.1, 200),
    Weather(0.07, 48, 8, 20, 1, 0.1, 528 + 200),
    Weather(-1, -1, -1, -1, -1, -1),
)

known_weathers[4].weather_name = "Connection lost...      "