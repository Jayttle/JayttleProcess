# 标准库导入
import math
import random
from datetime import datetime, timedelta
import time
import warnings

# 相关第三方库导入
from pyswarm import pso
import pyproj
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import statsmodels.api as sm
from collections import defaultdict
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.ar_model import AutoReg
from statsmodels.stats.diagnostic import acorr_ljungbox
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering 
from sklearn.linear_model import Ridge , Lasso, LassoCV, ElasticNet, LinearRegression
from sklearn.metrics import root_mean_squared_error, mean_absolute_error, r2_score, mean_squared_error, silhouette_score, davies_bouldin_score, calinski_harabasz_score, v_measure_score
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor, NearestNeighbors
from sklearn.preprocessing import PolynomialFeatures, StandardScaler, MinMaxScaler
from sklearn.pipeline import make_pipeline
from sklearn.mixture import GaussianMixture
from sklearn.svm import OneClassSVM
from sklearn.model_selection import GridSearchCV, cross_val_score
from scipy.spatial.distance import euclidean
from scipy import signal, fft
from scipy.cluster import hierarchy
from scipy.stats import t, shapiro, pearsonr, f_oneway, gaussian_kde, spearmanr, kendalltau
from scipy.signal import hilbert, find_peaks
from PyEMD import EMD, EEMD, CEEMDAN
from typing import List, Optional, Tuple, Union
import pywt
"""
python:
O(n)算法: 输入n: 1,000,000 耗时: 15.312433242797852 ms
O(n^2)算法输入n: 10,000 耗时: 1610.5492115020752 ms
O(nlogn)算法输入n: 10,000 耗时: 5.4988861083984375 ms 
"""
# region 字体设置
plt.rcParams['font.sans-serif'] = ['SimSun']  # 指定宋体为默认字体
plt.rcParams['font.sans-serif'] = 'SimSun'  # 使用指定的中文字体
# 禁用特定警告
warnings.filterwarnings('ignore', category=UserWarning, append=True)
# 或者关闭所有警告
warnings.filterwarnings("ignore")
# endregion

# region 无关功能
def check_data_type(data: np.ndarray) ->None:
    print("数据类型:", type(data))
    print("形状:", data.shape)


# endregion
# region 基础功能
def remove_average(data: list[float]) -> None:
    """对时序数据进行去平均 再乘以1000"""
    mean_value = np.mean(data)
    remove_specific_value(data, mean_value)


def remove_specific_value(data: list[float], specific_value: float) -> None:
    """对时序数据进行减去特定值 再乘以1000"""
    # 减去特定值并乘以1000
    for i in range(len(data)):
        data[i] = (data[i] - specific_value) * 1000
    

def plot_ListFloat(ListFloat: list[float], isShow: bool = False, SaveFilePath: Optional[str] = None, title: str = None) -> None:
    """绘制 ListFloat 对象的时间序列图"""
    # 不再使用 ListFloat，直接使用 ListFloat
    values = ListFloat
    datetimes = range(len(ListFloat))  # 使用数据长度生成简单的序号作为 x 轴

    # 修改标签和标题的文本为中文
    plt.figure(figsize=(14.4, 9.6)) # 单位是英寸
    plt.xlabel('日期')
    plt.ylabel('数值')
    if title is None:
        plt.title('时间序列数据')
    else:
        plt.title(f'{title}')

    # 设置最大显示的刻度数
    plt.tight_layout()  # 自动调整子图间的间距和标签位置
    plt.plot(datetimes, values)

    if SaveFilePath is not None:
        plt.savefig(SaveFilePath)
    elif isShow:
        plt.show()
    plt.close()


def plot_ListFloat_with_time_pitch(ListFloat: List[float], ListTime: List[datetime], isShow: bool = True, SaveFilePath: Optional[str] = None, title: str = None) -> None:
    """绘制 ListFloat 对象的时间序列图"""
    values = ListFloat
    datetimes = ListTime  # 使用数据长度生成简单的序号作为 x 轴

    plt.figure(figsize=(6, 4))  # 设置图的大小，单位是英寸

    # 隐藏右边框和上边框
    ax = plt.gca()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    plt.xlabel('2023年8月11日倾斜仪数据', fontsize=12)  # 可以省略 fontproperties
    plt.ylabel('俯仰角/°', fontsize=12)  # 可以省略 fontproperties

    # 设置日期格式化器和日期刻度定位器
    date_fmt = mdates.DateFormatter("%H:00")  # 仅显示小时和分钟
    date_locator = mdates.AutoDateLocator()  # 自动选择刻度间隔
    plt.gca().xaxis.set_major_formatter(date_fmt)
    plt.gca().xaxis.set_major_locator(date_locator)

    # 设置刻度朝向内部，并调整刻度与坐标轴的距离
    ax.tick_params(axis='x', direction='in', pad=10)
    ax.tick_params(axis='y', direction='in', pad=10)


    # 设置刻度格式化器，确保正负号显示正确
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: f'{y:.2f}'))

    # 调整底部边界向上移动一点
    plt.subplots_adjust(bottom=0.15)
    plt.subplots_adjust(left=0.15)


    # 绘制线条，设置颜色为黑色
    plt.plot(datetimes, values, color='black')
    # 设置保存或显示图形
    if SaveFilePath is not None:
        plt.savefig(SaveFilePath)
    elif isShow:
        plt.show()

    plt.close()


def plot_ListFloat_with_time_roll(ListFloat: List[float], ListTime: List[datetime], isShow: bool = True, SaveFilePath: Optional[str] = None, title: str = None) -> None:
    """绘制 ListFloat 对象的时间序列图"""
    values = ListFloat
    datetimes = ListTime  # 使用数据长度生成简单的序号作为 x 轴

    plt.figure(figsize=(6, 4))  # 设置图的大小，单位是英寸

    # 隐藏右边框和上边框
    ax = plt.gca()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    plt.xlabel('2023年8月11日倾斜仪数据', fontsize=12)  # 可以省略 fontproperties
    plt.ylabel('横滚角/°', fontsize=12)  # 可以省略 fontproperties

    # 设置日期格式化器和日期刻度定位器
    date_fmt = mdates.DateFormatter("%H:00")  # 仅显示小时和分钟
    date_locator = mdates.AutoDateLocator()  # 自动选择刻度间隔
    plt.gca().xaxis.set_major_formatter(date_fmt)
    plt.gca().xaxis.set_major_locator(date_locator)

    # 设置刻度朝向内部，并调整刻度与坐标轴的距离
    ax.tick_params(axis='x', direction='in', pad=10)
    ax.tick_params(axis='y', direction='in', pad=10)


    # 设置刻度格式化器，确保正负号显示正确
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: f'{y:.2f}'))

    # 调整底部边界向上移动一点
    plt.subplots_adjust(bottom=0.15)
    plt.subplots_adjust(left=0.15)


    # 绘制线条，设置颜色为黑色
    plt.plot(datetimes, values, color='black')
    # 设置保存或显示图形
    if SaveFilePath is not None:
        plt.savefig(SaveFilePath)
    elif isShow:
        plt.show()

    plt.close()


def plot_points(x_points, y_points, title=None):
    # Convert lists to numpy arrays
    y_points = np.array(y_points)
    
    plt.figure(figsize=(9, 6))  # 设置图的大小，单位是英寸
    
    # 绘制散点图
    plt.scatter(x_points, y_points)
    plt.xlabel('索道坐标X(mm)')  # 设置x轴标签
    plt.ylabel('索道坐标Y(mm)')  # 设置y轴标签
    
    # 隐藏右边框和上边框
    ax = plt.gca()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)  # 隐藏下边框
    ax.spines['left'].set_visible(False)    # 隐藏左边框
    
    # 添加箭头，指向坐标轴的正方向
    ax.annotate('', xy=(1, 0.001), xytext=(0, 0.001),
                arrowprops=dict(arrowstyle='->', lw=1, color='black'),
                xycoords='axes fraction', textcoords='axes fraction')
    ax.annotate('', xy=(0.001, 1), xytext=(0.001, 0),
                arrowprops=dict(arrowstyle='->', lw=1, color='black'),
                xycoords='axes fraction', textcoords='axes fraction')
    
    # 设置刻度朝向内部，并调整刻度与坐标轴的距离
    ax.tick_params(axis='x', direction='in', pad=10)  # pad 参数用于控制刻度与坐标轴的距离
    ax.tick_params(axis='y', direction='in', pad=10)
    
    # 设置标题
    if title is None:
        plt.suptitle('时间序列数据', y=0.0)  # 设置标题，默认为'时间序列数据'，y参数用于调整标题在垂直方向上的位置
    else:
        plt.suptitle(title, y=0.0)  # 设置标题为传入的参数title，y参数用于调整标题在垂直方向上的位置
    
    plt.tight_layout()  # 自动调整子图间的间距和标签位置
    plt.show()


def plot_ListFloat_x(ListFloat: list[float], isShow: bool = True, SaveFilePath: Optional[str] = None, title: str = None) -> None:
    """绘制 ListFloat 对象的时间序列图"""
    values = ListFloat
    datetimes = range(len(ListFloat))  # 使用数据长度生成简单的序号作为 x 轴

    plt.figure(figsize=(6, 4))  # 设置图的大小，单位是英寸

    # 隐藏右边框和上边框
    ax = plt.gca()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    plt.xlabel('数据期数/期', fontproperties='SimSun', fontsize=12)  # 设置字体为宋体
    plt.ylabel('索道坐标x轴方向位移监测/m', fontproperties='SimSun', fontsize=12)  # 设置字体为宋体

    # 设置最大显示的刻度数
    plt.tight_layout()  # 自动调整子图间的间距和标签位置
    # 设置刻度朝向内部，并调整刻度与坐标轴的距离
    ax.tick_params(axis='x', direction='in', pad=10)  # pad 参数用于控制刻度与坐标轴的距离
    ax.tick_params(axis='y', direction='in', pad=10)
    
    # 绘制线条和散点，设置颜色为黑色
    plt.plot(datetimes, values, color='black')
    plt.scatter(datetimes, values, s=10, color='black')

    if SaveFilePath is not None:
        plt.savefig(SaveFilePath)
    elif isShow:
        plt.show()
    plt.close()


def plot_ListFloat_Compare_without_marker(ListFloat1: list[float], ListFloat2: list[float], to_marker_idx: list[int] = []) -> None:
    """绘制两个ListFloat对象的时间序列图"""
    """绘制 ListFloat 对象的时间序列图"""
    values1 = [value for idx,value in enumerate(ListFloat1) if idx not in to_marker_idx]
    values2 = [value for idx,value in enumerate(ListFloat2) if idx not in to_marker_idx]

    pearson_corr, spearman_corr, kendall_corr = calculate_similarity(values1,values2)
    datetimes = range(len(values1))  # 使用数据长度生成简单的序号作为 x 轴

    plt.figure(figsize=(6, 4))  # 设置图的大小，单位是英寸

    # 隐藏右边框和上边框
    ax = plt.gca()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    plt.xlabel('数据期数/期', fontproperties='SimSun', fontsize=12)  # 设置字体为宋体
    plt.ylabel('索道坐标x轴方向位移监测/m', fontproperties='SimSun', fontsize=12)  # 设置字体为宋体

    # 设置最大显示的刻度数
    plt.tight_layout()  # 自动调整子图间的间距和标签位置
    # 设置刻度朝向内部，并调整刻度与坐标轴的距离
    ax.tick_params(axis='x', direction='in', pad=10)  # pad 参数用于控制刻度与坐标轴的距离
    ax.tick_params(axis='y', direction='in', pad=10)
    
    # 绘制线条和散点，设置颜色为黑色
    plt.plot(datetimes, values1, color='black')
    plt.plot(datetimes, values2, color='blue')

    plt.scatter(datetimes, values1, s=10, color='black')

    plt.show()
    plt.close()

def plot_ListFloat_with_marker(ListFloat: list[float], to_marker_idx: list[int] = []) -> None:
    """绘制两个ListFloat对象的时间序列图"""
    """绘制 ListFloat 对象的时间序列图"""
    """绘制 ListFloat 对象的时间序列图"""
    values = ListFloat
    datetimes = range(len(ListFloat))  # 使用数据长度生成简单的序号作为 x 轴

    plt.figure(figsize=(6, 4))  # 设置图的大小，单位是英寸

    # 隐藏右边框和上边框
    ax = plt.gca()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    plt.xlabel('数据期数/期', fontproperties='SimSun', fontsize=12)  # 设置字体为宋体
    plt.ylabel('索道坐标x轴方向位移监测/m', fontproperties='SimSun', fontsize=12)  # 设置字体为宋体

    # 设置最大显示的刻度数
    plt.tight_layout()  # 自动调整子图间的间距和标签位置
    # 设置刻度朝向内部，并调整刻度与坐标轴的距离
    ax.tick_params(axis='x', direction='in', pad=10)  # pad 参数用于控制刻度与坐标轴的距离
    ax.tick_params(axis='y', direction='in', pad=10)
    
    # 绘制线条和散点，设置颜色为黑色
    plt.plot(datetimes, values, color='black')
    for idx in range(len(values)):
        if idx not in to_marker_idx:
            plt.scatter(idx, values[idx], s=10, color='black')
        else:
            plt.scatter(idx, values[idx], s=10, color='red', marker='x')

    plt.show()
    plt.close()


def plot_ListFloat_y(ListFloat: list[float], isShow: bool = True, SaveFilePath: Optional[str] = None, title: str = None) -> None:
    """绘制 ListFloat 对象的时间序列图"""
    values = ListFloat
    datetimes = range(len(ListFloat))  # 使用数据长度生成简单的序号作为 x 轴

    plt.figure(figsize=(6, 4))  # 设置图的大小，单位是英寸

    # 隐藏右边框和上边框
    ax = plt.gca()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    plt.xlabel('数据期数/期', fontproperties='SimSun', fontsize=12)  # 设置字体为宋体
    plt.ylabel('索道坐标y轴方向位移监测/m', fontproperties='SimSun', fontsize=12)  # 设置字体为宋体

    # 设置最大显示的刻度数
    plt.tight_layout()  # 自动调整子图间的间距和标签位置
    # 设置刻度朝向内部，并调整刻度与坐标轴的距离
    ax.tick_params(axis='x', direction='in', pad=10)  # pad 参数用于控制刻度与坐标轴的距离
    ax.tick_params(axis='y', direction='in', pad=10)
    
    # 绘制线条和散点，设置颜色为黑色
    plt.plot(datetimes, values, color='black')
    plt.scatter(datetimes, values, s=10, color='black')

    if SaveFilePath is not None:
        plt.savefig(SaveFilePath)
    elif isShow:
        plt.show()
    plt.close()


