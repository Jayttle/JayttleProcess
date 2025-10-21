# CommonUtils 通用工具模块

通用工具模块提供了一系列实用的工具类和函数，涵盖装饰器、自动化控制、网络通信、数据传输等多个方面。

## 📋 模块概览

本模块包含以下5个核心工具文件：

| 文件名 | 代码量 | 主要功能 |
|--------|--------|----------|
| `CommonDecorator.py` | 69行 | 常用Python装饰器 |
| `ComputerControl.py` | 302行 | 计算机自动化控制 |
| `EmailsmtplibUse.py` | 249行 | 邮件收发功能 |
| `FTPCommonUse.py` | 678行 | FTP传输与RINEX处理 |
| `WebsiteCrawler.py` | 174行 | 网页爬虫工具 |

---

## 📄 CommonDecorator.py

### 功能说明
提供4种常用Python装饰器，用于增强函数功能。

### 装饰器列表

#### 1. `@log_function_call`
**功能**：记录函数调用的完整信息
- 调用时间
- 传入参数（仅记录基础类型）
- 返回值类型
- 执行时间

**使用示例**：
```python
from JayttleProcess.CommonUtils.CommonDecorator import log_function_call

@log_function_call
def process_data(data, threshold=0.5):
    # 处理数据
    return processed_result
```

**输出示例**：
```
Function 'process_data' called at 2024-01-01 12:00:00.123456
Arguments: data=100, threshold=0.5
Returned data type: dict
executed in 0.0023s
```

#### 2. `@cache_results`
**功能**：缓存函数执行结果，避免重复计算
- 基于参数生成缓存键
- 自动检测缓存命中
- 支持位置参数和关键字参数

**使用示例**：
```python
from JayttleProcess.CommonUtils.CommonDecorator import cache_results

@cache_results
def expensive_calculation(x, y):
    # 耗时计算
    return x ** y
```

#### 3. `@timeit`
**功能**：测量函数执行时间
- 精确到小数点后4位
- 不记录参数信息
- 轻量级性能测试

**使用示例**：
```python
from JayttleProcess.CommonUtils.CommonDecorator import timeit

@timeit
def data_processing():
    # 数据处理逻辑
    pass
```

**输出示例**：
```
Function 'data_processing' executed in 1.2345s
```

#### 4. `@catch_exceptions`
**功能**：捕获函数异常并返回默认值
- 防止程序崩溃
- 自动打印异常信息
- 可自定义默认返回值

**使用示例**：
```python
from JayttleProcess.CommonUtils.CommonDecorator import catch_exceptions

@catch_exceptions(default_value=[])
def read_file(file_path):
    with open(file_path, 'r') as f:
        return f.readlines()
```

### 组合使用
装饰器支持叠加使用：
```python
@log_function_call
@timeit
@cache_results
def complex_function(a, b):
    return a + b
```

---

## 💻 ComputerControl.py

### 功能说明
提供计算机自动化控制功能，包括鼠标键盘操作、OCR识别、文件管理和TBC自动处理。

### 依赖配置
```python
# Tesseract OCR路径配置（需修改为实际安装路径）
pytesseract.pytesseract.tesseract_cmd = r'D:\Program Files\Tesseract-OCR\tesseract.exe'
```

### 核心功能

#### 1. 鼠标操作

##### `move_and_click(x, y)`
移动鼠标到指定坐标并单击
```python
from JayttleProcess.CommonUtils.ComputerControl import move_and_click
move_and_click(100, 200)  # 点击坐标(100, 200)
```

##### `move_and_Twoclick(x, y)`
移动鼠标到指定坐标并双击
```python
move_and_Twoclick(100, 200)  # 双击坐标(100, 200)
```

##### `move_and_click_with_shift(x, y)`
按住Shift键的鼠标移动单击（用于多选）
```python
move_and_click_with_shift(100, 300)  # Shift+点击
```

##### `right_click_and_press_D()`
右键并按下键盘的D键（用于删除操作）

##### `move_up_with_right_click(distance)`
按住右键向上拖动指定距离
```python
move_up_with_right_click(100)  # 向上拖动100像素
```

##### `get_mouse_position()`
获取当前鼠标位置
```python
x, y = get_mouse_position()
print(f"鼠标位置: ({x}, {y})")
```

#### 2. 键盘操作

