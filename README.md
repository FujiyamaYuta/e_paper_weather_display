# 概要

Raspberry Pi × 電子ペーパーで最新のお天気情報を表示する電子版を作りました！！ 初めてRaspberryを触ってみたので、環境構築から開発するまでの取り組みをZennにまとめました！！

**RaspberryPiを購入して何かを作ろうとしている人**、**夏休みの工作で何か作ろうと考えている人**向けの内容になっております。

# 作ったもの

@[tweet](https://twitter.com/Fujiyama_Yuta/status/1589530686826106880)

# ソース

https://github.com/FujiyamaYuta/e_paper_weather_display

# 使っているデバイス
- Raspberry Pi 3 Model B
- Micro SDカード（32GB）
- 電子ペーパー（[7.5 inch e-Paper HAT](https://www.amazon.co.jp/dp/B08FZ4ZK4L)）

![](https://storage.googleapis.com/zenn-user-upload/914300d746d7-20221107.jpg)



# 使っている技術
- 開発言語：Python
- OS：Raspberry Pi OS（32-bit）

# 使っているAPI

ベースとなる天気情報は [OpenWeather](https://openweathermap.org) から取得して、降水確率や明日・明後日の天気は[天気予報 API（livedoor 天気互換）](https://weather.tsukumijima.net/)から取得して表示します。

- OpenWeather：[WeatherAPI](https://openweathermap.org/current)
	- https://openweathermap.org/current
- [天気予報 API（livedoor 天気互換）](https://weather.tsukumijima.net/)
	- https://weather.tsukumijima.net/

# 仕様

- 電子ペーパーに天気の情報が表示される
	- 現在の気温
	- 最高気温
	- 最低気温
	- 天気予報
	- 降水確率
	- 明日・明後日の天気予報
	- 更新された時間
- 30分の1回最新の情報を取得して表示する

# 実装

## ① RaspberryPi初期化

### Raspberry Pi Imagerインストール

Raspberry Piの公式サイトから、Raspberry Piで動かすOSをインストールするパッケージをインストールします。
https://www.raspberrypi.com/software/

![](https://storage.googleapis.com/zenn-user-upload/e823146697cd-20221107.png)


### Raspberry Pi ImagerでRaspberry Pi OSをインストール

- インストーラーのインストールが終わったら、OSをインストールします。OSは「Raspberry Pi OS（32-bit）」を選択します。（Raspberry Pi 3 Model Bの場合）

-  用意した「Micro SDカード」をセットすると「ストレージ」にMicro SDが選択できるようになるので、選択します。

![](https://storage.googleapis.com/zenn-user-upload/fc4da6530599-20221107.png)

- 右下のセッティングのアイコンを押して詳細設定を押します。
- 詳細設定の部分も下記のように設定します。
（ここの設定をミスると、Wifiに接続できなかったり、sshできなかったりするので指差し確認）
- 設定が終わったら「書き込む」を押す

![](https://storage.googleapis.com/zenn-user-upload/014b082261bb-20221107.png)
![](https://storage.googleapis.com/zenn-user-upload/fc8b67a17d2a-20221107.png)
![](https://storage.googleapis.com/zenn-user-upload/290d2cd5aaad-20221107.png)

### SSH接続するためのファイルを用意
- **sshするためにOSをインストールをしたディレクトリに下記のファイルを2つ追加する**
	- **`boot/ssh`**（空でOK）
	- **`boot/wpa_supplicant.conf`**
		- Wifi接続のIdとPasswordを記載
```wpa_supplicant.conf:wpa_supplicant.conf
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
country=JP
update_config=1

network={
    ssid="{ssid}"
    psk="{pwd}"
}
```
- OSのインストールが終わったら、Micro SDカードをRaspberry Piに挿入
- うまく設定ができていれば、これで動くはず👍

### 接続確認

- pingで接続できていることを確認

```bash
$ ping raspberrypi.local
PING raspberrypi.local (192.0.2.255): 56 data bytes
64 bytes from 192.0.2.255: icmp_seq=0 ttl=64 time=9.532 ms
64 bytes from 192.0.2.255: icmp_seq=1 ttl=64 time=4.341 ms
64 bytes from 192.0.2.255: icmp_seq=2 ttl=64 time=3.962 ms
64 bytes from 192.0.2.255: icmp_seq=3 ttl=64 time=8.963 ms
```

### Raspberry Pi のIPアドレスも確認

- ラズパイのIPアドレスも確認

```bash
$ sudo arp-scan -l
Interface: en0, type: EN10MB, MAC: 90:9c:4a:b7:40:e0, IPv4: 
Starting arp-scan 1.9.7 with 256 hosts (https://github.com/royhills/arp-scan)
192.0.2.255	b8:27:eb:2c:57:27	Raspberry Pi Foundation
```

- `arp-scan` コマンドが見つからない場合はインストールしてください。

```
$ brew install arp-scan
```

### SSHしてみる
- pingが確認できていればsshも可能

```bash
$ ssh pi@raspberrypi.local
pi@raspberrypi.local's password: {Raspberry Pi Imagerで設定したパスワード}

pi@raspberrypi:~ $ #ssh成功
```

### SFTPしてみる
- CLIが得意な人は必要ないとは思いますが、自分はあまり得意ではないので[ツール](https://panic.com/jp/transmit/)を使ってファイル転送をします。

![](https://storage.googleapis.com/zenn-user-upload/d8013cf4ef8e-20221107.png)

- 接続確認ができればOK（`home/pi`）

### Raspberry PiのI2C,SPIを有効化

- 電子ペーパーとラズベリーパイはGPIOヘッダーに接続されており、I2CとSPIという通信方法が利用されているので、それを許可する必要があります。

```bash
pi@raspberrypi:~ $sudo raspi-config
```
- 「3 Interface Options」を選択

![](https://storage.googleapis.com/zenn-user-upload/c0df75e6bf4e-20221108.png)

- 「I4 I2C」 と 「I5 SPI」を選択

![](https://storage.googleapis.com/zenn-user-upload/549c792cab24-20221108.png)


## ② 電子ペーパーの下準備

RaspberryPiの設定が終わったので次は電子ペーパーの設定です。情報があまりなかったので苦戦しましたが、下記のサイトのサンプルを動かすことができたので、そのソースをベースに開発しました。

- 電子ペーパーとRaspberryPiのGPIOヘッダーに接続でOK
- 下記のサイトの[サンプル](https://www.waveshare.com/wiki/Main_Page)を動かしながら、プログラムを書きました。
	- https://www.waveshare.com/wiki/Main_Page

## ③ OpenWeatherAPI keyを発行

現在の天候や予測履歴を含む、各種気象データの無料APIを提供しているサービスです。お天気情報のベースのデータはこちらから取得します。APIを呼び出すために、API Keyが必要になるので作成します。

- アカウント作成
- [My API Keys](https://home.openweathermap.org/api_keys)へ
- アカウント作成時にDefaultで一つ作られているのでそれをコピーします。

![](https://storage.googleapis.com/zenn-user-upload/4630392cddc9-20221108.png)

## ④ 天気予報 API（livedoor 天気互換）の地点コードを探す

降水確率については、OpenWeatherの無料のAPIでは取得できないので、[天気予報 API（livedoor 天気互換）](https://weather.tsukumijima.net)から取得することにします。

- [天気予報 API（livedoor 天気互換）](https://weather.tsukumijima.net)の[全国の地点定義表](https://weather.tsukumijima.net/primary_area.xml)から地域別に定義された ID 番号を取得

## ⑤ 開発

https://github.com/FujiyamaYuta/e_paper_weather_display

- GithubからcloneしてRaspberryPiの `home/pi`に配置
- `src/config@.py` を `src/config.py`にリネーム
- ④・⑤で取得した情報を`src/config.py`に記載
- `LATITUDE` と `LONGITUDE`は緯度経度を記載
	- 緯度経度はGoogleMapで赤いピンの上で右クリックをすれば調べれます

```python:config.py
API_KEY = '************************' # ③で取得したAPI KEYを記載
LATITUDE = '************************' # 緯度
LONGITUDE = '************************' #経度
TSUKURUMIJIMA_TENKI_CODE = '************************' #④で取得したID 番号を記載
```

- メインのソースは下記のようになっております。

```python:print_weather.py
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
```

## ⑥ 動かしてみる

実際にプログラムを実行してみます。

```
pi@raspberrypi:~ $ python home/pi/e_paper_weather_display-master/src/print_weather.py
```

上のプログラムを実行すると、APIから天気情報を取得して、電子ペーパーに情報を描画できます。
動作的には↓のような感じになります。

[![Image from Gyazo](https://i.gyazo.com/0d093e3cc6b321fb97c3706a5f2ccc98.gif)](https://gyazo.com/0d093e3cc6b321fb97c3706a5f2ccc98)

## ⑦ crontabで定期実行させる

`src/print_weather.py`では1回描画すると終了するプログラムとなっております。最新のデータを描画する場合は再度プログラムを実行する必要があります。
RaspberryPi OSでもcrontabが使えるので、これを設定します。

```
pi@raspberrypi:~ $ crontab -e
*/30 * * * * python home/pi/e_paper_weather_display-master/src/print_weather.py
```
これで30分毎に `print_weather.py` が実行されるようになりました🙌

# 完成

完成しました🙌

![](https://storage.googleapis.com/zenn-user-upload/0a6c4a00e437-20221108.jpg)


# まとめ

はじめてのラズベリーパイでしたが、なんとか動くものを作れました🙌 Raspberry Pi OSをインストールするときに、初期化がうまくいかずなぜかWIFIに繋がらない等があり時間がかかってしまいましたが、なんとか動かすことができました🙌

久しぶりに趣味開発をしてとても楽しい時間を過ごすことができました。RaspberryPiデビューができたので他にも何か作ってみようと思います。

# 参考にしたサイト

下記のサイトを参考に作りました。感謝を申し上げます🙇‍♂️

- [【初心者向け完全版】ラズパイの初期設定【win/mac対応】](https://sukiburo.jp/setup-raspberry-pi/)
- [ラズベリーパイと電子ペーパーで天気予報ステーションを作る](https://kotamorishita.com/rpi-epaper-weather-station/)
- [WAVASHAREの電子ペーパーとラズパイでサンプルを動かす](https://blog.ryou103.com/post/e-paper-raspi/)
- [Raspberry Piで電子ペーパーモジュールを動作させる](https://qiita.com/_shin_/items/0e9e7804531368ff0e90)


# ベースとなっているリポジトリ
今回作ったものは下記のリポジトリを参考にさせていただきました🙇‍♂️
- https://github.com/AbnormalDistributions/e_paper_weather_display
