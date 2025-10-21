# JayttleProcess

一个功能丰富的Python工具包项目，提供数据处理、算法分析、自动化控制等多种实用功能。

## 📋 项目简介

JayttleProcess是一个集成化的Python工具库，专注于提供数据处理、机器学习、时序分析、数据库操作等功能。该项目特别适用于GNSS数据处理、传感器数据分析、自动化任务、时序数据管理以及工业能源数据分析。

## 📁 项目结构

```
JayttleProcess/
├── JayttleProcess/              # 主包目录
│   ├── Algorithm/               # 算法模块
│   │   ├── MachineLearning.py        # 机器学习算法实现（线性分类器、多类SVM）
│   │   ├── PredictiveModel.py        # 预测模型（SARIMA时序预测）
│   │   ├── AnomalyDetectionModel.py  # 异常检测模型（多种无监督算法）
│   │   └── BaselineModel.py          # 基线模型（能源基线分析）
│   │
│   ├── CommonUtils/             # 通用工具模块
│   │   ├── CommonDecorator.py   # 常用装饰器（日志、计时、缓存、异常处理）
│   │   ├── ComputerControl.py   # 计算机自动化控制（鼠标键盘操作、OCR识别）
│   │   ├── EmailsmtplibUse.py   # 邮件收发功能（QQ邮箱）
│   │   ├── FTPCommonUse.py      # FTP文件传输与RINEX数据处理
│   │   └── WebsiteCrawler.py    # 网页爬虫（天气数据获取）
│   │
│   ├── DataProcess/             # 数据处理模块
│   │   ├── ListFloatDataMethod.py      # 列表浮点数据处理方法
│   │   ├── TiltmeterCommonUse.py       # 倾斜仪数据处理与可视化
│   │   ├── TimeDataFrameMethod.py      # 时间数据框处理方法
│   │   └── TimeSeriesDataMethod.py     # 时间序列数据分析（包含多种算法）
│   │
│   ├── PlotAnalysis/            # 绘图分析模块
│   │   ├── PNGProcess.py        # PNG图像处理（灰度转换）
│   │   └── PlotUtils.py         # 绘图工具集（专业数据可视化）
│   │
│   ├── SpecificProcess/         # 特定处理模块
│   │   ├── RinexCommonManage.py # RINEX文件管理（GNSS数据处理）
│   │   └── TBCProcessCsv.py     # TBC处理CSV数据（GNSS数据点处理）
│   │
│   └── SQLProcess/              # 数据库处理模块
│       ├── SQLCommonUse.py      # MySQL数据库通用操作
│       └── TaosUtils.py         # TDengine时序数据库工具
│
├── JayttleRead/                 # 文档资源目录
│   ├── markdown_theme/          # Markdown主题配置文件
│   ├── 如何用Docker做镜像.md     # Docker镜像制作指南
│   └── 深度学习入门学习指南.md   # 深度学习学习资料
│
├── git_commit_push.py           # Git自动提交推送脚本
└── README.md                    # 项目说明文档
```

## 🔧 主要功能模块

### 1. Algorithm（算法模块）

#### MachineLearning.py
- **LinearClassifier**: 线性分类器，使用梯度下降法训练
- **MulticlassSVM**: 多类支持向量机，实现hinge损失和L2正则化

#### PredictiveModel.py
- **SARIMA时序预测**: 季节性自回归综合移动平均模型
- **网格搜索参数优化**: 自动寻找最佳SARIMA参数
- **数据读取与准备**: 支持Excel数据导入和训练集/测试集划分
- **预测可视化**: 绘制训练集、实际值和预测值对比图

#### AnomalyDetectionModel.py
高度封装的无监督故障识别类，支持多种异常检测算法：
- **孤立森林 (Isolation Forest)**: 基于树结构的异常检测
- **单类支持向量机 (One-Class SVM)**: 基于SVM的异常检测
- **局部异常因子 (LOF)**: 基于密度的局部异常检测
- **DBSCAN聚类**: 基于密度的聚类异常检测
- **PCA异常检测**: 基于主成分分析的异常检测
- **统计学方法**: IQR和Z-score统计异常检测
- **特征权重支持**: 可自定义特征重要性权重
- **数据预处理**: 支持多种标准化方法（Standard/MinMax/Robust）
- **批次管理**: 支持按批次标识进行异常检测
- **结果可视化**: 提供异常分数和检测结果的可视化