def plot_points_with_markeridx(x_points: list[float], y_points: list[float], title: str = None, to_marker_idx: list[int] = []):
    # Convert lists to numpy arrays
    y_points = np.array(y_points)
    
    plt.figure(figsize=(6, 4))  # 设置图的大小，单位是英寸
    plt.xlabel('索道坐标x轴方向位移监测/m')  # 设置x轴标签
    plt.ylabel('索道坐标y轴方向位移监测/m')  # 设置y轴标签
    
    # 绘制正常点的散点图
    for idx, point in enumerate(x_points):
        if idx not in to_marker_idx:
            plt.scatter(x_points[idx], y_points[idx], color='blue', marker='o', s=20)  
    
    # 收集异常点的位置
    exception_points_x = []
    exception_points_y = []
    for idx in to_marker_idx:
        if 0 <= idx < len(x_points) and 0 <= idx < len(y_points):
            exception_points_x.append(x_points[idx])
            exception_points_y.append(y_points[idx])
    
    # 绘制异常点
    if exception_points_x and exception_points_y:
        plt.scatter(exception_points_x, exception_points_y, color='red', marker='x', s=20)
    
    # 隐藏右边框和上边框
    ax = plt.gca()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)  # 隐藏下边框
    ax.spines['left'].set_visible(False)    # 隐藏左边框
    
    # 添加箭头，指向坐标轴的正方向
    ax.annotate('', xy=(1, 0.001), xytext=(0, 0.001),
                arrowprops=dict(arrowstyle='->', lw=1, color='black'),
                xycoords='axes fraction', textcoords='axes fraction')
    ax.annotate('', xy=(0.001, 1), xytext=(0.001, 0),
                arrowprops=dict(arrowstyle='->', lw=1, color='black'),
                xycoords='axes fraction', textcoords='axes fraction')
    
    # 设置刻度朝向内部，并调整刻度与坐标轴的距离
    ax.tick_params(axis='x', direction='in', pad=10)  # pad 参数用于控制刻度与坐标轴的距离
    ax.tick_params(axis='y', direction='in', pad=10)
    
    # 设置标题
    if title is None:
        plt.suptitle('时间序列数据', y=1.0)  # 设置标题，默认为'时间序列数据'，y参数用于调整标题在垂直方向上的位置
    else:
        plt.suptitle(title, y=1.0)  # 设置标题为传入的参数title，y参数用于调整标题在垂直方向上的位置
    
    # 手动添加图例
    # plt.legend(['正常值', '异常值'], loc='upper right')  # 在这里手动指定图例的标签和位置
    
    plt.tight_layout()  # 自动调整子图间的间距和标签位置
    plt.show()

def plot_points_with_markeridx(x_points: list[float], y_points: list[float], title: str = None, to_marker_idx: list[int] = []):
    plt.figure(figsize=(14.4, 9.6))  # 设置图的大小，单位是英寸
    
    # 绘制散点图
    plt.scatter(x_points, y_points)
    
    # 标记指定索引处的数据点
    if to_marker_idx:
        for idx in to_marker_idx:
            if 0 <= idx < len(x_points) and 0 <= idx < len(y_points):
                plt.scatter(x_points[idx], y_points[idx], color='red', marker='o', s=100, label=f'Index {idx}')

    # 绘制x轴和y轴
    axhline = plt.axhline(0, color='black', linewidth=1, zorder=1)  # 绘制x轴，黑色，线宽1，zorder设置在最上层
    axvline = plt.axvline(0, color='black', linewidth=1, zorder=1)  # 绘制y轴，黑色，线宽1，zorder设置在最上层
    
    # 设置x轴和y轴的刻度放置方式为直接放在轴上
    plt.tick_params(axis='x', direction='in')
    plt.tick_params(axis='y', direction='in')
    
    plt.xlabel('X')  # 设置x轴标签
    plt.ylabel('Y')  # 设置y轴标签
    
    if title is None:
        plt.title('时间序列数据')  # 设置标题，默认为'时间序列数据'
    else:
        plt.title(title)  # 设置标题为传入的参数title
    
    # 获取当前的坐标轴对象
    ax = plt.gca()
    
    # 手动设置刻度标签的位置
    ax.xaxis.set_label_coords(.02, 0.5)  # 设置x轴标签的位置
    ax.yaxis.set_label_coords(0.5, 1.02)  # 设置y轴标签的位置
    
    plt.tight_layout()  # 自动调整子图间的间距和标签位置
    plt.show()

def plot_ListFloat_Compare(ListFloat1: list[float], ListFloat2: list[float], SaveFilePath: Optional[str] = None, title: str = None) -> None:
    """绘制两个ListFloat对象的时间序列图"""
    calculate_similarity(ListFloat1, ListFloat2)
    # 以个数索引序号为 x 轴
    x_values = range(len(ListFloat1))
    # 修改标签和标题的文本为中文
    plt.figure(figsize=(6, 4)) # 单位是英寸
    plt.xlabel('索引')
    plt.ylabel('数值')
    if title is None:
        plt.title('时间序列数据')
    else:
        plt.title(f'{title}')

    # 设置日期格式化器和日期刻度定位器
    date_locator = mdates.AutoDateLocator()  # 自动选择刻度间隔
    plt.gca().xaxis.set_major_locator(date_locator)
    
    # 设置最大显示的刻度数
    plt.tight_layout()  # 自动调整子图间的间距和标签位置

    plt.plot(x_values, ListFloat1, label='ListFloat1')
    plt.plot(x_values, ListFloat2, label='ListFloat2')

    plt.legend()  # 显示图例

    if SaveFilePath is not None:
        plt.savefig(SaveFilePath)
    else:
        plt.show()
    plt.close()


def plot_ListFloat_Compare_in_diff_dt(ListFloat1: List[float], dt_list1: List[datetime], ListFloat2: List[float], dt_list2: List[datetime]) -> None:
    """Plot ListFloat1 and ListFloat2 based on their datetime lists and compute similarity."""
    aligned_list1 = []
    aligned_list2 = []
    
    idx1 = 0
    idx2 = 0
    
    while idx1 < len(dt_list1) and idx2 < len(dt_list2):
        if dt_list1[idx1] == dt_list2[idx2]:
            aligned_list1.append(ListFloat1[idx1])
            aligned_list2.append(ListFloat2[idx2])
            idx1 += 1
            idx2 += 1
        elif dt_list1[idx1] < dt_list2[idx2]:
            idx1 += 1
        else:
            idx2 += 1
    plot_ListFloat_Compare(aligned_list1, aligned_list2, title='Comparison of ListFloat1 and ListFloat2')

def plot_ListFloat_with_markeridx(ListFloat: list[float], isShow: bool = False, SaveFilePath: Optional[str] = None, title: str = None, to_marker_idx: list[int] = []) -> None:
    """绘制 ListFloat 对象的时间序列图，并标记指定索引处的数据点"""
    values = ListFloat
    datetimes = range(len(ListFloat))  # 使用数据长度生成简单的序号作为 x 轴

    plt.figure(figsize=(14.4, 9.6))  # 设置图像大小，单位是英寸
    plt.xlabel('日期')
    plt.ylabel('数值')
    if title is None:
        plt.title('时间序列数据')
    else:
        plt.title(title)

    plt.tight_layout()  # 自动调整子图间的间距和标签位置
    plt.plot(datetimes, values)

    # 标记指定索引处的数据点
    if to_marker_idx:
        for idx in to_marker_idx:
            if 0 <= idx < len(values):
                plt.scatter(idx, values[idx], color='red', marker='o', s=100, label=f'Index {idx}')

    if SaveFilePath is not None:
        plt.savefig(SaveFilePath)
    elif isShow:
        plt.legend()
        plt.show()

    plt.close()

def plot_float_with_mididx(data: list[float], mididx: int):
    # 确保 mididx 不超过索引范围
    if mididx < 0 or mididx >= len(data):
        print("Error: mididx is out of range.")
        return
    
    # 确定 startidx 和 endidx
    startidx = max(mididx - 3, 0)
    endidx = min(mididx + 3, len(data))

    values = data[startidx: endidx+1]
    plt.figure(figsize=(14.4, 9.6)) # 单位是英寸
    plt.xlabel('idx')
    plt.ylabel('数值')
    plt.title(f'{startidx}-{endidx}索引数据可视化')
    
    plt.plot(range(len(values)), values)
    # 设置最大显示的刻度数
    plt.gcf().autofmt_xdate()  # 旋转日期标签以避免重叠
    plt.tight_layout()  # 自动调整子图间的间距和标签位置

    plt.show()
    plt.close()

def convert_coordinates(lat: float, lon: float) -> tuple[float, float]:
    # 定义原始坐标系（WGS84）
    from_proj = pyproj.Proj(proj='latlong', datum='WGS84')

    # 定义目标投影坐标系（例如，Transverse Mercator投影）
    to_proj_params = {
        'proj': 'tmerc',
        'lat_0': 0,
        'lon_0': 117,
        'k': 1,
        'x_0': 500000,
        'y_0': 0,
        'ellps': 'WGS84',
        'units': 'm'
    }
    to_proj = pyproj.Proj(to_proj_params)

    # 执行坐标转换
    easting, northing = pyproj.transform(from_proj, to_proj, lon, lat)

    return easting, northing

def convert_latlon_coordinates(lat_list: List[float], lon_list: List[float]) -> tuple[List[float], List[float]]:
    # 转换后的时序数据列表
    converted_lat_tsd = []
    converted_lon_tsd = []
    
    for lat, lon in zip(lat_list, lon_list):
        # 对纬度和经度进行坐标转换
        converted_lat, converted_lon = convert_coordinates(lat, lon)
        
        # 创建新的 ListFloat 对象并添加到列表中
        converted_lat_tsd.append(converted_lat)
        converted_lon_tsd.append(converted_lon)
    
    return converted_lat_tsd, converted_lon_tsd
# endregion
# region 基础统计分析
def calculate_mean(ListFloat: list[float]) -> float:
    """计算ListFloat对象的平均值"""
    total = sum(ListFloat)
    mean = total / len(ListFloat)
    return mean


