import datetime
import urllib
import requests
import os
import math
import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import cartopy.crs as ccrs
from bs4 import BeautifulSoup

from util import generate_path
from url import acquire_query
from gif import convert_jpg_to_gif
from map import make_blank_map
from constant import WIND_DIRECTION
from elevation import make_elevation_map



# 観測地点情報の取得処理
class AmedasObservstionStations:
   def __init__(self):
      url = 'https://www.data.jma.go.jp/obd/stats/etrn/select/prefecture00.php?prec_no=&block_no=&year=&month=&day=&view='
      html = urllib.request.urlopen(url)
      self.soup = BeautifulSoup(html, 'html.parser')

   def acquire_prec_no(self,url):
      query_dictionary = acquire_query(url)
      self.prec_no = query_dictionary["prec_no"][0]
      return self.prec_no

   def acquire_block_no(self,url):
      query_dictionay = acquire_query(url)
      try:
         self.block_no = query_dictionay["block_no"][0]
         return self.block_no
      except KeyError as err:
         # print("Block_no is not acquired.")
         return np.nan

   def get_area_info(self):
      elements = self.soup.find_all('area')
      self.area_list = [element['alt'] for element in elements]
      self.area_link_list = [element['href'] for element in elements]

   def get_station_info(self):
      out = pd.DataFrame(columns=['station','url','area'])
      for area, area_link in zip(self.area_list, self.area_link_list):
         url = 'https://www.data.jma.go.jp/obd/stats/etrn/select/'+ area_link
         html = urllib.request.urlopen(url)
         soup = BeautifulSoup(html, 'html.parser')
         elements = soup.find_all('area')
         station_list = [element['alt'] for element in elements]
         station_link_list = [element['href'].strip('../') for element in elements]
         prec_no_list = map(self.acquire_prec_no, station_link_list)
         block_no_list = map(self.acquire_block_no, station_link_list)
         df1 = pd.DataFrame(station_list,columns=['station'])
         df2 = pd.DataFrame(prec_no_list,columns=['prec_no'])
         df3 = pd.DataFrame(block_no_list,columns=['block_no'])
         df = pd.concat([df1, df2, df3],axis=1).assign(area=area)
         out = pd.concat([out,df])
         # print(area)
      self.out = out

   def arange_data(self):
      out = self.out[~self.out.duplicated()]
      out = out.loc[:,['station','prec_no','block_no']]
      out = out.dropna(how="any")
      out.to_csv(generate_path("/data/prec_block_no.csv"),index=None, encoding='UTF-8')
      self.df_no = out

   def acquire_observation_stations_dataframe(self):
      """amedasの観測地点の情報の一覧をdataframeとして取得
      """
      #観測地点情報の取得
      url = "https://www.jma.go.jp/bosai/amedas/const/amedastable.json"
      with requests.get(url) as response:
         json = response.json()
         df = pd.DataFrame(json).transpose()

      #緯度経度を十進数に変換
      df["lat"] = df["lat"].str[0] + df["lat"].str[1]/60
      df["lon"] = df["lon"].str[0] + df["lon"].str[1]/60

      #dfに2列追加
      df["prec_no"] = np.nan
      df["block_no"] = np.nan

      #prec_noとblock_noの情報を取得して結合
      df_no = self.df_no
      df_no = df_no.reset_index(drop=True)
      for index_number, station_name in enumerate(df_no["station"]):
         matched_row = df[df["kjName"] == station_name]
         if matched_row.empty:
            pass
         else:
            df.loc[matched_row.index.values[0],"prec_no"] = df_no.loc[index_number,"prec_no"]
            df.loc[matched_row.index.values[0],"block_no"] = df_no.loc[index_number,"block_no"]
      df = df.dropna(how="any")

      #dataframeの情報を表示
      pd.set_option("display.max_rows", 2000)
      pd.set_option("display.max_columns", 100)
      pd.set_option("display.width", 1000)
      print(df)

      #[elems]列を分割して末尾に列を追加
      colnames = ["temperature", "precipitation", "windDirection",
                  "wind", "sunshine", "snowDepth", "humidity", "pressure"]
      elems_split = np.array(df["elems"].apply(list).to_list()).astype("int32")
      for i in range(len(colnames)):
         df[colnames[i]] = elems_split[:, i]

      #dataframeをcsvとして保存
      df.to_csv(generate_path("/data/amedas_observation_points.csv"))


