import requests
import numpy as np
import pandas as pd
import cartopy.crs as ccrs
import cartopy.io.shapereader as shapereader
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.axes as maxes
from math import log, tan, atan, pi, e
from io import StringIO
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
from mpl_toolkits.axes_grid1 import make_axes_locatable

"""
z means zoom level.
"""

def convert_lonlat_to_tile(lon,lat,z):
    x = int((lon / 180 + 1) * 2**z / 2) # x座標
    y = int(((-log(tan((45 + lat / 2) * pi / 180)) + pi) * 2**z / (2 * pi))) # y座標
    return x, y

def convert_tile_to_northwest_lonlat(x,y,z):
    lon_left = (x / 2.0**z) * 360 - 180 # 経度（東経）
    mapy = (y / 2.0**z) * 2 * pi - pi
    lat_upper = 2 * atan(e ** (- mapy)) * 180 / pi - 90 # 緯度（北緯）
    return lon_left,lat_upper

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

def load_gis(z, x1, x2, y1, y2):

    a = np.array([])
    for x in range(x1, x2+1):
        b = np.array([])
        for y in range(y1, y2+1):

            #地形データを読み込む
            url = 'http://cyberjapandata.gsi.go.jp/xyz/dem/{0}/{1}/{2}.txt'.format(z,x,y)
            response = requests.get(url)
            if response.status_code == 404:
                 #メッシュデータが無い区画は全ての点が0mのメッシュとしてとりあえず用意する
                 Z = np.zeros((256, 256))
            else:
                 #標高値がない点はとりあえず0mに置換する
                #  maptxt = string.replace(response.text, u'e', u'0.0')
                 maptxt = response.text.replace(u'e', u'0.0')
                 Z = pd.read_csv(StringIO(maptxt), header=None)
                 Z = Z.values
                 #Z = Z.transpose()             
            if len(b)==0:
                b = Z
            else:
                b = np.append(b,Z,0)
            
        if len(a)==0:
            a = b
        else:
            a = np.append(a,b,1)
            
    return a


def make_elevation_map(lon_left,lon_right,lat_lower,lat_upper,z,contour=False,
                       deg_min_format=True,lon_interval=0.5,lat_interval=0.5,
                       height_max=1050,height_min=150,height_interval=100):
    
    # 緯度経度をタイル座標に変換して、標高データを取得
    x1, y1 = convert_lonlat_to_tile(lon_left,lat_upper,z)
    x2, y2 = convert_lonlat_to_tile(lon_right,lat_lower,z)
    Z = load_gis(z, x1, x2, y1, y2)

    # 県境データを取得
    shpfilename = shapereader.natural_earth(resolution='10m', category='cultural', name='admin_1_states_provinces')
    provinces = shapereader.Reader(shpfilename).records()
    prefs = filter(lambda province: province.attributes['admin'] == 'Japan', provinces)

    # 標高を描画するための座標を設定
    left_edge, upper_edge = convert_tile_to_northwest_lonlat(x1,y1,z)
    right_edge, lower_edge = convert_tile_to_northwest_lonlat(x2+1,y2+1,z)
    xlim = Z.shape[1]
    ylim = Z.shape[0]
    lon_grid = np.linspace(left_edge, right_edge, xlim)
    lat_grid = np.linspace(upper_edge, lower_edge, ylim)
    X, Y = np.meshgrid(lon_grid, lat_grid)  # X,Yグリッドを生成

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

    # 標高データのプロット
    levels_shade = np.arange(0,height_max+1,height_interval)
    levels_contour = np.arange(height_min,4001,height_interval)
    if contour:  # 等高線プロット
        cr = ax.contour(X, Y, Z, transform=ccrs.PlateCarree(), levels=levels_contour, linewidths=0.4, colors="black")
        ax.clabel(cr,fmt='%.{0[0]}f'.format([0]),fontsize=7)

    else: # 陰影プロット
        cmap = plt.get_cmap('YlOrRd').copy()    
        cmap.set_under("w")
        shadeplot = ax.contourf(X, Y, Z, alpha=.7, cmap=cmap, transform=ccrs.PlateCarree(), levels=levels_shade, extend="max")
        shadeplot.set_clim(vmin=height_min,vmax=height_max)

        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.2, axes_class=maxes.Axes)
        fig.add_axes(cax)
        cbar = plt.colorbar(shadeplot, cax=cax, orientation='vertical')
        cbar.set_label("[m]", y=1.07, rotation= 0, fontsize=12)

    # 緯度経度の表示
    xloc = np.arange(0,180+0.0001,lon_interval)
    yloc = np.arange(0,90+0.0001,lat_interval)
    ax.set_xticks(xloc,crs=ccrs.PlateCarree())
    ax.set_yticks(yloc,crs=ccrs.PlateCarree())
    ax.xaxis.set_major_formatter(LongitudeFormatter())
    ax.yaxis.set_major_formatter(LatitudeFormatter())
    
    if deg_min_format:
        ax.xaxis.set_major_formatter(format_longitude)
        ax.yaxis.set_major_formatter(format_latitude)

    # 描画範囲を設定
    ax.set_extent((lon_left, lon_right, lat_lower, lat_upper), ccrs.PlateCarree())
