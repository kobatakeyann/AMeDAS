import numpy as np
import cartopy.crs as ccrs
import cartopy.io.shapereader as shapereader
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter


def format_longitude(lon,pos):
    degrees = int(lon)
    minutes = abs(int((lon - degrees) * 60))
    if minutes == 0:
        minutes = "00"
    return f'{degrees}°{minutes}\'E'

def format_latitude(lat,pos):
    degrees = int(lat)
    minutes = abs(int((lat - degrees) * 60))
    if minutes == 0:
        minutes = "00"
    return f'{degrees}°{minutes}\'N'

def make_blank_map(lon_left,lon_right,lat_lower,lat_upper,deg_min_format=True,lon_interval=0.5,lat_interval=0.5):

    # 県境データを取得
    shpfilename = shapereader.natural_earth(resolution='10m', category='cultural', name='admin_1_states_provinces')
    provinces = shapereader.Reader(shpfilename).records()
    prefs = filter(lambda province: province.attributes['admin'] == 'Japan', provinces)

    # 図のサイズの設定
    aspect = (lat_upper-lat_lower)/(lon_right-lon_left)
    figsize= (10,9.5*aspect)
    fig = plt.figure(figsize=figsize)
    proj = ccrs.PlateCarree()
    ax = fig.add_axes((0.08, 0.1, 0.83, 0.83),projection=proj)

    # 国境・県境を描画
    ax.coastlines(linewidths=1, resolution='10m')
    for pref in prefs:
        geometry = pref.geometry
        ax.add_geometries([geometry], ccrs.PlateCarree(), facecolor="none", linestyle='-', linewidth=0.1)

    # 緯度経度の表示
    xloc = np.arange(0,180+0.0001,lon_interval)
    yloc = np.arange(0,90+0.0001,lat_interval)
    ax.set_xticks(xloc,crs=ccrs.PlateCarree())
    ax.set_yticks(yloc,crs=ccrs.PlateCarree())
    ax.xaxis.set_major_formatter(LatitudeFormatter())
    ax.yaxis.set_major_formatter(LongitudeFormatter())
    
    if deg_min_format:
        ax.xaxis.set_major_formatter(format_longitude)
        ax.yaxis.set_major_formatter(format_latitude)

    # 描画範囲を設定
    ax.set_extent((lon_left, lon_right, lat_lower, lat_upper), ccrs.PlateCarree())
