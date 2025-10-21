# DataProcess 数据处理模块

数据处理模块提供了强大的时序数据分析、处理和可视化功能，包含倾斜仪数据处理、时间序列分析、浮点数列表处理等。

## 📋 模块概览

本模块包含以下4个核心文件：

| 文件名 | 代码量 | 主要功能 |
|--------|--------|----------|
| `TiltmeterCommonUse.py` | 129行 | 倾斜仪数据处理 |
| `TimeDataFrameMethod.py` | 148行 | 时间数据框方法 |
| `TimeSeriesDataMethod.py` | 3630行 | 时间序列数据方法（完整版） |
| `ListFloatDataMethod.py` | 3452行 | 浮点列表数据方法 |

---

## 📄 TiltmeterCommonUse.py

### 类：TiltmeterData

**倾斜仪数据模型类**

#### `__init__(time, station_id, pitch, roll)`

**参数**：
- `time` (str): 时间字符串，格式：`'%Y-%m-%d %H:%M:%S.%f'` 或 `'%Y-%m-%d %H:%M:%S'`
- `station_id` (int): 站点ID
- `pitch` (float): 俯仰角
- `roll` (float): 横滚角

**属性**：
- `self.time` (datetime): 转换后的datetime对象
- `self.station_id` (int): 站点ID
- `self.pitch` (float): 俯仰角
- `self.roll` (float): 横滚角

#### `from_line(line)` [classmethod]

从文本行创建TiltmeterData对象

**参数**：
- `line` (str): 制表符分隔的文本行

**返回**：
- `TiltmeterData`: 倾斜仪数据对象

#### `from_file(file_path)` [classmethod]

从文件读取倾斜仪数据

**参数**：
- `file_path` (str): 文件路径

**返回**：
- `List[TiltmeterData]`: 倾斜仪数据列表

**功能**：跳过第一行（表头），读取后续所有数据行

#### `filter_by_date(tiltmeter_data_list, date)` [classmethod]

按日期筛选数据

**参数**：
- `tiltmeter_data_list` (List[TiltmeterData]): 倾斜仪数据列表
- `date` (str): 日期字符串，格式：`'YYYY-MM-DD'`

**返回**：
- `List[TiltmeterData]`: 筛选后的数据列表

#### `save_to_file(tiltmeter_data_list, file_path)` [classmethod]

保存数据到文件

**参数**：
- `tiltmeter_data_list` (List[TiltmeterData]): 倾斜仪数据列表
- `file_path` (str): 保存路径

**返回**：
- `None`

**功能**：以制表符分隔格式写入文件

### 函数：plot_tiltmeter_data

**绘制倾斜仪数据时序图**

**参数**：
- `tiltmeter_data_list` (List[TiltmeterData]): 倾斜仪数据列表

**返回**：
- `None`

**功能**：
- 创建2个子图，分别显示俯仰角和横滚角的时间序列
- 自动格式化日期显示为月-日-时

---

## 📊 TimeDataFrameMethod.py

### 类：TimeDataFrameMethod

**时间数据框处理方法类（所有方法均为类方法）**

#### `_save_pdDataFrame(df, save_file_path)` [classmethod]

保存DataFrame到CSV文件

**参数**：
- `df` (pd.DataFrame): 要保存的数据框
- `save_file_path` (str): 保存路径

**返回**：
- `None`

**功能**：使用制表符作为分隔符，不保存索引

#### `_capture_dataframe_output(df)` [classmethod]

捕获DataFrame的打印输出

**参数**：
- `df` (pd.DataFrame): 数据框

**返回**：
- `str`: DataFrame的字符串表示

#### `_pdData_clean(data)` [classmethod]

数据清洗

**参数**：
- `data` (pd.DataFrame): 原始数据框

**返回**：
- `pd.DataFrame`: 清洗后的数据框

**功能**：
- 计算并打印每列的缺失值数量
- 计算并打印重复行数量
- 删除重复行

#### `_clean_time_data(data, time_column)` [classmethod]

清洗时间数据

**参数**：
- `data` (pd.DataFrame): 数据框
- `time_column` (str): 时间列名

