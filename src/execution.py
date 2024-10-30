import datetime

import pandas as pd
from script import (
    Amedas10minDataAnalyzer,
    AmedasDataAcquisition,
    AmedasHourlyDataAnalyzer,
    AmedasObservstionStations,
)
from util import generate_path


################################################################################################
# 最初の観測地点情報の取得
def get_information_of_stations():
    amedas_stations_info = AmedasObservstionStations()
    amedas_stations_info.get_area_info()
    amedas_stations_info.get_station_info()
    amedas_stations_info.arange_data()
    amedas_stations_info.acquire_observation_stations_dataframe()


# 連続した期間について、データをcsvファイルとして取得する関数
def get_10min_data(start_date, end_date, stations):
    dates = pd.date_range(start_date, end_date, freq="D")
    amedas_10min_data = AmedasDataAcquisition(stations, dates=dates)
    amedas_10min_data.make_10min_data_csv()


def get_hourly_data(start_date, end_date, stations):
    dates = pd.date_range(start_date, end_date, freq="D")
    amedas_hourly_data = AmedasDataAcquisition(stations, dates=dates)
    amedas_hourly_data.make_hourly_data_csv()


def get_daily_data(start_date, end_date, stations):
    months = pd.date_range(start_date, end_date, freq="MS")
    amedas_daily_data = AmedasDataAcquisition(stations, months=months)
    amedas_daily_data.make_daily_data_csv()


def extract_station_name_from_prec_no(prec_no) -> list:
    dir_name = generate_path("/data")
    csv_file = "amedas_observation_points.csv"
    stations_info = pd.read_csv(
        f"{dir_name}/{csv_file}", dtype=str
    )  # 観測地点情報の一覧
    matched_df = stations_info[stations_info["prec_no"] == str(prec_no)]
    stations = list(matched_df["enName"])
    return stations


##################################################################################################


# 設定項目の説明
"""
starttime, endtime         (datetime): 描画したい期間の始めと終わりの時刻 
lon_left, lon_right        (float)   : 描画したい経度の左端と右端 
lat_lower, lat_upper       (float)   : 描画したい緯度の下端と上端 
lat_interval, lon_interval (float)   : 緯度経度の目盛りの間隔
prec_no_list               (list)    : 描画したい観測地点の都道府県番号(下のPREC_NUMBERを参照)
zoom_level                 (int)     : 標高地図にプロットする際のズームレベル(国土地理院マップ参照)
　　　　　　　　　　　　　　　　      　   0~18の整数で、大きいほど解像度が高い(目安8~11)
deg_min_format             (bool)    : 図の緯度経度目盛りについて、
                                       度分表記する際はTrueに、度表記にする際はFalseに
elevation                  (bool)    : 標高地図を用いる際はTrueに、白地図を用いる際はFalseに
contour                    (bool)    : 標高を等高線でプロットする際はTrueに、陰影でプロットする際はFalseに
height_max, height_min     (int)     : プロットする標高の最大値,最小値
height_interval            (int)     : 標高のプロット間隔
"""

PREC_NUMBER = {
    "宗谷地方": 11,
    "上川地方": 12,
    "留萌地方": 13,
    "石狩地方": 14,
    "空知地方": 15,
    "後志地方": 16,
    "網走・北見・紋別地方": 17,
    "根室地方": 18,
    "釧路地方": 19,
    "十勝地方": 20,
    "胆振地方": 21,
    "日高地方": 22,
    "渡島地方": 23,
    "檜山地方": 24,
    "青森県": 31,
    "秋田県": 32,
    "岩手県": 33,
    "宮城県": 34,
    "山形県": 35,
    "福島県": 36,
    "茨城県": 40,
    "栃木県": 41,
    "群馬県": 42,
    "埼玉県": 43,
    "東京都": 44,
    "千葉県": 45,
    "神奈川県": 46,
    "長野県": 48,
    "山梨県": 49,
    "静岡県": 50,
    "愛知県": 51,
    "岐阜県": 52,
    "三重県": 53,
    "新潟県": 54,
    "富山県": 55,
    "石川県": 56,
    "福井県": 57,
    "滋賀県": 60,
    "京都府": 61,
    "大阪府": 62,
    "兵庫県": 63,
    "奈良県": 64,
    "和歌山県": 65,
    "岡山県": 66,
    "広島県": 67,
    "島根県": 68,
    "鳥取県": 69,
    "徳島県": 71,
    "香川県": 72,
    "愛媛県": 73,
    "高知県": 74,
    "山口県": 81,
    "福岡県": 82,
    "大分県": 83,
    "長崎県": 84,
    "佐賀県": 85,
    "熊本県": 86,
    "宮崎県": 87,
    "鹿児島県": 88,
    "沖縄県": 91,
    "南極": 99,
}

# 以下を設定
starttime = datetime.datetime(2023, 7, 19, 0, 0)
endtime = datetime.datetime(2023, 7, 20, 0, 0)
lon_left, lon_right = 129.5, 131
lat_lower, lat_upper = 33, 34
lat_interval = 0.5
lon_interval = 0.5
prec_no_list = [82, 83, 85]

zoom_level = 8
deg_min_format = False
elevation = True
contour = False
height_max = 2050
height_min = 150
height_interval = 100


##########################################################################################################
stations = []
for prec_no in prec_no_list:
    each_prec_stations = extract_station_name_from_prec_no(prec_no)
    stations += each_prec_stations


