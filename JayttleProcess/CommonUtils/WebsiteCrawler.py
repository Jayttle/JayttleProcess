import requests  # 导入requests库，用于发送HTTP请求
from bs4 import BeautifulSoup  # 导入BeautifulSoup库，用于解析网页内容
import matplotlib.pyplot as plt  # 导入Matplotlib库，用于数据可视化
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
import time


def get_weather_data():
    url = 'http://www.weather.com.cn/weather/101010100.shtml'  # 天气预报页面的URL
    response = requests.get(url)  # 发送GET请求，获取网页内容
    response.encoding = 'utf-8'  # 设置编码为utf-8，确保正确解析中文
    soup = BeautifulSoup(response.text, 'html.parser')  # 使用BeautifulSoup解析网页内容

    temperatures = []  # 存储温度数据的列表
    temperature_elements = soup.select('.tem span')  # 使用CSS选择器获取温度数据的HTML元素
    for element in temperature_elements:
        temperatures.append(element.text)  # 提取温度数据并添加到列表中

    return temperatures  # 返回温度数据列表


def plot_weather_data(temperatures):
    plt.plot(temperatures)  # 绘制折线图

    plt.title('Weather Forecast')  # 设置图表标题
    plt.xlabel('Days')  # 设置X轴标签
    plt.ylabel('Temperature (°C)')  # 设置Y轴标签

    plt.show()  # 显示图表

def read_weather_data(file_path):
    data_dict = {}  # 创建一个空字典来存储数据

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            parts = line.strip().split('\t')  # 通过制表符分割行
            date_str = parts[0]  # 第一部分是日期字符串
            date = datetime.strptime(date_str, '%Y-%m-%d')  # 将日期字符串转换为datetime对象
            content = '\t'.join(parts[1:])  # 将剩余部分作为内容连接起来
            data_dict[date] = (date_str, content)  # 将内容作为元组与日期字符串一起存储

    return data_dict

def count_missing_dates(data_dict, year, month):
    # 获取每个月份的第一天和最后一天
    start_date = datetime(year, month, 1)
    end_date = datetime(year, month, 1) + timedelta(days=32)
    end_date = datetime(end_date.year, end_date.month, 1) - timedelta(days=1)

    # 计算缺失日期的个数
    missing_dates_count = sum(1 for current_date in (start_date + timedelta(n) for n in range((end_date - start_date).days + 1))
                              if current_date not in data_dict)

    return missing_dates_count


def drive_chrome():
    # 创建 Chrome WebDriver 的 Service 对象并指定路径
    service = Service(executable_path='D:\Program Files (x86)\Software\OneDrive\PyPackages_tool\chromedriver-win64\chromedriver.exe')

    # 使用 Service 对象创建 Chrome WebDriver
    driver = webdriver.Chrome(service=service)

    # 打开网页
    driver.get("https://www.msn.cn/zh-cn/weather/records/in-%E5%B1%B1%E4%B8%9C%E7%9C%81,%E4%B8%B4%E6%B2%82%E5%B8%82?loc=eyJhIjoi5bGx5Lic6LS55Y6%2F5Yac5p2R5ZCI5L2c6ZO26KGM5rCR5Li75YiG55CG5aSEIiwibCI6Iui0ueWOvyIsInIiOiLlsbHkuJznnIEiLCJyMiI6IuS4tOayguW4giIsImMiOiLkuK3ljY7kurrmsJHlhbHlkozlm70iLCJpIjoiY24iLCJ0IjoxMDEsImciOiJ6aC1jbiIsIngiOiIxMTcuOTc1ODczIiwieSI6IjM1LjI2MzA0NiJ9&weadegreetype=C&ocid=ansmsnweather&cvid=af7267d843b94c4bfce9c51bd1d9856d")

    try:
        file_path = r"D:\Program Files (x86)\Software\OneDrive\PyPackages\weather_data.txt"
        data_dict = read_weather_data(file_path)

        while True:
            # 显示等待直到 div 元素可见
            div_element = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "div.tooltipContainer-DS-EntryPoint1-1"))
            )

            # 获取 div 元素文本内容
            div_text = div_element.text

            # 解析日期和内容
            lines = div_text.split('\n')
            date_str = lines[0]

            # Convert date string to datetime object
            date = datetime.strptime(date_str, '%Y年%m月%d日')

            # Convert date object to desired format
            formatted_date = date.strftime('%Y-%m-%d')

            content = '\t'.join(lines[1:])  # Skip the date line

            # Check if the date already exists in data_dict
            if date not in data_dict:
                # Print the formatted date if it's a new entry
                print(formatted_date)
                # Add the data to the dictionary
                data_dict[date] = (formatted_date, content)
                # Calculate the number of missing dates for the current year and month
                missing_dates_count = count_missing_dates(data_dict, date.year, date.month)
                print(f"缺失日期数（{date.year}年{date.month}月）: {missing_dates_count}")

    except Exception as e:
        print("An error occurred:", e)

    # 打印并按照日期排序写入到文件
    with open("weather_data.txt", "w", encoding="utf-8") as file:
        for date, (formatted_date, content) in sorted(data_dict.items()):
            file.write(f"{formatted_date}\t{content}\n")
    # 关闭浏览器
    driver.quit()


def find_missing_dates(data_dict, start_year, end_year):
    missing_dates_by_month = {}  # 存储每个月份缺失日期的字典
    
    # 遍历每个年份
    for year in range(start_year, end_year + 1):
        # 遍历每个月份
        for month in range(1, 13):
            missing_dates = []  # 存储当前月份缺失日期的列表

            # 获取每个月份的第一天和最后一天
            start_date = datetime(year, month, 1)
            end_date = datetime(year, month, 1) + timedelta(days=32)
            end_date = datetime(end_date.year, end_date.month, 1) - timedelta(days=1)

            # 遍历每一天
            current_date = start_date
            while current_date <= end_date:
                # 检查当前日期是否在数据中缺失
                if current_date not in data_dict:
                    missing_dates.append(current_date)
                # 前进到下一天
                current_date += timedelta(days=1)

            # 存储当前月份的缺失日期
            if year not in missing_dates_by_month:
                missing_dates_by_month[year] = {}
            missing_dates_by_month[year][month] = missing_dates

    return missing_dates_by_month

def run_find_missing_dates():
    data_dict = {}  # 初始化空字典
    # 合并两年的数据
    data_dict.update(read_weather_data("weather_data.txt"))
    
    start_year = 2023
    end_year = 2024
    missing_dates_by_month = find_missing_dates(data_dict, start_year, end_year)

    # 打印每个年份、每个月份的缺失日期
    for year, missing_dates_in_year in missing_dates_by_month.items():
        for month, missing_dates in missing_dates_in_year.items():
            # 只处理2024年1到5月份的数据
            if year == 2024 and month > 5:
                continue
            
            month_name = datetime(year, month, 1).strftime("%B")  # 获取月份名称
            print(f"{year} {month_name} 缺失日期：")
            for date in missing_dates:
                print(date.strftime("%Y-%m-%d"))
            print()  # 为了可读性增加一个空行 

if __name__ == '__main__':
    # 打印并按照日期排序写入到文件
    run_find_missing_dates()
    drive_chrome()