**返回**：
- `pd.DataFrame`: 清洗后的数据框

**功能**：
- 将时间列转换为datetime类型
- 处理格式错误（coerce模式）
- 删除无效时间数据

**异常**：
- `ValueError`: 当指定列不存在时

#### `_create_summary_dataframe(datasets)` [classmethod]

创建数据集摘要

**参数**：
- `datasets` (dict[str, pd.DataFrame]): 数据集字典

**返回**：
- `pd.DataFrame`: 包含以下列的摘要数据框
  - `Dataset`: 数据集名称
  - `Rows`: 行数
  - `Columns`: 列数
  - `Missing Values`: 缺失值总数
  - `Duplicate Rows`: 重复行数

#### `_split_station_data(df)` [classmethod]

按站点ID分割数据

**参数**：
- `df` (pd.DataFrame): 包含`StationID`列的数据框

**返回**：
- `tuple[pd.DataFrame, pd.DataFrame]`: (站点3的数据, 站点8的数据)

#### `_split_avr_columns(df)` [classmethod]

分割AVR数据列

**参数**：
- `df` (pd.DataFrame): 包含`Time`、`Yaw`、`Tilt`、`Range`列的数据框

**返回**：
- `dict[str, pd.DataFrame]`: 包含三个键的字典
  - `'Yaw'`: Time和Yaw列
  - `'Tilt'`: Time和Tilt列
  - `'Range'`: Time和Range列

#### `_plot_timeDF(df, title, xlabel, ylabel)` [classmethod]

绘制时间序列图

**参数**：
- `df` (pd.DataFrame): 包含`Time`列的数据框
- `title` (str, 默认='Yaw时序图'): 图表标题
- `xlabel` (str, 默认='时间'): X轴标签
- `ylabel` (str, 默认='Yaw'): Y轴标签

**返回**：
- `None`

**功能**：
- 绘制时间序列折线图
- 自动格式化日期显示（小时:分钟）
- 隐藏右边框和上边框
- 刻度朝向内部

---

## 📈 TimeSeriesDataMethod.py

### 类：TimeSeriesData

**时间序列数据模型类**

#### `__init__(value, datetime_input)`

**参数**：
- `value` (float): 数值
- `datetime_input` (datetime | str): datetime对象或字符串
  - 字符串格式：`'%Y-%m-%d %H:%M:%S.%f'` 或 `'%Y-%m-%d %H:%M:%S'`

**属性**：
- `self.value` (float): 数值
- `self.datetime` (datetime): 时间

**异常**：
- `TypeError`: 当datetime_input类型不正确时

#### `__str__()`

**返回**：
- `str`: 格式化的字符串表示

---

### 基础功能函数

#### `load_csv_data(data_file)`

从CSV文件加载数据

**参数**：
- `data_file` (str, 默认='...'): 数据文件路径

**返回**：
- `list[TimeSeriesData]`: 时间序列数据列表

**功能**：读取最多100000条数据

#### `create_time_series_data(values, datetimes)`

创建时间序列数据列表

**参数**：
- `values` (List[float]): 数值列表
- `datetimes` (List[str]): 时间字符串列表

**返回**：
- `list[TimeSeriesData]`: 时间序列数据列表

#### `remove_average(data)`

去平均值处理

**参数**：
- `data` (list[TimeSeriesData]): 时间序列数据

**返回**：
- `None`

**功能**：对数据减去平均值后乘以1000（原地修改）

#### `remove_specific_value(data, specific_value)`

减去特定值

**参数**：
- `data` (List[TimeSeriesData]): 时间序列数据
- `specific_value` (float): 要减去的值

**返回**：
- `None`

**功能**：对数据减去指定值后乘以1000（原地修改）

---

### 绘图函数

#### `plot_TimeSeriesData(TimeSeriesData, isShow, SaveFilePath)`

绘制时间序列图

**参数**：
- `TimeSeriesData` (list[TimeSeriesData]): 时间序列数据
- `isShow` (bool, 默认=False): 是否显示图表
- `SaveFilePath` (Optional[str], 默认=None): 保存路径

**返回**：
- `None`

**功能**：绘制基础时间序列折线图，图表尺寸14.4x9.6英寸

