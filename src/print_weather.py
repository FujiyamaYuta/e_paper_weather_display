#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os

picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

from waveshare_epd import epd7in5_V2
import icon_mapping
import config

import logging
import time
from PIL import Image, ImageDraw, ImageFont
import traceback
import requests
import json
import math
from datetime import datetime, timedelta, date

API_KEY = config.API_KEY
LATITUDE = config.LATITUDE
LONGITUDE = config.LONGITUDE
TSUKURUMIJIMA_TENKI_CODE = config.TSUKURUMIJIMA_TENKI_CODE
UNITS = 'metric'

BASE_URL = 'https://api.openweathermap.org/data/2.5/weather?'
URL = BASE_URL + 'lat=' + LATITUDE + '&lon=' + LONGITUDE + '&units=' + UNITS + '&appid=' + API_KEY

TSUKURUMIJIMA_TENKI_URL = 'https://weather.tsukumijima.net/api/forecast/city/' + TSUKURUMIJIMA_TENKI_CODE

black = 'rgb(0,0,0)'
white = 'rgb(255,255,255)'
grey = 'rgb(235,235,235)'

logging.basicConfig(level=logging.DEBUG)


def write_to_screen():

    logging.info("epd7in5_V2 Demo")
    epd = epd7in5_V2.EPD()

    logging.info("init and Clear")
    epd.init()
    epd.Clear()

    # openweathermap API
    response = requests.get(URL)
    data = response.json()

    # 天気予報 API（livedoor 天気互換）
    tsukumijima_response = requests.get(TSUKURUMIJIMA_TENKI_URL)
    tsukumijima = tsukumijima_response.json()

    font12 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 12)
    font16 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 16)
    font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
    font22 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 22)
    font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
    font30 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 30)
    font35 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 35)
    font40 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 40)
    font50 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 50)
    font60 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 60)
    font100 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 100)
    font120 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 120)
    font160 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 160)

    # 気温・最高・最低を小数点第一まで表示する
    wather = str(tsukumijima['forecasts'][0]['detail']['weather']).replace('　', '')
    temp = '{:.1f}'.format(data['main']['temp'])
    temp_max = '{:.1f}'.format(data['main']['temp_max'])
    temp_min = '{:.1f}'.format(data['main']['temp_min'])

    DIFF_JST_FROM_UTC = 9
    now = datetime.utcnow() + timedelta(hours=DIFF_JST_FROM_UTC)
    w_list = ['（月）', '（火）', '（水）', '（木）', '（金）', '（土）', '（日）']
    today = now.today().weekday()
    time_str = now.strftime('%Y年%m月%d日' + w_list[today])

    logging.info("1.Drawing on the Horizontal image...")
    Himage = Image.open(os.path.join(picdir, '7in5_V2_template.png'))
    draw = ImageDraw.Draw(Himage)

    # === 気温 ===
    draw.text((275, 8), str(temp) + '°C', font=font160, fill=0)  # 気温
    draw.text((35, 335), '最高：' + str(temp_max) + '°C', font=font40, fill=0)  # 最高
    draw.rectangle((170, 385, 285, 387), fill=0)
    draw.text((35, 400), '最低：' + str(temp_min) + '°C', font=font40, fill=0)  # 最低
    # === 気温 ===

    # === アイコン + 日付 ===
    icon_image = Image.open(os.path.join(picdir, data['weather'][0]['icon'] + '.png'))
    Himage.paste(icon_image, (40, 15))
    draw.rectangle((25, 20, 225, 180), outline=0)
    draw.text((20, 200), str(time_str), font=font22, fill=0)
    draw.text((30, 240), str(wather), font=font22, fill=0)
    # === アイコン + 日付 ===

    # === 降水確率 ===
    draw.text((275, 220), '降水確率', font=font22, fill=0)
    draw.rectangle((375, 280, 372, 195), fill=0)
    draw.text((390, 200), '00-06時', font=font22, fill=0)
    draw.text((400, 240), str(tsukumijima['forecasts'][0]['chanceOfRain']['T00_06']), font=font22, fill=0)
    draw.text((490, 200), '06-12時', font=font22, fill=0)
    draw.text((500, 240), str(tsukumijima['forecasts'][0]['chanceOfRain']['T06_12']), font=font22, fill=0)
    draw.text((590, 200), '12-18時', font=font22, fill=0)
    draw.text((600, 240), str(tsukumijima['forecasts'][0]['chanceOfRain']['T12_18']), font=font22, fill=0)
    draw.text((690, 200), '18-24時', font=font22, fill=0)
    draw.text((700, 240), str(tsukumijima['forecasts'][0]['chanceOfRain']['T18_24']), font=font22, fill=0)
    # === 降水確率 ===

    # === 明日の天気 ===
    tommorow_telop = tsukumijima['forecasts'][1]['telop']
    tommorow_datetime = datetime.strptime(tsukumijima['forecasts'][1]['date'], '%Y-%m-%d').date()
    tommorow_week = datetime.strptime(tsukumijima['forecasts'][1]['date'], '%Y-%m-%d').date().weekday()
    tommorow = tommorow_datetime.strftime('%m月%d日' + w_list[tommorow_week])
    icon_tomorow_image = Image.open(os.path.join(picdir, icon_mapping.half_icon[tommorow_telop]))
    Himage.paste(icon_tomorow_image, (335, 335))
    draw.text((320, 316), tommorow, font=font18, fill=0)
    draw.text((325, 410), tommorow_telop, font=font16, fill=0)
    draw.text((325, 430), '最高：' + tsukumijima['forecasts'][1]['temperature']['max']['celsius'] + '°C', font=font16, fill=0)
    draw.text((325, 450), '最低：' + tsukumijima['forecasts'][1]['temperature']['min']['celsius'] + '°C', font=font16, fill=0)
    # === 明日の天気 ===

    # === 明後日の天気 ===
    day_after_tomorrow_telop = tsukumijima['forecasts'][2]['telop']
    day_after_tomorrow_datetime = datetime.strptime(tsukumijima['forecasts'][2]['date'], '%Y-%m-%d').date()
    day_after_tomorrow_week = datetime.strptime(tsukumijima['forecasts'][2]['date'], '%Y-%m-%d').date().weekday()
    day_after_tomorrow = day_after_tomorrow_datetime.strftime('%m月%d日' + w_list[day_after_tomorrow_week])
    icon_tomorow_image = Image.open(os.path.join(picdir, icon_mapping.half_icon[day_after_tomorrow_telop]))
    Himage.paste(icon_tomorow_image, (475, 335))
    draw.text((460, 316), day_after_tomorrow, font=font18, fill=0)
    draw.text((465, 410), day_after_tomorrow_telop, font=font16, fill=0)
    draw.text((465, 430), '最高：' + tsukumijima['forecasts'][2]['temperature']['max']['celsius'] + '°C', font=font16, fill=0)
    draw.text((465, 450), '最低：' + tsukumijima['forecasts'][2]['temperature']['min']['celsius'] + '°C', font=font16, fill=0)
    # === 明後日の天気 ===

    # === 更新の時間 ===
    draw.text((627, 330), 'UPDATED', font=font35, fill=white)
    current_time = datetime.now().strftime('%H:%M')
    draw.text((627, 375), current_time, font=font60, fill=white)
    # === 更新の時間 ===

    epd.display(epd.getbuffer(Himage))


try:
    write_to_screen()
except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd7in5_V2.epdconfig.module_exit()
    exit()
