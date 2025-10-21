import os
import csv
import pandas as pd
import json
import chardet
import pyproj
import numpy as np
from datetime import datetime
from collections import defaultdict
from dataclasses import dataclass
from typing import TypedDict, List, Dict, Optional
from JayttleProcess.CommonUtils import CommonDecorator
from JayttleProcess.DataProcess import TimeSeriesDataMethod as TSD
from JayttleProcess.DataProcess.TimeSeriesDataMethod import TimeSeriesData


# region class类声明
class DataPoint:
    def __init__(self, point_id: str, north_coordinate: float, east_coordinate: float, elevation: float,
                 latitude: float, longitude: float, ellipsoid_height: float, start_time: str, end_time: str,
                 duration: str, pdop: float, rms: float, horizontal_accuracy: float, vertical_accuracy: float,
                 north_coordinate_error: float, east_coordinate_error: float, elevation_error: float,
                 height_error: str):
        self.point_id = point_id  # 数据点的ID
        self.north_coordinate = north_coordinate  # 数据点的北坐标
        self.east_coordinate = east_coordinate  # 数据点的东坐标
        self.elevation = elevation  # 数据点的高程
        self.latitude = latitude  # 数据点的纬度
        self.longitude = longitude  # 数据点的经度
        self.ellipsoid_height = ellipsoid_height  # 数据点的椭球高度
        self.start_time = start_time  # 数据点的开始时间
        self.end_time = end_time  # 数据点的结束时间
        self.duration = duration  # 数据点的持续时间
        self.pdop = pdop  # 数据点的位置精度衰减因子（PDOP）
        self.rms = rms  # 数据点的均方根（RMS）
        self.horizontal_accuracy = horizontal_accuracy  # 数据点的水平精度
        self.vertical_accuracy = vertical_accuracy  # 数据点的垂直精度
        self.north_coordinate_error = north_coordinate_error  # 数据点的北坐标误差
        self.east_coordinate_error = east_coordinate_error  # 数据点的东坐标误差
        self.elevation_error = elevation_error  # 数据点的高程误差
        self.height_error = height_error  # 数据点的高度误差


class Coordinates(TypedDict):
    Lat: float
    Lon: float
    GeoHeight: float

class Correction(TypedDict):
    Distance: float
    TiltAngle: float
    TorsionAngle: float

class Threshold(TypedDict):
    Distance: float
    Tilt: float
    Torsion: float

class Data(TypedDict):
    GaussOption: Dict[str, float]
    CablewayOption: Dict[str, float]
    MaxDiffLength: float
    MaxDiffDistance: float
    Thresholds: List[Threshold]
    Coors: Dict[str, List[Coordinates]]
    Corrections: Dict[str, Correction]


@dataclass
class GgkxDto:
    Time: datetime
    StationId: int
    ReceiverId: int
    Lat: float
    Lon: float
    GeoHeight: float
    FixMode: int
    SateNum: int
    Pdop: float
    SigmaE: float
    SigmaN: float
    SigmaU: float
    Prop_Age: float
# endregion

# region  全局变量
encoding = None # csv文件的编码格式 全局变量
datapoints_csv = [] # 读取的csv点数据存储
json_data = None  # 初始化为 None 或者其他默认值
data_dict: dict[str, list[GgkxDto]] = defaultdict(list) # 使用 defaultdict 创建一个字典，值的默认类型是列表
# endregion
def read_csv_to_datapoints(csv_file: str) -> list[DataPoint]:
    global encoding
    
    # Detecting file encoding using chardet
    with open(csv_file, 'rb') as f:
        rawdata = f.read()
        encoding = chardet.detect(rawdata)['encoding']

    # Reading CSV file with detected encoding
    df = pd.read_csv(csv_file, sep='\t', encoding=encoding, nrows=1, parse_dates=['GNSS矢量观测.开始时间', 'GNSS矢量观测.结束时间'])
    
    datapoints = []
    for index, row in df.iterrows():
        datapoint = DataPoint(
            point_id=row['点ID'],
            north_coordinate=row['北坐标'],
            east_coordinate=row['东坐标'],
            elevation=row['高程'],
            latitude=row['纬度（全球）'],
            longitude=row['经度（全球）'],
            ellipsoid_height=row['GNSS矢量观测.起点ID'],
            start_time=row['GNSS矢量观测.开始时间'],
            end_time=row['GNSS矢量观测.结束时间'],
            duration=row['GNSS矢量观测.终点ID'],
            pdop=row['GNSS矢量观测.PDOP'],
            rms=row['GNSS矢量观测.均方根'],
            horizontal_accuracy=row['GNSS矢量观测.水平精度'],
            vertical_accuracy=row['GNSS矢量观测.垂直精度'],
            north_coordinate_error=row['GNSS矢量观测.X增量'],
            east_coordinate_error=row['GNSS矢量观测.Y增量'],
            elevation_error=row['GNSS矢量观测.Z增量'],
            height_error=row['GNSS矢量观测.解类型']
        )
        datapoints.append(datapoint)
    return datapoints


