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

class TimeSeriesData:
    def __init__(self, value: float, datetime_input):
        self.value = value
        # Check if the input is a datetime object or a string
        if isinstance(datetime_input, datetime):
            self.datetime = datetime_input
        elif isinstance(datetime_input, str):
            # Parse the datetime string
            try:
                self.datetime = datetime.strptime(datetime_input, "%Y-%m-%d %H:%M:%S.%f")
            except ValueError:
                # If parsing with microseconds fails, try parsing without microseconds
                self.datetime = datetime.strptime(datetime_input, "%Y-%m-%d %H:%M:%S")
        else:
            raise TypeError("datetime_input must be a datetime object or a datetime string in the format '%Y-%m-%d %H:%M:%S' or '%Y-%m-%d %H:%M:%S.%f'")

    def __str__(self):
        return f"Value: {self.value}, Datetime: {self.datetime}"

# region 无关功能
def check_data_type(data: np.ndarray) ->None:
    print("数据类型:", type(data))
    print("形状:", data.shape)


# endregion
# region 基础功能
def load_csv_data(data_file: str = "D:\python_proj\Data_dynamics\data_month_1.txt") -> list[TimeSeriesData]:
    num_data_to_read: int = 100000
    time_series_data: list[TimeSeriesData] = []
    count: int = 0

    with open(data_file, 'r') as file:
        for line in file:
            line_data = line.strip().split('\t')
            value: float = float(line_data[1])
            datetime: str = line_data[4]
            time_series_data.append(TimeSeriesData(value, datetime))
            
            count += 1
            if count == num_data_to_read:
                break
    return time_series_data


def create_time_series_data(values: List[float], datetimes: List[str]) -> list[TimeSeriesData]:
    """给values和datetimes return一个time_series_data"""
    time_series_data: list[TimeSeriesData] = []
    for value, datetime in zip(values, datetimes):
        data: TimeSeriesData = TimeSeriesData(value, datetime)
        time_series_data.append(data)
    return time_series_data


def remove_average(data: list[TimeSeriesData]) -> None:
    """对时序数据进行去平均 再乘以1000"""
    mean_value = np.mean([point.value for point in data])
    remove_specific_value(data, mean_value)


def remove_specific_value(data: List[TimeSeriesData], specific_value: float) -> None:
    """对时序数据进行减去特定值 再乘以1000"""
    # 减去平均值并乘以1000
    for point in data:
        point.value = (point.value - specific_value) * 1000
    

def plot_TimeSeriesData(TimeSeriesData: list[TimeSeriesData], isShow: bool = False, SaveFilePath: Optional[str] = None) -> None:
    """绘制TimeSeriesData对象的时间序列图"""
    values = [data.value for data in TimeSeriesData]
    datetimes = [data.datetime for data in TimeSeriesData]

    # 修改标签和标题的文本为中文
    plt.figure(figsize=(14.4, 9.6)) # 单位是英寸
    plt.xlabel('日期')
    plt.ylabel('数值')
    plt.title('时间序列数据')

    # 设置日期格式化器和日期刻度定位器
    date_fmt = mdates.DateFormatter("%m-%d")  # 仅显示月-日
    date_locator = mdates.AutoDateLocator()  # 自动选择刻度间隔
    plt.gca().xaxis.set_major_formatter(date_fmt)
    plt.gca().xaxis.set_major_locator(date_locator)
    
    # 设置最大显示的刻度数
    plt.gcf().autofmt_xdate()  # 旋转日期标签以避免重叠
    plt.tight_layout()  # 自动调整子图间的间距和标签位置

    plt.plot(datetimes, values)

    if SaveFilePath is not None:
        plt.savefig(SaveFilePath)
    elif isShow:
        plt.show()
    plt.close()


def plot_TimeSeriesData_in_threshold(TimeSeriesData: list[TimeSeriesData], threshold: timedelta, isShow: bool = False, SaveFilePath: Optional[str] = None) -> None:
    """绘制TimeSeriesData对象的时间序列图"""
    values = [data.value for data in TimeSeriesData]
    datetimes = [data.datetime for data in TimeSeriesData]

    # 修改标签和标题的文本为中文
    plt.figure(figsize=(14.4, 9.6)) # 单位是英寸
    plt.xlabel('日期')
    plt.ylabel('数值')
    plt.title('时间序列数据')

    # 设置日期格式化器和日期刻度定位器
    date_fmt = mdates.DateFormatter("%m-%d")  # 仅显示月-日
    date_locator = mdates.AutoDateLocator()  # 自动选择刻度间隔
    plt.gca().xaxis.set_major_formatter(date_fmt)
    plt.gca().xaxis.set_major_locator(date_locator)
    
    # 设置最大显示的刻度数
    plt.gcf().autofmt_xdate()  # 旋转日期标签以避免重叠
    plt.tight_layout()  # 自动调整子图间的间距和标签位置

    # 绘制折线图，根据阈值连接或不连接线段
    prev_datetime = None
    prev_value = None
    for datetime, value in zip(datetimes, values):
        if prev_datetime is not None:
            time_diff = datetime - prev_datetime
            if time_diff < threshold:  # 如果时间间隔小于阈值，则连接线段
                plt.plot([prev_datetime, datetime], [prev_value, value], linestyle='-', color='blue')
            else:  # 否则不连接线段
                plt.plot([prev_datetime, datetime], [prev_value, value], linestyle='', color='blue')
        prev_datetime = datetime
        prev_value = value

    if SaveFilePath is not None:
        plt.savefig(SaveFilePath)
    elif isShow:
        plt.show()
    plt.close()


def plot_data_with_datetimes(value: List[float], datetimes:List[datetime], color='blue'):
    # 绘制折线图，根据阈值连接或不连接线段，并使用不同颜色
    prev_datetime = None
    prev_value = None
    prev_month = None
    for datetime, value in zip(datetimes, value):
        month = datetime.month
        if prev_datetime is not None:
            time_diff = datetime - prev_datetime
            if time_diff < timedelta(days=2):  # 如果时间间隔小于阈值，则连接线段
                plt.plot([prev_datetime, datetime], [prev_value, value], linestyle='-', color=color)
            else:  # 否则不连接线段
                plt.plot([prev_datetime, datetime], [prev_value, value], linestyle='', color=color)
        prev_datetime = datetime
        prev_value = value
        prev_month = month
    # 显示图形
    plt.show()


def plot_TimeSeriesData_in_season(TimeSeriesData: list[TimeSeriesData], threshold: timedelta, isShow: bool = False, SaveFilePath: Optional[str] = None) -> None:
    """绘制TimeSeriesData对象的时间序列图，根据月份使用不同颜色标识"""
    values = [data.value for data in TimeSeriesData]
    datetimes = [data.datetime for data in TimeSeriesData]

    # 设置颜色映射
    color_map = {1: (242, 204, 142),   # 1、2、3月份
                 2: (242, 204, 142),
                 3: (242, 204, 142),
                 4: (223, 122, 94),    # 4、5、6月份
                 5: (223, 122, 94),
                 6: (223, 122, 94),
                 7: (60, 64, 91),      # 7、8、9月份
                 8: (60, 64, 91),
                 9: (60, 64, 91),
                 10: (130, 178, 154),  # 10、11、12月份
                 11: (130, 178, 154),
                 12: (130, 178, 154)}

    # 修改标签和标题的文本为中文
    plt.figure(figsize=(14.4, 9.6)) # 单位是英寸
    plt.xlabel('日期')
    plt.ylabel('数值')
    plt.title('时间序列数据')

    # 设置日期格式化器和日期刻度定位器
    date_fmt = mdates.DateFormatter("%m-%d")  # 仅显示月-日
    date_locator = mdates.AutoDateLocator()  # 自动选择刻度间隔
    plt.gca().xaxis.set_major_formatter(date_fmt)
    plt.gca().xaxis.set_major_locator(date_locator)
    
    # 设置最大显示的刻度数
    plt.gcf().autofmt_xdate()  # 旋转日期标签以避免重叠
    plt.tight_layout()  # 自动调整子图间的间距和标签位置

    # 绘制折线图，根据阈值连接或不连接线段，并使用不同颜色
    prev_datetime = None
    prev_value = None
    prev_month = None
    for datetime, value in zip(datetimes, values):
        month = datetime.month
        if prev_datetime is not None:
            time_diff = datetime - prev_datetime
            if time_diff < threshold:  # 如果时间间隔小于阈值，则连接线段
                color = tuple(c/255 for c in color_map[month])  # 将RGB转换为范围在0到1之间的值
                plt.plot([prev_datetime, datetime], [prev_value, value], linestyle='-', color=color)
            else:  # 否则不连接线段
                color = tuple(c/255 for c in color_map[prev_month])  # 将RGB转换为范围在0到1之间的值
                plt.plot([prev_datetime, datetime], [prev_value, value], linestyle='', color=color)
        prev_datetime = datetime
        prev_value = value
        prev_month = month

    if SaveFilePath is not None:
        plt.savefig(SaveFilePath)
    elif isShow:
        plt.show()
    plt.close()


