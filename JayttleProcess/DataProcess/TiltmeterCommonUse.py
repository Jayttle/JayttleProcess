# 标准库导入
import math
import random
from datetime import datetime, timedelta
import time
import warnings

# 相关第三方库导入
import pyproj
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import statsmodels.api as sm
from collections import defaultdict
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.ar_model import AutoReg
from statsmodels.stats.diagnostic import acorr_ljungbox
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering 
from sklearn.linear_model import Ridge , Lasso, LassoCV, ElasticNet, LinearRegression
from sklearn.metrics import root_mean_squared_error, mean_absolute_error, r2_score, mean_squared_error, silhouette_score, davies_bouldin_score, calinski_harabasz_score, v_measure_score
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.mixture import GaussianMixture
from sklearn.model_selection import GridSearchCV
from scipy.spatial.distance import euclidean
from scipy import signal, fft
from scipy.cluster import hierarchy
from scipy.stats import t, shapiro, pearsonr, f_oneway, gaussian_kde
from scipy.signal import hilbert, find_peaks
from PyEMD import EMD, EEMD, CEEMDAN
from typing import List, Optional, Tuple, Union
import pywt

# region 字体设置
plt.rcParams['font.sans-serif'] = ['SimSun']  # 指定宋体为默认字体
plt.rcParams['font.sans-serif'] = 'SimSun'  # 使用指定的中文字体
# 禁用特定警告
warnings.filterwarnings('ignore', category=UserWarning, append=True)
# 或者关闭所有警告
warnings.filterwarnings("ignore")
# endregion

class TiltmeterData:
    def __init__(self, time: str, station_id: int, pitch: float, roll: float):
        try:
            self.time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f')  # 尝试包含毫秒部分的格式
        except ValueError:
            self.time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')  # 失败时尝试不包含毫秒部分的格式
        self.station_id = station_id
        self.pitch = pitch
        self.roll = roll

    @classmethod
    def from_line(cls, line: str) -> 'TiltmeterData':
        parts = line.strip().split('\t')
        time: str = parts[0]
        station_id: int = int(parts[1])
        pitch: float = float(parts[2])
        roll: float = float(parts[3])
        return cls(time, station_id, pitch, roll)

    @classmethod
    def from_file(cls, file_path: str) -> List['TiltmeterData']:
        tiltmeter_data_list: List['TiltmeterData'] = []
        with open(file_path, 'r') as file:
            first_line = True
            for line in file:
                if first_line:
                    first_line = False
                    continue
                tiltmeter_data = cls.from_line(line)
                tiltmeter_data_list.append(tiltmeter_data)
        return tiltmeter_data_list

    @classmethod
    def filter_by_date(cls, tiltmeter_data_list: List['TiltmeterData'], date: str) -> List['TiltmeterData']:
        filtered_data: List['TiltmeterData'] = [data for data in tiltmeter_data_list if data.time.strftime('%Y-%m-%d') == date]
        return filtered_data

    @classmethod
    def save_to_file(cls, tiltmeter_data_list: List['TiltmeterData'], file_path: str) -> None:
        with open(file_path, 'w') as file:
            for data in tiltmeter_data_list:
                file.write(f"{data.time.strftime('%Y-%m-%d %H:%M:%S.%f')}\t{data.station_id}\t{data.pitch}\t{data.roll}\n")


def plot_tiltmeter_data(tiltmeter_data_list: List['TiltmeterData']):
    # 提取 pitch 和 roll 数据以及时间数据
    pitch_data = [data.pitch for data in tiltmeter_data_list]
    roll_data = [data.roll for data in tiltmeter_data_list]
    time_list = [data.time for data in tiltmeter_data_list]

    # 创建两个子图
    plt.figure(figsize=(12, 6))

    # 设置日期格式化器和日期刻度定位器
    date_fmt = mdates.DateFormatter("%m-%d-%H")  # 仅显示月-日-时
    date_locator = mdates.AutoDateLocator()  # 自动选择刻度间隔

    # 绘制 pitch 时序图
    plt.subplot(2, 1, 1)
    plt.plot(time_list, pitch_data, color='blue')
    plt.title('时间轴上的俯仰角变化')
    plt.xlabel('日期')
    plt.ylabel('俯仰角')
    plt.gca().xaxis.set_major_formatter(date_fmt)
    plt.gca().xaxis.set_major_locator(date_locator)

    # 绘制 roll 时序图
    plt.subplot(2, 1, 2)
    plt.plot(time_list, roll_data, color='green')
    plt.title('时间轴上的横滚角变化')
    plt.xlabel('日期')
    plt.ylabel('横滚角')
    plt.gca().xaxis.set_major_formatter(date_fmt)
    plt.gca().xaxis.set_major_locator(date_locator)

    plt.tight_layout()  # 调整子图布局以防止重叠
    plt.show()


# # 使用示例
# file_path = r'C:\Users\Jayttle\Desktop\tiltmeter_temp.txt'
# tiltmeter_data_list: List['TiltmeterData'] = TiltmeterData.from_file(file_path)

# # 找出时间为 2023-8-2 的数据
# filtered_data: List['TiltmeterData'] = TiltmeterData.filter_by_date(tiltmeter_data_list, "2023-08-01")
# plot_tiltmeter_data(filtered_data)