#### `plot_TimeSeriesData_in_threshold(TimeSeriesData, threshold, isShow, SaveFilePath)`

带阈值绘图

**参数**：
- `TimeSeriesData` (list[TimeSeriesData]): 时间序列数据
- `threshold` (timedelta): 时间间隔阈值
- `isShow` (bool, 默认=False): 是否显示
- `SaveFilePath` (Optional[str], 默认=None): 保存路径

**返回**：
- `None`

**功能**：当时间间隔超过阈值时断开连线

#### `plot_data_with_datetimes(value, datetimes, color)`

绘制数据与时间

**参数**：
- `value` (List[float]): 数值列表
- `datetimes` (List[datetime]): 时间列表
- `color` (str, 默认='blue'): 线条颜色

**返回**：
- `None`

**功能**：时间间隔超过2天时断开连线

#### `plot_TimeSeriesData_in_season(TimeSeriesData, threshold, isShow, SaveFilePath)`

按季节着色绘图

**参数**：
- `TimeSeriesData` (list[TimeSeriesData]): 时间序列数据
- `threshold` (timedelta): 时间间隔阈值
- `isShow` (bool, 默认=False): 是否显示
- `SaveFilePath` (Optional[str], 默认=None): 保存路径

**返回**：
- `None`

**功能**：
- 按月份使用不同颜色
- 1-3月：浅橙色
- 4-6月：橙红色
- 7-9月：深蓝色
- 10-12月：青绿色

#### `plot_TimeSeriesData_Compare(TimeSeriesData1, TimeSeriesData2, SaveFilePath)`

对比绘图

**参数**：
- `TimeSeriesData1` (list[TimeSeriesData]): 第一组数据
- `TimeSeriesData2` (list[TimeSeriesData]): 第二组数据
- `SaveFilePath` (Optional[str], 默认=None): 保存路径

**返回**：
- `None`

**功能**：在同一图表中绘制两组数据

#### `generate_random_data()`

生成随机测试数据

**参数**：无

**返回**：
- `list[TimeSeriesData]`: 150个随机数据点

**功能**：从2024-03-13开始，每小时一个数据点，值在10-30之间

---

### 坐标转换函数

#### `convert_coordinates(lat, lon)`

WGS84到平面坐标转换

**参数**：
- `lat` (float): 纬度
- `lon` (float): 经度

**返回**：
- `tuple[float, float]`: (东坐标, 北坐标)

**功能**：使用横轴墨卡托投影（中央经线117°）

#### `convert_latlon_coordinates(lat_tsd, lon_tsd)`

批量坐标转换

**参数**：
- `lat_tsd` (List[TimeSeriesData]): 纬度时间序列
- `lon_tsd` (List[TimeSeriesData]): 经度时间序列

**返回**：
- `tuple[List[TimeSeriesData], List[TimeSeriesData]]`: (转换后纬度, 转换后经度)

---

### 统计分析函数

#### `calculate_mean(TimeSeriesData)`

计算平均值

**参数**：
- `TimeSeriesData` (list[TimeSeriesData]): 时间序列数据

**返回**：
- `float`: 平均值

#### `calculate_median(TimeSeriesData)`

计算中位数

**参数**：
- `TimeSeriesData` (list[TimeSeriesData]): 时间序列数据

**返回**：
- `float`: 中位数

#### `calculate_variance(TimeSeriesData)`

计算方差

**参数**：
- `TimeSeriesData` (list[TimeSeriesData]): 时间序列数据

**返回**：
- `float`: 方差

#### `calculate_standard_deviation(TimeSeriesData)`

计算标准差

**参数**：
- `TimeSeriesData` (list[TimeSeriesData]): 时间序列数据

**返回**：
- `float`: 标准差

#### `calculate_change_rate(timeSeriesdata)`

计算变化率

**参数**：
- `timeSeriesdata` (list[TimeSeriesData]): 时间序列数据

**返回**：
- `List[float]`: 变化率列表（长度=原数据长度-1）

**功能**：计算相邻点的变化率 `(current - previous) / previous`

#### `calculate_correlation_Pearson(data1, data2)`