##### `type_string(string)`
输入字符串（仅支持英文）
```python
type_string("hello_world")
```

##### `press_delete_key()`
按下Delete键

##### `press_ctrl_space()`
按下Ctrl+Space组合键

#### 3. OCR文字识别

##### `read_text_from_window(window_region)`
从指定窗口区域读取文本
```python
# 参数：(x, y, width, height)
window_region = (100, 100, 200, 50)
text = read_text_from_window(window_region)
print(f"识别到的文本: {text}")
```

**说明**：
- 自动进行灰度化和二值化处理
- 支持中文识别（使用chi_sim语言包）
- 会保存临时截图文件`temp_screenshot.png`

#### 4. 文件夹管理

##### `get_subdirectories_with_no_csv(folder_path)`
获取目标文件夹中所有没有CSV文件的子文件夹
```python
folders = get_subdirectories_with_no_csv(r'D:\Data')
print(f"无CSV文件的文件夹: {folders}")
```

##### `get_csv_file_paths(folder_path)`
获取目标文件夹中所有CSV文件的路径（递归搜索）
```python
csv_files = get_csv_file_paths(r'D:\Data')
for file in csv_files:
    print(file)
```

##### `list_folders(directory)`
获取目标文件夹下的所有子文件夹名字（递归）
```python
folders = list_folders(r'D:\Projects')
```

##### `check_data_points(folder_path)`
检查文件夹中CSV文件的数据点数量，删除不符合要求的文件
```python
check_data_points(r'D:\Data\Station')
```

#### 5. TBC自动处理

##### `TBC_auto_Process(Merge_path, save_path)`
自动化处理TBC软件中的GNSS数据
```python
TBC_auto_Process(
    Merge_path=r'D:\GNSS\Merge',
    save_path='R051_0407'
)
```

**功能流程**：
1. 检查并清空TBC输入数据
2. 导入RINEX文件到TBC
3. 执行基线解算
4. 导出处理结果
5. 清理临时文件

**注意事项**：
- 需要TBC软件已打开
- 窗口坐标需要根据实际屏幕分辨率调整
- 超时时间设置：输入60秒，解算90秒

##### `auto_turn_off()`
自动关机功能
```python
auto_turn_off()  # 执行系统关机
```

---

## 📧 EmailsmtplibUse.py

### 功能说明
提供QQ邮箱的邮件收发功能，支持纯文本、附件发送和POP3接收。

### EmailUseType 类

#### 初始化

**方式1：从配置文件加载**
```python
from JayttleProcess.CommonUtils.EmailsmtplibUse import EmailUseType

email = EmailUseType('config.json')
```

**方式2：手动输入配置**
```python
email = EmailUseType()
email.input_emailInfo(
    sender='your_email@qq.com',
    passwd='your_auth_code',  # QQ邮箱授权码
    receiver='receiver@qq.com'
)
```

#### 配置文件格式（config.json）
```json
{
    "QQ_email_config": {
        "username": "your_email@qq.com",
        "passwd": "授权码（非邮箱密码）",
        "receiver": "receiver@qq.com"
    }
}
```

### 核心方法

#### 1. `check_emailInfo()`
检查当前邮箱配置
```python
email.check_emailInfo()
```

**输出**：
```
----- Email Info -----
Sender: your_email@qq.com
User: your_email@qq.com
Password: ****************
Receiver: receiver@qq.com
```

#### 2. `send_QQ_email_plain(email_title, email_content)`
发送纯文本邮件
```python
email.send_QQ_email_plain(
    email_title='测试邮件',
    email_content='这是邮件正文内容'
)
```

**参数**：
- `email_title`：邮件主题
- `email_content`：邮件正文（支持中文）

#### 3. `send_QQ_email_mul(email_title, email_content, annex_path)`
发送带附件的邮件
```python
email.send_QQ_email_mul(
    email_title='数据报告',
    email_content='请查收附件中的数据报告',
    annex_path=r'D:\report.pdf'
)
```

**参数**：
- `email_title`：邮件主题
- `email_content`：邮件正文
- `annex_path`：附件文件路径

**支持的附件格式**：
- 文档：PDF, Word, Excel, TXT
- 图片：JPG, PNG, GIF
- 压缩包：ZIP, RAR
- 其他任意格式

#### 4. `get_email_and_save()`
接收邮件并保存（最近7天内的邮件）
```python
email.get_email_and_save()
```