@CommonDecorator.log_function_call
def export_datapoints_to_csv(datapoints: list[DataPoint], output_file: str) -> None:
    fieldnames = ['GNSS矢量观测.开始时间', 'GNSS矢量观测.结束时间', '点ID', '北坐标', '东坐标', '高程', '纬度（全球）', '经度（全球）',
                  'GNSS矢量观测.PDOP', 'GNSS矢量观测.均方根', 'GNSS矢量观测.水平精度', 'GNSS矢量观测.垂直精度',
                  'GNSS矢量观测.起点ID', 'GNSS矢量观测.终点ID', 'GNSS矢量观测.X增量', 'GNSS矢量观测.Y增量',
                  'GNSS矢量观测.Z增量', 'GNSS矢量观测.矢量长度', 'GNSS矢量观测.解类型', 'GNSS矢量观测.状态']

    with open(output_file, 'w', newline='', encoding=encoding if encoding is not None else 'utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for datapoint in datapoints:
            writer.writerow({
                'GNSS矢量观测.开始时间': datapoint.start_time,
                'GNSS矢量观测.结束时间': datapoint.end_time,
                '点ID': datapoint.point_id,
                '北坐标': datapoint.north_coordinate,
                '东坐标': datapoint.east_coordinate,
                '高程': datapoint.elevation,
                '纬度（全球）': datapoint.latitude,
                '经度（全球）': datapoint.longitude,
                'GNSS矢量观测.PDOP': datapoint.pdop,
                'GNSS矢量观测.均方根': datapoint.rms,
                'GNSS矢量观测.水平精度': datapoint.horizontal_accuracy,
                'GNSS矢量观测.垂直精度': datapoint.vertical_accuracy,
                'GNSS矢量观测.起点ID': datapoint.ellipsoid_height,
                'GNSS矢量观测.终点ID': datapoint.duration,
                'GNSS矢量观测.X增量': datapoint.north_coordinate_error,
                'GNSS矢量观测.Y增量': datapoint.east_coordinate_error,
                'GNSS矢量观测.Z增量': datapoint.elevation_error,
                'GNSS矢量观测.矢量长度': datapoint.height_error,
                'GNSS矢量观测.解类型': datapoint.height_error,
                'GNSS矢量观测.状态': datapoint.height_error
            })



def dataPoint_create_timeseries_data(datapoint: DataPoint, value_key: str) -> TimeSeriesData:
    """
    value_key = "north_coordinate"  # 用你想要提取的属性键替换这里
    timeseries_data = create_timeseries_data(datapoint, value_key)
    getattr() 函数用于获取对象的属性值。它接受对象和属性名作为参数，并返回指定属性的值。
    如果对象中不存在该属性，则可以提供一个默认值作为第三个参数（可选）。
    这个函数在需要动态地获取对象的属性时非常有用，特别是当属性名称在运行时确定时。
    """
    selected_value = getattr(datapoint, value_key, None)
    if selected_value is None:
        return None
    # 将 datapoint.start_time 转换为字符串
    start_time_str = str(datapoint.start_time)
    return TimeSeriesData(selected_value, start_time_str)


def ggkxDto_create_timeseries_data(datapoint: GgkxDto, value_key: str) -> Optional[TimeSeriesData]:
    """
    从 GgkxDto 数据点中提取所需属性值，返回 TimeSeriesData 对象。
    """
    # 使用 getattr 获取 datapoint 中的属性值
    selected_value = getattr(datapoint, value_key, None)
    if selected_value is None:
        return None
    
    # 提取 Time 属性
    time_value = datapoint.Time
    
    # 创建 TimeSeriesData 对象并返回
    return TimeSeriesData(selected_value, time_value.strftime("%Y-%m-%d %H:%M:%S.%f"))


def export_list_to_excel(datapoints: list[DataPoint]) -> None:
    # 将 DataPoint 对象列表转换为 Pandas DataFrame
    datapoints_df = pd.DataFrame([vars(dp) for dp in datapoints])

    # 将 start_time 转换为日期并设置为索引
    datapoints_df['start_time'] = pd.to_datetime(datapoints_df['start_time'])
    datapoints_df.set_index(datapoints_df['start_time'].dt.date, inplace=True)

    # 删除原始的 start_time 列
    datapoints_df.drop(columns=['start_time'], inplace=True)

    # 确定日期范围的最小值和最大值
    min_date = datapoints_df.index.min()
    max_date = datapoints_df.index.max()

    # 创建整个日期范围的日期列表
    date_range = pd.date_range(start=min_date, end=max_date)

    # 创建一个空的 DataFrame，索引为整个日期范围
    empty_df = pd.DataFrame(index=date_range)

    # 将原始数据填充到空的 DataFrame 中，确保缺失的日期处填充为零或空值
    filled_df = empty_df.merge(datapoints_df, how='left', left_index=True, right_index=True)

    # 将 NaN 值替换为 0 或空值
    filled_df.fillna({'point_id': 'R031', 'north_coordinate': 0, 'east_coordinate': 0, 'elevation': 0, 'latitude': 0, 'longitude': 0,
                    'ellipsoid_height': 0, 'end_time': 0, 'duration': 0, 'pdop': 0, 'rms': 0, 'horizontal_accuracy': 0,
                    'vertical_accuracy': 0, 'north_coordinate_error': 0, 'east_coordinate_error': 0, 'elevation_error': 0,
                    'height_error': 0}, inplace=True)

    # 输出填充后的 DataFrame 到 Excel 文件
    output_excel_path = "filled_datapoints.xlsx"
    filled_df.to_excel(output_excel_path)

    print("已将填充后的数据导出到 Excel 文件:", output_excel_path)




def read_json_file(file_path: str) -> Data:
    with open(file_path, 'r') as file:
        data = json.load(file)
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


@CommonDecorator.log_function_call
def read_data(file_path: str) -> None:
    with open(file_path, 'r') as file:
        for line in file:
            row = line.strip().split(',')
            time_format = '%Y-%m-%d %H:%M:%S.%f' if '.' in row[0] else '%Y-%m-%d %H:%M:%S'
            time = datetime.strptime(row[0], time_format)
            station_id = int(row[1])
            receiver_id = int(row[2])
            lat = float(row[3])
            lon = float(row[4])
            geo_height = float(row[5])
            fix_mode = int(row[6])
            sate_num = int(row[7])
            pdop = float(row[8])
            sigma_e = float(row[9])
            sigma_n = float(row[10])
            sigma_u = float(row[11])
            prop_age = float(row[12])
            ggkx = GgkxDto(time, station_id, receiver_id, lat, lon, geo_height, fix_mode, sate_num, pdop, sigma_e, sigma_n, sigma_u, prop_age)
            # 将数据添加到字典中对应的列表中
            key = f'{station_id}{receiver_id}'
            data_dict[key].append(ggkx)

def convert_latlon_coordinates(lat_tsd: List[TimeSeriesData], lon_tsd: List[TimeSeriesData]) -> tuple[List[TimeSeriesData], List[TimeSeriesData]]:
    # 转换后的时序数据列表
    converted_lat_tsd = []
    converted_lon_tsd = []
    
    for lat, lon in zip(lat_tsd, lon_tsd):
        # 对纬度和经度进行坐标转换
        converted_lat, converted_lon = convert_coordinates(lat.value, lon.value)
        
        # 创建新的 TimeSeriesData 对象并添加到列表中
        converted_lat_tsd.append(TimeSeriesData(converted_lat, lat.datetime.strftime("%Y-%m-%d %H:%M:%S.%f")))
        converted_lon_tsd.append(TimeSeriesData(converted_lon, lon.datetime.strftime("%Y-%m-%d %H:%M:%S.%f")))
    
    return converted_lat_tsd, converted_lon_tsd

    
#TODO：再把晚上8点的~12点的 tbc处理
#TODO：把东坐标 北坐标放入一个坐标系里看角度与分布  是否与风向有关
#TODO：计算另一个天线进行对比比较 
#TODO：找出突变的原因 可以先计算他的前后差值如果大则查看他的计算精度
#TODO：按照季节分化 春夏秋冬看是否有差距
#TODO：10hz数据的处理和查看
#TODO：数据库里的环境数据是否可用hw


#TODO：用倾斜仪来看是否运营
#TODO：是否能用pyqt做个软件：
"""
1.要能看到读取的是什么class有哪些数据
2.能够选择用哪些数据来显示
3.尽可能放很多的时序数据功能来提供实现，
4.
"""

