#!/usr/bin/python
# _*_coding: utf-8 _*_
# Coder:Whitejoce

import sys
import time
import json
import requests
import bs4
import re
import urllib as urlparse
import http.client

# 输出模式，0为shell输出，1为窗口输出(窗口仅输出天气信息)
output = 0


def get_CityName():
    try:
        res = requests.post(url='http://ip-api.com/json/?lang=zh-CN', data={'ip': 'myip'}, timeout=10)
        result = res.json()['city']
    except:
        print(" [!]正在进行网络自检并重试")
        try:
            res = requests.post(url='http://ip-api.com/json/?lang=zh-CN', data={'ip': 'myip'}, timeout=15)
            result = res.json()['city']
        except:
            print(" [!]无法从相关网站获得请求(请求总时长：25s)，退出脚本")
            sys.exit(1)
    print(res.json())
    City = re.findall('(.*?)市', result)
    CityName = "".join(City)
    # CityName = CityName[-2:]
    if len(CityName) == 0:
        print(' [!] 未自动匹配到你所在地的地区信息:' + result)
    return CityName


def get_city_code(city):
    try:
        parameter = urlparse.parse.urlencode({'cityname': city})
        conn = http.client.HTTPConnection('toy1.weather.com.cn', 80, timeout=5)
        conn.request('GET', '/search?' + parameter)
        r = conn.getresponse()
        data = r.read().decode()[1:-1]
        json_data = json.loads(data)
        code = json_data[0]['ref'].split('~')[0]
        return code
    except:
        print(' [!] 错误，未能找到该地区信息')
        print(" [#] 退出脚本")
        sys.exit()


def get_weaPage(url, headers):
    res = requests.get(url, headers=headers)
    ##print(res.text)
    s = res.content
    s.decode('ISO-8859-1')
    bs = bs4.BeautifulSoup(s, "html.parser")
    html = bs.prettify()
    return html


def CheckInput(InputString):
    if any(char.isdigit() for char in InputString):
        return True
    match = re.search('[a-zA-Z]+$', InputString)
    if match:
        return True
    return False


def GetItem(name, list):
    name = re.findall(r'"' + list + '":"(.*?)"', name)
    name = "".join(name)
    return name