**功能**：
- 通过POP3协议接收邮件
- 只处理最近7天内的邮件
- 自动解析邮件头部（发件人、主题、日期）
- 根据邮件类型保存：
  - 纯文本：打印到控制台
  - HTML：保存为`.html`文件
  - 附件：保存原始文件
- 自动创建发件人文件夹分类存储

**保存结构**：
```
当前目录/
├── 发件人1/
│   ├── 邮件主题1.html
│   └── 邮件主题2.jpg
└── 发件人2/
    └── 邮件主题3.html
```

### 使用示例

**完整示例：发送报告邮件**
```python
from JayttleProcess.CommonUtils.EmailsmtplibUse import EmailUseType

# 初始化
email = EmailUseType('config.json')

# 检查配置
email.check_emailInfo()

# 发送带附件的邮件
email.send_QQ_email_mul(
    email_title='每日数据报告 - 2024-01-01',
    email_content='您好，\n\n附件是今日的数据分析报告，请查收。\n\n此致\n敬礼',
    annex_path=r'D:\Reports\daily_report_20240101.xlsx'
)
```

**完整示例：批量接收邮件**
```python
from JayttleProcess.CommonUtils.EmailsmtplibUse import EmailUseType

# 初始化
email = EmailUseType('config.json')

# 接收并保存最近7天的邮件
email.get_email_and_save()
```

### 注意事项
1. **授权码获取**：
   - 登录QQ邮箱网页版
   - 设置 → 账户 → POP3/IMAP/SMTP服务
   - 开启服务并生成授权码

2. **端口说明**：
   - SMTP SSL端口：465
   - POP3 SSL端口：995

3. **邮件编码**：自动处理中文编码问题

4. **错误处理**：所有方法都包含异常捕获，失败时会打印错误信息

---

## 🌐 FTPCommonUse.py

### 功能说明
提供FTP文件传输功能和RINEX数据处理流程，专门用于GNSS数据的自动化处理。

### FTPConfig 类

#### 初始化
从JSON配置文件加载FTP配置
```python
from JayttleProcess.CommonUtils.FTPCommonUse import FTPConfig

ftp_config = FTPConfig('options.json')
print(ftp_config)  # 打印配置信息
```

#### 配置文件格式（options.json）
```json
{
    "FtpOptions": {
        "Address": "ftp.example.com",
        "Port": 21,
        "UserName": "username",
        "Password": "password"
    },
    "RootFolder": "/data/gnss",
    "LocalSavePath": "D:\\GNSS\\Download"
}
```

### 核心函数

#### 1. FTP文件操作

##### `check_FTP_file()`
检查FTP服务器文件并保存文件列表
```python
from JayttleProcess.CommonUtils.FTPCommonUse import check_FTP_file

success = check_FTP_file()
```

**功能**：
- 连接FTP服务器
- 遍历指定文件夹（tower3, tower5, tower7, tower8, towerbase1, towerbase2）
- 将每个文件夹的文件列表保存到txt文件
- 生成汇总文件`all_files.txt`

##### `download_files_from_ftp(ftp_config, remote_folder, files_to_download, local_save_path)`
从FTP下载指定文件
```python
from JayttleProcess.CommonUtils.FTPCommonUse import download_files_from_ftp, FTPConfig

ftp_config = FTPConfig('options.json')
files = ['file1.rnx', 'file2.rnx']

success = download_files_from_ftp(
    ftp_config=ftp_config,
    remote_folder='tower3',
    files_to_download=files,
    local_save_path='D:\\GNSS\\Data'
)
```

**特点**：
- 自动跳过已存在的文件
- 支持.crx.Z和.rnx.Z格式识别
- 自动创建本地目录

##### `download_files_from_ftp_by_txt(ftp_config, txt_file_path, local_save_path)`
根据txt文件列表批量下载
```python
success = download_files_from_ftp_by_txt(
    ftp_config=ftp_config,
    txt_file_path='B011_toDownload.txt',
    local_save_path='D:\\GNSS\\Data'
)
```

**说明**：
- txt文件每行一个文件名
- 根据文件名前4个字符自动识别目标文件夹
- B011 → towerbase1, R031 → tower3

#### 2. RINEX数据处理流程