def plot_TimeSeriesData_Compare(TimeSeriesData1: list[TimeSeriesData], TimeSeriesData2: list[TimeSeriesData], SaveFilePath: Optional[str] = None) -> None:
    """绘制两个TimeSeriesData对象的时间序列图"""
    values1 = [data.value for data in TimeSeriesData1]
    datetimes1 = [data.datetime for data in TimeSeriesData1]

    values2 = [data.value for data in TimeSeriesData2]

    # 修改标签和标题的文本为中文
    plt.figure(figsize=(14.4, 9.6)) # 单位是英寸
    plt.xlabel('日期')
    plt.ylabel('数值')
    plt.title('时间序列数据')

    # 设置日期格式化器和日期刻度定位器
    date_fmt = mdates.DateFormatter("%m-%d")  # 仅显示月-日
    date_locator = mdates.AutoDateLocator()  # 自动选择刻度间隔
    plt.gca().xaxis.set_major_formatter(date_fmt)
    plt.gca().xaxis.set_major_locator(date_locator)
    
    # 设置最大显示的刻度数
    plt.gcf().autofmt_xdate()  # 旋转日期标签以避免重叠
    plt.tight_layout()  # 自动调整子图间的间距和标签位置

    plt.plot(datetimes1, values1, label='TimeSeriesData1')
    plt.plot(datetimes1, values2, label='TimeSeriesData2')

    plt.legend()  # 显示图例

    if SaveFilePath is not None:
        plt.savefig(SaveFilePath)
    else:
        plt.show()
    plt.close()


def generate_random_data() -> list[TimeSeriesData]:
    """生成随机的 TimeSeriesData 数据"""
    start_date: datetime = datetime(2024, 3, 13, 0, 0, 0)
    data: list[TimeSeriesData] = []

    for i in range(150):
        value: int = random.randint(10, 30)
        current_date: datetime = start_date + timedelta(hours=i)
        data_point: TimeSeriesData = TimeSeriesData(value=value, datetime=current_date)
        data.append(data_point)

    return data

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

def convert_latlon_coordinates(lat_tsd: List[TimeSeriesData], lon_tsd: List[TimeSeriesData]) -> tuple[List[TimeSeriesData], List[TimeSeriesData]]:
    # 转换后的时序数据列表
    converted_lat_tsd = []
    converted_lon_tsd = []
    
    for lat, lon in zip(lat_tsd, lon_tsd):
        # 对纬度和经度进行坐标转换
        converted_lat, converted_lon = convert_coordinates(lat.value, lon.value)
        
        # 创建新的 TimeSeriesData 对象并添加到列表中
        converted_lat_tsd.append(TimeSeriesData(converted_lat, lat.datetime))
        converted_lon_tsd.append(TimeSeriesData(converted_lon, lon.datetime))
    
    return converted_lat_tsd, converted_lon_tsd
# endregion
# region 基础统计分析
def calculate_mean(TimeSeriesData: list[TimeSeriesData]) -> float:
    """计算TimeSeriesData对象的平均值"""
    total = sum([data.value for data in TimeSeriesData])
    mean = total / len(TimeSeriesData)
    return mean