# スクレイピング
class AmedasDataAcquisition:
   def __init__(self,stations,dates=[],months=[]):
      """
      Args:
      dates(list): 取得したい日付(date)のリスト
      stations(list): 取得したい観測地点名のリスト
      months(list): 取得したい月の初日(date)のリスト
      """
      self.stations = stations
      self.dates = dates
      self.months = months
      self.stations_data = pd.read_csv(generate_path("/data/amedas_observation_points.csv"), dtype=str)

   def acquire_block_no(self,url):
      query_dictionay = acquire_query(url)
      self.block_no = query_dictionay["block_no"][0]
      return self.block_no

   def extract_10min_data(self,url):
      # webページ内の表をdataframeとして取得
      tables = pd.io.html.read_html(url)
      df = tables[0].iloc[:,1:] 

      # dataframeから必要な要素を抽出
      block_no = self.acquire_block_no(url)
      if len(block_no) == 5:
         df = df.loc[:,[True,True,True,True,True,True,True,True,True,True]] # --- 必要な行と列を抽出
         df = df.reset_index(drop=True)
      else:
         df = df.loc[:,[True,True,True,True,True,True,True,True]] # --- 必要な行と列を抽出
         df.insert(0,"現地",np.nan)
         df.insert(1,"海面",np.nan)
         df = df.reset_index(drop=True)

      # 観測地点名の取得
      stations_data = self.stations_data
      matched_row = stations_data[stations_data["block_no"] == f"{block_no}"]
      matched_index = matched_row.index.values[0]
      station_name = stations_data.loc[matched_index,"enName"]

      # 列名の指定
      column_name = ["station_pressure", "sea_level_pressure", "precipitation", "temperature", "rh",
                     "mean_ws", "mean_wd", "instantaneous_ws", "instantaneous_wd", "sunshine_hours"]
      df.columns = [f"{i}_{station_name}" for i in column_name]

      # 欠測値の処理 
      df = df.replace('///', '-999.9') # --- '///' を欠測値として処理
      df = df.replace('×', '-999.9') # --- '×' を欠測値として処理
      df = df.replace('\s\)', '', regex = True) # --- ')' が含まれる値を正常値として処理
      df = df.replace('.*\s\]', '-999.9', regex = True) # --- ']' が含まれる値を欠測値として処理
      df = df.replace('#', '-999.9') # --- '#'が含まれる値を欠測値として処理
      df = df.replace('--', '-999.9') # --- '--'が含まれる値を欠測値として処理

      # 風向を北を0°として時計回りの表記に変更
      df = df.replace(WIND_DIRECTION)

      self.df_10min = df
      return self.df_10min 
   
   def extract_hourly_data(self,url):
      # webページ内の表をdataframeとして取得
      tables = pd.io.html.read_html(url)
      df = tables[0].iloc[:,1:] 

      # dataframeから必要な要素を抽出
      block_no = self.acquire_block_no(url)
      if len(block_no) == 5:
         df = df.loc[:,[True,True,True,True,True,True,True,True,True,True,True,True,True,False,True,True]] # --- 必要な行と列を抽出
         df = df.reset_index(drop=True)
      else:
         df = df.loc[:,[True,True,True,True,True,True,True,True,True,True]] # --- 必要な行と列を抽出
         df.insert(0,"現地",np.nan)
         df.insert(1,"海面",np.nan)
         df.insert(10,"全天日射量",np.nan)
         df.insert(13,"雲量",np.nan)
         df.insert(14,"視程",np.nan)
         df = df.reset_index(drop=True)

      # 観測地点名の取得
      stations_data = self.stations_data
      matched_row = stations_data[stations_data["block_no"] == f"{block_no}"]
      matched_index = matched_row.index.values[0]
      station_name = stations_data.loc[matched_index,"enName"]

      # 列名の指定
      column_name = ["station_pressure", "sea_level_pressure", "precipitation", "temperature",
                     "dew_point", "water_vapor_pressure", "rh", "mean_ws", "mean_wd", "sunshine_hours",
                     "global_solar_radiation", "snow_fall", "snow_depth", "cloud_cover", "visibility"]
      df.columns = [f"{i}_{station_name}" for i in column_name]

      # 欠測値の処理 
      df = df.replace('///', '-999.9') # --- '///' を欠測値として処理
      df = df.replace('×', '-999.9') # --- '×' を欠測値として処理
      df = df.replace('\s\)', '', regex = True) # --- ')' が含まれる値を正常値として処理
      df = df.replace('.*\s\]', '-999.9', regex = True) # --- ']' が含まれる値を欠測値として処理
      df = df.replace('#', '-999.9') # --- '#'が含まれる値を欠測値として処理
      df = df.replace('--', '-999.9') # --- '--'が含まれる値を欠測値として処理

      # 風向を北を0°として時計回りの表記に変更
      df = df.replace(WIND_DIRECTION)

      self.df_hourly = df
      return self.df_hourly 

   def extract_daily_data(self,url):
      # webページ内の表をdataframeとして取得
      tables = pd.io.html.read_html(url)
      df = tables[0].iloc[:,1:] 

      # dataframeから必要な要素を抽出
      block_no = self.acquire_block_no(url)
      if len(block_no) == 5:
         df = df.loc[:,[True,True,True,True,True,True,True,True,True,True,True,True,True,True,True,True,True,True,False,False]] # --- 必要な行と列を抽出
         df.insert(15,"最多風向",np.nan)
         df = df.reset_index(drop=True)
      else:
         df = df.loc[:,[True,True,True,True,True,True,True,True,True,True,True,True,True,True,True,True,True]] # --- 必要な行と列を抽出
         df.insert(0,"現地平均",np.nan)
         df.insert(1,"海面平均",np.nan)
         df = df.reset_index(drop=True)

      # 観測地点名の取得
      stations_data = self.stations_data
      matched_row = stations_data[stations_data["block_no"] == f"{block_no}"]
      matched_index = matched_row.index.values[0]
      station_name = stations_data.loc[matched_index,"enName"]

      # 列名の指定
      column_name = ["mean_station_pressure", "mean_sea_level_pressure", "total_precipitation", "max_hourly_precipitation",
                     "max_10min_precipitation", "mean_temperature", "highest_temperature", "lowest_temperature", 
                     "mean_rh", "min_rh", "mean_ws", "max_ws", "max_wd", "max_instantaneous_ws", "max_instantanious_wd",
                     "most_frequent_wd", "sunshine_hours", "total_snow_fall", "max_snow_depth"]
      df.columns = [f"{i}_{station_name}" for i in column_name]

      # 欠測値の処理 
      df = df.replace('///', '-999.9') # --- '///' を欠測値として処理
      df = df.replace('×', '-999.9') # --- '×' を欠測値として処理
      df = df.replace('\s\)', '', regex = True) # --- ')' が含まれる値を正常値として処理
      df = df.replace('.*\s\]', '-999.9', regex = True) # --- ']' が含まれる値を欠測値として処理
      df = df.replace('#', '-999.9') # --- '#'が含まれる値を欠測値として処理
      df = df.replace('--', '-999.9') # --- '--'が含まれる値を欠測値として処理

      # 風向を北を0°として時計回りの表記に変更
      df = df.replace(WIND_DIRECTION)

      self.df_daily = df
      return self.df_daily 

   def make_10min_data_csv(self):
      dates = self.dates
      stations = self.stations
      stations_data = self.stations_data

      url_list = []
      # 各観測地点のprec_noとblock_noの取得
      for station in stations:
         matched_row = stations_data[stations_data["enName"] == f"{station}"]
         matched_index = matched_row.index.values[0]
         prec_no = stations_data.loc[matched_index,"prec_no"]
         block_no = stations_data.loc[matched_index,"block_no"]
         # url名を取得してリストに格納
         if len(block_no) == 5:
            url = f'http://www.data.jma.go.jp/obd/stats/etrn/view/10min_s1.php?prec_no={prec_no}&block_no={block_no}'
            url_list.append(url)
         else :
            url = f'http://www.data.jma.go.jp/obd/stats/etrn/view/10min_a1.php?prec_no={prec_no}&block_no={block_no}'
            url_list.append(url)

      first_loop = True
      for date in dates:
         year=str(date.year).zfill(4) 
         month=str(date.month).zfill(2) 
         day=str(date.day).zfill(2) 
         print(f'get data of {year}/{month}/{day}.')

         # リスト内のURLからデータを取得
         for count, url in enumerate(url_list):
            url = f"{url}&year={year}&month={month}&day={day}&view=p1"
            if count == 0:
               # もととなるdataframeを作成
               df = pd.DataFrame(np.arange(144).reshape(144, 1))
               df = df.drop(df.columns[[0]], axis=1)
               df = df.reset_index(drop=True)

               # 時刻列, 年/月/日/時/分 の各列を追加
               df['jst_datetime'] = pd.date_range(datetime.datetime(int(year),int(month),int(day), 0, 10, 0), periods=len(df), freq='10T')
               df['year'] = df['jst_datetime'].dt.year
               df['month'] = df['jst_datetime'].dt.month
               df['day'] = df['jst_datetime'].dt.day
               df['hour'] = df['jst_datetime'].dt.hour
               df['minute'] = df['jst_datetime'].dt.minute

               # データを取得して横方向に連結
               df = pd.concat([df, self.extract_10min_data(url)], axis=1)
            else:
               df = pd.concat([df, self.extract_10min_data(url)], axis=1)
      
         # csvファイルとして出力
         if first_loop:
            df.to_csv(
            generate_path(f"/data/10min_data/raw_amedas_data.csv"), header=True, index=False, na_rep="nan")
            first_loop = False
         else:
            df.to_csv(
            generate_path(f"/data/10min_data/raw_amedas_data.csv"), header=False, index=False, mode='a', na_rep="nan")
         
   def make_hourly_data_csv(self):
      dates = self.dates
      stations = self.stations
      stations_data = self.stations_data

      url_list = []
      # 各観測地点のprec_noとblock_noの取得
      for station in stations:
         matched_row = stations_data[stations_data["enName"] == f"{station}"]
         matched_index = matched_row.index.values[0]
         prec_no = stations_data.loc[matched_index,"prec_no"]
         block_no = stations_data.loc[matched_index,"block_no"]
         # url名を取得してリストに格納
         if len(block_no) == 5:
            url = f'https://www.data.jma.go.jp/stats/etrn/view/hourly_s1.php?prec_no={prec_no}&block_no={block_no}'
            url_list.append(url)
         else :
            url = f'https://www.data.jma.go.jp/stats/etrn/view/hourly_a1.php?prec_no={prec_no}&block_no={block_no}'
            url_list.append(url)

      first_loop = True
      for date in dates:
         year=str(date.year).zfill(4) 
         month=str(date.month).zfill(2) 
         day=str(date.day).zfill(2) 
         print(f'get data of {year}/{month}/{day}.')

         # リスト内のURLからデータを取得
         for count, url in enumerate(url_list):
            url = f"{url}&year={year}&month={month}&day={day}&view="
            if count == 0:
               # もととなるdataframeを作成
               df = pd.DataFrame(np.arange(24).reshape(24, 1))
               df = df.drop(df.columns[[0]], axis=1)
               df = df.reset_index(drop=True)

               # 時刻列, 年/月/日/時/分 の各列を追加
               df['jst_datetime'] = pd.date_range(datetime.datetime(int(year),int(month),int(day), 1, 0, 0), periods=len(df), freq='H')
               df['year'] = df['jst_datetime'].dt.year
               df['month'] = df['jst_datetime'].dt.month
               df['day'] = df['jst_datetime'].dt.day
               df['hour'] = df['jst_datetime'].dt.hour

               # データを取得して横方向に連結
               df = pd.concat([df, self.extract_hourly_data(url)], axis=1)
            else:
               df = pd.concat([df, self.extract_hourly_data(url)], axis=1)
      
         # csvファイルとして出力
         if first_loop:
            df.to_csv(
            generate_path(f"/data/hourly_data/raw_amedas_data.csv"), header=True, index=False, na_rep="nan")
            first_loop = False
         else:
            df.to_csv(
            generate_path(f"/data/hourly_data/raw_amedas_data.csv"), header=False, index=False, mode='a', na_rep="nan")

   def make_daily_data_csv(self):
      months = self.months
      stations = self.stations
      stations_data = self.stations_data

      url_list = []
      # 各観測地点のprec_noとblock_noの取得
      for station in stations:
         matched_row = stations_data[stations_data["enName"] == f"{station}"]
         matched_index = matched_row.index.values[0]
         prec_no = stations_data.loc[matched_index,"prec_no"]
         block_no = stations_data.loc[matched_index,"block_no"]
         # url名を取得してリストに格納
         if len(block_no) == 5:
            url = f'https://www.data.jma.go.jp/stats/etrn/view/daily_s1.php?prec_no={prec_no}&block_no={block_no}'
            url_list.append(url)
         else :
            url = f'https://www.data.jma.go.jp/stats/etrn/view/daily_a1.php?prec_no={prec_no}&block_no={block_no}'
            url_list.append(url)

      first_loop = True
      for date in months:
         year=str(date.year).zfill(4) 
         month=str(date.month).zfill(2) 
         print(f'get data of {year}/{month}.')

         # リスト内のURLからデータを取得
         for count, url in enumerate(url_list):
            url = f"{url}&year={year}&month={month}&day=&view="
            #各日のdataframeを取得
            df_each_day = self.extract_daily_data(url)
            number_of_days = len(df_each_day)

            if count == 0:
               # もととなるdataframeを作成
               df = pd.DataFrame(np.arange(number_of_days).reshape(number_of_days,1))
               df = df.drop(df.columns[[0]], axis=1)
               df = df.reset_index(drop=True)

               # 時刻列, 年/月/日/時/分 の各列を追加
               df['jst_datetime'] = pd.date_range(datetime.date(int(year),int(month),1), periods=number_of_days, freq='D')
               df['year'] = df['jst_datetime'].dt.year
               df['month'] = df['jst_datetime'].dt.month
               df['day'] = df['jst_datetime'].dt.day

               # データを取得して横方向に連結
               df = pd.concat([df, df_each_day], axis=1)
            else:
               df = pd.concat([df, df_each_day], axis=1)
      
         # csvファイルとして出力
         if first_loop:
            df.to_csv(
            generate_path(f"/data/daily_data/raw_amedas_data.csv"), header=True, index=False, na_rep="nan")
            first_loop = False
         else:
            df.to_csv(
            generate_path(f"/data/daily_data/raw_amedas_data.csv"), header=False, index=False, mode='a', na_rep="nan")