##### `Process_Part1(output_file_path, specified_marker_names, start_hour, end_hour)`
生成待下载文件列表
```python
from JayttleProcess.CommonUtils.FTPCommonUse import Process_Part1

Process_Part1(
    output_file_path='D:\\GNSS\\toDownload',
    specified_marker_names=['B011', 'B021', 'R031'],
    start_hour=16,
    end_hour=19
)
```

**功能**：
- 读取FTP文件列表
- 筛选指定时间段的文件
- 检查文件完整性（每个站点8个文件）
- 生成`站点_toDownload.txt`文件

##### `Process_Part2(toDownload_path, local_save_path)`
执行文件下载
```python
from JayttleProcess.CommonUtils.FTPCommonUse import Process_Part2

Process_Part2(
    toDownload_path='D:\\GNSS\\toDownload',
    local_save_path='D:\\GNSS\\FTP'
)
```

**功能**：
- 读取所有`_toDownload.txt`文件
- 批量下载文件
- 删除小文件（<0.1MB）

##### `Process_Part3(local_save_path)`
解压和格式转换
```python
from JayttleProcess.CommonUtils.FTPCommonUse import Process_Part3

Process_Part3(local_save_path='D:\\GNSS\\FTP')
```

**功能**：
- 解压缩.Z格式文件
- CRX转RNX格式（调用CRX2RNX.exe）

##### `Process_Part4(local_save_path, merge_path)`
合并RINEX文件
```python
from JayttleProcess.CommonUtils.FTPCommonUse import Process_Part4

Process_Part4(
    local_save_path='D:\\GNSS\\FTP',
    merge_path='D:\\GNSS\\Merge'
)
```

**功能**：
- 按日期合并同一天的RNX文件
- 分别合并观测文件（O）和导航文件（N）
- 修改MO文件的MARKER NAME

##### `Process_Copy(isFirst, from_copy_merge_folder_list, toDownload_path, merge_path)`
复制已处理的数据
```python
from JayttleProcess.CommonUtils.FTPCommonUse import Process_Copy

Process_Copy(
    isFirst=False,
    from_copy_merge_folder_list=['D:\\GNSS\\Merge1', 'D:\\GNSS\\Merge2'],
    toDownload_path='D:\\GNSS\\toDownload',
    merge_path='D:\\GNSS\\Merge'
)
```

**功能**：
- 复制历史处理数据，避免重复下载
- 自动更新待下载列表

#### 3. 一键处理流程

##### `Process_in_one_step()`
完整的GNSS数据处理流程
```python
from JayttleProcess.CommonUtils.FTPCommonUse import Process_in_one_step

Process_in_one_step()
```

**处理流程**：
```
1. 生成下载列表 (Process_Part1)
2. 复制历史数据 (Process_Copy)
3. 下载新数据 (Process_Part2)
4. 解压转换 (Process_Part3)
5. 合并文件 (Process_Part4)
6. TBC处理（可选）
7. 检查统计 (Process_Check)
```

**配置参数**（在函数内修改）：
```python
base_marker_names = ['B011', 'B021']  # 基准站
to_process_marker_names = ['R051', 'R052', 'R071']  # 流动站
start_hour = 4  # 开始时间
end_hour = 7    # 结束时间
TBC_Process = False  # 是否执行TBC处理
```

### 使用示例

**完整示例：GNSS数据自动处理**
```python
from JayttleProcess.CommonUtils.FTPCommonUse import *

# 方式1：分步执行
# 步骤1：生成下载列表
Process_Part1(
    output_file_path='D:\\GNSS\\toDownload',
    specified_marker_names=['B011', 'B021', 'R031'],
    start_hour=16,
    end_hour=19
)

# 步骤2：下载文件
Process_Part2(
    toDownload_path='D:\\GNSS\\toDownload',
    local_save_path='D:\\GNSS\\FTP'
)

# 步骤3：解压转换
Process_Part3(local_save_path='D:\\GNSS\\FTP')

# 步骤4：合并文件
Process_Part4(
    local_save_path='D:\\GNSS\\FTP',
    merge_path='D:\\GNSS\\Merge'
)

# 方式2：一键执行（推荐）
Process_in_one_step()
```

### 辅助函数

#### `copy_files(from_folder, to_folder, prefix)`
复制指定前缀的文件
```python
copy_files(
    from_folder='D:\\Source',
    to_folder='D:\\Target',
    prefix='R031'
)
```

#### `check_folders(folder_path)`
检查文件夹完整性
```python
check_folders('D:\\GNSS\\Merge')
```