def calculate_median(ListFloat: list[float]) -> float:
    """计算ListFloat对象的中位数"""
    sorted_data = sorted(ListFloat, key=lambda data: data)
    n = len(sorted_data)
    if n % 2 == 0:
        median = (sorted_data[n // 2 - 1] + sorted_data[n // 2]) / 2
    else:
        median = sorted_data[n // 2]
    return median


def calculate_variance(ListFloat: list[float]) -> float:
    """计算 ListFloat 对象的方差"""
    mean = calculate_mean(ListFloat)
    squared_diff = [(value - mean) ** 2 for value in ListFloat]
    variance = sum(squared_diff) / len(ListFloat)
    return variance


def calculate_standard_deviation(ListFloat: list[float]) -> float:
    """计算 ListFloat 对象的标准差"""
    variance = calculate_variance(ListFloat)
    standard_deviation = math.sqrt(variance)
    return standard_deviation


def calculate_change_rate(ListFloat: list[float]) -> list[float]:
    """计算 ListFloat 对象的变化率"""
    change_rates = []
    for i in range(1, len(ListFloat)):
        current_value = ListFloat[i]
        previous_value = ListFloat[i-1]
        change_rate = (current_value - previous_value) / previous_value
        change_rates.append(change_rate)
    return change_rates


def calculate_trend_line_residuals(data: list[float], trend_line: np.ndarray) -> np.ndarray:
    """计算残差"""
    residuals = np.array(data) - trend_line
    return residuals


def calculate_and_print_static(data: list[float]) -> None:
    mean = calculate_mean(data)
    median = calculate_median(data)
    variance = calculate_variance(data)
    standard_deviation = calculate_standard_deviation(data)
    print(f"mean = {mean}")
    print(f"median = {median}")
    print(f"variance = {variance}")
    print(f"standard_deviation = {standard_deviation}")
    

def plot_residuals(residuals: np.ndarray, SaveFilePath: Optional[str] = None) -> None:
    """绘制残差图"""
    plt.figure(figsize=(25.6, 14.4))
    plt.scatter(range(len(residuals)), residuals, color='blue', alpha=0.5)
    plt.axhline(y=0, color='red', linestyle='--')
    plt.title('残差图')
    plt.xlabel('数据点')
    plt.ylabel('残差')
    plt.grid(True)
    if SaveFilePath is not None:
        plt.savefig(SaveFilePath)
    else:
        plt.show()
    plt.close()


def calculate_r_squared(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """计算 R-squared (R方)"""
    mean_y_true = np.mean(y_true)
    total_sum_squares = np.sum((y_true - mean_y_true) ** 2)
    residual_sum_squares = np.sum((y_true - y_pred) ** 2)
    r_squared = 1 - (residual_sum_squares / total_sum_squares)
    return r_squared


def calculate_distance(x1, y1, x2, y2):
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return distance

def calculate_bearing(x, y):
    # 计算角度（弧度）
    angle_radians = math.atan2(y, x)
    # 将弧度转换为角度
    angle_degrees = math.degrees(angle_radians)
    # 确保角度在 [0, 360) 范围内
    bearing = (angle_degrees + 360) % 360
    return bearing


def calculate_durbin_watson(residuals: np.ndarray) -> float:
    """手动计算德宾沃森统计量"""
    diff_residuals = np.diff(residuals)  # 计算残差的差分
    durbin_watson_statistic = np.sum(diff_residuals ** 2) / np.sum(residuals ** 2)
    return durbin_watson_statistic
# endregion
# region 拟合多项式趋势线
def fit_polynomial_trend(data: list[float], degree: int = 3) -> np.ndarray:
    """拟合多项式趋势线"""
    x = range(len(data))
    coefficients = np.polyfit(x, data, degree)
    trend_line = np.polyval(coefficients, x)
    return trend_line


def calculate_trend_line_r_squared(data: list[float], trend_line: np.ndarray) -> float:
    """计算趋势线拟合度"""
    y_mean = np.mean(data)
    
    # 计算总平方和 TSS
    tss = np.sum((data - y_mean) ** 2)
    
    # 计算残差平方和 ESS
    ess = np.sum((data - trend_line) ** 2)
    
    # 计算 R 方值
    r_squared = 1 - (ess / tss)
    
    return r_squared


def plot_trend_line_residuals(data: list[float], residuals: np.ndarray, SaveFilePath: Optional[str] = None) -> None:
    """绘制残差图"""
    x = range(len(data))
    plt.scatter(x, residuals)
    plt.xlabel('数据')
    plt.ylabel('残差')
    plt.title('残差图')
    if SaveFilePath is not None:
        plt.savefig(SaveFilePath)
    else:
        plt.show()
    plt.close()


def print_trend_line_residuals_Statistics(residuals: np.ndarray) -> None:
    """计算残差的统计指标"""
    # 计算残差的统计指标
    residual_mean = np.mean(residuals)
    residual_std = np.std(residuals)
    residual_max = np.max(residuals)
    residual_min = np.min(residuals)

    # 执行正态性检验
    _, p_value = shapiro(residuals)
    is_normal = p_value > 0.05

    print("残差统计信息:")
    print("均值:", residual_mean)
    print("标准差:", residual_std)
    print("最大值:", residual_max)
    print("最小值:", residual_min)
    print("是否正态分布:", is_normal)


def plot_change_rate(change_rates: np.ndarray, SaveFilePath: Optional[str] = None) -> None:
    """对change_rate进行绘图"""
    # 绘制图表
    plt.figure(figsize=(14.4, 9.6)) # 单位是英寸
    plt.plot(change_rates)
    plt.xlabel('索引')
    plt.ylabel('变化率')
    plt.title('变化率可视化')
    plt.grid(True)
    if SaveFilePath is not None:
        plt.savefig(SaveFilePath)  
    else:
        plt.show()
    plt.close()
    

def find_Ridge_best_degree(data: list[float]) -> None:
    """找到 Ridge 回归模型最佳的阶数"""
    x = range(len(data))
    y = data
    x = np.array(x)
    y = np.array(y)

    best_degree = None
    best_r_squared = -1  # 初始化为负数,确保能够更新
    best_mae = float('inf')  # 初始化为正无穷
    best_mape = float('inf')  # 初始化为正无穷
    best_bic = float('inf')  # 初始化为正无穷

    for degree in range(1, 21):  # 假设循环从1到21的范围
        # 创建 Polynomial 特征转换器
        polynomial_features = PolynomialFeatures(degree=degree)
        X_poly = polynomial_features.fit_transform(x.reshape(-1, 1))

        # 创建 Ridge 回归模型
        ridge = Ridge()
        ridge.fit(X_poly, y)

        # 计算预测值
        y_pred = ridge.predict(X_poly)

        # 计算 R 方值
        r_squared = r2_score(y, y_pred)

        # 计算矫正决定系数
        n = len(y)
        adjusted_r_squared = 1 - (1 - r_squared) * (n - 1) / (n - degree - 1)

        # 计算误差平方和 SSE
        sse = np.sum((y - y_pred) ** 2)

         # 计算均方误差 MSE
        mse = mean_squared_error(y, y_pred)

        # 计算平均绝对误差 MAE
        mae = mean_absolute_error(y, y_pred)

        # 计算平均绝对百分比误差 MAPE
        mape = np.mean(np.abs((y - y_pred) / y)) * 100

        # 计算模型参数数量
        num_params = X_poly.shape[1]
        
        # 计算 AIC 值
        aic = 2 * num_params - 2 * np.log(np.sum((y - y_pred) ** 2))

        # 计算 BIC 值
        bic = n * np.log(sse / n) + num_params * np.log(n)

        print(f"Degree {degree}: R方值 = {r_squared}, 矫正R方值 = {adjusted_r_squared}, SSE = {sse},  MSE = {mse},MAE = {mae}, MAPE = {mape}, AIC = {aic}, BIC = {bic}")

        if r_squared > best_r_squared:
            best_r_squared = r_squared
            best_degree = degree

        if mae < best_mae:
            best_mae = mae

        if mape < best_mape:
            best_mape = mape

        if bic < best_bic:
            best_bic = bic

    print(f"最佳Degree: {best_degree}, 对应的最佳R方值: {best_r_squared}, 最佳MAE: {best_mae}, 最佳MAPE: {best_mape}, 最佳BIC: {best_bic}")
    return best_degree, best_r_squared


def find_Lasso_best_degree(data: list[float]) -> None:
    """找到 Lasso 回归模型最佳的阶数"""
    x = range(len(data))
    y = data
    x=np.array(x)
    y=np.array(y)

    best_degree = None
    best_r_squared = -1  # 初始化为负数,确保能够更新

    for degree in range(1, 21):  # 假设循环从1到21的范围
        # 创建 Polynomial 特征转换器
        polynomial_features = PolynomialFeatures(degree=degree)
        X_poly = polynomial_features.fit_transform(x.reshape(-1, 1))

        # 创建 Lasso 回归模型
        lasso = Lasso()
        lasso.fit(X_poly, y)

        # 计算预测值
        y_pred = lasso.predict(X_poly)

        # 计算 R 方值
        r_squared = r2_score(y, y_pred)

        print(f"Degree {degree}: R方值 = {r_squared}")

        if r_squared > best_r_squared:
            best_r_squared = r_squared
            best_degree = degree

    print(f"最佳Degree: {best_degree}, 对应的最佳R方值: {best_r_squared}")
    return best_degree, best_r_squared


def find_Ridge_best_degree_MSE(data: List[float]) -> tuple[int, float]:
    """找到 Ridge 回归模型最佳的阶数"""
    x = range(len(data))
    y = data
    x=np.array(x)
    y=np.array(y)

    best_degree = None
    best_mse = float('inf')  # 初始化为正无穷大

    for degree in range(1, 21):  # 假设循环从1到21的范围
        # 创建 Polynomial 特征转换器
        polynomial_features = PolynomialFeatures(degree=degree)
        X_poly = polynomial_features.fit_transform(x.reshape(-1, 1))

        # 创建 Ridge 回归模型
        ridge = Ridge()
        ridge.fit(X_poly, y)

        # 计算预测值
        y_pred: np.ndarray = ridge.predict(X_poly)

        # 计算 MSE 值
        mse = mean_squared_error(y, y_pred)

        print(f"Degree {degree}: MSE = {mse}")

        if mse < best_mse:
            best_mse = mse
            best_degree = degree

    print(f"最佳Degree: {best_degree}, 对应的最佳MSE值: {best_mse}")
    return best_degree, best_mse


def calculate_AIC(data: List[float], y_pred: np.ndarray, degree: int) -> float:
    """计算AIC值"""
    n = len(data)
    k = degree + 1  # 参数数量为阶数加上截距项
    mse = mean_squared_error(data, y_pred)
    likelihood = (n * math.log(2 * math.pi * mse) + n) / 2  # 根据高斯分布的似然函数计算
    AIC = 2 * k - 2 * math.log(likelihood)
    return AIC


def find_best_Lasso_degree_using_AIC(data: List[float]) -> Tuple[int, float]:
    """利用AIC找到最佳的Lasso回归模型阶数"""
    x = range(len(data))
    y = data
    x = np.array(x)
    y = np.array(y)

    best_degree = None
    best_AIC = float('inf')  # 初始化为正无穷大

    for degree in range(1, 21):  # 假设循环从1到21的范围
        # 创建 Polynomial 特征转换器
        polynomial_features = PolynomialFeatures(degree=degree)
        X_poly = polynomial_features.fit_transform(x.reshape(-1, 1))

        # 创建 Lasso 回归模型
        lasso = Lasso()
        lasso.fit(X_poly, y)

        # 计算预测值
        y_pred = lasso.predict(X_poly)

        # 计算 AIC 值
        AIC = calculate_AIC(data, y_pred, degree)

        print(f"Degree {degree}: AIC = {AIC}")

        if AIC < best_AIC:
            best_AIC = AIC
            best_degree = degree

    print(f"最佳Degree: {best_degree}, 对应的最佳AIC值: {best_AIC}")
    return best_degree, best_AIC


def calculate_BIC(data: List[float], y_pred: np.ndarray, degree: int) -> float:
    """计算BIC值"""
    n = len(data)
    k = degree + 1  # 参数数量为阶数加上截距项
    mse = mean_squared_error(data, y_pred)
    likelihood = (n * math.log(2 * math.pi * mse) + n) / 2  # 根据高斯分布的似然函数计算
    BIC = k * math.log(n) - 2 * math.log(likelihood)
    return BIC


def find_best_Lasso_degree_using_BIC(data: List[float]) -> Tuple[int, float]:
    """利用BIC找到最佳的Lasso回归模型阶数"""
    x = range(len(data))
    y = data
    x = np.array(x)
    y = np.array(y)

    best_degree = None
    best_BIC = float('inf')  # 初始化为正无穷大

    for degree in range(1, 21):  # 假设循环从1到21的范围
        # 创建 Polynomial 特征转换器
        polynomial_features = PolynomialFeatures(degree=degree)
        X_poly = polynomial_features.fit_transform(x.reshape(-1, 1))

        # 创建 Lasso 回归模型
        lasso = Lasso()
        lasso.fit(X_poly, y)

        # 计算预测值
        y_pred = lasso.predict(X_poly)

        # 计算 BIC 值
        BIC = calculate_BIC(data, y_pred, degree)

        print(f"Degree {degree}: BIC = {BIC}")

        if BIC < best_BIC:
            best_BIC = BIC
            best_degree = degree

    print(f"最佳Degree: {best_degree}, 对应的最佳BIC值: {best_BIC}")
    return best_degree, best_BIC


def fit_Ridge_polynomial_trend(data: list[float], degree: int=11, alpha: float=1.0) -> np.ndarray:
    """使用岭回归拟合多项式趋势线"""
    x = np.array(range(len(data)))
    y = np.array(data)

    # 创建 Polynomial 特征转换器
    polynomial_features = PolynomialFeatures(degree=degree)
    X_poly = polynomial_features.fit_transform(x.reshape(-1, 1))

    # 创建岭回归模型
    ridge = Ridge(alpha=alpha)
    ridge.fit(X_poly, y)

    # 预测拟合结果
    y_pred = ridge.predict(X_poly)

    return y_pred


def fit_Lasso_polynomial_trend(data: list[float], degree: int=11, alpha: float=1.0) -> np.ndarray:
    """使用Lasso回归拟合多项式趋势线"""
    x = np.array(range(len(data)))
    y = np.array(data)

    # 创建 Polynomial 特征转换器
    polynomial_features = PolynomialFeatures(degree=degree)
    X_poly = polynomial_features.fit_transform(x.reshape(-1, 1))

    # 创建Lasso回归模型
    lasso = Lasso(alpha=alpha)
    lasso.fit(X_poly, y)

    # 预测拟合结果
    y_pred = lasso.predict(X_poly)

    return y_pred


def fit_ElasticNet_polynomial_trend(data: list[float], degree: int=11, alpha: float=1.0, l1_ratio: float=0.5) -> np.ndarray:
    """使用弹性网络回归拟合多项式趋势线"""
    x = np.array(range(len(data)))
    y = np.array(data)

    # 创建 Polynomial 特征转换器
    polynomial_features = PolynomialFeatures(degree=degree)
    X_poly = polynomial_features.fit_transform(x.reshape(-1, 1))

    # 创建弹性网络回归模型
    elastic_net = ElasticNet(alpha=alpha, l1_ratio=l1_ratio)
    elastic_net.fit(X_poly, y)

    # 预测拟合结果
    y_pred = elastic_net.predict(X_poly)

    return y_pred


def evaluate_predictions(ridge_pred: np.ndarray, lasso_pred: np.ndarray, elastic_pred: np.ndarray, polynomial_pred: np.ndarray, data: list[float],degree: int) -> None:
    """评估 Ridge、Lasso、ElasticNet 和多项式拟合的预测结果拟合效果"""
    y_true = data
    # 计算 R方值
    ridge_r2 = r2_score(y_true, ridge_pred)
    lasso_r2 = r2_score(y_true, lasso_pred)
    elastic_r2 = r2_score(y_true, elastic_pred)
    polynomial_r2 = r2_score(y_true, polynomial_pred)

    # 计算均方误差(MSE)
    ridge_mse = mean_squared_error(y_true, ridge_pred)
    lasso_mse = mean_squared_error(y_true, lasso_pred)
    elastic_mse = mean_squared_error(y_true, elastic_pred)
    polynomial_mse = mean_squared_error(y_true, polynomial_pred)

    # 计算模型参数数量  
    num_parameters_ridge = degree 
    num_parameters_lasso = degree 
    num_parameters_elastic = degree 
    num_parameters_polynomial = degree  # 多项式拟合的参数数量为多项式次数 + 1

    # 计算 AIC 和 BIC
    aic_ridge = calculate_AIC(data, ridge_pred, num_parameters_ridge)
    bic_ridge = calculate_BIC(data, ridge_pred, num_parameters_ridge)
    aic_lasso = calculate_AIC(data, lasso_pred, num_parameters_lasso)
    bic_lasso = calculate_BIC(data, lasso_pred, num_parameters_lasso)
    aic_elastic = calculate_AIC(data, elastic_pred, num_parameters_elastic)
    bic_elastic = calculate_BIC(data, elastic_pred, num_parameters_elastic)
    aic_polynomial = calculate_AIC(data, polynomial_pred, num_parameters_polynomial)
    bic_polynomial = calculate_BIC(data, polynomial_pred, num_parameters_polynomial)

    # 打印结果
    print("Ridge回归模型的评估结果:")
    print("R方值: ", ridge_r2)
    print("均方误差 (MSE): ", ridge_mse)
    print("AIC: ", aic_ridge)
    print("BIC: ", bic_ridge)

    print("\nLasso回归模型的评估结果:")
    print("R方值: ", lasso_r2)
    print("均方误差 (MSE): ", lasso_mse)
    print("AIC: ", aic_lasso)
    print("BIC: ", bic_lasso)

    print("\nElasticNet回归模型的评估结果:")
    print("R方值: ", elastic_r2)
    print("均方误差 (MSE): ", elastic_mse)
    print("AIC: ", aic_elastic)
    print("BIC: ", bic_elastic)

    print("\n多项式回归模型的评估结果:")
    print("R方值: ", polynomial_r2)
    print("均方误差 (MSE): ", polynomial_mse)
    print("AIC: ", aic_polynomial)
    print("BIC: ", bic_polynomial)

    # 比较 R方值
    max_r2 = max(ridge_r2, lasso_r2, elastic_r2, polynomial_r2)
    if max_r2 == ridge_r2:
        print("\nRidge回归模型的拟合效果最好")
    elif max_r2 == lasso_r2:
        print("\nLasso回归模型的拟合效果最好")
    elif max_r2 == elastic_r2:
        print("\nElasticNet回归模型的拟合效果最好")
    else:
        print("\n多项式回归模型的拟合效果最好")

    # 比较 AIC
    min_aic = min(aic_ridge, aic_lasso, aic_elastic, aic_polynomial)
    if min_aic == aic_ridge:
        print("Ridge回归模型的拟合效果最好 (最小AIC)")
    elif min_aic == aic_lasso:
        print("Lasso回归模型的拟合效果最好 (最小AIC)")
    elif min_aic == aic_elastic:
        print("ElasticNet回归模型的拟合效果最好 (最小AIC)")
    else:
        print("多项式回归模型的拟合效果最好 (最小AIC)")

    # 比较 BIC
    min_bic = min(bic_ridge, bic_lasso, bic_elastic, bic_polynomial)
    if min_bic == bic_ridge:
        print("Ridge回归模型的拟合效果最好 (最小BIC)")
    elif min_bic == bic_lasso:
        print("Lasso回归模型的拟合效果最好 (最小BIC)")
    elif min_bic == bic_elastic:
        print("ElasticNet回归模型的拟合效果最好 (最小BIC)")
    else:
        print("多项式回归模型的拟合效果最好 (最小BIC)")


def plot_polynomial_trend(data: list[float], y_pred: Union[List[float], np.ndarray], SaveFilePath: Optional[str] = None) -> None:
    """绘制多项式趋势线"""
    # 提取日期时间和数值信息
    x = range(len(data))
    y = data

    # 修改标签和标题的文本为中文
    plt.figure(figsize=(14.4, 9.6)) # 设置图形大小
    plt.xlabel('索引')
    plt.ylabel('数值')
    plt.title('多项式趋势线')

    # 设置日期格式化器和日期刻度定位器
    date_locator = mdates.AutoDateLocator()  # 自动选择刻度间隔
    plt.gca().xaxis.set_major_locator(date_locator)
    
    # 设置最大显示的刻度数
    plt.gcf().autofmt_xdate()  # 旋转日期标签以避免重叠
    plt.tight_layout()  # 自动调整子图间的间距和标签位置

    # 绘制折线图
    plt.plot(x, y, label='原始数据', color='gray')
    plt.plot(x, y_pred, label='多项式趋势线', color='r')

    plt.legend()  # 添加图例
    if SaveFilePath is not None:
        plt.savefig(SaveFilePath)
    else:
        plt.show()
    plt.close()


def visualize_predictions(ListFloat: list[float], ridge_pred: np.ndarray, lasso_pred: np.ndarray, elastic_pred: np.ndarray, polynomial_pred: np.ndarray, SaveFilePath: str = None) -> None:
    x = range(len(ListFloat))
    y_true = np.array(ListFloat)

    plt.figure(figsize=(25.6, 14.4))
    plt.plot(x, y_true, color='blue', label='真实数据', alpha=0.5)
    plt.plot(x, ridge_pred, color='red', label='岭回归', linewidth=2)
    plt.plot(x, lasso_pred, color='green', label='Lasso回归', linewidth=2)
    plt.plot(x, elastic_pred, color='orange', label='弹性网络回归', linewidth=2)
    plt.plot(x, polynomial_pred, color='purple', label='多项式拟合', linewidth=2)

    plt.title('多项式趋势回归')
    plt.xlabel('时间')
    plt.ylabel('数值')
    plt.legend(loc='best')
    plt.grid(True)
    
    if SaveFilePath is not None:
        plt.savefig(SaveFilePath) 
    else:
        plt.show()
        
    plt.close()


def compare_trend_lines(ridge_pred: np.ndarray, lasso_pred: np.ndarray, elastic_pred: np.ndarray, polynomial_pred: np.ndarray) -> None:
    # 计算欧几里得距离
    euclidean_distances = {
        ('ridge', 'lasso'): euclidean(ridge_pred, lasso_pred),
        ('ridge', 'elastic'): euclidean(ridge_pred, elastic_pred),
        ('ridge', 'polynomial'): euclidean(ridge_pred, polynomial_pred),
        ('lasso', 'elastic'): euclidean(lasso_pred, elastic_pred),
        ('lasso', 'polynomial'): euclidean(lasso_pred, polynomial_pred),
        ('elastic', 'polynomial'): euclidean(elastic_pred, polynomial_pred)
    }

    # 计算皮尔逊相关系数
    pearson_correlations = {
        ('ridge', 'lasso'): pearsonr(ridge_pred, lasso_pred)[0],
        ('ridge', 'elastic'): pearsonr(ridge_pred, elastic_pred)[0],
        ('ridge', 'polynomial'): pearsonr(ridge_pred, polynomial_pred)[0],
        ('lasso', 'elastic'): pearsonr(lasso_pred, elastic_pred)[0],
        ('lasso', 'polynomial'): pearsonr(lasso_pred, polynomial_pred)[0],
        ('elastic', 'polynomial'): pearsonr(elastic_pred, polynomial_pred)[0]
    }

    # 计算ANOVA
    f_statistic, p_value = f_oneway(ridge_pred, lasso_pred, elastic_pred, polynomial_pred)

    return euclidean_distances, pearson_correlations, f_statistic, p_value


def find_Ridge_best_degree_without_print(data:list[float]) -> int:
    """找到 Ridge 回归模型最佳的阶数"""
    x = range(len(data))
    y = data
    x = np.array(x)
    y = np.array(y)

    best_degree = None
    best_bic = float('inf')  # 初始化为正无穷

    for degree in range(1, 16):  # 假设循环从1到21的范围
        # 创建 Polynomial 特征转换器
        polynomial_features = PolynomialFeatures(degree=degree)
        X_poly = polynomial_features.fit_transform(x.reshape(-1, 1))

        # 创建 Ridge 回归模型
        ridge = Ridge()
        ridge.fit(X_poly, y)

        # 计算预测值
        y_pred = ridge.predict(X_poly)

        # 计算矫正决定系数
        n = len(y)

        # 计算误差平方和 SSE
        sse = np.sum((y - y_pred) ** 2)

        # 计算模型参数数量
        num_params = X_poly.shape[1]
        
        # 计算 AIC 值

        # 计算 BIC 值
        bic = n * np.log(sse / n) + num_params * np.log(n)

        
        # 更新最佳degree和对应的评价指标
        if bic < best_bic:
            best_degree = degree
            best_bic = bic

    return best_degree
# endregion
# region 频域分析
def fourier_transform(ListFloat: List[float]) -> np.ndarray:
    """对ListFloat对象进行傅里叶变换"""
    transformed_values = np.fft.fft(ListFloat)
    return transformed_values

def extract_frequency_features(transformed_values: np.ndarray, sample_rate: int) -> dict[str, np.ndarray]:
    """
    从傅里叶变换结果中提取频域特征
    输入参数:
    - transformed_values: 傅里叶变换结果
    - sample_rate: 采样率(每秒钟的样本数)
    返回值:
    - frequency_features: 提取的频域特征
    """
    # 获取频率轴
    freqs = np.fft.fftfreq(len(transformed_values), d=1/sample_rate)

    # 计算频域特征
    # 清除零频率分量
    non_zero_indices = np.where(freqs != 0)[0]
    freqs = freqs[non_zero_indices]
    magnitude_spectrum = np.abs(transformed_values)[non_zero_indices]
    phase_spectrum = np.angle(transformed_values)[non_zero_indices]

    # 构造频域特征字典
    frequency_features = {
        'frequency': freqs,
        'magnitude_spectrum': magnitude_spectrum,
        'phase_spectrum': phase_spectrum
    }

    return frequency_features


def plot_frequency_features(frequency_features: dict[str, np.ndarray], SaveFilePath: str = None) -> None:
    """
    可视化频域特征
    输入参数:
    - frequency_features: 频域特征字典
    """
    freqs = frequency_features['frequency']
    magnitude_spectrum = frequency_features['magnitude_spectrum']
    phase_spectrum = frequency_features['phase_spectrum']
    plt.figure(figsize=(14.4, 9.6)) # 单位是英寸
    # 可视化幅度谱
    plt.plot(freqs, magnitude_spectrum)
    plt.title('幅度谱')
    plt.xlabel('频率')
    plt.ylabel('幅度')

    # 可视化相位谱
    plt.plot(freqs, phase_spectrum)
    plt.title('相位谱')
    plt.xlabel('频率')
    plt.ylabel('相位')
    if SaveFilePath is not None:
        plt.savefig(SaveFilePath)
    else:
        plt.show()
    plt.close()


def analyze_frequency_components(frequency_features: dict[str, np.ndarray], threshold: float = None) -> tuple[np.ndarray, np.ndarray]:
    """
    分析频率成分并查找峰值频率
    输入参数:
    - frequency_features: 频域特征字典
    - threshold: 峰值检测的阈值,可选参数,默认为None
    返回值:
    - peak_frequencies: 峰值频率
    - peak_values: 峰值对应的幅度值

    通过设置threshold参数来指定峰值检测的阈值。较大的阈值可以过滤掉小幅度的峰值。
    通过调整threshold参数的值,你可以控制检测到的峰值数量和灵敏度。进一步分析和处理这些峰值频率,可以获得关于主要频率成分的更多信息,例如频率的分布、频率的演化趋势等。
    
    threshold = None  # 可选参数,设定峰值检测的阈值,默认为None
    peak_frequencies, peak_values = analyze_frequency_components(frequency_features, threshold)

    """

    magnitude_spectrum = frequency_features['magnitude_spectrum']

    # 使用峰值检测算法查找幅度谱中的峰值
    peaks, _ = find_peaks(magnitude_spectrum, height=threshold)

    # 获取峰值对应的频率和幅度值
    peak_frequencies = frequency_features['frequency'][peaks]
    peak_values = magnitude_spectrum[peaks]

    return peak_frequencies, peak_values


def plot_frequency_components(peak_frequencies: np.ndarray, peak_values: np.ndarray, SaveFilePath: str = None) -> None:
    """
    可视化峰值频率和幅度值
    输入参数:
    - peak_frequencies: 峰值频率
    - peak_values: 峰值对应的幅度值

    peak_frequencies, peak_values = analyze_frequency_components(frequency_features, threshold)
    # 可视化峰值频率和幅度值
    plot_frequency_components(peak_frequencies, peak_values)
    """
    plt.figure(figsize=(14.4, 9.6)) # 单位是英寸
    plt.plot(peak_frequencies, peak_values, 'ro')
    plt.title('频率成分')
    plt.xlabel('频率')
    plt.ylabel('幅度')
    plt.grid(True)
    if SaveFilePath is not None:
        plt.savefig(SaveFilePath)
    else: 
        plt.show()
    plt.close()
    

def lowpass_filter(transformed_values: np.ndarray, cutoff_freq: float) -> np.ndarray:
    """
    使用低通滤波器去除高频噪声
    输入参数:
    - transformed_values: 傅里叶变换后的数据
    - cutoff_freq: 截止频率
    返回值:
    - filtered_data: 去除高频噪声后的数据
    """
    # 获取傅里叶频谱的频率轴
    freqs = np.fft.fftfreq(len(transformed_values))

    # 将高于截止频率的频谱部分设为0(去除高频噪声)
    transformed_values[np.abs(freqs) > cutoff_freq] = 0

    # 对处理后的数据进行逆傅里叶变换
    filtered_data = np.fft.ifft(transformed_values)

    return filtered_data


def highpass_filter(transformed_values: np.ndarray, cutoff_freq: float) -> np.ndarray:
    """
    使用高通滤波器去除低频趋势
    输入参数:
    - transformed_values: 傅里叶变换后的数据
    - cutoff_freq: 截止频率
    返回值:
    - filtered_data: 去除低频趋势后的数据
    """
    # 获取傅里叶频谱的频率轴
    freqs = np.fft.fftfreq(len(transformed_values))

    # 将低于截止频率的频谱部分设为0(去除低频趋势)
    transformed_values[np.abs(freqs) < cutoff_freq] = 0

    # 对处理后的数据进行逆傅里叶变换
    filtered_data = np.fft.ifft(transformed_values)

    return filtered_data


def bandpass_filter(transformed_values: np.ndarray, freq_low: float, freq_high: float) -> np.ndarray:
    """
    使用带通滤波器只保留特定频段的信号
    输入参数:
    - transformed_values: 傅里叶变换后的数据
    - freq_low: 保留频段的下限
    - freq_high: 保留频段的上限
    返回值:
    - filtered_data: 保留特定频段后的数据
    """
    # 获取傅里叶频谱的频率轴
    freqs = np.fft.fftfreq(len(transformed_values))

    # 将频率轴范围外的频率部分设为0
    transformed_values[(np.abs(freqs) < freq_low) | (np.abs(freqs) > freq_high)] = 0

    # 对处理后的数据进行逆傅里叶变换
    filtered_data = np.fft.ifft(transformed_values)

    return filtered_data


def remove_noise(transformed_values: np.ndarray, threshold: float) -> np.ndarray:
    """
    在频域中识别并去除噪声成分
    输入参数:
    - transformed_values: 傅里叶变换后的数据
    - threshold: 噪声判断阈值
    返回值:
    - filtered_data: 去除噪声成分后的数据
    """
    # 获取傅里叶频谱的振幅
    amplitudes = np.abs(transformed_values)

    # 将低于阈值的振幅部分设为0(去除噪声成分)
    transformed_values[amplitudes < threshold] = 0

    # 对处理后的数据进行逆傅里叶变换
    filtered_data = np.fft.ifft(transformed_values)

    return filtered_data


def plot_remove_low_frequency_trends_data(filtered_data: np.ndarray, SaveFilePath: str = None) -> None:
    """
    可视化去除低频趋势后的数据
    输入参数:
    - filtered_data: 去除低频趋势后的数据
    """
    plt.figure(figsize=(14.4, 9.6)) # 单位是英寸
    plt.plot(filtered_data)
    plt.title('滤波数据')
    plt.xlabel('Time')
    plt.ylabel('Amplitude')
    if SaveFilePath is not None:
        plt.savefig(SaveFilePath)
    else:
        plt.show()
    plt.close()


def plot_harmonic_frequency_distribution(peak_frequencies: List[float], SaveFilePath: Optional[str] = None) -> None:
    """
    绘制谐波频率的直方图
    输入参数:
    - peak_frequencies: 谐波频率
    """
    plt.figure(figsize=(14.4, 9.6)) # 单位是英寸
    plt.hist(peak_frequencies, bins='auto')
    plt.title('谐波频率分布')
    plt.xlabel('频率')
    plt.ylabel('频次')
    plt.grid(True)
    if SaveFilePath is not None:
        plt.savefig(SaveFilePath)
    else:
        plt.show()
    plt.close()


def plot_harmonic_frequency_bar_chart(peak_frequencies: List[float], peak_values: List[float], SaveFilePath: Optional[str] = None) -> None:
    """
    绘制谐波频率的条形图
    输入参数:
    - peak_frequencies: 谐波频率
    - peak_values: 谐波频率对应的幅度值
    """
    plt.figure(figsize=(14.4, 9.6)) # 单位是英寸
    plt.bar(peak_frequencies, peak_values)
    plt.title('谐波频率分布')
    plt.xlabel('频率')
    plt.ylabel('幅度')
    plt.grid(True)
    if SaveFilePath is not None:
        plt.savefig(SaveFilePath)
    else: 
        plt.show()
    plt.close()


def chebyshev_filter(ListFloat: List[float], cutoff_freq: float = 0.8, order: int = 4, filter_type: str = 'lowpass') -> Tuple[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
    """
    使用切比雪夫滤波器对时序数据进行滤波
    输入参数:
    - data: 时序数据的数组或列表
    - cutoff_freq: 截止频率
    - order: 滤波器的阶数(低阶数表示较为平滑的滤波)
    - filter_type: 滤波器的类型,可选参数为'lowpass', 'highpass', 'bandpass'和'bandstop'(默认为'lowpass')
    返回值:
    - filtered_data: 经过滤波处理后的数据
    - b,a: IIR滤波器的分子(b)和分母(a)多项式系数向量。output='ba'
    高通滤波
    b, a = signal.butter(8, 0.02, 'highpass')
    filtedData = signal.filtfilt(b, a, data)#data为要过滤的信号
    低通滤波
    b, a = signal.butter(8, 0.02, 'lowpass') 
    filtedData = signal.filtfilt(b, a, data)       #data为要过滤的信号
    带通滤波
    b, a = signal.butter(8, [0.02,0.8], 'bandpass')
    filtedData = signal.filtfilt(b, a, data)   #data为要过滤的信号
    """
    # 将输入转换为numpy数组
    data = np.array(ListFloat)

    # 计算滤波器的参数
    b, a = signal.cheby1(order, 0.5, cutoff_freq, btype=filter_type, analog=False, output='ba')

    # 应用滤波器
    filtered_data = signal.filtfilt(b, a, data)

    return filtered_data
# endregion
# region 移动平均
def moving_average(ListFloat: List[float], window_size: int) -> List[float]:
    """计算移动平均值"""
    n = len(ListFloat)
    moving_avg = []

    for i in range(n - window_size + 1):
        window_values = ListFloat[i : i + window_size]
        avg = sum(window_values) / window_size
        moving_avg.append(avg)

    return moving_avg


def plot_moving_average(ListFloat: List[float], window_size: int, SaveFilePath: str = None) -> None:
    """绘制移动平均线"""
    avg_values = moving_average(ListFloat, window_size)
    x = range(len(ListFloat))

    # 计算移动平均线的索引范围
    moving_idx = range(window_size // 2, len(ListFloat) - window_size // 2)

    plt.figure(figsize=(14.4, 9.6)) # 单位是英寸
    plt.plot(x, ListFloat, label="原始数据")
    plt.plot(moving_idx, avg_values, label="移动平均")
    plt.xlabel('索引')  # 指定中文标签
    plt.ylabel('数值') # 指定中文标签
    plt.title('移动平均线')  # 指定中文标签

    # 设置日期格式化器和日期刻度定位器
    date_fmt = mdates.DateFormatter("%m-%d")  # 仅显示月-日
    date_locator = mdates.DayLocator()  # 每天显示一个刻度

    plt.gca().xaxis.set_major_formatter(date_fmt)
    plt.gca().xaxis.set_major_locator(date_locator)
    plt.legend()  # 添加图例
    if SaveFilePath is not None:
        plt.savefig(SaveFilePath)
    else: 
        plt.show()
    plt.close()


def analyze_fourier_fft_freq(north_freq: np.ndarray, 
                             north_fft: np.ndarray, 
                             east_freq: np.ndarray, 
                             east_fft: np.ndarray) -> None:
    """
    函数“analyze_fourier_transform_results”用于计算和可视化北坐标和东坐标的振幅谱，并识别数据中的主要周期分量。

    :param north_freq: 北坐标数据的频率值，与傅立叶变换结果相关联。
    :type north_freq: numpy.ndarray
    :param north_fft: 北坐标数据的傅里叶变换结果，包含有关不同频率分量的幅度和相位信息。
    :type north_fft: numpy.ndarray
    :param east_freq: 东坐标数据的频率值，与傅立叶变换结果相关联。
    :type east_freq: numpy.ndarray
    :param east_fft: 东坐标数据的傅里叶变换结果，包含有关不同频率分量的幅度和相位信息。
    :type east_fft: numpy.ndarray
    
    该函数排除了零频率，并绘制了北坐标和东坐标的振幅谱图。然后，它识别出每个坐标系中的主要周期成分，并将其打印出来。
    """
    # 排除零频率
    north_amplitude_spectrum: np.ndarray = np.abs(north_fft[1:])
    east_amplitude_spectrum: np.ndarray = np.abs(east_fft[1:])
    non_zero_north_freq: np.ndarray = north_freq[1:]
    non_zero_east_freq: np.ndarray = east_freq[1:]
    
    # 计算主周期频率
    north_main_period_index: int = np.argmax(north_amplitude_spectrum)
    east_main_period_index: int = np.argmax(east_amplitude_spectrum)
    north_main_period_frequency: float = non_zero_north_freq[north_main_period_index]
    east_main_period_frequency: float = non_zero_east_freq[east_main_period_index]
    
    # 绘制频谱图
    plt.figure(figsize=(12, 6))
    plt.subplot(2, 1, 1)
    plt.plot(non_zero_north_freq, north_amplitude_spectrum, color='black', linestyle='-', linewidth=1)  # 使用灰色线条
    plt.scatter(north_main_period_frequency, north_amplitude_spectrum[north_main_period_index], color='red', marker='o', s=10)  # 添加红色标记，并设置大小为10
    plt.title(f'北坐标幅度谱 (主周期: {1 / north_main_period_frequency:.2f})')
    plt.xlabel('频率')
    plt.ylabel('幅度')
    
    plt.subplot(2, 1, 2)
    plt.plot(non_zero_east_freq, east_amplitude_spectrum, color='black', linestyle='-', linewidth=1)  # 使用灰色线条
    plt.scatter(east_main_period_frequency, east_amplitude_spectrum[east_main_period_index], color='red', marker='o', s=10)  # 添加红色标记，并设置大小为10
    plt.title(f'东坐标幅度谱 (主周期: {1 / east_main_period_frequency:.2f})')
    plt.xlabel('频率')
    plt.ylabel('幅度')
    
    plt.tight_layout()
    
    plt.show()
# endregion
# region statsmodels的运用

# endregion
# region 突变检测
def kendall_change_point_detection(input_data: List[float]) -> List[float]:
    """时序数据的kendall突变点检测"""
    n = len(input_data)
    Sk = [0]
    UFk = [0]
    s = 0
    Exp_value = [0]
    Var_value = [0]

    for i in range(1, n):
        for j in range(i):
            if input_data[i] > input_data[j]:
                s += 1
        Sk.append(s)
        Exp_value.append((i + 1) * (i + 2) / 4.0)
        Var_value.append((i + 1) * i * (2 * (i + 1) + 5) / 72.0)
        UFk.append((Sk[i] - Exp_value[i]) / math.sqrt(Var_value[i]))

    Sk2 = [0]
    UBk = [0]
    UBk2 = [0]
    s2 = 0
    Exp_value2 = [0]
    Var_value2 = [0]
    input_data_t = list(reversed(input_data))

    for i in range(1, n):
        for j in range(i):
            if input_data_t[i] > input_data_t[j]:
                s2 += 1
        Sk2.append(s2)
        Exp_value2.append((i + 1) * (i + 2) / 4.0)
        Var_value2.append((i + 1) * i * (2 * (i + 1) + 5) / 72.0)
        UBk.append((Sk2[i] - Exp_value2[i]) / math.sqrt(Var_value2[i]))
        UBk2.append(-UBk[i])

    UBkT = list(reversed(UBk2))
    diff = [x - y for x, y in zip(UFk, UBkT)]
    K = []

    for k in range(1, n):
        if diff[k - 1] * diff[k] < 0:
            K.append(k)

    return K


def pettitt_change_point_detection(data: List[float]) -> Tuple[int, float]:
    """
    使用Pettitt突变检测方法检测时间序列数据中的突变点。

    :param data: ListFloat 类型的列表,包含 value 和 datetime 属性。
    :return: 突变点的位置和统计量。
    """
    # 提取 value 值
    values = data

    # 计算累积和
    cumulative_sum = np.cumsum(values)

    # 突变点的位置和统计量
    change_point = 0
    max_test_statistic = 0

    n = len(values)

    for i in range(n):
        current_statistic = abs(cumulative_sum[i] - cumulative_sum[n-i-1])
        if current_statistic > max_test_statistic:
            max_test_statistic = current_statistic
            change_point = i

    return change_point, max_test_statistic


def cusum(data: list[float], threshold: float=1) -> List[float]:
    """
    计算CUSUM
    设置阈值,根据具体情况调整
    """
    # 计算CUSUM
    cusum_values = [0]  # 起始值为0
   
    for i in range(1, len(data)):
        diff = data[i] - data[i-1]
        cusum_values.append(max(0, cusum_values[i-1] + diff - threshold))
    
    return cusum_values


def cusum_total(data: list[float], threshold: float=1) -> float:
    """
    计算整段数据的CUSUM值
    """
    cusum_value = 0  # 初始CUSUM值为0

    for i in range(1, len(data)):
        diff = data[i] - data[i-1]
        cusum_value = max(0, cusum_value + diff - threshold)
    
    return cusum_value

def cusum_z_transform(data: list[float], threshold: float=1) -> List[float]:
    """
    计算CUSUM
    # 设置阈值,根据具体情况调整
    """
    # 计算CUSUM
    cusum_values = [0]  # 起始值为0

    for i in range(1, len(data)):
        diff = data[i].value - data[i-1].value
        cusum_values.append(max(0, cusum_values[i-1] + diff - threshold))

    # 对CUSUM序列进行Z变换
    cusum_array = np.array(cusum_values)
    cusum_mean = np.mean(cusum_array)
    cusum_std = np.std(cusum_array)
    z_transformed = (cusum_array - cusum_mean) / cusum_std

    return z_transformed


def plot_cusum(data: list[float], cusum_values: List[float], SaveFilePath: Optional[str] = None) -> None:
    """绘制CUSUM"""
    # 绘制CUSUM
    x = np.arange(len(data))
    y = data
    plt.figure(figsize=(14.4, 9.6)) # 单位是英寸
    plt.plot(x, y, label='时序数据')
    plt.plot(x, cusum_values, label='CUSUM')
    plt.xlabel('时间步')
    plt.ylabel('数值')
    plt.legend()
    plt.title('时序数据的CUSUM')
    if SaveFilePath is not None:
        plt.savefig(SaveFilePath)
    else: 
        plt.show()
    plt.close()


def plot_cusum_in_threshold(cusum: List[float], threshold: float, SaveFilePath: Optional[str] = None) -> None:
    plt.plot(cusum)
    plt.axhline(threshold, color='red', linestyle='--')  # Add horizontal line at the threshold
    plt.xlabel('时间点')
    plt.ylabel('CUSUM')
    plt.title('CUSUM控制图')
    if SaveFilePath is not None:
        plt.savefig(SaveFilePath)
    else: 
        plt.show()
    plt.close()


def determine_threshold(cusum: List[float]) -> float:
    std = np.std(cusum)
    threshold = 3 * std  # Adjust the multiplier as needed
    return threshold


def detect_cusum_threshold(cusum_values, threshold):
    """
    对cusum_values设置阈值,并将超过阈值的值作为变化点
    """
    change_points = []
    for i, value in enumerate(cusum_values):
        if value > threshold:
            change_points.append(i)
    
    return change_points


def detect_cusum_diff_threshold(cusum_values: List[float], threshold: float) -> List[int]:
    """
    计算相邻CUSUM值的差异diff,如果差异超过了设定的阈值threshold
    """
    change_points = []
  
    for i in range(1, len(cusum_values)):
        diff = cusum_values[i] - cusum_values[i-1]
        if diff > threshold:
            change_points.append(i)
    
    return change_points


def detect_cusum_window(cusum_values: List[float], threshold: float, window_size: int) -> List[int]:
    """
    滑动窗口来检测连续的CUSUM值
    使用启发式规则:一些经验法则建议窗口大小选择为数据点总数的一定比例,例如窗口大小为数据总点数的1/10或1/20。
    统计方法:可以根据数据的统计特征来选择阈值。例如,基于数据的标准差、平均值等来设置阈值,使得超过阈值的CUSUM值被认为是结构性变化点。
    可视化和交互:可以通过可视化CUSUM图形,并与领域专家或数据分析人员进行交互来优化阈值的选择。观察图形中的结构性变化,根据专家意见或实际需求来调整阈值。
    """
    change_points = []

    for i in range(window_size, len(cusum_values)):
        sub_cusum = cusum_values[i-window_size:i+1]

        if all(value >= threshold for value in sub_cusum):
            change_points.append(i)
    
    return change_points


def calculate_rolling_std(data: list[float], window_size: int) -> List[float]:
    """滚动标准差来检测波动性的变动"""
    values = data  # 提取时序数据中的值
    rolling_std = np.std(values[:window_size])  # 初始窗口的标准差
    std_values = [rolling_std]

    for i in range(window_size, len(values)):
        window_values = values[i-window_size+1:i+1]
        rolling_std = np.std(window_values)
        std_values.append(rolling_std)
    
    return std_values


def calculate_cumulative_std(data: list[float]) -> List[float]:
    """计算每个点到data[0:n]的标准差"""
    values = data  # 提取时序数据中的值
    std_values = []

    for i in range(1, len(values) + 1):
        std_values.append(np.std(values[:i]))

    return std_values


def plot_std_values(std_values: List[float], SaveFilePath: Optional[str] = None) -> None:
    x = range(len(std_values))  # x轴为数据点的索引
    y = std_values  # y轴为滚动标准差的值
    plt.figure(figsize=(14.4, 9.6)) # 单位是英寸
    plt.plot(x, y)
    plt.xlabel('数据点')  # x轴标签
    plt.ylabel('标准差')  # y轴标签
    plt.title('滚动标准差')  # 图表标题
    if SaveFilePath is not None:
        plt.savefig(SaveFilePath)
    else: 
        plt.show()
    plt.close()


def calculate_cumulative_std_with_break(data: list[float], threshold: float = 1.5) -> Tuple[List[float], List[int]]:
    """计算每个点到data[0:n]的标准差,如果超过阈值则隔断,并记录隔断点的索引位置"""
    std_values = []
    break_points = []  # 记录隔断点的索引位置
    start_index = 0  # 开始计算的索引

    for i in range(1, len(data) + 1):
        current_std = np.std(data[start_index:i])
        if current_std > threshold:
            # 如果当前的标准差超过了阈值,记录隔断点的索引位置,并重置开始索引为当前位置
            start_index = i - 1  # 重置为当前位置,因为i是从1开始的
            std_values.append(None)  # 使用 None 表示隔断点
            break_points.append(start_index)
        else:
            std_values.append(current_std)

    return std_values, break_points


def apply_grubbs_test(data: list[float], alpha: float=0.05) -> List[float]:
    """实现格拉布斯检验函数"""
    values = data
    n = len(values)
    outliers = []

    while True:
        mean = np.mean(values)
        std = np.std(values)
        t_critical = t.ppf(1 - alpha / (2*n), n - 2)
        max_residual = np.max(np.abs(values - mean))
        max_residual_idx = np.argmax(np.abs(values - mean))
        test_statistic = max_residual / std

        if test_statistic < t_critical:
            break

        outliers.append(data.pop(max_residual_idx))
        values = data
        n -= 1

    return outliers


def calculate_z_scores(data: list[float]) -> List[float]:
    """计算Z分数"""
    values = data
    mean = np.mean(values)
    std = np.std(values)
    z_scores = []
    for item in data:
        z_score = (item - mean) / std
        z_scores.append(z_score)
    return z_scores


def detect_outliers(z_scores: List[float], threshold: float=3) -> List[float]:
    """标记异常值:
    z_scores = calculate_z_scores(data)
    outliers = detect_outliers(z_scores, threshold=3)
    """
    outliers = []
    for i, z_score in enumerate(z_scores):
        if z_score < -threshold or z_score > threshold:
            outliers.append(i)
    return outliers


def apply_dbscan_clustering(data: List[float], epsilon: float, min_samples: int) -> dict[int, List[float]]:
    """
    实现DBSCAN聚类函数
    epsilon = 0.5  # DBSCAN的邻域半径
    min_samples = 5  # 聚类的最小样本数
    clusters = apply_dbscan_clustering(data, epsilon, min_samples)
    """
    values = np.array(data).reshape(-1, 1)
    
    dbscan = DBSCAN(eps=epsilon, min_samples=min_samples).fit(values)
    labels = dbscan.labels_
    
    clusters = {}
    for i, label in enumerate(labels):
        if label in clusters:
            clusters[label].append(data[i])
        else:
            clusters[label] = [data[i]]
    return clusters


def sliding_t_test(data: List[float], window_size: int = 10, significance_level: float = 0.05) -> List[Tuple[str, float, float]]:
    results = []
    
    for i in range(len(data) - window_size):
        window_values = [data[i:i+window_size]]
        mean_before = np.mean(window_values[:window_size // 2])
        mean_after = np.mean(window_values[window_size // 2:])
        std_dev = np.std(window_values)
        t_statistic = (mean_after - mean_before) / (std_dev / np.sqrt(window_size // 2))
        p_value = 2 * (1 - t.cdf(abs(t_statistic), df=window_size - 1))
        results.append((i + window_size // 2, t_statistic, p_value))
    
    return results


def calculate_control_limits(data: List[float]) -> Tuple[float, float, float, float, float, float]:
    values = np.array(data)
    n = len(data)  # 样本大小
    sigma = np.std(values)  # 样本标准差
    X_bar = np.mean(values)  # 样本均值
    CL_X_bar = X_bar
    UCL_X_bar = X_bar + 3 * sigma / np.sqrt(n)  # 上控制限
    LCL_X_bar = X_bar - 3 * sigma / np.sqrt(n)  # 下控制限

    R_values = np.abs(np.diff(values))  # 计算样本范围
    CL_R = np.mean(R_values)  # 样本范围的均值
    UCL_R = 3 * CL_R  # 上控制限
    LCL_R = 0  # 下控制限

    return CL_X_bar, UCL_X_bar, LCL_X_bar, CL_R, UCL_R, LCL_R

def plot_x_hart_control_chart(data: list[float], SaveFilePath: Optional[str]=None) -> None:
    CL_X_bar, UCL_X_bar, LCL_X_bar, CL_R, UCL_R, LCL_R = calculate_control_limits(data)

    values = data
    idxs = range(len(data))

    plt.figure(figsize=(12, 6))

    plt.subplot(2, 1, 1)
    plt.plot(idxs, values, 'b-', label='数据值')
    plt.axhline(y=CL_X_bar, color='r', linestyle='--', label='中心线')
    plt.axhline(y=UCL_X_bar, color='g', linestyle='--', label='上控制限')
    plt.axhline(y=LCL_X_bar, color='g', linestyle='--', label='下控制限')
    plt.title('X-bar 控制图')
    plt.xlabel('索引')
    plt.ylabel('数值')
    plt.legend()

    plt.subplot(2, 1, 2)
    R_values = np.abs(np.diff(values))
    plt.plot(idxs[:-1], R_values, 'b-', label='R 值')
    plt.axhline(y=CL_R, color='r', linestyle='--', label='中心线')
    plt.axhline(y=UCL_R, color='g', linestyle='--', label='上控制限')
    plt.axhline(y=LCL_R, color='g', linestyle='--', label='下控制限')
    plt.title('R 控制图')
    plt.xlabel('索引')
    plt.ylabel('范围')
    plt.legend()

    plt.tight_layout()
    if SaveFilePath is not None:
        plt.savefig(SaveFilePath) 
    else:
        plt.show()
    plt.close()


def ewma(data: List[float], alpha: float = 0.2) -> np.ndarray:
    """
    计算指数加权移动平均 (Exponential Weighted Moving Average, EWMA)

    Args:
    - data (List[ListFloat]): 数据序列,包含时间和数值
    - alpha (float): 平滑系数, 控制对最新观测值的权重, 通常取值范围为[0, 1]

    Returns:
    - np.ndarray: 指数加权移动平均序列
    """
    ewma_values = data[0]  # 初始化第一个值为初始EWMA值
    for i in range(1, len(data)):
        ewma_values.append(alpha * data[i] + (1 - alpha) * ewma_values[-1])
    return np.array(ewma_values)


def calculate_control_limits_ewma(data: List[float], alpha: float = 0.2) -> Tuple[float, float, float]:
    """
    计算EWMA控制图的控制限

    Args:
    - data (List[ListFloat]): 数据序列,包含时间和数值
    - alpha (float): 平滑系数

    Returns:
    - Tuple[float, float, float]: CL(中心线)、UCL(上控制限)、LCL(下控制限)
    """
    ewma_values = ewma(data, alpha)
    CL = np.mean(ewma_values)  # 中心线即为EWMA序列的均值
    std_dev = np.std(ewma_values)  # 计算EWMA序列的标准差

    # 计算控制限
    UCL = CL + 3 * std_dev
    LCL = CL - 3 * std_dev

    return CL, UCL, LCL


def plot_control_limits_ewma(data: list[float], alpha=0.2, SaveFilePath: Optional[str]=None) -> None:
    # 将数据转换为列表以便计算
    data_values = data

    # 计算EWMA控制图的控制限
    CL, UCL, LCL = calculate_control_limits_ewma(data, alpha)

    # 绘制EWMA控制图
    plt.plot(data_values, label='数据')
    plt.plot([CL] * len(data_values), 'r--', label='中心线')
    plt.plot([UCL] * len(data_values), 'g--', label='上控制限')
    plt.plot([LCL] * len(data_values), 'b--', label='下控制限')
    plt.xlabel('样本')
    plt.ylabel('数值')
    plt.title('指数加权移动平均控制图')
    plt.legend()
    if SaveFilePath is not None:
        plt.savefig(SaveFilePath) 
    else:
        plt.show()
    plt.close()

# endregion
# region scikit-learn使用
def calculate_similarity(ts1: List[float], ts2: List[float]) -> None:
    """
    计算并打印两个时间序列之间的皮尔逊、斯皮尔曼和肯德尔相关系数。

    参数:
    ts1 -- 时间序列1，列表形式的浮点数。
    ts2 -- 时间序列2，列表形式的浮点数。
    """
    # 计算皮尔逊相关系数
    pearson_corr, _ = pearsonr(ts1, ts2)
    
    # 计算斯皮尔曼相关系数
    spearman_corr, _ = spearmanr(ts1, ts2)
    
    # 计算肯德尔相关系数
    kendall_corr, _ = kendalltau(ts1, ts2)
    
    # 打印相关系数
    print("皮尔逊相关系数:", pearson_corr)
    print("斯皮尔曼相关系数:", spearman_corr)
    print("肯德尔相关系数:", kendall_corr)
    
    return pearson_corr, spearman_corr, kendall_corr



def clustering_listfloat(data: List[float], num_clusters: int) -> np.ndarray:
    """
    对时间序列数据进行聚类
    
    Args:
        ts_data (List[ListFloat]): 时间序列数据
        num_clusters (int): 聚类的数量
    
    Returns:
        np.ndarray: 每个时间序列的聚类标签
    """
    # 取出时间序列数据的值
    values = data
    
    # 转换为numpy数组
    X = np.array(values).reshape(-1, 1)
    
    # 使用K-means进行聚类
    kmeans = KMeans(n_clusters=num_clusters, random_state=0).fit(X)
    
    # 获取每个时间序列的聚类标签
    labels = kmeans.labels_
    
    # 返回聚类结果
    return labels


# endregion
# region 归一化处理

def min_max_normalization(data: List[float]) -> List[float]:
    """
    最大值最小值归一化处理。

    :param data: 要归一化的数据，float对象列表。
    :return: 归一化后的float对象列表。
    """
    min_val = min(data)
    max_val = max(data)
    normalized_data = [(value - min_val) / (max_val - min_val) for value in data]
    return normalized_data


def decimal_scaling_normalization(data: List[float]) -> List[float]:
    """
    使用小数定标归一化对时序数据进行归一化处理。

    :param data: 要归一化的时间序列数据，float对象列表。
    :return: 归一化后的float对象列表。
    """
    max_abs = max(abs(min(data)), abs(max(data)))

    normalized_data = [value / max_abs for value in data]
  
    return normalized_data


def log_normalization(data: List[float]) -> List[float]:
    """
    使用对数归一化对时序数据进行归一化处理。

    :param data: 要归一化的时间序列数据，float对象列表。
    :return: 归一化后的float对象列表。
    """
    min_val = min(data)
    normalized_values = np.log(data) - np.log(min_val)
  
    return normalized_values


def l1_normalization(data: List[float]) -> List[float]:
    """
    使用L1范数归一化对时序数据进行归一化处理。

    :param data: 要归一化的时间序列数据，float对象列表。
    :return: 归一化后的float对象列表。
    """
    l1_norm = np.sum(np.abs(data))

    normalized_values = [value / l1_norm for value in data]
  
    return normalized_values


def l2_normalization(data: List[float]) -> List[float]:
    """
    使用L2范数归一化对时序数据进行归一化处理。

    :param data: 要归一化的时间序列数据，float对象列表。
    :return: 归一化后的float对象列表。
    """
    l2_norm = np.linalg.norm(data)

    normalized_values = [value / l2_norm for value in data]
  
    return normalized_values

# endregion
# region 模态分解
def hilbert_transform(data: List[float]) -> Tuple[np.ndarray, np.ndarray]:
    """对时间序列进行希尔伯特变换
    amplitude_envelope, instantaneous_phase = hilbert_transform(data)
    process_and_plot_hilbert_transform(amplitude_envelope, instantaneous_phase)
    """
    values = data
    analytic_signal = hilbert(values)
    amplitude_envelope = np.abs(analytic_signal)
    instantaneous_phase = np.unwrap(np.angle(analytic_signal))
    
    return amplitude_envelope, instantaneous_phase


def process_and_plot_hilbert_transform(amplitude_envelope: np.ndarray, instantaneous_phase: np.ndarray, SaveFilePath: Optional[str] = None) -> None:
    """处理和可视化希尔伯特变换的结果"""
    plt.figure(figsize=(14.4, 9.6)) # 单位是英寸
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))

    # 可视化振幅包络
    ax1.plot(amplitude_envelope)
    ax1.set_title("振幅包络")
    ax1.set_xlabel("时间")
    ax1.set_ylabel("振幅")

    # 可视化瞬时相位
    ax2.plot(instantaneous_phase)
    ax2.set_title("瞬时相位")
    ax2.set_xlabel("时间")
    ax2.set_ylabel("相位")

    if SaveFilePath is not None:
        plt.savefig(SaveFilePath)
    else: 
        plt.show()
    plt.close()


def empirical_mode_decomposition(data: List[float]) -> np.ndarray:
    """对时序数据进行经验模态分解
    imfs = empirical_mode_decomposition(data)
    """
    values = np.array(data)
    
    # 创建EMD对象,并进行分解
    emd = EMD()
    imfs = emd.emd(values)
    
    return imfs


def plot_imfs(imfs: np.ndarray, SaveFilePath: Optional[str] = None) -> None:
    """绘制IMFs"""
    num_imfs = len(imfs)
    plt.figure(figsize=(14.4, 9.6)) # 单位是英寸
    # 创建子图布局
    fig, axes = plt.subplots(num_imfs, 1, figsize=(8, 2*num_imfs), sharex=True)

    # 绘制每个IMF的图形
    for i, imf in enumerate(imfs):
        axes[i].plot(imf)
        axes[i].set_ylabel(f"IMF {i+1}")

    # 设置横坐标标签
    axes[-1].set_xlabel("Time")

    # 调整子图之间的间距
    plt.tight_layout()
    if SaveFilePath is not None:
        plt.savefig(SaveFilePath)
    # 显示图形
    else: 
        plt.show()
    plt.close()


def plot_imfs_rm(imfs: np.ndarray, rm: np.ndarray, SaveFilePath: Optional[str] = None) -> None:
    """绘制IMFs和残差项Rm"""
    num_imfs = len(imfs)
    num_rows = num_imfs // 2 + num_imfs % 2
    
    # 创建子图布局
    plt.figure(figsize=(14.4, 9.6)) # 单位是英寸
    fig, axes = plt.subplots(num_rows, 2, figsize=(12, 3*num_rows), sharex=True)

    # 绘制每个IMF的图形
    for i, imf in enumerate(imfs):
        row_idx = i // 2
        col_idx = i % 2
        axes[row_idx, col_idx].plot(imf)
        axes[row_idx, col_idx].set_ylabel(f"IMF {i+1}")

    # 绘制残差项的图形
    rm_row_idx = num_imfs // 2
    rm_col_idx = 0 if num_imfs % 2 == 0 else 1
    axes[rm_row_idx, rm_col_idx].plot(rm)
    axes[rm_row_idx, rm_col_idx].set_ylabel("Rm")

    # 清除未使用的子图
    for i in range(rm_row_idx+1, num_rows):
        for j in range(2):
            axes[i, j].axis("off")

    # 设置横坐标标签
    axes[-1, 0].set_xlabel("Time")
    axes[-1, 1].set_xlabel("Time")

    # 调整子图之间的间距
    plt.tight_layout()
    if SaveFilePath is not None:
        plt.savefig(SaveFilePath)
    # 显示图形
    else: 
        plt.show()
    plt.close()


def eemd(data: List[float], num_trials: int = 100) -> Tuple[np.ndarray, np.ndarray]:
    """实现EEMD"""
    values = np.array(data)
    eemd = EEMD()
    eemd.trials = num_trials
    imfs = eemd.eemd(values)
    
    rm = values - np.sum(imfs, axis=0)
    return imfs, rm


def ceemd(data: List[float], num_trials: int = 100) -> Tuple[np.ndarray, np.ndarray]:
    """实现CEEMD"""
    values = np.array(data)
    ceemdan = CEEMDAN(trials=num_trials)
    imfs = ceemdan.ceemdan(values)

    rm = values - np.sum(imfs, axis=0)
    return imfs, rm


def calculate_variance_imfs(imfs: np.ndarray) -> List[float]:
    """计算每个IMF的方差"""
    variances = []
    for imf in imfs:
        variance = np.var(imf)
        variances.append(variance)
    return variances


def calculate_energy_ratio(imfs: np.ndarray) -> np.ndarray:
    """计算每个IMF的能量比"""
    total_energy = np.sum(np.square(imfs))
    energy_ratios = np.square(imfs) / total_energy
    return energy_ratios


def calculate_snr(variances: List[float]) -> List[float]:
    """
    计算每个 IMF 的信噪比。
    信噪比的单位是 dB。
    """
    snr_values = []
    noise_variance = np.mean(variances)  # 假设噪声方差为所有 IMF 方差的均值

    for variance in variances:
        snr = 10 * math.log10(variance / noise_variance)
        snr_values.append(snr)
    
    return snr_values


def plot_imf_properties(variances: List[float], SaveFilePath: Optional[str] = None) -> None:
    """
    用柱状图显示每个 IMF 的方差。
    """
    num_imfs = len(variances)
    imf_indices = np.arange(num_imfs)

    plt.figure(figsize=(14.4, 9.6)) # 单位是英寸
    plt.bar(imf_indices, variances)
    plt.ylabel("方差")
    plt.xticks(imf_indices, [f"{i + 1}号IMF" for i in range(num_imfs)])
    plt.title("IMF 方差")

    plt.tight_layout()  # 调整子图之间的间距
    
    if SaveFilePath:
        plt.savefig(SaveFilePath)
    else:
        plt.show()

    plt.close()


def wavelet_packet_analysis(signal: Union[List[float], np.ndarray], wavelet_name: str = 'db4', level: int = 5) -> List[float]:
    """
    使用小波包分析信号并返回每个层次的频谱能量。
    """
    wp = pywt.WaveletPacket(data=signal, wavelet=wavelet_name, mode='symmetric')
    wp_level = wp.get_level(level)

    spectral_energy = []
    for node in wp_level:
        spectral_energy.append(sum(node.data ** 2))
    
    return spectral_energy


def calculate_peak_frequency(spectral_energy: List[float], sample_rate: float = 1) -> float:
    """
    找到频谱能量列表中的最大值及其对应的索引，并计算对应的频率。
    """
    max_energy = max(spectral_energy)
    peak_index = spectral_energy.index(max_energy)

    # 将索引转换为对应的频率
    max_frequency = peak_index * (sample_rate / len(spectral_energy))

    return max_frequency


def calculate_peak_energy(spectral_energy: List[float]) -> float:
    """找到频谱能量列表中的最大值"""
    peak_energy = max(spectral_energy)
    return peak_energy


def plot_spectral_energy(spectral_energy: List[float], SaveFilePath: Optional[str] = None) -> None:
    """
    可视化频谱能量
    """
    frequencies = range(len(spectral_energy))  # 假设频率范围是0到N-1
    
    plt.figure(figsize=(14.4, 9.6)) # 单位是英寸
    plt.plot(frequencies, spectral_energy)
    plt.xlabel('频率')
    plt.ylabel('频谱能量')
    plt.title('频谱能量分析')
    if SaveFilePath is not None:
        plt.savefig(SaveFilePath)
    else:
        plt.show()
    plt.close()


def calculate_energy_bandwidth(spectral_energy: List[float], threshold: float) -> int:
    """
    计算频谱能量的带宽:
    """
    total_energy = sum(spectral_energy)
    target_energy = threshold * total_energy

    cumulative_energy = 0
    bandwidth = 0

    for energy in spectral_energy:
        cumulative_energy += energy
        if cumulative_energy >= target_energy:
            bandwidth += 1
        else:
            break

    return bandwidth


def calculate_energy_ratio(spectral_energy: List[float]) -> List[float]:
    """
    计算频谱能量的能量比值
    """
    total_energy = sum(spectral_energy)
    energy_ratio = []

    for energy in spectral_energy:
        ratio = energy / total_energy
        energy_ratio.append(ratio)

    return energy_ratio


def calculate_spectrum_centroid(spectral_energy: List[float]) -> Optional[float]:
    """谱心是频谱能量的重心位置"""
    frequencies = range(len(spectral_energy))  # 假设频率范围是0到N-1
    energy_sum = 0
    centroid_sum = 0

    for i in range(len(spectral_energy)):
        energy_sum += spectral_energy[i]
        centroid_sum += frequencies[i] * spectral_energy[i]

    if energy_sum != 0:
        centroid = centroid_sum / energy_sum
    else:
        centroid = None

    return centroid


def calculate_spectrum_width(spectral_energy: List[float], threshold: float = 0.5) -> int:
    """
    计算频谱的宽度通常涉及到定义何种情况下能量减少到原来的一定百分比
    常见的定义是计算能量减少到原来能量的一半所对应的频率范围,即谱宽度为能量衰减到50%的频率范围
    """
    frequencies = range(len(spectral_energy))  # 假设频率范围是0到N-1
    total_energy = sum(spectral_energy)
    target_energy = threshold * total_energy

    left_index = 0
    right_index = len(spectral_energy) - 1

    cumulative_energy = 0
    while cumulative_energy < target_energy and left_index < right_index:
        left_energy = spectral_energy[left_index]
        right_energy = spectral_energy[right_index]

        if cumulative_energy + left_energy <= target_energy:
            cumulative_energy += left_energy
            left_index += 1

        if cumulative_energy + right_energy <= target_energy:
            cumulative_energy += right_energy
            right_index -= 1

    width = frequencies[right_index] - frequencies[left_index]

    return width


def calculate_primary_frequency_range(spectral_energy: List[float], top_n: int = 1) -> Tuple[int, int]:
    """
    计算主要频段
    """
    frequencies = range(len(spectral_energy))  # 假设频率范围是0到N-1
    sorted_indices = sorted(range(len(spectral_energy)), key=lambda i: spectral_energy[i], reverse=True)
    top_indices = sorted_indices[:top_n]
    start_freq = frequencies[top_indices[0]]
    end_freq = frequencies[top_indices[-1]]

    return (start_freq, end_freq)


def butterworth_filter(imfs: List[np.ndarray], rm: np.ndarray, order: int, cutoff_freq: float) -> Tuple[List[np.ndarray], Optional[np.ndarray]]:
    """butter worth滤波"""
    filtered_imfs = []
    filtered_rm = None
    
    # 对每个IMF分量进行滤波
    for imf in imfs:
        b, a = signal.butter(order, cutoff_freq, output='ba')
        filtered_imf = signal.lfilter(b, a, imf)
        filtered_imfs.append(filtered_imf)
    
    # 对rm进行滤波
    b, a = signal.butter(order, cutoff_freq, output='ba')
    filtered_rm = signal.lfilter(b, a, rm)
    
    return filtered_imfs, filtered_rm


def reconstruct_signal(filtered_imfs: List[np.ndarray], filtered_rm: Optional[np.ndarray]) -> np.ndarray:
    """还原时域数据"""
    signal_reconstructed = np.sum(filtered_imfs, axis=0) + filtered_rm
    return signal_reconstructed


def plot_reconstruct_signal(signal_reconstructed: np.ndarray, SaveFilePath: Optional[str] = None) -> None:
    # 绘制信号重构结果的时间序列图
    plt.figure(figsize=(14.4, 9.6)) # 单位是英寸
    plt.plot(signal_reconstructed)
    plt.xlabel('时间')
    plt.ylabel('信号值')
    plt.title('信号重构结果')
    if SaveFilePath is not None:
        plt.savefig(SaveFilePath)
    else:
        plt.show()
    plt.close()


# endregion
# region 自回归模型及预测值评估
def ar_model_forecast(data: List[float], lags: int = 1, future_steps: int = 10, SaveFilePath: Optional[str] = None) -> Tuple[np.ndarray, float]:
    """
    自回归模型(Autoregressive Model, AR)
    """
    # 提取时序数据的观测值
    X = np.array(data)

    # 拟合AR模型
    model = AutoReg(X, lags=lags)
    model_fit = model.fit()

    # 进行未来预测
    future_forecast = model_fit.forecast(steps=future_steps)

    # 计算均方根误差
    mse = root_mean_squared_error(X[-future_steps:], future_forecast)
    plt.figure(figsize=(14.4, 9.6)) # 单位是英寸
    # 绘制原始数据和预测结果
    plt.plot(X, label='原始数据')
    plt.plot(np.arange(len(X), len(X) + future_steps), future_forecast, label='预测结果')
    plt.xlabel('时间')
    plt.ylabel('观测值')
    plt.legend()
    plt.title('AR模型预测结果')
    if SaveFilePath is not None:
        plt.savefig(SaveFilePath)
    else:
        plt.show()
    plt.close()

    return future_forecast, mse


def ma_model_forecast(data: List[float], q: int = 1, future_steps: int = 10, SaveFilePath: Optional[str] = None) -> Tuple[np.ndarray, float]:
    """
    移动平均模型(Moving Average Model, MA)
    """
    # 提取时序数据的观测值
    X = np.array(data)
    
    # 拟合MA模型
    model = ARIMA(X, order=(0, 0, q))
    model_fit = model.fit()
    
    # 进行未来预测
    future_forecast = model_fit.forecast(steps=future_steps)
    
    mse = root_mean_squared_error(X[-future_steps:], future_forecast)
    plt.figure(figsize=(14.4, 9.6)) # 单位是英寸
    # 绘制原始数据和预测结果
    plt.plot(X, label='原始数据')
    plt.plot(np.arange(len(X), len(X) + future_steps), future_forecast, label='预测结果')
    plt.xlabel('时间')
    plt.ylabel('观测值')
    plt.legend()
    plt.title('MA模型预测结果')
    if SaveFilePath is not None:
        plt.savefig(SaveFilePath)
    else:
        plt.show()
    plt.close()
    
    return future_forecast, mse


def arima_model_forecast(data: list[float], p: int, q: int, future_steps: int, SaveFilePath: Optional[str] = None) -> Tuple[np.ndarray, float]:
    """
    自回归移动平均模型(Autoregressive Moving Average Model,ARM)
    并指定合适的p、q以及未来预测的步数future_steps,然后该函数将返回未来预测的结果以及均方根误差。
    """
    # 提取时序数据的观测值
    X = data
    
    # 拟合ARMA模型
    model = ARIMA(X, order=(p, 0, q))
    model_fit = model.fit()
    
    # 进行未来预测
    future_forecast = model_fit.forecast(steps=future_steps)[0]
    
    # 计算均方根误差
    mse = root_mean_squared_error(X[-future_steps:], future_forecast, squared=False)
    plt.figure(figsize=(14.4, 9.6)) # 单位是英寸
    # 绘制原始数据和预测结果
    plt.plot(X, label='原始数据')
    plt.plot(np.arange(len(X), len(X) + future_steps), future_forecast, label='预测结果')
    plt.xlabel('时间')
    plt.ylabel('观测值')
    plt.legend()
    plt.title('ARMA模型预测结果')
    if SaveFilePath is not None:
        plt.savefig(SaveFilePath)
    else: 
        plt.show()
    plt.close()
    
    return future_forecast, mse


def plot_float_with_idx(data: list[float], startidx: int, endidx: int):
    # 修改标签和标题的文本为中文
    values = data[startidx: endidx]
    plt.figure(figsize=(14.4, 9.6)) # 单位是英寸
    plt.xlabel('idx')
    plt.ylabel('数值')
    plt.title(f'{startidx}-{endidx}索引数据可视化')
    
    plt.plot(range(len(values)), values)
    # 设置最大显示的刻度数
    plt.gcf().autofmt_xdate()  # 旋转日期标签以避免重叠
    plt.tight_layout()  # 自动调整子图间的间距和标签位置

    plt.show()
    plt.close()

def plot_ACF(data: list[float], SaveFilePath: Optional[str] = None) -> None:
    """绘制自相关函数(ACF)图表"""
    # 提取时序数据的观测值
    X = data

    # 计算自相关函数(ACF)
    acf = sm.tsa.acf(X, nlags=len(data))
    # 绘制自相关函数(ACF)图表
    plt.figure(figsize=(14.4, 9.6)) # 单位是英寸
    plt.stem(acf)
    plt.xlabel('滞后阶数')
    plt.ylabel('相关系数')
    plt.title('自相关函数(ACF)')
    if SaveFilePath is not None:
        plt.savefig(SaveFilePath)
    else:
        plt.show()
    plt.close()

# 定义一个函数来绘制极坐标图
def plot_polar(distances_and_bearings: List[Tuple[float, float]], title = None):
    # 创建一个极坐标图
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    
    # 遍历距离和方位角，绘制每个点
    for distance, bearing in distances_and_bearings:
        # 将方位角转换为弧度
        theta = np.deg2rad(bearing)
        # 绘制点
        ax.plot(theta, distance, 'o', color='blue')
    
    # 设置极坐标图的标题
    ax.set_title(f'{title}极坐标')
    
    # 显示图形
    plt.show()

def plot_polar_with_rms(rms_list: List[float], distances_and_bearings: List[Tuple[float, float]], threshold: float, title=None):
    # 创建一个极坐标图
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    
    # 遍历距离、方位角和 RMS 值，绘制每个点
    for i, (distance, bearing) in enumerate(distances_and_bearings):
        # 将方位角转换为弧度
        theta = np.deg2rad(bearing)
        
        # 绘制点
        if rms_list[i] > threshold:
            ax.plot(theta, distance, 'o', color='red', label='RMS Exceeded Threshold')
        else:
            ax.plot(theta, distance, 'o', color='blue')
    
    # 设置极坐标图的标题
    ax.set_title(f'{title}极坐标')
    
    # 显示图形
    plt.show()

def plot_polar_with_rms_exceeded(rms_list: List[float], distances_and_bearings: List[Tuple[float, float]], threshold: float, title=None):
    # 创建一个极坐标图
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    
    # 遍历距离、方位角和 RMS 值，仅绘制超过阈值的点
    for i, (distance, bearing) in enumerate(distances_and_bearings):
        # 将方位角转换为弧度
        theta = np.deg2rad(bearing)
        
        # 绘制超过阈值的点
        if rms_list[i] > threshold:
            ax.plot(theta, distance, 'o', color='blue', label='RMS Exceeded Threshold')
    
    # 设置极坐标图的标题
    ax.set_title(f'{title}极坐标 (只显示超过阈值的点)')

    # 显示图形
    plt.show()
    
def plot_PACF(data: list[float], lags: int = 48, SaveFilePath: Optional[str] = None) -> None:
    """绘制偏自相关函数(PACF)图表"""
    # 提取时序数据的观测值
    X = data

    # 计算偏自相关函数(PACF)
    pacf = sm.tsa.pacf(X, nlags=lags)
    # 绘制偏自相关函数(PACF)图表
    plt.figure(figsize=(14.4, 9.6)) # 单位是英寸
    plt.stem(pacf)
    plt.xlabel('滞后阶数')
    plt.ylabel('相关系数')
    plt.title('偏自相关函数(PACF)')
    if SaveFilePath is not None:
        plt.savefig(SaveFilePath)
    else:
        plt.show()
    plt.close()


def fit_arima_model(data: List[float], p: int = 1, d: int = 1, q: int = 1, num_steps: int = 10, output_file: str = "arima_results.txt") -> np.ndarray:
    """
    差分自回归移动平均模型(ARIMA)
    该函数接受一个时序数据作为输入(例如ListFloat实例的列表),并设置ARIMA模型的阶数(p、d、q)以及预测步数(num_steps)。
    它使用此时序数据来执行ARIMA模型的拟合,并打印出模型的统计摘要和预测的未来数据点。
    """

    X = [point.value for point in data]

    # 创建ARIMA模型对象
    model = sm.tsa.ARIMA(X, order=(p, d, q))

    # 拟合ARIMA模型
    results = model.fit()

    # 将结果写入txt文件
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(results.summary().as_text())

        # 预测未来的数据点
        forecast = results.forecast(steps=num_steps)
        file.write("\n\n预测结果:\n")
        file.write(str(forecast))

    return forecast
# endregion
# region 数据去噪
def smooth_noise(data: List[float], window_size: int) -> List[float]:
    smoothed_data = []
    for i in range(len(data)):
        start_index = max(0, i - window_size + 1)
        end_index = min(len(data), i + 1)

        window_values = [data[j] for j in range(start_index, end_index)]
        smoothed_value = sum(window_values) / len(window_values)
        smoothed_data.append(smoothed_value)

    return smoothed_data


def equal_depth_binning(data: List[float], num_bins: int) -> List[List[float]]:
    sorted_data = sorted(data, key=lambda x: x)
    bin_size = len(data) // num_bins

    bins = []
    start_index = 0

    for i in range(num_bins - 1):
        end_index = start_index + bin_size
        bin_data = sorted_data[start_index:end_index]
        bins.append(bin_data)
        start_index = end_index

    # Add remaining data to the last bin
    last_bin = sorted_data[start_index:]
    bins.append(last_bin)

    return bins


def mean_smoothing(bins: List[List[float]]) -> List[List[float]]:
    smoothed_bins = []
    for bin_data in bins:
        bin_values = [data for data in bin_data]
        mean_value = sum(bin_values) / len(bin_values)
        smoothed_bins.append(mean_value)

    return smoothed_bins


def plot_smoothed_data_and_bins(data: List[float], smoothed_data: List[float], bins: List[List[float]], smoothed_bins: List[List[float]]) -> None:
    # 绘制平滑噪声的结果
    plt.figure(figsize=(10, 5))
    plt.plot([data_point.datetime for data_point in data], smoothed_data, label="平滑数据")
    plt.xlabel("时间")
    plt.ylabel("数值")
    plt.title("平滑噪声")
    plt.legend()
    plt.show()

    # 绘制等深分箱和均值平滑的结果
    plt.figure(figsize=(10, 5))
    for i, bin_data in enumerate(smoothed_bins):
        bin_values = [data_point for data_point in bin_data]
        bin_datetimes = range(len(bin_data))
        plt.plot(bin_datetimes, bin_values, label=f"箱子 {i+1}")

    plt.xlabel("时间")
    plt.ylabel("数值")
    plt.title("等深分箱和均值平滑")
    plt.legend()
    plt.show()


# 平滑噪声—等深分箱—均值平滑
def aequilatus_box_mean(data: List[float], bins: int = 3) -> List[float]:
    length = len(data)
    labels = []
    
    for i in range(bins):
        labels.append('a' + str(i+1)) # 添加标签
    
    data_df = pd.DataFrame({'value': data})
    new_data = pd.qcut(data_df['value'], bins, labels=labels) # 等深分箱
    data_df['label'] = new_data

    for label in labels:
        label_index_min = data_df[data_df.label==label].index.min() # 分箱后索引最小值
        label_index_max = data_df[data_df.label==label].index.max() # 分箱后索引最大值
        mean_value = np.mean([data[label_index_min:label_index_max+1]]) # 计算各箱均值
        for i in range(label_index_min, label_index_max+1):
            data[i] = mean_value # 修改各数据点的数值为均值

    return data


def wavelet_denoising(data: List[float]) -> List[float]:
    """小波转换去噪"""
    # 提取数据中的数值部分
    signal_values = data

    # 选择小波基函数和分解级别
    wavelet = 'db4'
    level = pywt.dwt_max_level(len(signal_values), wavelet)

    # 进行小波分解
    coeffs = pywt.wavedec(signal_values, wavelet, level=level)

    # 估计噪声水平并计算阈值
    sigma = np.median(np.abs(coeffs[-level])) / 0.6745
    threshold = sigma * np.sqrt(2 * np.log(len(signal_values)))

    # 对小波系数进行阈值处理
    coeffs = [pywt.threshold(c, threshold) for c in coeffs]

    # 进行小波重构
    denoised_signal = pywt.waverec(coeffs, wavelet)

    return denoised_signal


def plot_denoised_signal(signal_data: List[float], denoised_signal: List[float]) -> None:
    # 从 ListFloat 对象中提取数值部分
    plt.figure(figsize=(10, 5))
    plt.plot(signal_data, label='原始信号')
    plt.plot(denoised_signal, label='去噪后信号')
    plt.xlabel('时间')
    plt.ylabel('幅值')
    plt.title('时序信号去噪')
    plt.legend()
    plt.show()


# endregion
# region 概率论相关
def kernel_density_estimation(data: list[float], SaveFilePath: Optional[str]=None) -> None:
    # 从ListFloat对象列表中提取值,并将其转换为numpy数组
    values = np.array([data_point.value for data_point in data])

    # 使用高斯核函数创建核密度估计对象
    kde = gaussian_kde(values)

    # 定义用于计算核密度函数的数据点集合
    density_x = np.linspace(min(values), max(values), 100)

    # 计算核密度估计的概率密度函数值
    density_y = kde(density_x)

    # 绘制核密度估计结果
    plt.plot(density_x, density_y)
    plt.xlabel('数值')
    plt.ylabel('密度')
    plt.title('核密度估计')
    if SaveFilePath is not None:
        plt.savefig(SaveFilePath) 
    else:
        plt.show()
    plt.close()


# endregion
# region 聚类分析np.ndarray
def cluster_analysis(complete_trend_line: np.ndarray, num_clusters: int) -> np.ndarray:
    """使用 K-means 聚类算法对趋势线进行聚类分析"""
    # Reshape the trend line array to be a column vector
    trend_line_vector = complete_trend_line.reshape(-1, 1)

    # Initialize KMeans model
    kmeans = KMeans(n_clusters=num_clusters, random_state=0)

    # Fit KMeans model to the trend line data
    kmeans.fit(trend_line_vector)

    # Get the cluster labels
    cluster_labels = kmeans.labels_

    return cluster_labels


def cluster_analysis_GMM(complete_trend_line: np.ndarray, num_clusters: int) -> np.ndarray:
    """使用高斯混合聚类算法GMM 对趋势线进行聚类分析"""
    # Reshape the trend line array to be a column vector
    trend_line_vector = complete_trend_line.reshape(-1, 1)

    # Initialize Gaussian Mixture model
    gmm = GaussianMixture(n_components=num_clusters, random_state=0)

    # Fit Gaussian Mixture model to the trend line data
    gmm.fit(trend_line_vector)

    # Predict the cluster labels
    cluster_labels = gmm.predict(trend_line_vector)

    return cluster_labels


def cluster_analysis_GMM_in_GridSearchCV(complete_trend_line: np.ndarray) -> np.ndarray:
    """使用高斯混合聚类算法对趋势线进行聚类分析"""
    # Reshape the trend line array to be a column vector
    trend_line_vector = complete_trend_line.reshape(-1, 1)

    # 定义参数网格
    param_grid = {'n_components': np.arange(2, 11)}  # 可以根据需求调整范围

    # 初始化 Gaussian Mixture model
    gmm = GaussianMixture(random_state=0)

    # 使用 GridSearchCV 寻找最优参数值
    grid_search = GridSearchCV(gmm, param_grid, cv=5)  # 5折交叉验证
    grid_search.fit(trend_line_vector)

    # 打印最优参数值
    print("最优的 n_components 参数值:", grid_search.best_params_)

    # 使用最优参数值重新训练模型
    best_gmm = grid_search.best_estimator_
    best_gmm.fit(trend_line_vector)

    # 预测聚类标签
    cluster_labels = best_gmm.predict(trend_line_vector)

    return cluster_labels


def cluster_analysis_AgglomerativeClustering(complete_trend_line: np.ndarray, num_clusters: int) -> np.ndarray:
    """使用层次聚类算法对趋势线进行聚类分析"""
    # Reshape the trend line array to be a column vector
    trend_line_vector = complete_trend_line.reshape(-1, 1)

    # Initialize Agglomerative Clustering model
    agg_clustering = AgglomerativeClustering(n_clusters=num_clusters)

    # Fit Agglomerative Clustering model to the trend line data
    cluster_labels = agg_clustering.fit_predict(trend_line_vector)

    return cluster_labels


def cluster_analysis_DBSCAN(complete_trend_line: np.ndarray, eps: float = 0.5, min_samples: int = 2) -> np.ndarray:
    """
    使用DBSCAN算法对趋势线进行聚类分析
    参数：
        - complete_trend_line: 包含完整趋势线的数组
        - eps: DBSCAN算法中的邻域半径
        - min_samples: DBSCAN算法中的最小样本数
    返回值：
        - cluster_labels: 聚类标签数组
    """
    # Reshape the trend line array to be a column vector
    trend_line_vector = complete_trend_line.reshape(-1, 1)

    # Initialize DBSCAN model
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)

    # Fit DBSCAN model to the trend line data
    cluster_labels = dbscan.fit_predict(trend_line_vector)

    return cluster_labels


def cluster_cluster_labels_with_score(complete_trend_line: np.ndarray, cluster_labels: np.ndarray) -> tuple:
    """
    """
    # 将趋势线数组重塑为列向量
    trend_line_vector = complete_trend_line.reshape(-1, 1)

    # 计算轮廓系数
    silhouette = silhouette_score(trend_line_vector, cluster_labels)

    # 计算 Davies-Bouldin 指数
    davies_bouldin = davies_bouldin_score(trend_line_vector, cluster_labels)

    # 计算 Calinski-Harabasz 指数
    calinski_harabasz = calinski_harabasz_score(trend_line_vector, cluster_labels)

    return silhouette, davies_bouldin, calinski_harabasz


def elbow_method(complete_trend_line: np.ndarray, max_clusters: int) -> None:
    """
    使用平均肘法选择最优的聚类数
    参数：
        - complete_trend_line: 包含完整趋势线的数组
        - max_clusters: 最大的聚类数
    """
    # Reshape the trend line array to be a column vector
    trend_line_vector = complete_trend_line.reshape(-1, 1)
    
    # 存储每个聚类数的平均轮廓系数
    silhouette_scores = []
    
    # 计算每个聚类数对应的平均轮廓系数
    for i in range(2, max_clusters + 1):
        kmeans = KMeans(n_clusters=i, random_state=0)
        cluster_labels = kmeans.fit_predict(trend_line_vector)
        silhouette_avg = silhouette_score(trend_line_vector, cluster_labels)
        silhouette_scores.append(silhouette_avg)
    
    # 绘制肘部法则图
    plt.plot(range(2, max_clusters + 1), silhouette_scores, marker='o', label='平均轮廓系数')
    plt.xlabel('聚类数')
    plt.ylabel('平均轮廓系数')
    plt.title('平均肘法')
    for i, txt in enumerate(silhouette_scores):
        plt.annotate(round(txt, 2), (i+2, silhouette_scores[i]), textcoords="offset points", xytext=(0,10), ha='center')
    plt.legend()
    plt.show()


def elbow_method_GMM(complete_trend_line: np.ndarray, max_clusters: int) -> None:
    """
    使用肘部法则选择最优的聚类数
    参数：
        - complete_trend_line: 包含完整趋势线的数组
        - max_clusters: 最大的聚类数
    """
    # Reshape the trend line array to be a column vector
    trend_line_vector = complete_trend_line.reshape(-1, 1)
    
    # 存储每个聚类数的似然函数值
    likelihoods = []
    
    # 计算每个聚类数对应的似然函数值
    for i in range(1, max_clusters + 1):
        gmm = GaussianMixture(n_components=i, random_state=0)
        gmm.fit(trend_line_vector)
        likelihoods.append(gmm.score(trend_line_vector))
    
    # 绘制肘部法则图
    plt.plot(range(1, max_clusters + 1), likelihoods, marker='o', label='似然函数值')
    plt.xlabel('聚类数')
    plt.ylabel('对数似然函数值')
    plt.title('肘部法则')
    for i, txt in enumerate(likelihoods):
        plt.annotate(round(txt, 2), (i+1, likelihoods[i]), textcoords="offset points", xytext=(0,10), ha='center')
    plt.legend()
    plt.show()


def cluster_evaluation(complete_trend_line: np.ndarray, cluster_labels: np.ndarray, true_labels: np.ndarray) -> tuple:
    """
    评估聚类模型的拟合优度和聚类结果与原始类别之间的契合度
    参数：
        - complete_trend_line: 包含完整趋势线的数组
        - cluster_labels: 聚类标签数组
        - true_labels: 真实的类别标签数组
    返回值：
        - silhouette: Silhouette Score
        - v_measure: V-Measure Score
    """
    # 计算 Silhouette Score
    silhouette = silhouette_score(complete_trend_line.reshape(-1, 1), cluster_labels)
    
    # 计算 V-Measure Score
    v_measure = v_measure_score(true_labels, cluster_labels)
    
    return silhouette, v_measure


def visualize_clusters(complete_trend_line: np.ndarray, cluster_labels: np.ndarray) -> None:
    """可视化聚类分析结果"""
    plt.figure(figsize=(10, 6))

    # 绘制散点图,按照聚类标签进行着色
    plt.scatter(np.arange(len(complete_trend_line)), complete_trend_line, c=cluster_labels, cmap='viridis', alpha=0.5, s=10)

    # 标记聚类中心
    cluster_centers = []
    for i in range(max(cluster_labels) + 1):
        cluster_center = np.mean(complete_trend_line[cluster_labels == i])
        cluster_centers.append(cluster_center)
        plt.scatter(np.arange(len(complete_trend_line))[cluster_labels == i], complete_trend_line[cluster_labels == i], label=f'Cluster {i}', alpha=0.5, s=10)
        plt.plot([0, len(complete_trend_line)], [cluster_center, cluster_center], 'k--')

    plt.title('趋势线的聚类分析')
    plt.xlabel('数据点')
    plt.ylabel('数值')
    plt.legend()
    plt.grid(True)
    plt.show()


def normalize_features(features: np.ndarray) -> np.ndarray:
    """标准化特征"""
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)
    return scaled_features



def detect_lv_dbscan_anomaly(data: list[float], eps: float, min_samples: int, lof_threshold: float) -> None:
    # 将数据转换为NumPy数组
    data_array = np.array(data).reshape(-1, 1)

    # 数据标准化
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(data_array)

    # 使用LV-DBSCAN算法进行聚类
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    dbscan.fit(scaled_data)

    # 获取每个样本的聚类标签
    labels = dbscan.labels_

    # 计算每个样本的局部异常因子（LOF）
    lof_scores = LocalOutlierFactor(n_neighbors=min_samples + 1).fit_predict(scaled_data)

    # 标记异常点
    outliers = np.where(lof_scores == -1)[0]

    # 打印异常点
    print("Detected anomalies:")
    for outlier in outliers:
        print(f"Data point {outlier}: Cluster label: {labels[outlier]}, LOF score: {lof_scores[outlier]}")


def optimize_dbscan_params(data: np.ndarray) -> Tuple[float, float]:
    # 目标函数，用于优化
    def dbscan_objective(params: Tuple[float, float]) -> float:
        eps, min_samples = params
        min_samples = int(min_samples)
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        labels = dbscan.fit_predict(data.reshape(-1, 1))
        # 优化轮廓系数，尽量不要有噪声点
        if len(set(labels)) == 1 or -1 in labels:
            return -1  # 一个簇或者有噪声，轮廓系数无法计算
        score = silhouette_score(data.reshape(-1, 1), labels)
        return -score  # pyswarm 是最小化目标函数

    # 参数范围
    lb: list[float] = [0.1, 2]  # eps的最小值，min_samples的最小值
    ub: list[float] = [2, 20]   # eps的最大值，min_samples的最大值

    # 粒子群优化
    xopt, fopt = pso(dbscan_objective, lb, ub, swarmsize=50, maxiter=100)

    return xopt


def detect_ipsodbscan_anomaly(data: list[float]) -> Tuple[np.ndarray, np.ndarray]:
    # 数据标准化
    scaler = StandardScaler()
    # 将列表转换为NumPy数组，并调整形状为(n_samples, n_features)
    scaled_data = scaler.fit_transform(np.array(data).reshape(-1, 1))
    
    # 使用IPSO优化DBSCAN参数
    eps, min_samples = optimize_dbscan_params(scaled_data)
    min_samples = int(min_samples)

    # 使用优化后的参数运行DBSCAN
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    dbscan.fit(scaled_data)

    # 异常点标记
    labels = dbscan.labels_
    outliers = np.where(labels == -1)[0]

    # 打印结果
    print(f"Optimal eps: {eps}, Optimal min_samples: {min_samples}")
    print("Detected anomalies:", outliers)

    return outliers, labels


def detect_knn_anomaly(data: list[float], k: int = 5, outlier_fraction: float = 0.01) -> tuple[np.ndarray, np.ndarray, float]:
    # 确保数据为NumPy数组
    data = np.array(data).reshape(-1, 1)  # 转换数据为正确的形状

    # 数据标准化
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(data)

    # 训练K近邻模型
    neighbors = NearestNeighbors(n_neighbors=k)
    neighbors.fit(data_scaled)
    
    # 计算每个点到其k个最近邻居的距离
    distances, indices = neighbors.kneighbors(data_scaled)

    # 计算每个点的异常分数（平均距离）
    anomaly_scores = distances.mean(axis=1)

    # 确定异常分数的阈值
    threshold = np.percentile(anomaly_scores, 100 * (1 - outlier_fraction))

    # 检测异常点
    outliers = np.where(anomaly_scores > threshold)[0]
    return outliers, anomaly_scores, threshold


def detect_knn_anomaly_xy(x_points: list[float], y_points: list[float], k: int = 5, outlier_fraction: float = 0.01) -> tuple[np.ndarray, np.ndarray, float]:
    # 将 x_points 和 y_points 合并成一个特征矩阵
    data = np.column_stack((x_points, y_points))

    # 数据标准化
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(data)

    # 训练K近邻模型
    neighbors = NearestNeighbors(n_neighbors=k)
    neighbors.fit(data_scaled)
    
    # 计算每个点到其k个最近邻居的距离
    distances, indices = neighbors.kneighbors(data_scaled)

    # 计算每个点的异常分数（平均距离）
    anomaly_scores = distances.mean(axis=1)

    # 确定异常分数的阈值
    threshold = np.percentile(anomaly_scores, 100 * (1 - outlier_fraction))

    # 检测异常点
    outliers = np.where(anomaly_scores > threshold)[0]
    
    # 打印异常分数的值
    print("异常分数的值:")
    for idx in outliers:
        print(anomaly_scores[idx])
    
    # 打印正常值的分数平均值
    normal_scores_mean = anomaly_scores[np.where(anomaly_scores <= threshold)].mean()
    print("正常值的分数平均值:", normal_scores_mean)
    
    return anomaly_scores, outliers, normal_scores_mean


def detect_anomalies_with_ema(data: list[float], alpha: float = 0.1, threshold_factor: float = 2.0) -> tuple[list[tuple[int, float]], np.ndarray]:
    data_array = np.array(data)
    ema = np.zeros_like(data_array)
    ema[0] = data_array[0]
    for i in range(1, len(data_array)):
        ema[i] = alpha * data_array[i] + (1 - alpha) * ema[i - 1]
    deviations = np.abs(data_array - ema)
    std_deviation = np.std(data_array)
    threshold = std_deviation * threshold_factor
    anomalies = [(index, data_array[index]) for index, deviation in enumerate(deviations) if deviation > threshold]
    return anomalies, ema


def detect_anomalies_with_mad(data: list[float], threshold_factor: float = 3.0) -> list[tuple[int, float]]:
    data_array = np.array(data)
    median = np.median(data_array)
    mad = np.median(np.abs(data_array - median))
    mad_std_equivalent = 1.4826 * mad
    upper_threshold = median + threshold_factor * mad_std_equivalent
    lower_threshold = median - threshold_factor * mad_std_equivalent
    anomalies = [(index, value) for index, value in enumerate(data_array)
                 if value > upper_threshold or value < lower_threshold]
    return anomalies


def detect_anomalies_with_IsolationForest(data: list[float]) -> None:
    data_reshaped = np.array(data).reshape(-1, 1)
    model = IsolationForest(n_estimators=100, contamination=0.1)
    model.fit(data_reshaped)
    predictions = model.predict(data_reshaped)
    print("Anomalies detected at indices:")
    for i, val in enumerate(predictions):
        if val == -1:
            print(f"Index: {i}, Value: {data[i]}")


def detect_anomalies_with_rolling_std(data: list[float], window_size: int, threshold_factor: float = 3.0) -> list[tuple[int, float]]:
    data_series = pd.Series(data)
    rolling_std = data_series.rolling(window=window_size).std()
    std_mean = rolling_std.mean()
    upper_threshold = std_mean + threshold_factor * std_mean
    lower_threshold = std_mean - threshold_factor * std_mean
    anomalies = [(index, data[index]) for index, std_dev in enumerate(rolling_std)
                 if std_dev > upper_threshold or std_dev < lower_threshold]
    return anomalies


def detect_anomalies_with_OneClassSVM(data: list[float]) -> list[tuple[int, float]]:
    data_array = np.array(data).reshape(-1, 1)
    ocsvm = OneClassSVM(nu=0.05, kernel='rbf', gamma='auto')
    ocsvm.fit(data_array)
    predictions = ocsvm.predict(data_array)
    anomaly_indices = np.where(predictions == -1)[0]
    anomalies = [(index, data[index]) for index in anomaly_indices]
    return anomalies