计算皮尔逊相关系数

**参数**：
- `data1` (List[TimeSeriesData]): 第一组数据
- `data2` (List[TimeSeriesData]): 第二组数据

**返回**：
- `float`: 皮尔逊相关系数

**功能**：自动对齐时间轴后计算相关性

#### `get_x_values(data)`

获取时间步索引

**参数**：
- `data` (list[TimeSeriesData]): 时间序列数据

**返回**：
- `List[int]`: 索引列表 [0, 1, 2, ...]

#### `get_y_values(data)`

获取数值列表

**参数**：
- `data` (list[TimeSeriesData]): 时间序列数据

**返回**：
- `List[float]`: 数值列表

#### `calculate_trend_line_residuals(data, trend_line)`

计算残差

**参数**：
- `data` (list[TimeSeriesData]): 原始数据
- `trend_line` (np.ndarray): 趋势线数值

**返回**：
- `np.ndarray`: 残差数组

#### `plot_residuals(residuals, SaveFilePath)`

绘制残差图

**参数**：
- `residuals` (np.ndarray): 残差数组
- `SaveFilePath` (Optional[str], 默认=None): 保存路径

**返回**：
- `None`

**功能**：绘制残差散点图，包含零线

#### `calculate_r_squared(y_true, y_pred)`

计算R²

**参数**：
- `y_true` (np.ndarray): 真实值
- `y_pred` (np.ndarray): 预测值

**返回**：
- `float`: R²值

#### `calculate_distance(x1, y1, x2, y2)`

计算欧氏距离

**参数**：
- `x1, y1` (float): 第一个点坐标
- `x2, y2` (float): 第二个点坐标

**返回**：
- `float`: 距离

#### `calculate_bearing(x, y)`

计算方位角

**参数**：
- `x` (float): X坐标
- `y` (float): Y坐标

**返回**：
- `float`: 方位角（度），范围[0, 360)

#### `calculate_durbin_watson(residuals)`

计算德宾-沃森统计量

**参数**：
- `residuals` (np.ndarray): 残差数组

**返回**：
- `float`: DW统计量

**功能**：检验残差的自相关性

---

### 趋势分析函数

#### `fit_polynomial_trend(data, degree)`

拟合多项式趋势线

**参数**：
- `data` (list[TimeSeriesData]): 时间序列数据
- `degree` (int, 默认=3): 多项式阶数

**返回**：
- `np.ndarray`: 趋势线数值

#### `calculate_trend_line_r_squared(data, trend_line)`

计算趋势线拟合度

**参数**：
- `data` (list[TimeSeriesData]): 原始数据
- `trend_line` (np.ndarray): 趋势线

**返回**：
- `float`: R²值

**注意**：此模块包含大量高级时序分析函数（如ARIMA、小波分析、EMD分解、聚类等），由于篇幅限制，仅列出核心基础函数。完整函数列表包含100+个函数。

---

## 🔢 ListFloatDataMethod.py

### 基础功能函数

#### `check_data_type(data)`

检查数据类型

**参数**：
- `data` (np.ndarray): 数组数据

**返回**：
- `None`

**功能**：打印数据类型和形状

#### `remove_average(data)`

去平均值

**参数**：
- `data` (list[float]): 浮点数列表

**返回**：
- `None`

**功能**：减去平均值后乘以1000（原地修改）

#### `remove_specific_value(data, specific_value)`

减去特定值

**参数**：
- `data` (list[float]): 浮点数列表
- `specific_value` (float): 要减去的值

**返回**：
- `None`

**功能**：减去指定值后乘以1000（原地修改）

---

### 绘图函数

#### `plot_ListFloat(ListFloat, isShow, SaveFilePath, title)`

绘制浮点列表图

**参数**：
- `ListFloat` (list[float]): 浮点数列表
- `isShow` (bool, 默认=False): 是否显示
- `SaveFilePath` (Optional[str], 默认=None): 保存路径
- `title` (str, 默认=None): 图表标题

**返回**：
- `None`

**功能**：使用索引作为X轴绘制折线图

#### `plot_ListFloat_with_time_pitch(ListFloat, ListTime, isShow, SaveFilePath, title)`