# 10分値の処理
class Amedas10minDataAnalyzer:
   def __init__(self):
      # 観測データをcsvファイルから取得
      dir_name = generate_path("/data/10min_data")
      csv_file = "raw_amedas_data.csv"
      self.df = pd.read_csv(f"{dir_name}/{csv_file}")
      columns = self.df.columns
      self.stations = columns[columns.str.contains("rh")].str[3:] #観測地点名を抽出

      # 各観測地点のlatとlonの取得
      dir_name = generate_path("/data")
      csv_file = "amedas_observation_points.csv"
      stations_info = pd.read_csv(f"{dir_name}/{csv_file}",dtype=str) #観測地点情報の一覧
      lon_dict, lat_dict = {}, {}
      for station in self.stations:
         matched_row = stations_info[stations_info["enName"] == f"{station}"]
         matched_index = matched_row.index.values[0]
         lon = stations_info.loc[matched_index,"lon"]
         lat = stations_info.loc[matched_index,"lat"]
         lon_dict[station] = float(lon)
         lat_dict[station] = float(lat)
      self.lon_dict = lon_dict
      self.lat_dict = lat_dict
      print("Data download has been completed.")

   def make_mean_wind_figure(self,start_datetime,end_datetime,lon_left,lon_right,lat_lower,lat_upper,zoom_level,deg_min_format,
                             contour,lon_interval,lat_interval,
                             height_max=1050,height_min=150,height_interval=100):

      # 観測データ、観測地点情報を取得
      df = self.df
      stations = self.stations

      # 下地となる白地図を取得
      print("Elevation data is now loading…")
      make_elevation_map(lon_left,lon_right,lat_lower,lat_upper,zoom_level,contour,
                         deg_min_format,lon_interval,lat_interval,
                         height_max,height_min,height_interval)
      print("Data loading has been completed!")

      fig = plt.gcf()
      basefig = pickle.dumps(fig)

      # 風データのプロット
      for index, obs_time in zip(df.index,df["jst_datetime"]):
         obs_time = datetime.datetime.strptime(obs_time,'%Y-%m-%d %H:%M:%S')
         if start_datetime <= obs_time <= end_datetime: # 指定時間内のデータであることを確認
            print(obs_time)
            copied_fig = pickle.loads(basefig)
            ax = plt.gcf().get_axes()[0]
            for station in stations:
               wind_speed = df.loc[index,f"mean_ws_{station}"]
               wind_dirction = df.loc[index,f"mean_wd_{station}"]
               wind_speed = float(wind_speed)
               wind_dirction = float(wind_dirction)
               lon, lat = self.lon_dict[station], self.lat_dict[station]
               if wind_speed > -888.8:
                  wind_u = wind_speed*(-math.sin(math.radians(wind_dirction)))
                  wind_v = wind_speed*(-math.cos(math.radians(wind_dirction)))
                  print(f"station name : {station}")
                  quiver = ax.quiver(lon, lat, wind_u, wind_v, color="darkblue", pivot="tail", scale=50, headlength=2.8, headaxislength=2.5, headwidth=3, width=0.01)
               elif wind_speed == -888.8: # 静穏時-888.8の処理
                  ax.plot(lon, lat, 'o', markeredgecolor='blue', markerfacecolor='none', markersize=3)

            # 凡例のプロット
            legend_value = 5
            legendname = f"{legend_value} "+r'[$\mathrm{m/s}$]'
            ax.quiverkey(quiver, 1.04, -0.1, legend_value, legendname, labelpos='E',coordinates='axes',transform=ccrs.PlateCarree(), color="darkblue")

            # 観測時間をプロット
            year = str(obs_time.year).zfill(4)
            month = str(obs_time.month).zfill(2)
            day = str(obs_time.day).zfill(2)
            hour = str(obs_time.hour).zfill(2)
            minute = str(obs_time.minute).zfill(2)
            plt.sca(ax)
            plt.title(f"{year}/{month}/{day} {hour}{minute}JST", fontsize=17)

            # 図の保存
            save_dir = generate_path(f"/img/10min_data/meanwind/{start_datetime}_{end_datetime}_stations{len(stations)}")
            filename = f"{year}{month}{day}{hour}{minute}.jpg"
            os.makedirs(save_dir,exist_ok=True)
            copied_fig.savefig(f"{save_dir}/{filename}", dpi=300, pad_inches=0.1)
            plt.clf()
            plt.close()

      print("Figures are successfully made.")

      # gifの作成
      print("Converting figures into gif…")
      gif_name = "wind_variation.gif"
      convert_jpg_to_gif(save_dir,save_dir,gif_name)
      print("Gif is successfully made.")

   def make_temperature_figure(self,start_datetime,end_datetime,lon_left,lon_right,lat_lower,lat_upper,zoom_level,deg_min_format,
                               elevation,contour,lon_interval,lat_interval,
                               height_max=1050,height_min=150,height_interval=100):

      # 観測データ、観測地点情報を取得
      df = self.df
      stations = self.stations

      # 下地となる白地図を取得
      if elevation:
         print("Elevation data is now loading…")
         make_elevation_map(lon_left,lon_right,lat_lower,lat_upper,zoom_level,contour,
                            deg_min_format,lon_interval,lat_interval,
                            height_max,height_min,height_interval)
      else:
         print("Base map is now loading…")
         make_blank_map(lon_left,lon_right,lat_lower,lat_upper,deg_min_format,lon_interval=0.5,lat_interval=0.5)

      fig = plt.gcf()
      basefig = pickle.dumps(fig)
      print("Data loading has been completed!")

      # プロットする気温の文字列の色分けを指定
      number_of_class = 9
      temp_min, temp_max = -5, 40
      cmap_name = "jet"
      # cmap_name = "nipy_spectral"

      class_interval = int((temp_max-temp_min)/(number_of_class))
      cmap_number = range(number_of_class)
      boundary_values = range(temp_min,temp_max,class_interval)
      TEMPERATURE_CMAP = {(i,i+5):j for i,j in zip(boundary_values,cmap_number)}
      cmap = plt.get_cmap(cmap_name,number_of_class).copy()

      # 気温データのプロット
      for index, obs_time in zip(df.index,df["jst_datetime"]):
         obs_time = datetime.datetime.strptime(obs_time,'%Y-%m-%d %H:%M:%S')
         if start_datetime <= obs_time <= end_datetime: # 指定時間内のデータであることを確認
            print(obs_time)
            copied_fig = pickle.loads(basefig)
            ax = plt.gcf().get_axes()[0]
            for station in stations:
               temperature = df.loc[index,f"temperature_{station}"]
               lon, lat = self.lon_dict[station], self.lat_dict[station]
               if lon_left <= lon <= lon_right and lat_lower <= lat <= lat_upper:
                  if int(temperature) > -900:
                     print(f"station name : {station}")
                     for temp_range, cmap_number in TEMPERATURE_CMAP.items():
                        if temp_range[0] <= int(temperature) < temp_range[1]:
                           ax.text(lon,lat,temperature,color=cmap(cmap_number),ha="center", fontsize=15)
                           break
                  else: # 欠測時の処理
                     ax.plot(lon, lat, '.', markeredgecolor='black', markerfacecolor='none', markersize=3)

            # 観測時間をプロット
            year = str(obs_time.year).zfill(4)
            month = str(obs_time.month).zfill(2)
            day = str(obs_time.day).zfill(2)
            hour = str(obs_time.hour).zfill(2)
            minute = str(obs_time.minute).zfill(2)
            plt.sca(ax)
            plt.title(f"{year}/{month}/{day} {hour}{minute}JST", fontsize=17)

            # 図の保存
            save_dir = generate_path(f"/img/10min_data/temperature/{start_datetime}_{end_datetime}_stations{len(stations)}")
            filename = f"{year}{month}{day}{hour}{minute}.jpg"
            os.makedirs(save_dir,exist_ok=True)
            copied_fig.savefig(f"{save_dir}/{filename}", dpi=300, pad_inches=0.1)
            plt.clf()
            plt.close()
  
      print("Figures are successfully made.")

      # gifの作成
      print("Converting figures into gif…")
      gif_name = "temp_variation.gif"
      convert_jpg_to_gif(save_dir,save_dir,gif_name)
      print("Gif is successfully made.")

   def make_precipitation_figure(self,start_datetime,end_datetime,lon_left,lon_right,lat_lower,lat_upper,zoom_level,deg_min_format,
                                 elevation,contour,lon_interval,lat_interval,height_max=1050,height_min=150,height_interval=100):

      # 観測データ、観測地点情報を取得
      df = self.df
      stations = self.stations

      # 下地となる白地図を取得
      if elevation:
         print("Elevation data is now loading…")
         make_elevation_map(lon_left,lon_right,lat_lower,lat_upper,zoom_level,contour,
                            deg_min_format,lon_interval,lat_interval,
                            height_max,height_min,height_interval)
      else:
         print("Base map is now loading…")
         make_blank_map(lon_left,lon_right,lat_lower,lat_upper,deg_min_format,lon_interval=0.5,lat_interval=0.5)

      fig = plt.gcf()
      basefig = pickle.dumps(fig)
      print("Data loading has been completed!")

      # プロットする気温の文字列の色分けを指定
      number_of_class = 8
      precipitaion_min, precipitaion_max = 0, 16
      # cmap_name = "jet"
      cmap_name = "nipy_spectral"

      class_interval = int((precipitaion_max-precipitaion_min)/(number_of_class))
      cmap_number = range(number_of_class)
      boundary_values = range(precipitaion_min,precipitaion_max,class_interval)
      PRECIPITATION_CMAP = {(i,i+5):j for i,j in zip(boundary_values,cmap_number)}
      cmap = plt.get_cmap(cmap_name,number_of_class).copy()

      # 気温データのプロット
      for index, obs_time in zip(df.index,df["jst_datetime"]):
         obs_time = datetime.datetime.strptime(obs_time,'%Y-%m-%d %H:%M:%S')
         if start_datetime <= obs_time <= end_datetime: # 指定時間内のデータであることを確認
            print(obs_time)
            copied_fig = pickle.loads(basefig)
            ax = plt.gcf().get_axes()[0]
            for station in stations:
               precipitaion = df.loc[index,f"precipitaion_{station}"]
               lon, lat = self.lon_dict[station], self.lat_dict[station]
               if int(precipitaion) > -900:
                  print(f"station name : {station}")
                  for temp_range, cmap_number in PRECIPITATION_CMAP.items():
                     if temp_range[0] <= int(precipitaion) < temp_range[1]:
                        ax.text(lon,lat,precipitaion,color=cmap(cmap_number),ha="center", fontsize=13)
                        break
               else: # 欠測時の処理
                  ax.plot(lon, lat, '.', markeredgecolor='black', markerfacecolor='none', markersize=3)

            # 観測時間をプロット
            year = str(obs_time.year).zfill(4)
            month = str(obs_time.month).zfill(2)
            day = str(obs_time.day).zfill(2)
            hour = str(obs_time.hour).zfill(2)
            minute = str(obs_time.minute).zfill(2)
            plt.sca(ax)
            plt.title(f"{year}/{month}/{day} {hour}{minute}JST", fontsize=17)

            # 図の保存
            save_dir = generate_path(f"/img/10min_data/temperature/{start_datetime}_{end_datetime}_stations{len(stations)}")
            filename = f"{year}{month}{day}{hour}{minute}.jpg"
            os.makedirs(save_dir,exist_ok=True)
            copied_fig.savefig(f"{save_dir}/{filename}", dpi=300, pad_inches=0.1)
            plt.clf()
            plt.close()
  
      print("Figures are successfully made.")

      # gifの作成
      print("Converting figures into gif…")
      gif_name = "preciptation_variation.gif"
      convert_jpg_to_gif(save_dir,save_dir,gif_name)
      print("Gif is successfully made.")