#### `delete_small_rnx_files(folder_path)`
删除小于2KB的RNX文件
```python
delete_small_rnx_files('D:\\GNSS\\Data')
```

### 注意事项
1. **CRX2RNX.exe**：需要单独下载并配置路径
2. **文件命名规范**：严格遵循RINEX 3.0命名规范
3. **时间处理**：所有时间使用GPS时间
4. **多线程**：合并操作支持多线程（默认4线程）
5. **错误处理**：所有步骤都有完整的错误处理和日志输出

---

## 🕷️ WebsiteCrawler.py

### 功能说明
提供网页数据爬虫功能，支持静态和动态网页爬取，专门用于天气数据获取。

### 依赖配置
```python
# Chrome WebDriver路径配置（需修改为实际路径）
service = Service(executable_path='D:\Program Files (x86)\Software\OneDrive\PyPackages_tool\chromedriver-win64\chromedriver.exe')
```

### 核心函数

#### 1. 静态网页爬取

##### `get_weather_data()`
爬取天气预报网站数据
```python
from JayttleProcess.CommonUtils.WebsiteCrawler import get_weather_data

temperatures = get_weather_data()
print(temperatures)  # ['23°', '25°', '22°', ...]
```

**说明**：
- 目标网站：weather.com.cn
- 返回温度数据列表
- 自动处理中文编码

##### `plot_weather_data(temperatures)`
绘制温度数据折线图
```python
from JayttleProcess.CommonUtils.WebsiteCrawler import plot_weather_data

temperatures = get_weather_data()
plot_weather_data(temperatures)
```

#### 2. 动态网页爬取

##### `drive_chrome()`
使用Selenium爬取动态网页天气数据
```python
from JayttleProcess.CommonUtils.WebsiteCrawler import drive_chrome

drive_chrome()
```

**功能**：
- 自动打开Chrome浏览器
- 爬取指定城市的天气历史记录
- 自动识别页面元素
- 保存数据到`weather_data.txt`
- 自动去重和排序
- 统计缺失日期

**数据格式**：
```
日期\t内容1\t内容2\t...
2024-01-01	晴	23°C	...
2024-01-02	多云	21°C	...
```

**特点**：
- 只处理最近7天内的邮件
- 自动跳过已存在的数据
- 实时显示缺失日期统计

#### 3. 数据处理

##### `read_weather_data(file_path)`
读取天气数据文件
```python
from JayttleProcess.CommonUtils.WebsiteCrawler import read_weather_data

data_dict = read_weather_data('weather_data.txt')
# data_dict: {datetime对象: (日期字符串, 内容)}
```

**返回格式**：
```python
{
    datetime(2024, 1, 1): ('2024-01-01', '晴\t23°C\t...'),
    datetime(2024, 1, 2): ('2024-01-02', '多云\t21°C\t...'),
    ...
}
```

##### `count_missing_dates(data_dict, year, month)`
统计指定月份的缺失日期数量
```python
from JayttleProcess.CommonUtils.WebsiteCrawler import count_missing_dates

missing_count = count_missing_dates(data_dict, 2024, 1)
print(f"2024年1月缺失 {missing_count} 天数据")
```

##### `find_missing_dates(data_dict, start_year, end_year)`
查找指定时间范围内所有缺失日期
```python
from JayttleProcess.CommonUtils.WebsiteCrawler import find_missing_dates

missing_dates = find_missing_dates(data_dict, 2023, 2024)
# 返回: {年份: {月份: [缺失日期列表]}}
```

##### `run_find_missing_dates()`
运行缺失日期检测（2023-2024年）
```python
from JayttleProcess.CommonUtils.WebsiteCrawler import run_find_missing_dates

run_find_missing_dates()
```

**输出示例**：
```
2024 January 缺失日期：
2024-01-05
2024-01-12

2024 February 缺失日期：
2024-02-08
```

### 使用示例

**示例1：快速爬取天气数据**
```python
from JayttleProcess.CommonUtils.WebsiteCrawler import get_weather_data, plot_weather_data

# 爬取数据
temperatures = get_weather_data()

# 可视化
plot_weather_data(temperatures)
```

**示例2：爬取历史天气数据**
```python
from JayttleProcess.CommonUtils.WebsiteCrawler import drive_chrome

# 启动自动爬虫
drive_chrome()
# 注意：需要手动点击浏览器中的"前一天"按钮来翻页
```

