import pandas as pd
import datetime
import calendar
from pytz import timezone
from solartime import SolarTime
import numpy as np
import matplotlib.pyplot as plt


def str_to_hour(s):
    h, m = s.split(',')
    h = int(h)
    m = int(m)
    return h + m / 60


# Loading data into DataFrame and limiting results to Poland
wcits_df = pd.read_csv('data/worldcities.csv')
polcits_df = wcits_df.loc[(wcits_df['country'] == 'Poland')]

while True:
    city_name = input('Which polish city are you interested in?\n')
    # Handling 'Warszawa' input as its only city name in database in english
    if city_name == 'Warszawa':
        city_name = 'Warsaw'

    try:
        if not polcits_df['city'].isin([city_name]).any():
            raise ValueError
        else:
            break
    except ValueError:
        print('We have no record of such city :( \nPlease, try again.')

# Choosing data for given city
cit_df = polcits_df.loc[(polcits_df['city'] == city_name)]
cit_arr = cit_df.to_numpy()
lat = round(cit_df['lat'].to_numpy()[0], 2)
lng = round(cit_df['lng'].to_numpy()[0], 2)

# Getting current year and timezone in Poland (CET)
year = int(datetime.datetime.now().strftime('%Y'))
local_tz = timezone('Europe/Warsaw')

# Collecting dates from current year
curr_year_dates = []
for month in range(1, 13):
    num_days = calendar.monthrange(year, month)[1]
    for day in range(1, num_days + 1):
        date = datetime.date(year, month, day)
        curr_year_dates.append(date)

# Looping over the dates to get the sunrise and sunset times using solartime package
sr_times = []
ss_times = []
for date in curr_year_dates:
    sun = SolarTime()
    schedule = sun.sun_utc(date, lat, lng)
    sr_times.append(schedule['sunrise'].astimezone(local_tz).strftime('%H, %M'))
    ss_times.append(schedule['sunset'].astimezone(local_tz).strftime('%H, %M'))

sr_hours = [str_to_hour(sr_time) for sr_time in sr_times]
ss_hours = [str_to_hour(ss_time) for ss_time in ss_times]
day_hours = np.array(ss_hours) - np.array(sr_hours)

fig, ax = plt.subplots()

# Plotting the sunrise and sunset hours
ax.plot(curr_year_dates, sr_hours, 'r-', label='Sunrise')
ax.plot(curr_year_dates, ss_hours, 'b-', label='Sunset')
ax.plot(curr_year_dates, day_hours, 'g--', alpha=0.25, label='Day duration')

# Setting the x-axis to show the dates of the year
ax.set_xticks(curr_year_dates[::30])  # Use every 30th date as a tick
ax.set_xticklabels([date.strftime('%b %d') for date in curr_year_dates[::30]])  # Format the dates as month and day

# Setting the y-axis to show the hours of the day
ax.set_yticks(range(0, 25))  # Use every hour as a tick
ax.set_yticklabels([f'{hour}:00' for hour in range(0, 25)])  # Format the hours as HH:00

# Setting the labels, title, legend and grid
ax.set_xlabel('Date')
ax.set_ylabel('Hour')
ax.set_title(f'Sunrise and sunset hours for {city_name} in {year}')
ax.legend()
plt.rc('grid', linestyle="-", color='black')
plt.grid(True)

plt.show()