# 1時間値の処理
class AmedasHourlyDataAnalyzer:
   def __init__(self):
      # 観測データをcsvファイルから取得
      dir_name = generate_path("/data/hourly_data")
      csv_file = "raw_amedas_data.csv"
      self.df = pd.read_csv(f"{dir_name}/{csv_file}")
      columns = self.df.columns
      self.stations = columns[columns.str.contains("rh")].str[3:] #観測地点名を抽出

      # 各観測地点のlatとlonの取得
      dir_name = generate_path("/data")
      csv_file = "amedas_observation_points.csv"
      stations_info = pd.read_csv(f"{dir_name}/{csv_file}",dtype=str) #観測地点情報の一覧
      lon_dict, lat_dict = {}, {}
      for station in self.stations:
         matched_row = stations_info[stations_info["enName"] == f"{station}"]
         matched_index = matched_row.index.values[0]
         lon = stations_info.loc[matched_index,"lon"]
         lat = stations_info.loc[matched_index,"lat"]
         lon_dict[station] = float(lon)
         lat_dict[station] = float(lat)
      self.lon_dict = lon_dict
      self.lat_dict = lat_dict
      print("Data download has been completed.")

   def make_mean_wind_figure(self,start_datetime,end_datetime,lon_left,lon_right,lat_lower,lat_upper,zoom_level,deg_min_format,
                             contour,lon_interval,lat_interval,
                             height_max=1050,height_min=150,height_interval=100):

      # 観測データ、観測地点情報を取得
      df = self.df
      stations = self.stations

      # 下地となる標高地図を取得
      print("Elevation data is now loading…")
      make_elevation_map(lon_left,lon_right,lat_lower,lat_upper,zoom_level,contour,
                         deg_min_format,lon_interval,lat_interval,
                         height_max,height_min,height_interval)
      fig = plt.gcf()
      basefig = pickle.dumps(fig)
      print("Data loading has been completed!")

      # 風データのプロット
      for index, obs_time in zip(df.index,df["jst_datetime"]):
         obs_time = datetime.datetime.strptime(obs_time,'%Y-%m-%d %H:%M:%S')
         if start_datetime <= obs_time <= end_datetime: # 指定時間内のデータであることを確認
            print(obs_time)
            copied_fig = pickle.loads(basefig)
            ax = plt.gcf().get_axes()[0]
            for station in stations:
               wind_speed = df.loc[index,f"mean_ws_{station}"]
               wind_dirction = df.loc[index,f"mean_wd_{station}"]
               wind_speed = float(wind_speed)
               wind_dirction = float(wind_dirction)
               lon, lat = self.lon_dict[station], self.lat_dict[station]
               if lon_left <= lon <= lon_right and lat_lower <= lat <= lat_upper:
                  if wind_speed > -888.8:
                     wind_u = wind_speed*(-math.sin(math.radians(wind_dirction)))
                     wind_v = wind_speed*(-math.cos(math.radians(wind_dirction)))
                     print(f"station name : {station}")
                     quiver = ax.quiver(lon, lat, wind_u, wind_v, color="darkblue", pivot="tail", scale=50, headlength=2.8, headaxislength=2.5, headwidth=3, width=0.01)
                  elif wind_speed == -888.8: # 静穏時-888.8の処理
                     ax.plot(lon, lat, 'o', markeredgecolor='blue', markerfacecolor='none', markersize=3)

            # 凡例のプロット
            legend_value = 5
            legendname = f"{legend_value} "+r'[$\mathrm{m/s}$]'
            ax.quiverkey(quiver, 1.04, -0.1, legend_value, legendname, labelpos='E',coordinates='axes',transform=ccrs.PlateCarree(), color="darkblue")

            # 観測時間をプロット
            year = str(obs_time.year).zfill(4)
            month = str(obs_time.month).zfill(2)
            day = str(obs_time.day).zfill(2)
            hour = str(obs_time.hour).zfill(2)
            minute = str(obs_time.minute).zfill(2)
            plt.sca(ax)
            plt.title(f"{year}/{month}/{day} {hour}{minute}JST", fontsize=17)

            # 図の保存
            save_dir = generate_path(f"/img/hourly_data/meanwind/{start_datetime}_{end_datetime}_stations{len(stations)}")
            filename = f"{year}{month}{day}{hour}{minute}.jpg"
            os.makedirs(save_dir,exist_ok=True)
            copied_fig.savefig(f"{save_dir}/{filename}", dpi=300, pad_inches=0.1)
            plt.clf()
            plt.close()

      print("Figures are successfully made.")

      # gifの作成
      print("Converting figures into gif…")
      gif_name = "wind_variation.gif"
      convert_jpg_to_gif(save_dir,save_dir,gif_name)
      print("Gif is successfully made.")

   def make_composite_wind_figure(self,groupname,dates,lon_left,lon_right,lat_lower,lat_upper,zoom_level,deg_min_format,
                                  contour,lon_interval,lat_interval,height_max=1050,height_min=150,height_interval=100):
      
      # 観測データ、観測地点情報を取得
      df = self.df
      stations = self.stations

      # 下地となる標高地図を取得
      print("Elevation data is now loading…")
      make_elevation_map(lon_left,lon_right,lat_lower,lat_upper,zoom_level,contour,
                           deg_min_format,lon_interval,lat_interval,
                           height_max,height_min,height_interval)
      fig = plt.gcf()
      basefig = pickle.dumps(fig)
      print("Data loading has been completed!")


      # 1時間ごとに各観測所におけるデータを取得し平均
      for i in range(24):
         count = 1
         print(f"Now making a figure of {i}-{i+1} JST.")
         for date in dates:
            first_station = True
            for station in stations:
               for index, obs_time in zip(df.index,df["jst_datetime"]):
                  obs_time = datetime.datetime.strptime(obs_time,'%Y-%m-%d %H:%M:%S')
                  designated_time = datetime.datetime.combine(date,datetime.time(1)) + datetime.timedelta(hours=i)
                  if obs_time == designated_time:
                     wind_speed = df.loc[index,f"mean_ws_{station}"]
                     wind_dirction = df.loc[index,f"mean_wd_{station}"]
                     wind_speed = float(wind_speed)
                     wind_dirction = float(wind_dirction)
                     if wind_speed > -888.8:
                        wind_u = wind_speed*(-math.sin(math.radians(wind_dirction)))
                        wind_v = wind_speed*(-math.cos(math.radians(wind_dirction)))
                     elif wind_speed == -888.8: # 静穏時-888.8の処理
                        wind_u = 0
                        wind_v = 0
                     else: # 欠測値の処理
                        wind_u = np.nan
                        wind_v = np.nan

                     # dataframeに追加・結合していき平均を取る
                     if first_station: # 最初の地点ではdataframeを作成
                        df_u_each = pd.DataFrame([wind_u]).T
                        df_u_each.columns = [date]
                        df_u_each.index = [station]
                        df_v_each = pd.DataFrame([wind_v]).T
                        df_v_each.columns = [date]
                        df_v_each.index = [station]
                        first_station = False
                     else: # 2地点目以降は横方向に結合
                        df_u_fac = pd.DataFrame([wind_u]).T
                        df_u_fac.columns = [date]
                        df_u_fac.index = [station]
                        df_u_each = pd.concat([df_u_each,df_u_fac], ignore_index=False)
                        df_v_fac = pd.DataFrame([wind_v]).T
                        df_v_fac.columns = [date]
                        df_v_fac.index = [station]
                        df_v_each = pd.concat([df_v_each,df_v_fac], ignore_index=False)
                     
            if count == 1: # 1日目はそのまま渡す
               df_u = df_u_each
               df_v = df_v_each
               count +=1
            else: # 2日目以降は縦方向に結合
               df_u = pd.concat([df_u,df_u_each], ignore_index=False, axis=1) 
               df_v = pd.concat([df_v,df_v_each], ignore_index=False, axis=1)

         # 平均をとる
         df_u_mean = df_u.mean(axis=1)
         df_v_mean = df_v.mean(axis=1)

         # 図の描画
         copied_fig = pickle.loads(basefig)
         ax = plt.gcf().get_axes()[0]

         for station in stations:
            wind_u = df_u_mean[station]
            wind_v = df_v_mean[station]
            lon, lat = self.lon_dict[station], self.lat_dict[station]
            if lon_left <= lon <= lon_right and lat_lower <= lat <= lat_upper:
               quiver = ax.quiver(lon, lat, wind_u, wind_v, color="darkblue", pivot="tail", scale=30, headlength=3, headaxislength=2.5, headwidth=3, width=0.012)

         # 凡例のプロット
         legend_value = 5
         legendname = f"{legend_value} "+r'[$\mathrm{m/s}$]'
         ax.quiverkey(quiver, 1.04, -0.1, legend_value, legendname, labelpos='E',coordinates='axes',transform=ccrs.PlateCarree(), color="darkblue")

         # 観測時刻のプロット
         hour_before = str(i).zfill(2)
         hour_later = str(i+1).zfill(2)
         minute = str(0).zfill(2)
         plt.sca(ax)
         plt.title(f"{groupname} composite  {hour_before}{minute}-{hour_later}{minute}JST", fontsize=16)

         # 図の保存
         save_dir = generate_path(f"/img/hourly_data/composite/meanwind/{groupname}/stations{len(stations)}")
         filename = f"{groupname}_{hour_before}_{hour_later}_composite.jpg"
         os.makedirs(save_dir,exist_ok=True)
         copied_fig.savefig(f"{save_dir}/{filename}", dpi=300, pad_inches=0.1)
         plt.clf()
         plt.close()

      print("Figures are successfully made.")

      # gifの作成
      print("Converting figures into gif…")
      gif_name = "wind_variation.gif"
      convert_jpg_to_gif(save_dir,save_dir,gif_name)
      print("Gif is successfully made.")

   def make_temperature_figure(self,start_datetime,end_datetime,lon_left,lon_right,lat_lower,lat_upper,zoom_level,deg_min_format,
                               elevation,contour,lon_interval,lat_interval,height_max=1050,height_min=150,height_interval=100):

      # 観測データ、観測地点情報を取得
      df = self.df
      stations = self.stations

      # 下地となる白地図を取得
      if elevation:
         print("Elevation data is now loading…")
         make_elevation_map(lon_left,lon_right,lat_lower,lat_upper,zoom_level,contour,
                            deg_min_format,lon_interval,lat_interval,
                            height_max,height_min,height_interval)
      else:
         print("Base map is now loading…")
         make_blank_map(lon_left,lon_right,lat_lower,lat_upper,deg_min_format,lon_interval=0.5,lat_interval=0.5)

      fig = plt.gcf()
      basefig = pickle.dumps(fig)
      print("Data loading has been completed!")

      # プロットする気温の文字列の色分けを指定
      number_of_class = 9
      temp_min, temp_max = -5, 40
      cmap_name = "jet"
      # cmap_name = "nipy_spectral"

      class_interval = int((temp_max-temp_min)/(number_of_class))
      cmap_number = range(number_of_class)
      boundary_values = range(temp_min,temp_max,class_interval)
      TEMPERATURE_CMAP = {(i,i+5):j for i,j in zip(boundary_values,cmap_number)}
      cmap = plt.get_cmap(cmap_name,number_of_class).copy()

      # 気温データのプロット
      for index, obs_time in zip(df.index,df["jst_datetime"]):
         obs_time = datetime.datetime.strptime(obs_time,'%Y-%m-%d %H:%M:%S')
         if start_datetime <= obs_time <= end_datetime: # 指定時間内のデータであることを確認
            print(obs_time)
            copied_fig = pickle.loads(basefig)
            ax = plt.gcf().get_axes()[0]
            for station in stations:
               temperature = df.loc[index,f"temperature_{station}"]
               lon, lat = self.lon_dict[station], self.lat_dict[station]
               if lon_left <= lon <= lon_right and lat_lower <= lat <= lat_upper:
                  if int(temperature) > -900:
                     print(f"station name : {station}")
                     for temp_range, cmap_number in TEMPERATURE_CMAP.items():
                        if temp_range[0] <= int(temperature) < temp_range[1]:
                           ax.text(lon,lat,temperature,color=cmap(cmap_number),ha="center",fontsize=15,clip_on=True)
                           break
                  else: # 欠測時の処理
                     ax.plot(lon,lat,'.',markeredgecolor='black',markerfacecolor='none',markersize=3)

            # 観測時間をプロット
            year = str(obs_time.year).zfill(4)
            month = str(obs_time.month).zfill(2)
            day = str(obs_time.day).zfill(2)
            hour = str(obs_time.hour).zfill(2)
            minute = str(obs_time.minute).zfill(2)
            plt.sca(ax)
            plt.title(f"{year}/{month}/{day} {hour}{minute}JST", fontsize=17)

            # 図の保存
            save_dir = generate_path(f"/img/hourly_data/temperature/{start_datetime}_{end_datetime}_stations{len(stations)}")
            filename = f"{year}{month}{day}{hour}{minute}.jpg"
            os.makedirs(save_dir,exist_ok=True)
            copied_fig.savefig(f"{save_dir}/{filename}", dpi=300, pad_inches=0.1)
            plt.clf()
            plt.close()
  
      print("Figures are successfully made.")

      # gifの作成
      print("Converting figures into gif…")
      gif_name = "temp_variation.gif"
      convert_jpg_to_gif(save_dir,save_dir,gif_name)
      print("Gif is successfully made.")

   def make_composite_temperature_figure(self,groupname,dates,lon_left,lon_right,lat_lower,lat_upper,zoom_level,deg_min_format,
                                         elevation,contour,lon_interval,lat_interval,height_max=1050,height_min=150,height_interval=100):
      
      # 観測データ、観測地点情報を取得
      df = self.df
      stations = self.stations

      # 下地となる標高地図を取得
      if elevation:
         print("Elevation data is now loading…")
         make_elevation_map(lon_left,lon_right,lat_lower,lat_upper,zoom_level,contour,
                            deg_min_format,lon_interval,lat_interval,
                            height_max,height_min,height_interval)
      else:
         print("Base map is now loading…")
         make_blank_map(lon_left,lon_right,lat_lower,lat_upper,deg_min_format,lon_interval=0.5,lat_interval=0.5)

      fig = plt.gcf()
      basefig = pickle.dumps(fig)
      print("Data loading has been completed!")


      # 1時間ごとに各観測所におけるデータを取得し平均
      for i in range(24):
         count = 1
         print(f"Now making a figure of {i}-{i+1} JST.")
         for date in dates:
            first_station = True
            for station in stations:
               for index, obs_time in zip(df.index,df["jst_datetime"]):
                  obs_time = datetime.datetime.strptime(obs_time,'%Y-%m-%d %H:%M:%S')
                  designated_time = datetime.datetime.combine(date,datetime.time(1)) + datetime.timedelta(hours=i)
                  if obs_time == designated_time:
                     temperature = df.loc[index,f"temperature_{station}"]
                     temperature = float(temperature)
                     if temperature > -900: # 正常値の処理
                        pass
                     else: # 欠測値の処理
                        temperature = np.nan

                     # dataframeに追加・結合していき平均を取る
                     if first_station: # 最初の地点ではdataframeを作成
                        df_each = pd.DataFrame([temperature]).T
                        df_each.columns = [date]
                        df_each.index = [station]
                        first_station = False
                     else: # 2地点目以降は横方向に結合
                        df_fac = pd.DataFrame([temperature]).T
                        df_fac.columns = [date]
                        df_fac.index = [station]
                        df_each = pd.concat([df_each,df_fac], ignore_index=False)
                     
            if count == 1: # 1日目はそのまま渡す
               df_temperature = df_each
               count +=1
            else: # 2日目以降は縦方向に結合
               df_temperature = pd.concat([df_temperature,df_each], ignore_index=False, axis=1) 

         # 平均をとる
         df_temperature_mean = df_temperature.mean(axis=1)

         # 図の描画
         copied_fig = pickle.loads(basefig)
         ax = plt.gcf().get_axes()[0]

         # プロットする気温の文字列の色分けを指定
         number_of_class = 9
         temp_min, temp_max = -5, 40
         cmap_name = "jet"
         # cmap_name = "nipy_spectral"

         class_interval = int((temp_max-temp_min)/(number_of_class))
         cmap_number = range(number_of_class)
         boundary_values = range(temp_min,temp_max,class_interval)
         TEMPERATURE_CMAP = {(i,i+5):j for i,j in zip(boundary_values,cmap_number)}
         cmap = plt.get_cmap(cmap_name,number_of_class).copy()


         for station in stations:
            temperature = df_temperature_mean[station]
            lon, lat = self.lon_dict[station], self.lat_dict[station]
            if lon_left <= lon <= lon_right and lat_lower <= lat <= lat_upper:
               if np.isnan(temperature): # 欠測値の処理
                  ax.plot(lon,lat,'.',markeredgecolor='black',markerfacecolor='none',markersize=3)
               else: # 正常値の処理
                  print(f"station name : {station}")
                  for temp_range, cmap_number in TEMPERATURE_CMAP.items():
                     if temp_range[0] <= int(temperature) < temp_range[1]:
                        temperature = round(temperature,1) #小数第2位以下切り捨て
                        ax.text(lon,lat,temperature,color=cmap(cmap_number),ha="center",fontsize=15,clip_on=True)
                        break

         # 観測時刻のプロット
         hour_before = str(i).zfill(2)
         hour_later = str(i+1).zfill(2)
         minute = str(0).zfill(2)
         plt.sca(ax)
         plt.title(f"{groupname} composite  {hour_before}{minute}-{hour_later}{minute}JST", fontsize=16)

         # 図の保存
         save_dir = generate_path(f"/img/hourly_data/composite/temperature/{groupname}/stations{len(stations)}")
         filename = f"{groupname}_{hour_before}_{hour_later}_composite.jpg"
         os.makedirs(save_dir,exist_ok=True)
         copied_fig.savefig(f"{save_dir}/{filename}", dpi=300, pad_inches=0.1)
         plt.clf()
         plt.close()

      print("Figures are successfully made.")

      # gifの作成
      print("Converting figures into gif…")
      gif_name = "temp_variation.gif"
      convert_jpg_to_gif(save_dir,save_dir,gif_name)
      print("Gif is successfully made.")