绘制俯仰角时序图

**参数**：
- `ListFloat` (List[float]): 俯仰角数据
- `ListTime` (List[datetime]): 时间列表
- `isShow` (bool, 默认=True): 是否显示
- `SaveFilePath` (Optional[str], 默认=None): 保存路径
- `title` (str, 默认=None): 图表标题

**返回**：
- `None`

**功能**：
- 图表尺寸6x4英寸
- Y轴标签：俯仰角/°
- 隐藏右边框和上边框
- 日期格式：小时:00

#### `plot_ListFloat_with_time_roll(ListFloat, ListTime, isShow, SaveFilePath, title)`

绘制横滚角时序图

**参数**：
- `ListFloat` (List[float]): 横滚角数据
- `ListTime` (List[datetime]): 时间列表
- `isShow` (bool, 默认=True): 是否显示
- `SaveFilePath` (Optional[str], 默认=None): 保存路径
- `title` (str, 默认=None): 图表标题

**返回**：
- `None`

**功能**：
- 图表尺寸6x4英寸
- Y轴标签：横滚角/°
- 隐藏右边框和上边框
- 日期格式：小时:00

#### `plot_points(x_points, y_points, title)`

绘制散点图

**参数**：
- `x_points` (list[float]): X坐标列表
- `y_points` (list[float]): Y坐标列表
- `title` (str, 默认=None): 图表标题

**返回**：
- `None`

**功能**：
- 图表尺寸6x4英寸
- 坐标轴箭头样式
- 隐藏边框

#### `plot_ListFloat_x(ListFloat, isShow, SaveFilePath, title)`

绘制X轴位移图

**参数**：
- `ListFloat` (list[float]): 位移数据
- `isShow` (bool, 默认=True): 是否显示
- `SaveFilePath` (Optional[str], 默认=None): 保存路径
- `title` (str, 默认=None): 图表标题

**返回**：
- `None`

**功能**：
- Y轴标签：索道坐标x轴方向位移监测/m
- 同时绘制折线和散点

#### `plot_ListFloat_y(ListFloat, isShow, SaveFilePath, title)`

绘制Y轴位移图

**参数**：
- `ListFloat` (list[float]): 位移数据
- `isShow` (bool, 默认=True): 是否显示
- `SaveFilePath` (Optional[str], 默认=None): 保存路径
- `title` (str, 默认=None): 图表标题

**返回**：
- `None`

**功能**：
- Y轴标签：索道坐标y轴方向位移监测/m
- 同时绘制折线和散点

#### `plot_ListFloat_with_marker(ListFloat, to_marker_idx)`

带标记点绘图

**参数**：
- `ListFloat` (list[float]): 数据列表
- `to_marker_idx` (list[int], 默认=[]): 要标记的索引列表

**返回**：
- `None`

**功能**：
- 正常点用黑色圆点
- 标记点用红色叉号

#### `plot_points_with_markeridx(x_points, y_points, title, to_marker_idx)`

带标记的散点图

**参数**：
- `x_points` (list[float]): X坐标
- `y_points` (list[float]): Y坐标
- `title` (str, 默认=None): 图表标题
- `to_marker_idx` (list[int], 默认=[]): 标记索引

**返回**：
- `None`

**功能**：
- 正常点蓝色圆点
- 异常点红色叉号
- 坐标轴箭头样式

#### `plot_ListFloat_Compare(ListFloat1, ListFloat2, SaveFilePath, title)`

对比绘图

**参数**：
- `ListFloat1` (list[float]): 第一组数据
- `ListFloat2` (list[float]): 第二组数据
- `SaveFilePath` (Optional[str], 默认=None): 保存路径
- `title` (str, 默认=None): 图表标题

**返回**：
- `None`

**功能**：
- 计算并打印相似度
- 绘制两组数据的折线图

#### `plot_ListFloat_Compare_without_marker(ListFloat1, ListFloat2, to_marker_idx)`

排除标记点的对比图

**参数**：
- `ListFloat1` (list[float]): 第一组数据
- `ListFloat2` (list[float]): 第二组数据
- `to_marker_idx` (list[int], 默认=[]): 要排除的索引