def make_10min_mean_wind_figure(starttime, endtime, stations):
    """
    Args:
      starttime(datetime) : 描画する期間の開始時刻(10分刻み)
      endtime(datetime) : 描画する期間の終了時刻(10分刻み)
      stations(list) : プロットする観測地点の英語名称(../data/amedas_observation_points.txt を参照)
    """
    start_date = starttime.date()
    end_date = endtime.date()
    get_10min_data(start_date, end_date, stations)
    analysis = Amedas10minDataAnalyzer()
    analysis.make_mean_wind_figure(
        starttime,
        endtime,
        lon_left,
        lon_right,
        lat_lower,
        lat_upper,
        zoom_level,
        deg_min_format=deg_min_format,
        contour=contour,
        lon_interval=lon_interval,
        lat_interval=lat_interval,
        height_max=height_max,
        height_min=height_min,
        height_interval=height_interval,
    )


def make_10min_temperature_figure(starttime, endtime, stations):
    """
    Args:
      starttime(datetime) : 描画する期間の開始時刻(10分刻み)
      endtime(datetime) : 描画する期間の終了時刻(10分刻み)
      stations(list) : プロットする観測地点の英語名称(../data/amedas_observation_points.txt を参照)
    """
    start_date = starttime.date()
    end_date = endtime.date()
    get_10min_data(start_date, end_date, stations)
    analysis = Amedas10minDataAnalyzer()
    analysis.make_temperature_figure(
        starttime,
        endtime,
        lon_left,
        lon_right,
        lat_lower,
        lat_upper,
        zoom_level,
        elevation=elevation,
        contour=contour,
        deg_min_format=deg_min_format,
        lon_interval=lon_interval,
        lat_interval=lat_interval,
        height_max=height_max,
        height_min=height_min,
        height_interval=height_interval,
    )


def make_hourly_mean_wind_figure(starttime, endtime, stations):
    """
    Args:
      starttime(datetime) : 描画する期間の開始時刻(1時間刻み)
      endtime(datetime) : 描画する期間の終了時刻(1時間刻み)
      stations(list) : プロットする観測地点の英語名称(../data/amedas_observation_points.txt を参照)
    """
    start_date = starttime.date()
    end_date = endtime.date()
    get_hourly_data(start_date, end_date, stations)
    analysis = AmedasHourlyDataAnalyzer()
    analysis.make_mean_wind_figure(
        starttime,
        endtime,
        lon_left,
        lon_right,
        lat_lower,
        lat_upper,
        zoom_level,
        deg_min_format=deg_min_format,
        contour=contour,
        lon_interval=lon_interval,
        lat_interval=lat_interval,
        height_max=height_max,
        height_min=height_min,
        height_interval=height_interval,
    )


def make_hourly_temprature_figure(starttime, endtime, stations):
    """
    Args:
      starttime(datetime) : 描画する期間の開始時刻(1時間刻み)
      endtime(datetime) : 描画する期間の終了時刻(1時間刻み)
      stations(list) : プロットする観測地点の英語名称(../data/amedas_observation_points.txt を参照)
    """
    start_date = starttime.date()
    end_date = endtime.date()
    get_hourly_data(start_date, end_date, stations)
    analysis = AmedasHourlyDataAnalyzer()
    analysis.make_temperature_figure(
        starttime,
        endtime,
        lon_left,
        lon_right,
        lat_lower,
        lat_upper,
        zoom_level,
        deg_min_format=deg_min_format,
        elevation=elevation,
        contour=contour,
        lon_interval=lon_interval,
        lat_interval=lat_interval,
        height_max=height_max,
        height_min=height_min,
        height_interval=height_interval,
    )


# 降水量、複数日の平均気温・平均風向風速もok
###########################################################################################################

# 最初に一度だけ実行して、観測地点情報を取得する
# get_information_of_stations()

# 以後、以下で実行
# make_10min_mean_wind_figure(starttime,endtime,stations)
# make_10min_temperature_figure(starttime,endtime,stations)
# make_hourly_mean_wind_figure(starttime,endtime,stations)
# make_hourly_temprature_figure(starttime,endtime,stations)

"""
def change_to_date(each_date):
  year = int(each_date[0:4])
  month = int(each_date[5:7])
  day = int(each_date[8:10])
  return datetime.date(year, month, day)


hig_group = []
with open("/work6/kobatake_yusuke/analysis/research/data/DATE_txt/thr_16mm_5mm_grid7×7_1600-1670_950-1020/none_group.txt") as f:
   while True:
      each_line = f.readline()
      each_date = each_line[0:10]
      if each_line == '':
            break
      hig_group.append(change_to_date(each_date))

dates = hig_group
amedas_hourly_data = AmedasDataAcquisition(stations,dates=dates)
amedas_hourly_data.make_hourly_data_csv()
analysis = AmedasHourlyDataAnalyzer()
# analysis.make_composite_wind_figure("high-group",dates,lon_left,lon_right,lat_lower,lat_upper,zoom_level,deg_min_format,
                                      height_max=height_max,height_min=height_min,height_interval=height_interval)
analysis.make_composite_temperature_figure("none-group",dates,lon_left,lon_right,lat_lower,lat_upper,zoom_level,deg_min_format,elevation,
                                            height_max=height_max,height_min=height_min,height_interval=height_interval)

"""