def get_weather(City_code):
    headers1 = {
        'Referer': "http://www.weather.com.cn",
        'Cookie': '',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0'
    }

    # timestamp的长度为13
    # timestamp = ''.join(str(random.choice(range(10))) for i in range(13))
    t = time.time()
    timestamp = str(int(round(t * 1000)))
    port = "http://d1.weather.com.cn/weather_index/" + City_code + ".html?_=" + timestamp
    html = get_weaPage(port, headers1)
    # print(html)
    wea_list_all = html.split("var")
    # print(wea_list_all)
    temp_port = "http://d1.weather.com.cn/dingzhi/" + City_code + ".html?_=" + timestamp
    temp_html = get_weaPage(temp_port, headers1)
    # print(temp_html)

    # cityDZ
    # -----------------------------------------------------
    html1 = wea_list_all[1]
    wea_list1 = html1.split(",")
    temp_list = temp_html.split(",")

    # print(temp_list)
    # 城市英文
    city_en = wea_list1[1]
    city_en = GetItem(city_en, "cityname")
    # 温度区间
    maxtemp = temp_list[3]
    maxtemp = GetItem(maxtemp, "temp")

    mintemp = temp_list[4]
    mintemp = GetItem(mintemp, "tempn")
    # 实时天气
    wea_now = wea_list1[4]
    wea_now = GetItem(wea_now, "weather")

    # alarmDZ
    # -----------------------------------------------------
    wea_list2 = wea_list_all[2]
    wea_alarm_all = re.findall(r'alarmDZ ={"w":[(.*?)]};', wea_list2)
    warning = 0
    EmptyList = ['']
    if wea_alarm_all == EmptyList:
        pass
    else:
        warning = 1

    # dataSK
    # -----------------------------------------------------
    html3 = wea_list_all[3]
    wea_list3 = html3.split(",")
    # 城市
    cityname = wea_list3[1]
    cityname = GetItem(cityname, "cityname")
    # 当前温度
    temp_now = wea_list3[3]
    temp_now = GetItem(temp_now, "temp")
    # 湿度
    wet = wea_list3[9]
    wet = GetItem(wet, "SD")
    # 时间
    update = wea_list3[13]
    update = GetItem(update, "time")
    # 空气质量
    aqi = wea_list3[16]
    aqi = GetItem(aqi, "aqi")
    # PM2.5
    aqi_pm25 = wea_list3[17]
    aqi_pm25 = GetItem(aqi_pm25, "aqi_pm25")
    # 日期
    date = wea_list3[22]
    date = GetItem(date, "date")
    # -----------------------------------------------------

    # dataZS
    wea_list4 = wea_list_all[4]
    # -----------------------------------------------------
    ##print(wea_list4)
    # ataZS=re.findall(r',"(.*?)":',wea_list4)
    ##print(dataZS)
    # -----------------------------------------------------
    umbrella = GetItem(wea_list4, "ys_des_s")

    # 和风天气
    headers2 = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0'
    }
    qwea_url = "https://www.qweather.com/weather/" + city_en + "-" + City_code + ".html"
    qwea_html = get_weaPage(qwea_url, headers2)
    # print(qwea_html)
    wea_comment = re.findall(r'<div class="current-abstract">(.*?)</div>', qwea_html, flags=16)
    wea_comment = "".join(wea_comment)
    aqi_level = re.findall(r'<p class="city-air-chart__txt text-center">(.*?)</p>', qwea_html, flags=16)
    aqi_level = aqi_level[0].replace("\n", "")
    aqi_level = aqi_level.replace(" ", "")
    wea_comment = wea_comment.strip('\n')
    wea_comment = wea_comment.replace(" ", "").replace("\n", "")

    # -----------------------------------------------------
    weather_text = ''' {0}

 ===================================
 定位城市:  {1}
 实时天气:  {2}
 实时温度:  {3}℃
 温度区间:  {4} - {5}
 空气湿度:  {6}
 空气质量:  {7}({8}),PM2.5: {9}
 雨具携带:  {10}
 [更新时间: {11} {12}]
 ==================================='''.format \
        (wea_comment, cityname, wea_now, temp_now, maxtemp, \
         mintemp, wet, aqi, aqi_level, aqi_pm25, umbrella, date, update)
    # -----------------------------------------------------
    # print("\n " + wea_comment)

    # print(" ===================================")
    # print(" 定位城市:  "+cityname)
    # print(" 实时天气:  "+wea_now)
    # print(" 实时温度:  "+temp_now+"℃")
    # print(" 温度区间:  "+maxtemp+"℃ - "+mintemp+"℃")
    # print(" 空气湿度:  "+wet)
    # 0~50优，51~100良，101~150轻度污染，151~200中度污染，201~300重度污染，>300严重污染
    # print(" 空气质量:  "+aqi+"("+aqi_level+"),PM2.5: "+aqi_pm25)
    # print(" 雨具携带:  "+umbrella)
    # print(" [更新时间: "+date+" "+update +"]")
    # print(" ===================================")
    # -----------------------------------------------------

    # 处理天气预警
    if warning == 1:
        wea_alarm_all = "".join(wea_alarm_all)
        wea_alarm = re.findall(r'"w9":"(.*?)"', wea_alarm_all)
        wea_counter = len(wea_alarm)
        if wea_counter == 1:
            weather_text = weather_text + "\n [!]气象部门发布预警,请注意:"
            # print(" [!]气象部门发布预警,请注意:")
        else:
            weather_text = weather_text + "\n [!]气象部门发布" + str(wea_counter) + "则预警,请注意:"
            # print(" [!]气象部门发布"+ str(wea_counter) +"则预警,请注意:")
        # wea_alarm = "".join(wea_alarm)
        if wea_alarm != "":
            i = 1
            for alarm in wea_alarm:
                alarm = alarm.replace("\\", "")
                alarm = alarm.replace("：", ":\n ", 1)
                if wea_counter == 1:
                    weather_text = weather_text + " \n " + alarm
                    # print(" "+alarm)
                else:
                    weather_text = weather_text + " \n [" + str(i) + "]" + alarm
                    # print(" ["+ str(i) +"]"+alarm)
                    i = i + 1
        else:
            print(" [!]无法获取气象预警详情")
            option = input(" [?]显示完整数据结构?[y/n]")
            if option == "y" or option == "Y":
                # wea_alarm = wea_alarm.replace("{","")
                # wea_alarm = wea_alarm.replace("}","")
                weather_text = weather_text + " \n " + wea_alarm_all
    return weather_text


if __name__ == '__main__':
    try:
        address = get_CityName()
        if len(address) == 0:
            address = input(" [?] 请手动输入所在地（例：广州）[输入为空即退出]：")
            if address == "":
                print(" [#] 退出脚本")
                sys.exit(1)
            else:
                if CheckInput(address) == 1:
                    print(" [!]检测非地名字符，退出脚本")
                    sys.exit(1)
                else:
                    print(" [+] 使用手动输入定位位置：" + address)
        else:
            print(" [+] 自动定位位置：" + address)
        code = get_city_code(address)
        try:
            weather_text = get_weather(code)
            if output == 0:
                print("\n" + weather_text)
            elif output == 1:
                from tkinter import *

                windows = Tk()
                windows.title("GetWeather")
                text1 = Text(windows)
                text1.insert(INSERT, weather_text)
                text1.pack()
                windows.mainloop()
        except Exception as Error:
            print(' [!] 未能找到该地区的天气信息')
            print(" [#] 退出脚本")
            # raise Error
            sys.exit()
    except Exception as Error:
        raise Error