#### BaselineModel.py
能源基线模型，用于工业能源消耗基线分析：
- **当前基线与历史基线**: 支持当前数据和历史数据的双基线模式
- **基线权重配置**: 可自定义当前基线和历史基线的权重
- **自动异常检测**: 集成AnomalyDetectionModel进行基线计算
- **特征范围提取**: 自动提取正常样本的特征上下限
- **能源数据处理**: 针对工业能源数据的专业处理
- **TDengine集成**: 支持将基线数据保存到TDengine数据库

### 2. CommonUtils（通用工具模块）

#### CommonDecorator.py
提供多种实用装饰器：
- `@log_function_call`: 函数调用日志记录（参数、返回类型、执行时间）
- `@cache_results`: 函数结果缓存
- `@timeit`: 函数执行时间统计
- `@catch_exceptions`: 异常捕获与默认值返回

#### ComputerControl.py
计算机自动化控制功能：
- **鼠标操作**: 移动、单击、双击、右键、按住移动等
- **键盘操作**: 按键、快捷键、输入文本
- **OCR文字识别**: 从屏幕区域读取文本（基于Tesseract）
- **文件夹管理**: 获取文件夹列表、CSV文件检查
- **TBC自动处理**: 自动化GNSS数据处理流程

#### EmailsmtplibUse.py
邮件收发功能：
- **发送纯文本邮件**: QQ邮箱SMTP发送
- **发送带附件邮件**: 支持多种文件格式附件
- **接收邮件**: POP3协议接收并保存邮件内容
- **配置文件支持**: 从JSON文件加载邮箱配置

#### FTPCommonUse.py
FTP文件传输与RINEX数据处理：
- **FTP连接**: 支持配置文件或直接输入连接信息
- **文件下载**: 批量下载指定文件
- **RINEX文件处理**: 
  - 文件解压缩（.Z格式）
  - CRX转RNX格式转换
  - 文件合并
  - 文件信息解析
- **自动化流程**: FTP下载、解压、转换、合并一键完成

#### WebsiteCrawler.py
网页数据爬虫：
- **天气数据获取**: 爬取天气预报网站数据
- **Selenium自动化**: 使用Chrome WebDriver进行动态网页爬取
- **数据存储**: 将爬取数据保存到文本文件
- **缺失日期检测**: 统计和查找数据缺失情况

### 3. DataProcess（数据处理模块）

#### TiltmeterCommonUse.py
倾斜仪数据处理：
- **TiltmeterData类**: 倾斜仪数据模型（时间、站点ID、俯仰角、横滚角）
- **数据读取**: 从文本文件读取倾斜仪数据
- **数据过滤**: 按日期筛选数据
- **数据可视化**: 绘制俯仰角和横滚角时序图

#### TimeDataFrameMethod.py
时间数据框处理：
- **数据清洗**: 缺失值检测、重复行删除
- **时间数据处理**: 时间格式转换和验证
- **数据分割**: 按站点ID分割数据
- **时序图绘制**: 时间序列数据可视化

#### TimeSeriesDataMethod.py
时间序列数据分析（包含大量算法）：
- **趋势分析**: 线性回归、多项式拟合
- **平稳性检验**: ADF检验、KPSS检验
- **时序模型**: ARIMA、AR模型
- **频域分析**: FFT、功率谱分析
- **小波分析**: 小波变换、去噪
- **EMD分解**: 经验模态分解
- **聚类分析**: K-means、DBSCAN、层次聚类
- **异常检测**: 多种异常检测算法

### 4. PlotAnalysis（绘图分析模块）

#### PNGProcess.py
- **图像转灰度**: 将PNG彩色图像转换为灰度图