**示例3：检测缺失数据**
```python
from JayttleProcess.CommonUtils.WebsiteCrawler import run_find_missing_dates

# 检测2023-2024年的缺失数据
run_find_missing_dates()
```

**示例4：完整数据处理流程**
```python
from JayttleProcess.CommonUtils.WebsiteCrawler import *

# 1. 读取已有数据
data_dict = read_weather_data('weather_data.txt')

# 2. 检测缺失
missing_dates = find_missing_dates(data_dict, 2024, 2024)

# 3. 启动爬虫补充缺失数据
if missing_dates:
    drive_chrome()

# 4. 再次检测
run_find_missing_dates()
```

### 注意事项
1. **Chrome Driver版本**：需与Chrome浏览器版本匹配
2. **反爬机制**：添加适当的等待时间，避免被封IP
3. **数据去重**：自动处理重复数据
4. **编码问题**：自动处理UTF-8编码
5. **等待元素**：使用WebDriverWait确保元素加载完成
6. **手动操作**：drive_chrome需要手动点击翻页按钮

---

## 🔧 依赖安装

### 所有模块通用依赖
```bash
pip install functools
pip install datetime
```

### ComputerControl.py 依赖
```bash
pip install pyautogui
pip install pillow
pip install pytesseract  # 需要先安装Tesseract-OCR
pip install chardet
```

### EmailsmtplibUse.py 依赖
```bash
pip install email
pip install smtplib
pip install poplib
pip install json
```

### FTPCommonUse.py 依赖
```bash
pip install ftplib
pip install shutil
pip install openpyxl
pip install pathlib
```

### WebsiteCrawler.py 依赖
```bash
pip install requests
pip install beautifulsoup4
pip install matplotlib
pip install selenium
```

### 外部软件依赖
1. **Tesseract-OCR**：
   - 下载：https://github.com/tesseract-ocr/tesseract
   - 安装后配置路径到`ComputerControl.py`

2. **Chrome WebDriver**：
   - 下载：https://chromedriver.chromium.org/
   - 版本需与Chrome浏览器匹配
   - 配置路径到`WebsiteCrawler.py`

3. **CRX2RNX.exe**：
   - 用于RINEX文件格式转换
   - 下载：https://terras.gsi.go.jp/ja/crx2rnx.html

---

## 📦 配置文件模板

### config.json（完整配置）
```json
{
    "QQ_email_config": {
        "username": "your_email@qq.com",
        "passwd": "your_auth_code",
        "receiver": "receiver@qq.com"
    },
    "FtpOptions": {
        "Address": "ftp.example.com",
        "Port": 21,
        "UserName": "username",
        "Password": "password"
    },
    "RootFolder": "/data/gnss",
    "LocalSavePath": "D:\\GNSS\\Download"
}
```

---

## 🎯 应用场景

### 1. 自动化测试
- 使用装饰器进行性能测试
- 使用ComputerControl进行UI自动化

### 2. 数据采集
- 使用WebsiteCrawler爬取网页数据
- 使用EmailsmtplibUse接收数据邮件

### 3. GNSS数据处理
- 使用FTPCommonUse完整处理流程
- 使用ComputerControl自动化TBC软件操作

### 4. 日志监控
- 使用装饰器记录函数执行情况
- 使用Email发送告警邮件

### 5. 批量任务
- 使用FTP批量下载文件
- 使用装饰器缓存计算结果

---

## ⚠️ 注意事项

1. **路径配置**：所有涉及文件路径的地方都需要根据实际情况修改
2. **权限问题**：某些自动化操作可能需要管理员权限
3. **网络问题**：FTP和Email功能需要稳定的网络连接
4. **编码问题**：所有文本处理都支持UTF-8编码
5. **异常处理**：建议在实际使用时添加try-except块
6. **性能优化**：大批量数据处理时建议使用多线程
7. **安全性**：配置文件中的密码需妥善保管

---

## 📝 更新日志

- **v1.0.0** (2024-01)
  - 初始版本发布
  - 包含5个核心工具模块
  - 支持装饰器、自动化控制、邮件、FTP、爬虫功能

---

## 👥 贡献

欢迎提交Issue和Pull Request来改进这些工具！

---

**最后更新**: 2024年
**模块版本**: 1.0.0