**返回**：
- `None`

**功能**：
- 排除指定索引的数据点
- 计算并打印相似度

#### `plot_ListFloat_Compare_in_diff_dt(ListFloat1, dt_list1, ListFloat2, dt_list2)`

不同时间轴对比图

**参数**：
- `ListFloat1` (List[float]): 第一组数据
- `dt_list1` (List[datetime]): 第一组时间
- `ListFloat2` (List[float]): 第二组数据
- `dt_list2` (List[datetime]): 第二组时间

**返回**：
- `None`

**功能**：
- 自动对齐相同时间点的数据
- 计算相似度并绘图

**注意**：ListFloatDataMethod.py包含大量数据处理函数（统计分析、滤波、插值、聚类、异常检测等），由于篇幅限制，仅列出核心基础函数。完整函数列表包含100+个函数，涵盖：

- **统计分析**：均值、中位数、方差、偏度、峰度等
- **滤波方法**：移动平均、指数平滑、小波去噪、卡尔曼滤波等
- **插值方法**：线性插值、样条插值、多项式插值等
- **趋势分析**：线性回归、多项式拟合、季节分解等
- **聚类分析**：K-means、DBSCAN、层次聚类等
- **异常检测**：IQR、Z-score、孤立森林、LOF等
- **相似度计算**：皮尔逊、斯皮尔曼、肯德尔相关系数等
- **频域分析**：FFT、功率谱、小波变换等

---

## 🔧 依赖安装

### 基础依赖
```bash
pip install numpy pandas
pip install matplotlib
pip install scipy statsmodels
```

### 科学计算依赖
```bash
pip install scikit-learn
pip install PyEMD  # 经验模态分解
pip install pywt   # 小波变换
pip install pyproj # 坐标转换
pip install pyswarm # 粒子群优化
```

### 完整安装
```bash
pip install numpy pandas matplotlib scipy statsmodels scikit-learn PyEMD pywt pyproj pyswarm
```

---

## 📊 数据格式说明

### TiltmeterData 文件格式
```
时间\t站点ID\t俯仰角\t横滚角
2023-08-01 12:00:00.000	3	0.125	-0.083
2023-08-01 12:00:01.000	3	0.126	-0.082
```

### TimeSeriesData 格式要求
- 时间格式：`'YYYY-MM-DD HH:MM:SS.ffffff'` 或 `'YYYY-MM-DD HH:MM:SS'`
- 数值：浮点数
- 列表元素：按时间顺序排列

---

## 📝 注意事项

1. **内存使用**：
   - TimeSeriesDataMethod和ListFloatDataMethod包含大量函数（3000+行）
   - 处理大数据集时注意内存占用
   - 建议分批处理超大数据

2. **时间格式**：
   - 所有时间处理函数支持两种格式（带/不带微秒）
   - 确保时间数据格式一致

3. **坐标转换**：
   - convert_coordinates使用横轴墨卡托投影
   - 中央经线设置为117°
   - 适用于中国东部地区

4. **绘图**：
   - 所有绘图函数支持保存或显示
   - 默认中文字体为宋体（SimSun）
   - 图表尺寸可通过figsize参数调整

5. **数据修改**：
   - remove_average和remove_specific_value会原地修改数据
   - 使用前请备份原始数据

6. **性能优化**：
   - 大数据集建议使用numpy数组而非list
   - 频繁操作建议转换为pandas DataFrame

---

## 🎯 应用场景

1. **倾斜仪监测**：
   - 建筑物倾斜监测
   - 边坡位移监测
   - 桥梁形变监测

2. **时间序列分析**：
   - 趋势分析和预测
   - 周期性检测
   - 异常值识别

3. **GNSS数据处理**：
   - 坐标转换
   - 位移计算
   - 轨迹分析

4. **传感器数据分析**：
   - 数据清洗
   - 滤波去噪
   - 特征提取

5. **科学数据可视化**：
   - 多维数据展示
   - 对比分析
   - 报告生成

---

## 📄 许可证

本模块采用开源许可证。

---

**最后更新**: 2024年  
**模块版本**: 1.0.0