#### PlotUtils.py
专业数据可视化工具集，提供丰富的绘图函数：
- **散点箱线联合图**: `plot_dataframe_scatter_with_boxplt` - 结合散点图和箱线图的多维数据展示
- **分组散点图**: `plot_scatter_horizontal` - 横向分组散点图，支持异常标记
- **分组时序图**: `plot_df_timeseries_groupby` - 按分组绘制时间序列数据
- **分组对比图**: `plot_df_value_groupby` - 分组数据对比可视化
- **双Y轴时序图**: `plot_double_y_timeseries` - 支持两个不同量级数据同时展示
- **分类决策边界**: `plot_decision_boundary` - 机器学习分类器决策边界可视化
- **多彩线图**: `plot_multicolor_line` - 支持按标签着色的多彩线条图
- **PDF批量导出**: `plot_multiple_figures_to_pdf` - 将多个图表保存到单个PDF文件
- **配置功能**:
  - 支持中文显示（楷体）
  - 自定义颜色映射
  - 统计分析集成（IQR、异常值检测）
  - 高DPI输出（150 DPI）
  - 自适应布局

### 5. SpecificProcess（特定处理模块）

#### RinexCommonManage.py
RINEX文件管理（GNSS数据处理）：
- **RinexFileInfo类**: RINEX文件信息解析
  - 站点名称、标记名称
  - GPS时间解析
  - 文件类型识别（观测值O/导航N）
  - 文件格式识别（CRX/RNX）
- **文件操作**:
  - 批量解压缩
  - CRX转RNX格式转换
  - 文件合并（按日期）
  - 文件统计与检查
- **多线程处理**: 支持多线程并行处理提高效率

#### TBCProcessCsv.py
TBC处理CSV数据：
- **DataPoint类**: GNSS数据点模型（坐标、精度、时间等）
- **GgkxDto类**: GNSS定位数据传输对象
- **CSV数据读写**: 支持多种编码格式
- **坐标转换**: WGS84到高斯投影转换
- **时序数据生成**: 将GNSS数据转换为时序数据
- **数据导出**: 导出到Excel或CSV格式

### 6. SQLProcess（数据库处理模块）

#### SQLCommonUse.py
MySQL数据库通用操作：
- **数据库连接**: 支持配置文件加载
- **SQL执行**: 执行任意SQL语句（SELECT/INSERT/UPDATE/DELETE）
- **查询结果保存**: 将查询结果保存到文本文件
- **时间范围查询**: 查询指定时间段的数据
- **数据统计**: 统计表中数据行数、时间差等

#### TaosUtils.py
TDengine时序数据库工具（功能非常丰富）：
- **数据库连接**: 支持TDengine WebSocket连接
- **超级表管理**: 创建超级表和子表
- **批量数据插入**:
  - 实时数据（nengyuan_real）
  - 批次数据（nengyuan_recipe）
  - 周期数据（nengyuan_period）
  - 预测数据（nengyuan_predict）
  - 基线数据（nengyuan_baseline）
  - 异常数据（nengyuan_anomaly）
- **数据查询**: 支持分批查询避免数据库压力
- **表管理**: 列出表、查看表结构等
- **工业数据支持**: 专门针对能源工业数据优化

### 7. JayttleRead（文档资源）

#### markdown_theme
- **Markdown主题配置**: 包含完整的Typora主题配置
- **SeeYue主题**: 精美的Markdown样式主题
  - 代码块高亮（支持明暗主题）
  - 图标字体支持
  - 中英文字体配置
  - 网站图标库（生活、工具、资源、编程、笔记等）
  - 响应式布局
  - 搜索面板美化
  - 表格样式优化

#### 如何用Docker做镜像.md
Docker容器化实践指南：
- Python项目Docker打包流程
- Dockerfile编写规范
- 镜像构建与推送
- 容器运行与管理
- requirements.txt配置
- 国内镜像源配置

#### 深度学习入门学习指南.md
深度学习系统学习资料：
- 学习路径规划（短期、中期、长期目标）
- 数学基础准备（线性代数、概率论、微积分）
- 深度学习基础理论
- 开发环境搭建（Python、PyTorch、TensorFlow）
- 核心算法学习（神经网络、CNN、RNN、Transformer）
- 实验项目实践
- 进阶学习方向
- 学习资源推荐（书籍、课程、论文）

### 8. 其他工具

