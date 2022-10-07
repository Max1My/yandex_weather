import os
import time
import re
import pandas as pd
from bs4 import BeautifulSoup
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from UliPlot.XLSX import auto_adjust_xlsx_column_width
import sqlite3
from sqlite3 import Error
from datetime import datetime

from db import insert_into_table


def create_data_with_selenium(city):
    url = f"https://www.yandex.com/weather/{city}"
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.get(url=url)
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(3)

        with open(f"{city}.html", "w") as file:
            file.write(driver.page_source)
    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()


def get_date(soup, city):
    weather_days = soup.find_all("strong", class_="forecast-details__day-number")
    if weather_days:
        for day in weather_days:
            day_date = f"{day.text} {day.parent.findNext('span', class_='forecast-details__day-month').text}"
            forecast_field = day.findNext('dl', class_="forecast-fields")
            try:
                forecast_fields = forecast_field.find_all("dt", class_="forecast-fields__label")
                for field in forecast_fields:
                    if field.text == 'Magnetic field':
                        magnetic_field = field.find_next_sibling().text
            except AttributeError:
                pass
            day_parent = day.find_parent('article', class_="card")
            pre_data = []
            weather = get_weather(day_parent)
            avg = get_avg_temp(weather)
            air_pressure = get_air_pressure(day_parent)
            status_air = get_air_status(air_pressure)
            pre_data.append(weather)
            pre_data.append(air_pressure)
            pre_data.append(get_humidity(day_parent))
            pre_data.append(get_weather_conditions(day_parent))
            list_weather = pre_data[0]
            list_air_pressure = pre_data[1]
            list_humidity = pre_data[2]
            list_weather_conditions = pre_data[3]
            response = []
            for d in range(4):
                data = []
                data.append(list_weather[d])
                data.append(list_air_pressure[d])
                data.append(list_humidity[d])
                data.append(list_weather_conditions[d])
                response.append(data)
            magnetic_list = ['', '', '']
            magnetic_list.insert(0, magnetic_field)
            avg_temp_list = ['', '', '']
            avg_temp_list.insert(0, avg)
            status_air_list = ['', '', '']
            status_air_list.insert(1, status_air)
            response.append(magnetic_list)
            response.append(avg_temp_list)
            response.append(status_air_list)
            response = tuple(response)
            create_excel(response, day_date, city)
    else:
        insert_into_table(False, city)


def get_weather(day):
    daypart = day.find_all('div', class_="weather-table__daypart")
    data = []
    for day_value in daypart:
        data.append(day_value.find_next_sibling().text)
    return data


def get_air_pressure(day):
    air_pressure = day.find_all("td", class_="weather-table__body-cell weather-table__body-cell_type_air-pressure")
    data = []
    for pressure in air_pressure:
        data.append(pressure.text.strip())
    return data


def get_air_status(values):
    min_value = values[0]
    max_value = values[-1:][0]
    difference = int(max_value) - int(min_value)
    if difference < 5 and difference > 0:
        return ''
    if difference < -5:
        return 'ожидается резкое падение атмосферного давления'
    elif difference > 5:
        return 'ожидается резкое увеличение атмосферного давления'


def get_humidity(day):
    humidity_fields = day.find_all("td", class_="weather-table__body-cell weather-table__body-cell_type_humidity")
    data = []
    for humidity in humidity_fields:
        data.append(humidity.text)
    return data


def get_weather_conditions(day):
    weather_conditions = day.find_all("td", class_="weather-table__body-cell weather-table__body-cell_type_condition")
    data = []
    for weather_condition in weather_conditions:
        data.append(re.sub('[\t\r\n]', '', weather_condition.text).replace(" ", ""))
    return data


def average(lst):
    return int(sum(lst) / len(lst))


def get_avg_temp(temp):
    avg_temp = []
    for i in temp:
        avg_temp.append(int(re.search(r'\d+', i).group()))
    return average(avg_temp)


def get_data(city):
    with open(f"{city}.html") as file:
        src = file.read()
    soup = BeautifulSoup(src, "lxml")
    get_date(soup, city)


def create_excel(data, date, city):
    if os.path.isfile(f'./weather_{city}.xlsx') == False:
        df = pd.DataFrame(data, index=['Утро', 'День', 'Вечер', 'Ночь', 'Магнитное поле', 'Средняя температура', ""],
                          columns=['Температура', 'Давление', 'Влажность', 'Погодное явление'])
        with pd.ExcelWriter(f'weather_{city}.xlsx', mode='w') as writer:
            df.to_excel(writer, sheet_name=date)
            auto_adjust_xlsx_column_width(df, writer, sheet_name=date, margin=4)
    else:
        append_to_excel(data, date, city)


def append_to_excel(data, date, city):
    df = pd.DataFrame(data, index=['Утро', 'День', 'Вечер', 'Ночь', 'Магнитное поле', 'Средняя температура', ""],
                      columns=['Температура', 'Давление', 'Влажность', 'Погодное явление'])
    with pd.ExcelWriter(f'weather_{city}.xlsx', mode='a') as writer:
        df.to_excel(writer, sheet_name=date)
        auto_adjust_xlsx_column_width(df, writer, sheet_name=date, margin=4)
    insert_into_table(True, city)


def start_render_excel(city):
    try:
        create_data_with_selenium(city)
        get_data(city)
    except Exception as ex:
        insert_into_table(False, city)
    finally:
        os.remove(f'{city}.html')


if __name__ == '__main__':
    try:
        city = input('enter city: ').lower()
        start_render_excel(city)
    except Exception as ex:
        insert_into_table(False, city)
    finally:
        os.remove(f'{city}.html')
