import io
import os 
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# region 字体设置
plt.rcParams['font.sans-serif'] = ['SimSun']  # 指定宋体为默认字体
plt.rcParams['font.sans-serif'] = 'SimSun'  # 使用指定的中文字体
plt.rcParams['axes.unicode_minus']=False#用来正常显示负

class TimeDataFrameMethod:
    @classmethod
    def _save_pdDataFrame(self, df: pd.DataFrame, save_file_path: str) -> None:
        df.to_csv(save_file_path, sep='\t', index=False)


    # 将 DataFrame 的打印输出捕获到一个字符串中
    @classmethod
    def _capture_dataframe_output(cls, df: pd.DataFrame) -> str:
        output = io.StringIO()
        df.to_string(buf=output)
        return output.getvalue()

    @classmethod
    def _pdData_clean(cls, data: pd.DataFrame) -> pd.DataFrame:
        # 计算每列的缺失值数量
        missing_values = data.isnull().sum()
        print("Missing values per column:\n", missing_values)

        # 计算并删除重复行
        duplicate_count = data.duplicated().sum()
        print(f"Duplicate rows count: {duplicate_count}")
        data = data.drop_duplicates()
        
        return data

    @classmethod
    def _clean_time_data(cls, data: pd.DataFrame, time_column: str) -> pd.DataFrame:
        # 处理时间数据
        if time_column not in data.columns:
            raise ValueError(f"Column '{time_column}' not found in DataFrame.")

        # 将时间列转换为 datetime 类型，处理格式错误
        data[time_column] = pd.to_datetime(data[time_column], errors='coerce')

        # 打印转换后的时间列
        print(f"After conversion, unique time values:\n{data[time_column].unique()}")

        # 检查转换后的缺失值
        missing_time_values = data[time_column].isnull().sum()
        print(f"Missing time values count: {missing_time_values}")

        # 删除时间列中无效的时间数据
        data = data.dropna(subset=[time_column])
        
        return data

    
    @classmethod
    def _create_summary_dataframe(self, datasets: dict[str, pd.DataFrame]) -> pd.DataFrame:
        summary = []
        for name, df in datasets.items():
            if df.empty:
                # 处理空的数据框
                row_count = 0
                col_count = 0
                missing_values = 0
                duplicate_count = 0
            else:
                # 计算缺失值总数
                missing_values = df.isnull().sum().sum()
                # 计算重复行数
                duplicate_count = df.duplicated().sum()
                # 统计行数和列数
                row_count = df.shape[0]
                col_count = df.shape[1]

            summary_entry = {
                'Dataset': name,
                'Rows': row_count,
                'Columns': col_count,
                'Missing Values': missing_values,
                'Duplicate Rows': duplicate_count,
            }
            summary.append(summary_entry)
        
        return pd.DataFrame(summary)
    
    @classmethod
    def _split_station_data(cls, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        # Split the DataFrame based on StationID values 3 and 8
        df_station_3 = df[df['StationID'] == 3]
        df_station_8 = df[df['StationID'] == 8]
        return df_station_3, df_station_8

    @classmethod
    def _split_avr_columns(cls, df: pd.DataFrame) -> dict[str, pd.DataFrame]:
        # 选择需要的列并创建新的 DataFrame
        df_yaw = df[['Time', 'Yaw']].copy()
        df_tilt = df[['Time', 'Tilt']].copy()
        df_range = df[['Time', 'Range']].copy()
        
        # 返回字典，其中包含三个 DataFrame
        return {
            'Yaw': df_yaw,
            'Tilt': df_tilt,
            'Range': df_range
        }
    
    @classmethod
    def _plot_timeDF(cls, df: pd.DataFrame, title: str = 'Yaw时序图', xlabel: str = '时间', ylabel: str = 'Yaw') -> None:
        # 时间序列分析
        df['Time'] = pd.to_datetime(df['Time'])
        df = df.sort_values('Time')

        plt.figure(figsize=(10, 5))
        ax = plt.gca()

        # 设置日期格式化器和日期刻度定位器
        date_fmt = mdates.DateFormatter("%H:%M")  # 显示小时:分钟
        date_locator = mdates.AutoDateLocator()  # 自动选择刻度间隔

        # 隐藏右边框和上边框
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)

        # 绘制折线图
        plt.plot(df['Time'], df['Yaw'], marker='o', linestyle='-', color='b')

        # 设置x轴日期格式和刻度定位
        ax.xaxis.set_major_formatter(date_fmt)
        ax.xaxis.set_major_locator(date_locator)

        # 设置刻度朝向内部，并调整刻度与坐标轴的距离
        ax.tick_params(axis='x', direction='in', pad=10)
        ax.tick_params(axis='y', direction='in', pad=10)

        plt.xlabel(xlabel, fontproperties='SimSun', fontsize=10)
        plt.ylabel(ylabel, fontproperties='SimSun', fontsize=10)
        plt.title(title, fontproperties='SimSun', fontsize=12)
        plt.grid(True)

        # 调整底部边界向上移动一点
        plt.subplots_adjust(bottom=0.15)
        plt.show()