def calculate_median(TimeSeriesData: list[TimeSeriesData]) -> float:
    """计算TimeSeriesData对象的中位数"""
    sorted_data = sorted(TimeSeriesData, key=lambda data: data.value)
    n = len(sorted_data)
    if n % 2 == 0:
        median = (sorted_data[n // 2 - 1].value + sorted_data[n // 2].value) / 2
    else:
        median = sorted_data[n // 2].value
    return median


def calculate_variance(TimeSeriesData: list[TimeSeriesData]) -> float:
    """计算TimeSeriesData对象的方差"""
    mean = calculate_mean(TimeSeriesData)
    squared_diff = [(data.value - mean) ** 2 for data in TimeSeriesData]
    variance = sum(squared_diff) / len(TimeSeriesData)
    return variance


def calculate_standard_deviation(TimeSeriesData: list[TimeSeriesData]) -> float:
    """计算TimeSeriesData对象的标准差"""
    variance = calculate_variance(TimeSeriesData)
    standard_deviation = math.sqrt(variance)
    return standard_deviation


def calculate_change_rate(timeSeriesdata: list[TimeSeriesData]) -> List[float]:
    """计算TimeSeriesData对象的变化率"""
    change_rates = []
    for i in range(1, len(timeSeriesdata)):
        current_value = timeSeriesdata[i].value
        previous_value = timeSeriesdata[i-1].value
        change_rate = (current_value - previous_value) / previous_value
        change_rates.append(change_rate)
    return change_rates


def calculate_correlation_Pearson(data1: List[TimeSeriesData], data2: List[TimeSeriesData]) -> float:
    # 转换为 Pandas DataFrame
    df1 = pd.DataFrame([(ts.datetime, ts.value) for ts in data1], columns=['Datetime', 'Value']).set_index('Datetime')
    df2 = pd.DataFrame([(ts.datetime, ts.value) for ts in data2], columns=['Datetime', 'Value']).set_index('Datetime')
    
    # 确保两个 DataFrame 在计算相关性前在同一时间轴对齐
    combined_df = df1.join(df2, lsuffix='_1', rsuffix='_2')
    
    # 使用 Pandas 的 corr 方法计算相关性
    pearson_correlation = combined_df['Value_1'].corr(combined_df['Value_2'])
    
    print("皮尔逊相关系数:", pearson_correlation)
    
    return pearson_correlation


def get_x_values(data: list[TimeSeriesData]) -> List[int]:
    """获取时间步作为x值"""
    # 获取时间步作为x值
    x = []
    for i in range(len(data)):
        x.append(i)
    return x


def get_y_values(data: list[TimeSeriesData]) -> List[float]:
    """获取数值作为y值"""
    # 使用列表推导式获取数值作为y值
    y = [entry.value for entry in data]
    return y


def calculate_trend_line_residuals(data: list[TimeSeriesData], trend_line: np.ndarray) -> np.ndarray:
    """计算残差"""
    y = get_y_values(data)
    residuals = np.array(y) - trend_line
    return residuals


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
def fit_polynomial_trend(data: list[TimeSeriesData], degree: int = 3) -> np.ndarray:
    """拟合多项式趋势线"""
    # 拟合多项式趋势线
    x = get_x_values(data)
    y = get_y_values(data)
    coefficients = np.polyfit(x, y, degree)
    trend_line = np.polyval(coefficients, x)
    return trend_line


def calculate_trend_line_r_squared(data: list[TimeSeriesData], trend_line: np.ndarray) -> float:
    """计算趋势线拟合度"""
    y = get_y_values(data)
    y_mean = np.mean(y)
    
    # 计算总平方和 TSS
    tss = np.sum((y - y_mean) ** 2)
    
    # 计算残差平方和 ESS
    ess = np.sum((y - trend_line) ** 2)
    
    # 计算 R 方值
    r_squared = 1 - (ess / tss)
    
    return r_squared


def plot_trend_line_residuals(data: list[TimeSeriesData], residuals: np.ndarray, SaveFilePath: Optional[str] = None) -> None:
    """绘制残差图"""
    x = get_x_values(data)
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
    

def find_Ridge_best_degree(data: list[TimeSeriesData]) -> None:
    """找到 Ridge 回归模型最佳的阶数"""
    x = get_x_values(data)
    y = get_y_values(data)
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


def find_Lasso_best_degree(data: list[TimeSeriesData]) -> None:
    """找到 Lasso 回归模型最佳的阶数"""
    x = get_x_values(data)
    y = get_y_values(data)
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


def find_Ridge_best_degree_MSE(data: List[TimeSeriesData]) -> tuple[int, float]:
    """找到 Ridge 回归模型最佳的阶数"""
    x = get_x_values(data)
    y = get_y_values(data)
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


def calculate_AIC(data: List[TimeSeriesData], y_pred: np.ndarray, degree: int) -> float:
    """计算AIC值"""
    n = len(data)
    k = degree + 1  # 参数数量为阶数加上截距项
    mse = mean_squared_error(get_y_values(data), y_pred)
    likelihood = (n * math.log(2 * math.pi * mse) + n) / 2  # 根据高斯分布的似然函数计算
    AIC = 2 * k - 2 * math.log(likelihood)
    return AIC


def find_best_Lasso_degree_using_AIC(data: List[TimeSeriesData]) -> Tuple[int, float]:
    """利用AIC找到最佳的Lasso回归模型阶数"""
    x = get_x_values(data)
    y = get_y_values(data)
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


def calculate_BIC(data: List[TimeSeriesData], y_pred: np.ndarray, degree: int) -> float:
    """计算BIC值"""
    n = len(data)
    k = degree + 1  # 参数数量为阶数加上截距项
    mse = mean_squared_error(get_y_values(data), y_pred)
    likelihood = (n * math.log(2 * math.pi * mse) + n) / 2  # 根据高斯分布的似然函数计算
    BIC = k * math.log(n) - 2 * math.log(likelihood)
    return BIC


def find_best_Lasso_degree_using_BIC(data: List[TimeSeriesData]) -> Tuple[int, float]:
    """利用BIC找到最佳的Lasso回归模型阶数"""
    x = get_x_values(data)
    y = get_y_values(data)
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


def fit_Ridge_polynomial_trend(data: list[TimeSeriesData], degree: int=11, alpha: float=1.0) -> np.ndarray:
    """使用岭回归拟合多项式趋势线"""
    x = np.array(get_x_values(data))
    y = np.array([point.value for point in data])

    # 创建 Polynomial 特征转换器
    polynomial_features = PolynomialFeatures(degree=degree)
    X_poly = polynomial_features.fit_transform(x.reshape(-1, 1))

    # 创建岭回归模型
    ridge = Ridge(alpha=alpha)
    ridge.fit(X_poly, y)

    # 预测拟合结果
    y_pred = ridge.predict(X_poly)

    return y_pred


def fit_Lasso_polynomial_trend(data: list[TimeSeriesData], degree: int=11, alpha: float=1.0) -> np.ndarray:
    """使用Lasso回归拟合多项式趋势线"""
    x = np.array(get_x_values(data))
    y = np.array([point.value for point in data])

    # 创建 Polynomial 特征转换器
    polynomial_features = PolynomialFeatures(degree=degree)
    X_poly = polynomial_features.fit_transform(x.reshape(-1, 1))

    # 创建Lasso回归模型
    lasso = Lasso(alpha=alpha)
    lasso.fit(X_poly, y)

    # 预测拟合结果
    y_pred = lasso.predict(X_poly)

    return y_pred


def fit_ElasticNet_polynomial_trend(data: list[TimeSeriesData], degree: int=11, alpha: float=1.0, l1_ratio: float=0.5) -> np.ndarray:
    """使用弹性网络回归拟合多项式趋势线"""
    x = np.array(get_x_values(data))
    y = np.array([point.value for point in data])

    # 创建 Polynomial 特征转换器
    polynomial_features = PolynomialFeatures(degree=degree)
    X_poly = polynomial_features.fit_transform(x.reshape(-1, 1))

    # 创建弹性网络回归模型
    elastic_net = ElasticNet(alpha=alpha, l1_ratio=l1_ratio)
    elastic_net.fit(X_poly, y)

    # 预测拟合结果
    y_pred = elastic_net.predict(X_poly)

    return y_pred


def evaluate_predictions(ridge_pred: np.ndarray, lasso_pred: np.ndarray, elastic_pred: np.ndarray, polynomial_pred: np.ndarray, data: list[TimeSeriesData],degree: int) -> None:
    """评估 Ridge、Lasso、ElasticNet 和多项式拟合的预测结果拟合效果"""
    y_true = get_y_values(data)
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


def plot_polynomial_trend(data: list[TimeSeriesData], y_pred: Union[List[float], np.ndarray], SaveFilePath: Optional[str] = None) -> None:
    """绘制多项式趋势线"""
    # 提取日期时间和数值信息
    datetimes = [point.datetime for point in data]
    values = [point.value for point in data]

    # 修改标签和标题的文本为中文
    plt.figure(figsize=(14.4, 9.6)) # 设置图形大小
    plt.xlabel('日期')
    plt.ylabel('数值')
    plt.title('多项式趋势线')

    # 设置日期格式化器和日期刻度定位器
    date_fmt = mdates.DateFormatter("%m-%d")  # 仅显示月-日
    date_locator = mdates.AutoDateLocator()  # 自动选择刻度间隔
    plt.gca().xaxis.set_major_formatter(date_fmt)
    plt.gca().xaxis.set_major_locator(date_locator)
    
    # 设置最大显示的刻度数
    plt.gcf().autofmt_xdate()  # 旋转日期标签以避免重叠
    plt.tight_layout()  # 自动调整子图间的间距和标签位置

    # 绘制折线图
    plt.plot(datetimes, values, label='原始数据', color='gray')
    plt.plot(datetimes, y_pred, label='多项式趋势线', color='r')

    plt.legend()  # 添加图例
    if SaveFilePath is not None:
        plt.savefig(SaveFilePath)
    else:
        plt.show()
    plt.close()


def visualize_predictions(TimeSeriesData: list[TimeSeriesData], ridge_pred: np.ndarray, lasso_pred: np.ndarray, elastic_pred: np.ndarray, polynomial_pred: np.ndarray, SaveFilePath: str = None) -> None:
    x = np.array([point.datetime for point in TimeSeriesData])
    y_true = np.array([point.value for point in TimeSeriesData])

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


def find_Ridge_best_degree_without_print(data:list[TimeSeriesData]) -> int:
    """找到 Ridge 回归模型最佳的阶数"""
    x = get_x_values(data)
    y = get_y_values(data)
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


def calculate_acceleration(data: list[TimeSeriesData]) -> List[float]:
    """
    计算加速度序列
    时间复杂度为 ( O(n) )
    """
    accelerations = []
    for i in range(1, len(data) - 1):
        dt1 = (data[i].datetime - data[i-1].datetime).total_seconds()
        dt2 = (data[i+1].datetime - data[i].datetime).total_seconds()
        dv1 = data[i].value - data[i-1].value
        dv2 = data[i+1].value - data[i].value
        acceleration = (dv2/dt2 - dv1/dt1) / ((dt1 + dt2) / 2)
        accelerations.append(acceleration)
    return accelerations


def calculate_acceleration_for_cycles(data: list[TimeSeriesData]) -> List[List[float]]:
    """
    计算每个“圈”的加速度序列。
    时间复杂度为 ( O(n) ),其中 n 是数据点的数量。
    """
    # 提取值序列
    values = np.array([point.value for point in data])

    # 寻找峰值
    peaks, _ = find_peaks(values)

    # 如果没有找到足够的峰值,则返回空列表
    if len(peaks) < 2:
        return []

    # 计算每个圈的加速度
    cycle_accelerations = []
    for i in range(len(peaks) - 1):
        cycle_data = data[peaks[i]:peaks[i + 1] + 1]
        accelerations = calculate_acceleration(cycle_data)
        cycle_accelerations.append(accelerations)

    return cycle_accelerations


def plot_acceleration(data: list[TimeSeriesData], accelerations: List[float], SaveFilePath: Optional[str]=None) -> None:
    timestamps = [data[i].datetime for i in range(1, len(data) - 1)]
    
    plt.figure(figsize=(10, 5))
    plt.plot(timestamps, accelerations, color='blue', marker='.', linestyle='-')  # 将 marker 参数设置为更小的点
    plt.title('加速度随时间变化图')
    plt.xlabel('时间戳')
    plt.ylabel('加速度')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    if SaveFilePath is not None:
        plt.savefig(SaveFilePath) 
    else:
        plt.show()
        
    plt.close()


def adaptive_polynomial_fitting(data: list[TimeSeriesData], initial_threshold: float) -> np.ndarray:
    """
    自适应拟合趋势线
    外层循环:外层循环 while n < N - 1: 的执行次数取决于数据的长度 N。假设数据长度为 N,那么外层循环的执行次数为 N 次,时间复杂度为 O(N)。
    内层循环:内层循环 while n + r < N - 1:在最坏情况下,内层循环的执行次数可能会达到 O(N)。
    拟合趋势线和计算相关系数:假设这两个步骤的时间复杂度为 O(M),其中 M 是数据的长度和拟合多项式的阶数中较大的一个。
    总的时间复杂度可以近似为 O(N^2 * M),其中 N 是数据的长度,M 是拟合多项式的阶数。
    """
    N = len(data)
    trend_lines = []  # 存储所有拟合的趋势线
    accelerations = calculate_acceleration(data)  # 预先计算所有加速度值

    n = 0
    original_threshold = initial_threshold  # 保存原始阈值

    while n < N - 1:
        r = 1
        while n + r < N - 1:
            segment_accelerations = accelerations[n:n+r]
            Δa = max(segment_accelerations) - min(segment_accelerations)
            if Δa > initial_threshold:
                break
            r += 1
        segment_data = data[n:n+r]
        # 拟合多项式趋势线并计算相关系数
        best_degree = find_Ridge_best_degree_without_print(segment_data)
        trend_line = fit_Ridge_polynomial_trend(segment_data, best_degree)
        correlation = np.corrcoef(np.array([point.value for point in segment_data]), trend_line)[0, 1]
        
        # 检查相关系数是否满足条件
        if correlation < 0.8:
            initial_threshold *= 0.9  # 调整阈值
            continue
        
        # 将当前窗口的拟合趋势线添加到列表中
        trend_lines.append(trend_line)  

        # 更新索引并重置r
        n += r
        r = 1
        
        # 恢复原始阈值
        initial_threshold = original_threshold

    # 将所有拟合的趋势线连接起来,得到完整的趋势线
    complete_trend_line = np.concatenate(trend_lines)
    print(f"complete_trend_line: {len(complete_trend_line)}")  
    return complete_trend_line


def split_TimeSeries_data(data: list[TimeSeriesData], break_points: List[int]) -> List[list[TimeSeriesData]]:
    """根据隔断点将时序数据分割成不同的分组"""
    groups = []
    start_index = 0

    for break_point in break_points:
        group = data[start_index:break_point]
        groups.append(group)
        start_index = break_point

    # 添加最后一个分组
    groups.append(data[start_index:])

    return groups


def fit_and_concatenate_trend_lines(segmented_data: List[list[TimeSeriesData]]) -> np.ndarray:
    """拟合多项式趋势线并将所有拟合的趋势线连接起来"""
    trend_lines = []

    for segment_data in segmented_data:
        # 拟合多项式趋势线并计算相关系数
        best_degree = find_Ridge_best_degree_without_print(segment_data)
        trend_line = fit_Ridge_polynomial_trend(segment_data, best_degree)
        trend_lines.append(trend_line)

    complete_trend_line = np.concatenate(trend_lines)
    return complete_trend_line


def adaptive_polynomial_fitting_in_std(data: list[TimeSeriesData]) -> np.ndarray:
    values = [entry.value for entry in data]
    std_value = np.std(values)
    original_threshold = std_value / 2.0

    initial_threshold = original_threshold
    trend_lines = []  # 存储所有拟合的趋势线
    n, N= 0, len(data)
    while n < N - 1:
        r = 1
        while n + r < N - 1:
            segment_data = data[n:n+r]
            values = [entry.value for entry in segment_data]
            std_value = np.std(values)
            # print(f"{std_value}\t{initial_threshold} n: {n} r: {r} ")
            if std_value > initial_threshold:
                break
            r += 1
        # 拟合多项式趋势线并计算相关系数
        best_degree = find_Ridge_best_degree_without_print(segment_data)
        trend_line = fit_Ridge_polynomial_trend(segment_data, best_degree)
        correlation = np.corrcoef(np.array([point.value for point in segment_data]), trend_line)[0, 1]
        # print(f"tl: {len(trend_line)}, sgd: {len(segment_data)} n: {n} r: {r} correlation: {correlation}")

        # 检查相关系数是否满足条件
        if correlation < 0.8:
            initial_threshold *= 0.9  # 调整阈值
            continue
        
        # 将当前窗口的拟合趋势线添加到列表中
        trend_lines.append(trend_line)  
        
        # 更新索引并重置r
        n += r
        r = 1
        
        # 恢复原始阈值
        initial_threshold = original_threshold
        # 将所有拟合的趋势线连接起来,得到完整的趋势线

    complete_trend_line = np.concatenate(trend_lines)
    # print(f"complete_trend_line: {len(complete_trend_line)}")  
    return complete_trend_line


def adaptive_polynomial_fitting_in_cusum(data: list[TimeSeriesData]) -> np.ndarray:
    """
    基于cusum值自适应拟合趋势线
    """
    cusum_values = cusum(data, 1)
    original_threshold = determine_threshold(cusum_values)   
    initial_threshold = original_threshold
    trend_lines = []  # 存储所有拟合的趋势线
    n, N= 0, len(data)
    while n < N - 1:
        r = 1
        while n + r < N - 1:
            segment_data = data[n:n+r]
            cusum_total_value = cusum_total(segment_data)
            print(f"{cusum_total_value}\t{initial_threshold} n: {n} r: {r} ")
            if cusum_total_value > initial_threshold:
                break
            r += 1
        # 拟合多项式趋势线并计算相关系数
        best_degree = find_Ridge_best_degree_without_print(segment_data)
        trend_line = fit_Ridge_polynomial_trend(segment_data, best_degree)
        correlation = np.corrcoef(np.array([point.value for point in segment_data]), trend_line)[0, 1]
        print(f"tl: {len(trend_line)}, sgd: {len(segment_data)} n: {n} r: {r} correlation: {correlation}")

        # 检查相关系数是否满足条件
        if correlation < 0.8:
            initial_threshold *= 0.9  # 调整阈值
            continue
        
        # 将当前窗口的拟合趋势线添加到列表中
        trend_lines.append(trend_line)  
        
        # 更新索引并重置r
        n += r
        r = 1
        
        # 恢复原始阈值
        initial_threshold = original_threshold
        # 将所有拟合的趋势线连接起来,得到完整的趋势线

    complete_trend_line = np.concatenate(trend_lines)
    # print(f"complete_trend_line: {len(complete_trend_line)}")  
    return complete_trend_line


def calculate_cusum(time_series: list[TimeSeriesData], target: float) -> Tuple[List[float], List[float]]:
    """
    """
    cusum_pos = [0]  # Positive CUSUM values
    cusum_neg = [0]  # Negative CUSUM values
    for data in time_series[1:]:  # Skipping the first element as we've initialized with it
        deviation = data.value - target
        cusum_pos.append(max(0, cusum_pos[-1] + deviation))
        cusum_neg.append(min(0, cusum_neg[-1] + deviation))
    return cusum_pos, cusum_neg

def plot_cusum_pos_and_neg(cusum_pos: List[float], cusum_neg: List[float]) -> None:
    # 绘图
    plt.figure(figsize=(12, 6))
    plt.plot(cusum_pos, label='CUSUM正向', color='blue')
    plt.plot(cusum_neg, label='CUSUM负向', color='red')
    plt.axhline(y=0, color='k', linestyle='--')  # 目标线
    plt.xlabel('观测数目')
    plt.ylabel('CUSUM值')
    plt.title('CUSUM控制图')
    plt.legend()
    plt.show()
# endregion
# region 频域分析
def fourier_transform(TimeSeriesData: List[TimeSeriesData]) -> np.ndarray:
    """对TimeSeriesData对象进行傅里叶变换"""
    values = [data.value for data in TimeSeriesData]
    transformed_values = np.fft.fft(values)
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


def plot_filtered_data(filtered_data: np.ndarray, SaveFilePath: str = None) -> None:
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


def analyze_fourier_transform_results(data: List[TimeSeriesData], SaveFilePath: Optional[str] = None) -> None:
    """
    函数 analyze_fourier_transform_results 用于计算和可视化 TimeSeriesData 数据的振幅谱,并识别数据中的主要周期分量。
    
    :param data: TimeSeriesData 类型的列表,包含 value 和 datetime 属性。
    """
    # 提取 value 值和构建时间序列
    values = [entry.value for entry in data]
    datetime = [entry.datetime for entry in data]

    # 计算采样率
    sampling_rate = (data[-1].datetime - data[0].datetime).total_seconds() / len(data)

    # 进行傅里叶变换
    transformed_values = np.fft.fft(values)

    # 构建频率轴
    N = len(data)  # 数据的长度
    frequencies = np.fft.fftfreq(N, d=sampling_rate)

    # 获取右半边的频率和对应的振幅值
    frequencies_right = frequencies[:N//2+1]
    transformed_values_right = transformed_values[:N//2+1]
    plt.figure(figsize=(14.4, 9.6)) # 单位是英寸
    # 可视化振幅谱
    plt.plot(frequencies_right, np.abs(transformed_values_right))
    plt.xlabel('频率')
    plt.ylabel('振幅')
    plt.title('振幅谱')
    plt.grid(True)
    if SaveFilePath is not None:
        plt.savefig(SaveFilePath)
    else:
        plt.show()
    plt.close()

    """
    通过绘制频谱的幅度谱图,可以观察不同频率成分的能量分布情况。从图中你可以获取以下信息:
    峰值表示在该频率上存在主要的周期性成分。
    频谱中的宽峰表示存在多个相关频率的周期性成分。
    幅度谱中较低的值表示在该频率上不存在明显的周期性成分。
    """

def chebyshev_filter(TimeSeriesData: List[TimeSeriesData], cutoff_freq: float = 0.8, order: int = 4, filter_type: str = 'lowpass') -> Tuple[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
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
    data = np.array([data.value for data in TimeSeriesData])

    # 计算滤波器的参数
    b, a = signal.cheby1(order, 0.5, cutoff_freq, btype=filter_type, analog=False, output='ba')

    # 应用滤波器
    filtered_data = signal.filtfilt(b, a, data)

    return filtered_data
# endregion
# region 移动平均
def moving_average(TimeSeriesData: List[TimeSeriesData], window_size: int) -> List[float]:
    """计算移动平均值"""
    values = [data.value for data in TimeSeriesData]
    datetimes = [data.datetime for data in TimeSeriesData]
    n = len(values)
    moving_avg = []

    for i in range(n - window_size + 1):
        window_values = values[i : i + window_size]
        avg = sum(window_values) / window_size
        moving_avg.append(avg)

    return moving_avg


def plot_moving_average(TimeSeriesData: List[TimeSeriesData], window_size: int, SaveFilePath: str = None) -> None:
    """绘制移动平均线"""
    avg_values = moving_average(TimeSeriesData, window_size)
    datetimes = [data.datetime for data in TimeSeriesData]
    moving_date=datetimes[window_size - 1:]

    plt.figure(figsize=(14.4, 9.6)) # 单位是英寸
    plt.plot(moving_date, avg_values, label="移动平均")
    plt.xlabel('日期')  # 指定中文标签
    plt.ylabel('数值') # 指定中文标签
    plt.title('移动平均线')  # 指定中文标签

    # 设置日期格式化器和日期刻度定位器
    date_fmt = mdates.DateFormatter("%m-%d")  # 仅显示月-日
    date_locator = mdates.DayLocator()  # 每天显示一个刻度

    plt.gca().xaxis.set_major_formatter(date_fmt)
    plt.gca().xaxis.set_major_locator(date_locator)
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
def plot_time_series_decomposition(time_series: List[TimeSeriesData], SaveFilePath: str = None) -> None:
    """进行季节性分解"""
    # 将 TimeSeriesData 转换为 Pandas 的 Series 对象
    values = [data.value for data in time_series]
    datetimes = [data.datetime for data in time_series]
    index = pd.to_datetime(datetimes)
    index = pd.DatetimeIndex(index, freq='2D')
    ts = pd.Series(values, index=index)

  
    # 进行季节性分解
    decomposition = sm.tsa.seasonal_decompose(ts, model='additive')

    # 提取分解后的各部分
    trend = decomposition.trend
    seasonal = decomposition.seasonal
    residual = decomposition.resid

    # 绘制分解后的组成部分
    plt.figure(figsize=(14.4, 9.6)) # 单位是英寸
    fig, axes = plt.subplots(4, 1, figsize=(10, 10), sharex=True)
    ts.plot(ax=axes[0])
    axes[0].set_ylabel('原始数据')
    trend.plot(ax=axes[1])
    axes[1].set_ylabel('趋势')
    seasonal.plot(ax=axes[2])
    axes[2].set_ylabel('季节性')
    residual.plot(ax=axes[3])
    axes[3].set_ylabel('残差')
    
    plt.xlabel('日期')
    plt.tight_layout()
    if SaveFilePath is not None:
        plt.savefig(SaveFilePath)
    else: 
        plt.show()
    plt.close()


def stl_decomposition(time_series: List[TimeSeriesData], SaveFilePath: Optional[str] = None) -> None:
    """进行季节性分解时序回归模型(STL)"""
    # 将 TimeSeriesData 转换为 Pandas 的 Series 对象
    values = [data.value for data in time_series]
    datetimes = [data.datetime for data in time_series]
    index = pd.to_datetime(datetimes)
    index = pd.DatetimeIndex(index, freq='2D')
    ts = pd.Series(values, index=index)

    # 进行季节性分解时序回归模型(STL)
    result = sm.tsa.STL(ts, seasonal=13).fit()  # 以13为季节周期,可以根据需要进行调整

    # 提取分解后的各部分
    trend = result.trend
    seasonal = result.seasonal
    residual = result.resid

    # 绘制分解后的组成部分
    plt.figure(figsize=(14.4, 9.6)) # 单位是英寸
    fig, axes = plt.subplots(4, 1, figsize=(10, 10), sharex=True)
    ts.plot(ax=axes[0])
    axes[0].set_ylabel('原始数据')
    trend.plot(ax=axes[1])
    axes[1].set_ylabel('趋势')
    seasonal.plot(ax=axes[2])
    axes[2].set_ylabel('季节性')
    residual.plot(ax=axes[3])
    axes[3].set_ylabel('残差')
    
    plt.xlabel('日期')
    plt.tight_layout()
    if SaveFilePath is not None:
        plt.savefig(SaveFilePath)
    else: 
        plt.show()
    plt.close()


# # 创建ARMA模型
# def create_arma_model(time_series: List[TimeSeriesData], order: Tuple[int, int]) -> sm.tsa.ARMA:
#      # 将 TimeSeriesData 转换为 Pandas 的 Series 对象
#     values = [data.value for data in time_series]
#     datetimes = [data.datetime for data in time_series]
#     ts = pd.Series(values, index=datetimes)
#     model = sm.tsa.ARMA(ts, order=order).fit()
#     return model


# 创建ARIMA模型
def create_arima_model(time_series: List[TimeSeriesData], order: Tuple[int, int, int]) -> sm.tsa.ARIMA:
    # 将 TimeSeriesData 转换为 Pandas 的 Series 对象
    values = [data.value for data in time_series]
    datetimes = [data.datetime for data in time_series]
    ts = pd.Series(values, index=datetimes)
    model = sm.tsa.ARIMA(ts, order=order).fit()
    return model


def predict_analyze_evaluate(time_series: List[TimeSeriesData], order: Tuple[int, int, int] = (2, 1, 1), SaveFilePath: Optional[str] = None) -> None:
    # 将 TimeSeriesData 转换为 Pandas 的 Series 对象
    values = [data.value for data in time_series]
    datetimes = [data.datetime for data in time_series]
    ts = pd.Series(values, index=datetimes)
    
    # 创建ARIMA模型
    arima_model = sm.tsa.ARIMA(ts, order=order).fit()
    
    arima_predictions = arima_model.predict(start=len(ts), end=len(ts)+2)
    
    print("ARIMA模型预测结果:", arima_predictions)
    
    # 残差分析
    arima_residuals = arima_model.resid
    plt.figure(figsize=(14.4, 9.6)) # 单位是英寸
    plt.subplot(1, 2, 1)
    plt.plot(arima_residuals)
    plt.xlabel('时间')
    plt.ylabel('残差')
    plt.title('ARIMA模型残差图')

    plt.tight_layout()
    if SaveFilePath is not None:
        plt.savefig(SaveFilePath)
    else: 
        plt.show()
    plt.close()
    
    # 模型评估
    arima_aic = arima_model.aic

    print("ARIMA模型AIC:", arima_aic)
# endregion
# region 突变检测
def kendall_change_point_detection(input_data: List[TimeSeriesData]) -> List[TimeSeriesData]:
    """时序数据的kendall突变点检测"""
    n = len(input_data)
    Sk = [0]
    UFk = [0]
    s = 0
    Exp_value = [0]
    Var_value = [0]

    for i in range(1, n):
        for j in range(i):
            if input_data[i].value > input_data[j].value:
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
            if input_data_t[i].value > input_data_t[j].value:
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
            K.append(input_data[k])

    # 绘图代码可以在这里添加,如果需要的话

    return K


def pettitt_change_point_detection(data: List[TimeSeriesData]) -> Tuple[int, float]:
    """
    使用Pettitt突变检测方法检测时间序列数据中的突变点。

    :param data: TimeSeriesData 类型的列表,包含 value 和 datetime 属性。
    :return: 突变点的位置和统计量。
    """
    # 提取 value 值
    values = [entry.value for entry in data]

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


def cusum(data: list[TimeSeriesData], threshold: float=1) -> List[float]:
    """
    计算CUSUM
    设置阈值,根据具体情况调整
    """
    # 计算CUSUM
    cusum_values = [0]  # 起始值为0
   
    for i in range(1, len(data)):
        diff = data[i].value - data[i-1].value
        cusum_values.append(max(0, cusum_values[i-1] + diff - threshold))
    
    return cusum_values


def cusum_total(data: list[TimeSeriesData], threshold: float=1) -> float:
    """
    计算整段数据的CUSUM值
    """
    cusum_value = 0  # 初始CUSUM值为0

    for i in range(1, len(data)):
        diff = data[i].value - data[i-1].value
        cusum_value = max(0, cusum_value + diff - threshold)
    
    return cusum_value


def save_list_to_txt(data: List[float], filename: str) -> None:
    with open(filename, 'w') as file:
        for item in data:
            file.write(str(item) + '\n')


def cusum_z_transform(data: list[TimeSeriesData], threshold: float=1) -> List[float]:
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


def plot_cusum(data: list[TimeSeriesData], cusum_values: List[float], SaveFilePath: Optional[str] = None) -> None:
    """绘制CUSUM"""
    # 绘制CUSUM
    x = np.arange(len(data))
    y = get_y_values(data)
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


def calculate_rolling_std(data: list[TimeSeriesData], window_size: int) -> List[float]:
    """滚动标准差来检测波动性的变动"""
    values = [item.value for item in data]  # 提取时序数据中的值
    rolling_std = np.std(values[:window_size])  # 初始窗口的标准差
    std_values = [rolling_std]

    for i in range(window_size, len(values)):
        window_values = values[i-window_size+1:i+1]
        rolling_std = np.std(window_values)
        std_values.append(rolling_std)
    
    return std_values


def calculate_cumulative_std(data: list[TimeSeriesData]) -> List[float]:
    """计算每个点到data[0:n]的标准差"""
    values = [item.value for item in data]  # 提取时序数据中的值
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


def calculate_cumulative_std_with_break(data: list[TimeSeriesData], threshold: float = 1.5) -> Tuple[List[float], List[int]]:
    """计算每个点到data[0:n]的标准差,如果超过阈值则隔断,并记录隔断点的索引位置"""
    values = [item.value for item in data]  # 提取时序数据中的值
    std_values = []
    break_points = []  # 记录隔断点的索引位置
    start_index = 0  # 开始计算的索引

    for i in range(1, len(values) + 1):
        current_std = np.std(values[start_index:i])
        if current_std > threshold:
            # 如果当前的标准差超过了阈值,记录隔断点的索引位置,并重置开始索引为当前位置
            start_index = i - 1  # 重置为当前位置,因为i是从1开始的
            std_values.append(None)  # 使用 None 表示隔断点
            break_points.append(start_index)
        else:
            std_values.append(current_std)

    return std_values, break_points


def apply_grubbs_test(data: list[TimeSeriesData], alpha: float=0.05) -> List[float]:
    """实现格拉布斯检验函数"""
    values = [item.value for item in data]
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
        values = [item.value for item in data]
        n -= 1

    return outliers


def calculate_z_scores(data: list[TimeSeriesData]) -> List[float]:
    """计算Z分数"""
    values = [item.value for item in data]
    mean = np.mean(values)
    std = np.std(values)
    z_scores = []
    for item in data:
        z_score = (item.value - mean) / std
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


def apply_dbscan_clustering(data: List[TimeSeriesData], epsilon: float, min_samples: int) -> dict[int, List[TimeSeriesData]]:
    """
    实现DBSCAN聚类函数
    epsilon = 0.5  # DBSCAN的邻域半径
    min_samples = 5  # 聚类的最小样本数
    clusters = apply_dbscan_clustering(data, epsilon, min_samples)
    """
    values = np.array([item.value for item in data]).reshape(-1, 1)
    
    dbscan = DBSCAN(eps=epsilon, min_samples=min_samples).fit(values)
    labels = dbscan.labels_
    
    clusters = {}
    for i, label in enumerate(labels):
        if label in clusters:
            clusters[label].append(data[i])
        else:
            clusters[label] = [data[i]]
    return clusters


def sliding_t_test(time_series_data: List[TimeSeriesData], window_size: int = 10, significance_level: float = 0.05) -> List[Tuple[str, float, float]]:
    results = []
    
    for i in range(len(time_series_data) - window_size):
        window_values = [data_point.value for data_point in time_series_data[i:i+window_size]]
        mean_before = np.mean(window_values[:window_size // 2])
        mean_after = np.mean(window_values[window_size // 2:])
        std_dev = np.std(window_values)
        t_statistic = (mean_after - mean_before) / (std_dev / np.sqrt(window_size // 2))
        p_value = 2 * (1 - t.cdf(abs(t_statistic), df=window_size - 1))
        results.append((time_series_data[i + window_size // 2].datetime, t_statistic, p_value))
    
    return results


def calculate_control_limits(data: List[TimeSeriesData]) -> Tuple[float, float, float, float, float, float]:
    values = np.array([point.value for point in data])
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

def plot_x_hart_control_chart(data: list[TimeSeriesData], SaveFilePath: Optional[str]=None) -> None:
    CL_X_bar, UCL_X_bar, LCL_X_bar, CL_R, UCL_R, LCL_R = calculate_control_limits(data)

    values = [point.value for point in data]
    dates = [point.datetime for point in data]

    plt.figure(figsize=(12, 6))

    plt.subplot(2, 1, 1)
    plt.plot(dates, values, 'b-', label='数据值')
    plt.axhline(y=CL_X_bar, color='r', linestyle='--', label='中心线')
    plt.axhline(y=UCL_X_bar, color='g', linestyle='--', label='上控制限')
    plt.axhline(y=LCL_X_bar, color='g', linestyle='--', label='下控制限')
    plt.title('X-bar 控制图')
    plt.xlabel('日期')
    plt.ylabel('数值')
    plt.legend()

    plt.subplot(2, 1, 2)
    R_values = np.abs(np.diff(values))
    plt.plot(dates[:-1], R_values, 'b-', label='R 值')
    plt.axhline(y=CL_R, color='r', linestyle='--', label='中心线')
    plt.axhline(y=UCL_R, color='g', linestyle='--', label='上控制限')
    plt.axhline(y=LCL_R, color='g', linestyle='--', label='下控制限')
    plt.title('R 控制图')
    plt.xlabel('日期')
    plt.ylabel('范围')
    plt.legend()

    plt.tight_layout()
    if SaveFilePath is not None:
        plt.savefig(SaveFilePath) 
    else:
        plt.show()
    plt.close()


def ewma(data: List[TimeSeriesData], alpha: float = 0.2) -> np.ndarray:
    """
    计算指数加权移动平均 (Exponential Weighted Moving Average, EWMA)

    Args:
    - data (List[TimeSeriesData]): 数据序列,包含时间和数值
    - alpha (float): 平滑系数, 控制对最新观测值的权重, 通常取值范围为[0, 1]

    Returns:
    - np.ndarray: 指数加权移动平均序列
    """
    ewma_values = [data[0].value]  # 初始化第一个值为初始EWMA值
    for i in range(1, len(data)):
        ewma_values.append(alpha * data[i].value + (1 - alpha) * ewma_values[-1])
    return np.array(ewma_values)


def calculate_control_limits_ewma(data: List[TimeSeriesData], alpha: float = 0.2) -> Tuple[float, float, float]:
    """
    计算EWMA控制图的控制限

    Args:
    - data (List[TimeSeriesData]): 数据序列,包含时间和数值
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


def plot_control_limits_ewma(data: list[TimeSeriesData], alpha=0.2, SaveFilePath: Optional[str]=None) -> None:
    # 将数据转换为列表以便计算
    data_values = [point.value for point in data]

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
def calculate_similarity(ts1: List[float], ts2: List[float], similarity_metric: str = 'euclidean') -> float:
    """
    计算两个时间序列之间的相似性或差异性
    
    Args:
        ts1 (list or numpy array): 第一个时间序列
        ts2 (list or numpy array): 第二个时间序列
        similarity_metric (str, optional): 相似性度量方法,默认为'euclidean'(欧氏距离)。可选值包括'euclidean'(欧氏距离),
                                            'pearson'(皮尔逊相关系数)。
    
    Returns:
        float: 两个时间序列之间的相似性或差异性值
    """
    if similarity_metric == 'euclidean':
        # 计算欧氏距离
        similarity = euclidean(ts1, ts2)
    elif similarity_metric == 'pearson':
        # 计算皮尔逊相关系数
        similarity = np.corrcoef(ts1, ts2)[0, 1]
    else:
        raise ValueError("不支持的相似性度量方法")

    return similarity


def time_series_clustering(ts_data: List[TimeSeriesData], num_clusters: int) -> np.ndarray:
    """
    对时间序列数据进行聚类
    
    Args:
        ts_data (List[TimeSeriesData]): 时间序列数据
        num_clusters (int): 聚类的数量
    
    Returns:
        np.ndarray: 每个时间序列的聚类标签
    """
    # 取出时间序列数据的值
    values = [data.value for data in ts_data]
    
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
def min_max_normalization(data: List[TimeSeriesData]) -> List[TimeSeriesData]:
    """
    使用最小-最大归一化对时序数据进行归一化处理。

    :param data: 要归一化的时间序列数据,TimeSeriesData对象列表。
    :return: 归一化后的TimeSeriesData对象列表。
    """
    values = [entry.value for entry in data]
    min_val = min(values)
    max_val = max(values)
    normalized_values = [(val - min_val) / (max_val - min_val) for val in values]
  
    normalized_data = [
        TimeSeriesData(value, entry.datetime)
        for value, entry in zip(normalized_values, data)
    ]
    return normalized_data


def standardization(data: List[TimeSeriesData]) -> List[TimeSeriesData]:
    """
    使用标准化对时序数据进行归一化处理。

    :param data: 要归一化的时间序列数据,TimeSeriesData对象列表。
    :return: 归一化后的TimeSeriesData对象列表。
    """
    values = [entry.value for entry in data]
    mean_val = np.mean(values)
    std_dev = np.std(values)
    normalized_values = [(val - mean_val) / std_dev for val in values]
  
    normalized_data = [
        TimeSeriesData(value, entry.datetime)
        for value, entry in zip(normalized_values, data)
    ]
    return normalized_data


def decimal_scaling_normalization(data: List[TimeSeriesData]) -> List[TimeSeriesData]:
    """
    使用小数定标归一化对时序数据进行归一化处理。

    :param data: 要归一化的时间序列数据,TimeSeriesData对象列表。
    :return: 归一化后的TimeSeriesData对象列表。
    """
    values = [entry.value for entry in data]
    max_abs = max(abs(min(values)), abs(max(values)))

    normalized_data = [
        TimeSeriesData(value / max_abs, entry.datetime)
        for value, entry in zip(values, data)
    ]
    return normalized_data


def log_normalization(data: List[TimeSeriesData]) -> List[TimeSeriesData]:
    """
    使用对数归一化对时序数据进行归一化处理。

    :param data: 要归一化的时间序列数据,TimeSeriesData对象列表。
    :return: 归一化后的TimeSeriesData对象列表。
    """
    values = [entry.value for entry in data]
    min_val = min(values)
    normalized_values = np.log(values) - np.log(min_val)
  
    normalized_data = [
        TimeSeriesData(value, entry.datetime)
        for value, entry in zip(normalized_values, data)
    ]
  
    return normalized_data


def l1_normalization(data: List[TimeSeriesData]) -> List[TimeSeriesData]:
    """
    使用L1范数归一化对时序数据进行归一化处理。

    :param data: 要归一化的时间序列数据,TimeSeriesData对象列表。
    :return: 归一化后的TimeSeriesData对象列表。
    """
    values = [entry.value for entry in data]
    l1_norm = np.sum(np.abs(values))

    normalized_values = [value / l1_norm for value in values]
  
    normalized_data = [
        TimeSeriesData(value, entry.datetime)
        for value, entry in zip(normalized_values, data)
    ]
  
    return normalized_data


def l2_normalization(data: List[TimeSeriesData]) -> List[TimeSeriesData]:
    """
    使用L2范数归一化对时序数据进行归一化处理。

    :param data: 要归一化的时间序列数据,TimeSeriesData对象列表。
    :return: 归一化后的TimeSeriesData对象列表。
    """
    values = [entry.value for entry in data]
    l2_norm = np.linalg.norm(values)

    normalized_values = [value / l2_norm for value in values]
  
    normalized_data = [
        TimeSeriesData(value, entry.datetime)
        for value, entry in zip(normalized_values, data)
    ]
  
    return normalized_data


# endregion
# region 模态分解
def hilbert_transform(time_series: List[TimeSeriesData]) -> Tuple[np.ndarray, np.ndarray]:
    """对时间序列进行希尔伯特变换
    amplitude_envelope, instantaneous_phase = hilbert_transform(data)
    process_and_plot_hilbert_transform(amplitude_envelope, instantaneous_phase)
    """
    values = [data.value for data in time_series]
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


def empirical_mode_decomposition(time_series_data: List[TimeSeriesData]) -> np.ndarray:
    """对时序数据进行经验模态分解
    imfs = empirical_mode_decomposition(data)
    """
    values = np.array([data.value for data in time_series_data])
    
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


def eemd(time_series_data: List[TimeSeriesData], num_trials: int = 100) -> Tuple[np.ndarray, np.ndarray]:
    """实现EEMD"""
    values = np.array([data.value for data in time_series_data])
    eemd = EEMD()
    eemd.trials = num_trials
    imfs = eemd.eemd(values)
    
    rm = values - np.sum(imfs, axis=0)
    return imfs, rm


def ceemd(time_series_data: List[TimeSeriesData], num_trials: int = 100) -> Tuple[np.ndarray, np.ndarray]:
    """实现CEEMD"""
    values = np.array([data.value for data in time_series_data])
    ceemdan = CEEMDAN(trials=num_trials)
    imfs = ceemdan.ceemdan(values)

    rm = values - np.sum(imfs, axis=0)
    return imfs, rm


def calculate_variance(imfs: np.ndarray) -> List[float]:
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
def ar_model_forecast(TimeSeriesData: List[float], lags: int = 1, future_steps: int = 10, SaveFilePath: Optional[str] = None) -> Tuple[np.ndarray, float]:
    """
    自回归模型(Autoregressive Model, AR)
    """
    # 提取时序数据的观测值
    X = np.array(TimeSeriesData)

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


def ma_model_forecast(TimeSeriesData: List[float], q: int = 1, future_steps: int = 10, SaveFilePath: Optional[str] = None) -> Tuple[np.ndarray, float]:
    """
    移动平均模型(Moving Average Model, MA)
    """
    # 提取时序数据的观测值
    X = np.array(TimeSeriesData)
    
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


def arima_model_forecast(TimeSeriesData: list[TimeSeriesData], p: int, q: int, future_steps: int, SaveFilePath: Optional[str] = None) -> Tuple[np.ndarray, float]:
    """
    自回归移动平均模型(Autoregressive Moving Average Model,ARM)
    并指定合适的p、q以及未来预测的步数future_steps,然后该函数将返回未来预测的结果以及均方根误差。
    """
    # 提取时序数据的观测值
    X = [data.value for data in TimeSeriesData]
    
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


def plot_ACF(TimeSeriesData: list[TimeSeriesData], SaveFilePath: Optional[str] = None) -> None:
    """绘制自相关函数(ACF)图表"""
    # 提取时序数据的观测值
    X = [data.value for data in TimeSeriesData]

    # 计算自相关函数(ACF)
    acf = sm.tsa.acf(X, nlags=len(TimeSeriesData))
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

def plot_polar_with_rms_exceeded(rms_list: List[float], distances_and_bearings: List[Tuple[TimeSeriesData, TimeSeriesData]], threshold: float, title=None):
    # 创建一个极坐标图
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    
    # 遍历距离、方位角和 RMS 值，仅绘制超过阈值的点
    for i, (distance, bearing) in enumerate(distances_and_bearings):
        # 将方位角转换为弧度
        theta = np.deg2rad(bearing.value)
        
        # 绘制超过阈值的点
        if rms_list[i] > threshold:
            ax.plot(theta, distance.value, 'o', color='blue', label='RMS Exceeded Threshold')
    
    # 设置极坐标图的标题
    ax.set_title(f'{title}极坐标 (只显示超过阈值的点)')

    # 显示图形
    plt.show()


def plot_polar_in_month(distances_and_bearings: List[Tuple[TimeSeriesData, TimeSeriesData]], title = None):
    # 创建一个极坐标图
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    
    # 定义一个默认颜色
    default_color = 'k'
    
    # 创建一个颜色映射，将月份映射到颜色
    month_to_color = defaultdict(lambda: default_color)
    month_to_color.update({
        1: 'b', 2: 'b', 3: 'b',  # January, February, March: blue
        4: 'r', 5: 'r', 6: 'r',  # April, May, June: red
        7: 'g', 8: 'g', 9: 'g',  # July, August, September: green
        10: 'orange', 11: 'orange', 12: 'orange',  # October, November, December: yellow
    })

    # 遍历距离和方位角，绘制每个点
    for distance, bearing in distances_and_bearings:
        # 将方位角转换为弧度
        theta = np.deg2rad(bearing.value)
        # 获取月份
        month = distance.datetime.month
        color = month_to_color[month]
        # 绘制点
        ax.plot(theta, distance.value, 'o', color=color, label=f'Month {month}')

    # 添加假线条以创建图例
    for month, color in month_to_color.items():
        ax.plot([], [], 'o', color=color, label=f'Month {month}')

    # 绘制 bearing 角度为 176.91600324062733 的直线
    bearing_line_theta = np.deg2rad(176.91600324062733)
    ax.plot([bearing_line_theta, bearing_line_theta], [0, ax.get_ylim()[1]], color='k', linestyle='--', label='Bearing Line')
    
    # 设置极坐标图的标题
    ax.set_title(f'{title}极坐标')
    
    
    # 显示图形
    plt.show()
    
def plot_PACF(TimeSeriesData: list[TimeSeriesData], lags: int = 48, SaveFilePath: Optional[str] = None) -> None:
    """绘制偏自相关函数(PACF)图表"""
    # 提取时序数据的观测值
    X = [data.value for data in TimeSeriesData]

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


# def evaluate_arma_model(data: List[TimeSeriesData]) -> None:
#     # 提取时序数据的观测值
#     X = [point.value for point in data]

#     # 选择一系列可能的模型阶数
#     p_values = range(1, 5)  # 自回归阶数
#     q_values = range(1, 5)  # 移动平均阶数

#     # 用网格搜索方式寻找最佳的ARMA模型
#     best_aic = np.inf
#     best_params = None

#     for p in p_values:
#         for q in q_values:
#             try:
#                 model = sm.tsa.ARMA(X, order=(p, q))
#                 results = model.fit()
#                 aic = results.aic
#                 bic = results.bic
#                 if aic < best_aic:
#                     best_aic = aic
#                     best_bic = bic
#                     best_params = (p, q)
#             except:
#                 continue

#     if best_params is not None:
#         print("最佳模型的参数:p={}, q={}".format(best_params[0], best_params[1]))
#         print("最佳模型的AIC值:{}".format(best_aic))
#         print("最佳模型的BIC值:{}".format(best_bic))
#     else:
#         print("未找到最佳模型")
        

def fit_arima_model(data: List[TimeSeriesData], p: int = 1, d: int = 1, q: int = 1, num_steps: int = 10, output_file: str = "arima_results.txt") -> np.ndarray:
    """
    差分自回归移动平均模型(ARIMA)
    该函数接受一个时序数据作为输入(例如TimeSeriesData实例的列表),并设置ARIMA模型的阶数(p、d、q)以及预测步数(num_steps)。
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


def evaluate_forecast(TimeSeriesData: List[TimeSeriesData], predicted_values: List[float]) -> Tuple[float, float, float, float]:
    """
    评估预测结果的准确度
    输入参数:
    - actual_values: 实际观测值的数组或列表
    - predicted_values: 预测值的数组或列表
    返回值:
    - rmse: 均方根误差(RMSE)
    - mae: 平均绝对误差(MAE)

    # 评估预测结果
    rmse, mae, correlation, r2 = evaluate_forecast(data, predicted_values)
    print("RMSE:", rmse)
    print("MAE:", mae)
    print("Correlation:", correlation)
    print("R^2:", r2)
    """
    # 将输入转换为numpy数组
    predicted_values = np.array(predicted_values)
    # 提取实际观测值
    actual_values = np.array([data.value for data in TimeSeriesData])
    actual_values = [point.value for point in TimeSeriesData[-len(predicted_values):]]

    # 均方根误差(RMSE)
    rmse = np.sqrt(root_mean_squared_error(actual_values, predicted_values))

    # 平均绝对误差(MAE)
    mae = mean_absolute_error(actual_values, predicted_values)

    # 相关系数
    correlation = np.corrcoef(actual_values, predicted_values)[0, 1]

    # 决定系数
    r2 = r2_score(actual_values, predicted_values)

    return rmse, mae, correlation, r2


# endregion
# region 数据去噪
def smooth_noise(data: List[TimeSeriesData], window_size: int) -> List[float]:
    smoothed_data = []
    for i in range(len(data)):
        start_index = max(0, i - window_size + 1)
        end_index = min(len(data), i + 1)

        window_values = [data[j].value for j in range(start_index, end_index)]
        smoothed_value = sum(window_values) / len(window_values)
        smoothed_data.append(smoothed_value)

    return smoothed_data


def equal_depth_binning(data: List[TimeSeriesData], num_bins: int) -> List[List[TimeSeriesData]]:
    sorted_data = sorted(data, key=lambda x: x.value)
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


def mean_smoothing(bins: List[List[TimeSeriesData]]) -> List[List[TimeSeriesData]]:
    smoothed_bins = []
    for bin_data in bins:
        bin_values = [data.value for data in bin_data]
        mean_value = sum(bin_values) / len(bin_values)
        smoothed_bin = [TimeSeriesData(mean_value, data.datetime) for data in bin_data]
        smoothed_bins.append(smoothed_bin)

    return smoothed_bins


def plot_smoothed_data_and_bins(data: List[TimeSeriesData], smoothed_data: List[float], bins: List[List[TimeSeriesData]], smoothed_bins: List[List[TimeSeriesData]]) -> None:
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
        bin_values = [data_point.value for data_point in bin_data]
        bin_datetimes = [data_point.datetime for data_point in bin_data]
        plt.plot(bin_datetimes, bin_values, label=f"箱子 {i+1}")

    plt.xlabel("时间")
    plt.ylabel("数值")
    plt.title("等深分箱和均值平滑")
    plt.legend()
    plt.show()


# 平滑噪声—等深分箱—均值平滑
def aequilatus_box_mean(data: List[TimeSeriesData], bins: int = 3) -> List[TimeSeriesData]:
    length = len(data)
    labels = []
    
    for i in range(bins):
        labels.append('a' + str(i+1)) # 添加标签
    
    data_df = pd.DataFrame({'value': [data_point.value for data_point in data]})
    new_data = pd.qcut(data_df['value'], bins, labels=labels) # 等深分箱
    data_df['label'] = new_data

    for label in labels:
        label_index_min = data_df[data_df.label==label].index.min() # 分箱后索引最小值
        label_index_max = data_df[data_df.label==label].index.max() # 分箱后索引最大值
        mean_value = np.mean([data_point.value for data_point in data[label_index_min:label_index_max+1]]) # 计算各箱均值
        for i in range(label_index_min, label_index_max+1):
            data[i].value = mean_value # 修改各数据点的数值为均值

    return data


def wavelet_denoising(data: List[TimeSeriesData]) -> List[float]:
    """小波转换去噪"""
    # 提取数据中的数值部分
    signal_values = [data_point.value for data_point in data]

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


def plot_denoised_signal(signal_data: List[TimeSeriesData], denoised_signal: List[float]) -> None:
    # 从 TimeSeriesData 对象中提取数值部分
    signal = [data_point.value for data_point in signal_data]

    plt.figure(figsize=(10, 5))
    plt.plot(signal, label='原始信号')
    plt.plot(denoised_signal, label='去噪后信号')
    plt.xlabel('时间')
    plt.ylabel('幅值')
    plt.title('时序信号去噪')
    plt.legend()
    plt.show()


# endregion
# region 概率论相关
def kernel_density_estimation(data: list[TimeSeriesData], SaveFilePath: Optional[str]=None) -> None:
    # 从TimeSeriesData对象列表中提取值,并将其转换为numpy数组
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