#### git_commit_push.py
Git自动提交推送脚本：
- **自动分支管理**: 根据电脑名称自动选择分支
- **智能提交**: 检测代码变更，有变更才提交
- **自动推送**: 支持pull rebase和强制推送
- **错误处理**: 完善的异常捕获和重试机制
- **分支映射配置**: 
  - `Jayttle` → `xujuntao`分支
  - 其他电脑 → `feature-2`分支（默认）

## 🚀 安装依赖

### 基础依赖
```bash
pip install numpy pandas matplotlib
pip install scikit-learn scipy
pip install pyautogui pillow pytesseract
pip install requests beautifulsoup4 selenium
pip install pymysql taosws
pip install statsmodels PyEMD pywt
pip install pyproj chardet openpyxl
pip install seaborn joblib
```

### 深度学习依赖（可选）
```bash
pip install torch torchvision
pip install tensorflow
```

## 📦 配置文件

### config.json 示例

```json
{
    "QQ_email_config": {
        "username": "your_email@qq.com",
        "passwd": "your_auth_code",
        "receiver": "receiver@example.com"
    },
    "SQL_tianmeng_config": {
        "host": "localhost",
        "user": "root",
        "password": "password",
        "database": "database_name"
    },
    "TDengine_config": {
        "host": "localhost",
        "user": "root",
        "password": "taosdata",
        "database": "test_db",
        "port": 6030
    },
    "FtpOptions": {
        "Address": "ftp.example.com",
        "Port": 21,
        "UserName": "username",
        "Password": "password"
    },
    "RootFolder": "/path/to/folder",
    "LocalSavePath": "/path/to/save"
}
```

## 🛠️ 依赖软件

- **Tesseract-OCR**: 用于OCR文字识别功能（需单独安装）
- **Chrome WebDriver**: 用于Selenium网页爬虫（需下载对应版本）
- **CRX2RNX.exe**: 用于RINEX文件格式转换（需单独下载）
- **Docker**: 用于容器化部署（可选）

## 📝 注意事项

1. **Tesseract路径**: 在`ComputerControl.py`中需要配置Tesseract安装路径
2. **Chrome WebDriver**: 在`WebsiteCrawler.py`中需要配置Chrome WebDriver路径
3. **配置文件**: 大部分功能需要配置文件，请参考config.json示例
4. **编码问题**: 处理CSV文件时自动检测编码格式，支持多种编码
5. **时区问题**: 部分时间处理功能会自动处理时区转换
6. **异常检测**: AnomalyDetectionModel支持多种算法，建议根据数据特点选择合适算法
7. **基线计算**: BaselineModel需要足够的历史数据才能准确计算基线

## 🔄 Git分支管理

项目使用`git_commit_push.py`实现自动化Git操作，根据计算机名称自动选择分支：
- `Jayttle` → `xujuntao`分支
- 其他电脑 → `feature-2`分支（默认）

## 📈 应用场景

1. **GNSS数据处理**: RINEX文件处理、TBC自动化处理、坐标转换
2. **传感器数据分析**: 倾斜仪数据处理、时序数据分析
3. **时序预测**: SARIMA模型预测、异常检测
4. **自动化任务**: 邮件收发、FTP传输、网页爬虫
5. **数据库管理**: MySQL和TDengine数据库操作
6. **数据可视化**: 各类图表绘制和数据展示
7. **工业能源分析**: 能源消耗基线建模、异常检测、能耗预测
8. **无监督学习**: 多种无监督算法的异常检测和聚类分析
9. **科研文档**: Markdown主题定制、学习资料整理

## 🎯 特色功能

### 异常检测系统
- 支持6种主流无监督异常检测算法
- 可自定义特征权重
- 批次级别的异常识别
- 完整的可视化分析

### 能源基线模型
- 双基线模式（当前+历史）
- 自动提取特征范围
- 与TDengine无缝集成
- 支持工业能源数据分析

### 专业绘图工具
- 10+种专业绘图函数
- 支持统计分析集成
- 高质量输出（150 DPI）
- 批量PDF导出

### 完整文档资源
- Docker容器化指南
- 深度学习学习路径
- 精美Markdown主题

## 👥 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📄 许可证

本项目采用开源许可证，具体信息请查看LICENSE文件。

## 📞 联系方式

如有问题或建议，请通过Issue联系。

---

**最后更新**: 2024年

**版本**: 2.0.0
