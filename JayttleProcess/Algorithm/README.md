# Algorithm 算法模块

算法模块提供了机器学习、时序预测、异常检测和基线建模等多种算法实现，专注于工业能源数据分析和预测。

## 📋 模块概览

本模块包含以下4个核心算法文件：

| 文件名 | 代码量 | 主要功能 |
|--------|--------|----------|
| `MachineLearning.py` | 71行 | 基础机器学习算法 |
| `PredictiveModel.py` | 690行 | 能源预测模型 |
| `AnomalyDetectionModel.py` | 850行 | 异常检测模型 |
| `BaselineModel.py` | 312行 | 基线建模 |

---

## 🤖 MachineLearning.py

### 功能说明
提供基础的机器学习算法实现，包括线性分类器和多类支持向量机。

### LinearClassifier 类

**线性分类器，使用梯度下降法训练**

#### 初始化
```python
from JayttleProcess.Algorithm.MachineLearning import LinearClassifier

classifier = LinearClassifier(num_features=10)
```

**参数**：
- `num_features` (int): 特征数量

**属性**：
- `weights` (np.ndarray): 权重向量，初始化为零向量
- `bias` (float): 偏置项，初始化为0.0

#### 方法

##### `predict(X)`
计算预测值
```python
X = np.array([[1, 2, 3, ...], [4, 5, 6, ...]])  # shape: (n_samples, n_features)
predictions = classifier.predict(X)
```

**参数**：
- `X` (np.ndarray): 输入特征，形状为 (n_samples, n_features)

**返回**：
- `np.ndarray`: 预测值，形状为 (n_samples,)

##### `train(X, y, learning_rate, num_epochs)`
使用梯度下降法训练模型
```python
X_train = np.array([[1, 2], [3, 4], [5, 6]])
y_train = np.array([0, 1, 1])

classifier.train(
    X=X_train,
    y=y_train,
    learning_rate=0.1,
    num_epochs=100
)
```

**参数**：
- `X` (np.ndarray): 训练特征
- `y` (np.ndarray): 训练标签
- `learning_rate` (float, 默认0.1): 学习率
- `num_epochs` (int, 默认100): 训练轮数

**训练过程**：
- 逐样本更新权重和偏置
- 使用均方误差作为损失函数

### MulticlassSVM 类

**多类支持向量机，实现hinge损失和L2正则化**

#### 初始化
```python
from JayttleProcess.Algorithm.MachineLearning import MulticlassSVM

svm = MulticlassSVM(
    num_classes=3,
    num_features=10,
    learning_rate=0.01,
    lambda_param=0.01
)
```

**参数**：
- `num_classes` (int): 类别数量
- `num_features` (int): 特征数量
- `learning_rate` (float, 默认0.01): 学习率
- `lambda_param` (float, 默认0.01): L2正则化参数

**属性**：
- `weights` (np.ndarray): 权重矩阵，形状为 (num_classes, num_features)
- `bias` (np.ndarray): 偏置向量，形状为 (num_classes,)

#### 方法

##### `hinge_loss(scores, correct_class_index)`
计算hinge损失
```python
scores = np.array([2.5, 1.0, 3.0])
correct_class = 2
loss = svm.hinge_loss(scores, correct_class)
```

##### `compute_loss(X, y)`
计算总损失（包括正则化项）
```python
loss = svm.compute_loss(X_train, y_train)
print(f"当前损失: {loss}")
```

##### `compute_gradients(X, y)`
计算梯度
```python
dW, db = svm.compute_gradients(X_train, y_train)
```

**返回**：
- `dW` (np.ndarray): 权重梯度
- `db` (np.ndarray): 偏置梯度

##### `train(X, y, num_epochs)`
训练模型
```python
X_train = np.random.randn(100, 10)
y_train = np.random.randint(0, 3, 100)

svm.train(X_train, y_train, num_epochs=100)
```

**输出示例**：
```
Epoch 1/100, Loss: 2.5432
Epoch 2/100, Loss: 2.3156
...
```

##### `predict(X)`
预测类别
```python
predictions = svm.predict(X_test)
```

**返回**：
- `np.ndarray`: 预测的类别标签

### 使用示例

**完整示例：线性分类器**
```python
import numpy as np
from JayttleProcess.Algorithm.MachineLearning import LinearClassifier

# 准备数据
X_train = np.array([[1, 2], [2, 3], [3, 4], [4, 5]])
y_train = np.array([0, 0, 1, 1])

# 创建分类器
clf = LinearClassifier(num_features=2)

# 训练
clf.train(X_train, y_train, learning_rate=0.1, num_epochs=1000)

# 预测
X_test = np.array([[2.5, 3.5], [3.5, 4.5]])
predictions = clf.predict(X_test)
print(f"预测结果: {predictions}")
```

**完整示例：多类SVM**
```python
import numpy as np
from JayttleProcess.Algorithm.MachineLearning import MulticlassSVM

# 准备数据（3类问题）
X_train = np.random.randn(300, 10)
y_train = np.random.randint(0, 3, 300)

# 创建SVM
svm = MulticlassSVM(num_classes=3, num_features=10)

# 训练
svm.train(X_train, y_train, num_epochs=100)

# 预测
X_test = np.random.randn(50, 10)
predictions = svm.predict(X_test)
print(f"预测类别: {predictions}")
```

---

## 📈 PredictiveModel.py

### 功能说明
提供能源预测模型，支持多种时序预测算法，专门用于工业能源消耗预测。

### EnergyPredictModel 类

**能源预测模型，支持5种时序预测算法**

#### 初始化
```python
from JayttleProcess.Algorithm.PredictiveModel import EnergyPredictModel
import pandas as pd

df = pd.DataFrame({
    'recipename': ['batch1', 'batch2', 'batch3'],
    'total_steam': [100, 110, 105],
    'total_energy': [50, 55, 52]
})

model = EnergyPredictModel(
    df=df,
    patch_col='recipename',
    model_corpus=['SMA', 'WMA', 'EMA', 'Holt-Winters', 'ARIMA'],
    step_num=3
)
```

**参数**：
- `df` (pd.DataFrame): 输入数据框
- `patch_col` (str): 不参与预测的列名（如批次号）
- `model_corpus` (list): 预测算法列表
  - `'SMA'`: 简单移动平均
  - `'WMA'`: 加权移动平均
  - `'EMA'`: 指数移动平均
  - `'Holt-Winters'`: 三重指数平滑
  - `'ARIMA'`: 自回归综合移动平均
- `step_num` (int): 预测步数

#### 支持的预测算法

##### 1. SMA (Simple Moving Average)
**简单移动平均 - 适用于平稳数据**

```python
predictions = model._sma_predict(series, window=5, steps=3)
```

**特点**：
- 计算最近window个值的平均值
- 适合无趋势、无季节性的数据
- 计算简单，速度快

##### 2. WMA (Weighted Moving Average)
**加权移动平均 - 强调近期数据**

```python
predictions = model._wma_predict(series, window=5, steps=3)
```

**特点**：
- 线性递增权重，最近数据权重最大
- 对近期变化更敏感
- 适合有轻微趋势的数据

##### 3. EMA (Exponential Moving Average)
**指数移动平均 - 适用于大多数时间序列**

```python
predictions = model._ema_predict(series, alpha=0.3, steps=3)
```

**特点**：
- 指数衰减权重
- 考虑趋势因子
- 多步预测时趋势逐渐衰减
- 适应性强

**参数**：
- `alpha` (float): 平滑系数，范围[0,1]，越大对近期数据越敏感

##### 4. Holt-Winters
**三重指数平滑 - 处理趋势和季节性**

```python
predictions = model._holt_winters_predict(series, steps=3, seasonal_period=12)
```

**特点**：
- 同时处理水平、趋势和季节性
- 自动检测季节周期
- 适合有明显季节性的数据
- 支持加法和乘法模型

**依赖**：
- 优先使用statsmodels实现
- 无statsmodels时使用内置实现

##### 5. ARIMA
**自回归综合移动平均 - 复杂时序数据**

```python
predictions = model._arima_predict(series, steps=3, order=(1, 1, 1))
```

**特点**：
- 自动参数选择（使用AIC准则）
- 支持差分消除趋势
- 适合非平稳数据
- 预测精度高但计算较慢

**参数自动选择范围**：
- p: [0, 3] - 自回归阶数
- d: [0, 2] - 差分阶数
- q: [0, 3] - 移动平均阶数

#### 核心方法

##### `_analyze_data_characteristics(series)`
分析数据特征
```python
characteristics = model._analyze_data_characteristics(series)
print(characteristics)
```

**返回特征**：
```python
{
    'is_stationary': True/False,      # 是否平稳
    'has_trend': True/False,          # 是否有趋势
    'trend_strength': 0.75,           # 趋势强度 [0,1]
    'has_seasonality': True/False,    # 是否有季节性
    'seasonal_period': 12             # 季节周期（如有）
}
```

**检验方法**：
- 平稳性：ADF检验或均值/方差稳定性检验
- 趋势：线性回归斜率和R²
- 季节性：自相关函数峰值检测

##### `predict_all_columns()`
对所有数值列进行预测
```python
result_df = model.predict_all_columns()
```

**返回**：
- `pd.DataFrame`: 包含所有预测结果的数据框

**输出格式**：
```
列名_算法名_预测步数
例如：total_steam_SMA_1, total_steam_SMA_2, total_steam_EMA_1, ...
```

##### `get_predictions_dataframe()`
获取预测结果数据框
```python
predictions = model.get_predictions_dataframe()
```

##### `save_predictions_to_tdengine(device_name, td_config_path)`
保存预测结果到TDengine数据库
```python
model.save_predictions_to_tdengine(
    device_name='A_HT',
    td_config_path='config.json'
)
```

**功能**：
- 自动连接TDengine
- 批量插入预测数据
- 包含设备名、模块、时间戳等信息

##### `calculate_metrics(actual, predicted, metric_name)`
计算预测指标
```python
metrics = model.calculate_metrics(
    actual=actual_values,
    predicted=pred_values,
    metric_name='RMSE'
)
```

**支持的指标**：
- `'MAE'`: 平均绝对误差
- `'RMSE'`: 均方根误差
- `'MAPE'`: 平均绝对百分比误差
- `'R2'`: R²决定系数

### 使用示例

**示例1：基础预测**
```python
import pandas as pd
from JayttleProcess.Algorithm.PredictiveModel import EnergyPredictModel

# 准备数据
df = pd.DataFrame({
    'batch': ['b1', 'b2', 'b3', 'b4', 'b5'],
    'steam': [100, 105, 110, 108, 112],
    'energy': [50, 52, 55, 53, 56]
})

# 创建模型（使用多种算法）
model = EnergyPredictModel(
    df=df,
    patch_col='batch',
    model_corpus=['SMA', 'EMA', 'Holt-Winters'],
    step_num=3
)

# 执行预测
result = model.predict_all_columns()
print(result)
```

**示例2：单一算法详细使用**
```python
import pandas as pd
import numpy as np

# 准备时间序列数据
series = pd.Series([100, 105, 110, 108, 112, 115, 118])

# 创建模型
model = EnergyPredictModel(
    df=pd.DataFrame({'batch': range(len(series)), 'value': series}),
    patch_col='batch',
    model_corpus=['ARIMA'],
    step_num=5
)

# ARIMA预测
predictions = model._arima_predict(series, steps=5)
print(f"未来5步预测: {predictions}")
```

**示例3：数据特征分析**
```python
# 分析数据特征
characteristics = model._analyze_data_characteristics(series)

print(f"数据是否平稳: {characteristics['is_stationary']}")
print(f"是否有趋势: {characteristics['has_trend']}")
print(f"趋势强度: {characteristics['trend_strength']:.2f}")
print(f"是否有季节性: {characteristics['has_seasonality']}")
if characteristics['seasonal_period']:
    print(f"季节周期: {characteristics['seasonal_period']}")
```

**示例4：保存到TDengine**
```python
# 执行预测
result = model.predict_all_columns()

# 保存到数据库
model.save_predictions_to_tdengine(
    device_name='Device_A',
    td_config_path='tdengine_config.json'
)
print("预测结果已保存到TDengine")
```

**示例5：算法比较**
```python
# 使用所有算法进行预测
model = EnergyPredictModel(
    df=df,
    patch_col='batch',
    model_corpus=['SMA', 'WMA', 'EMA', 'Holt-Winters', 'ARIMA'],
    step_num=3
)

result = model.predict_all_columns()

# 比较不同算法的预测结果
for col in model.numeric_cols:
    print(f"\n特征: {col}")
    for algo in model.model_corpus:
        pred_col = f"{col}_{algo}_1"  # 第1步预测
        if pred_col in result.columns:
            print(f"  {algo}: {result[pred_col].iloc[0]:.2f}")
```

---

## 🔍 AnomalyDetectionModel.py

### 功能说明
高度封装的无监督异常检测类，支持6种主流异常检测算法，专门用于工业数据异常检测。

### AnomalyDetectionModel 类

**多算法无监督异常检测模型**

#### 初始化
```python
from JayttleProcess.Algorithm.AnomalyDetectionModel import AnomalyDetectionModel
import pandas as pd

feature_df = pd.DataFrame({
    'batch_id': ['b1', 'b2', 'b3', 'b4'],
    'temperature': [100, 102, 101, 150],  # b4异常
    'pressure': [50, 51, 49, 45],
    'flow_rate': [10, 11, 10.5, 9]
})

model = AnomalyDetectionModel(
    feature_df=feature_df,
    model_corpus=['isolation_forest', 'lof', 'one_class_svm'],
    patch_col='batch_id',
    seed=42
)
```

**参数**：
- `feature_df` (pd.DataFrame): 特征数据框
- `model_corpus` (list): 使用的算法列表
- `patch_col` (str): 批次标识列（不参与检测）
- `seed` (int, 默认42): 随机种子

**支持的算法**：
- `'isolation_forest'`: 孤立森林
- `'one_class_svm'`: 单类支持向量机
- `'local_outlier_factor'` 或 `'lof'`: 局部异常因子
- `'dbscan'`: 基于密度的聚类
- `'pca_anomaly'`: 基于PCA的异常检测
- `'statistical'`: 统计学方法（IQR/Z-score）

#### 核心方法

##### `preprocess_data(scaler_type, apply_pca, n_components)`
数据预处理
```python
model.preprocess_data(
    scaler_type='Standard',  # 'Standard', 'MinMax', 'Robust'
    apply_pca=False,
    n_components=None
)
```

**参数**：
- `scaler_type` (str): 标准化方法
  - `'Standard'`: 标准化（均值0，方差1）
  - `'MinMax'`: 最小-最大缩放到[0,1]
  - `'Robust'`: 鲁棒缩放（对异常值不敏感）
- `apply_pca` (bool): 是否应用PCA降维
- `n_components` (int): PCA保留的成分数

##### `fit_predict(**kwargs)`
训练并预测所有算法
```python
results = model.fit_predict(
    contamination=0.1,      # 异常比例
    n_estimators=100,       # 孤立森林树数量
    n_neighbors=20          # LOF邻居数
)
```

**返回**：
- `Dict[str, np.ndarray]`: 各算法的预测结果
  - 0: 正常
  - 1: 异常

**常用参数**：

1. **Isolation Forest**:
   - `contamination` (float): 异常比例
   - `n_estimators` (int): 树的数量
   - `max_samples` (int/float): 每棵树的样本数

2. **One-Class SVM**:
   - `nu` (float): 异常比例上界
   - `kernel` (str): 核函数类型
   - `gamma` (str/float): 核系数

3. **LOF**:
   - `n_neighbors` (int): 邻居数量
   - `contamination` (float): 异常比例

4. **DBSCAN**:
   - `eps` (float): 邻域半径
   - `min_samples` (int): 最小样本数

5. **PCA Anomaly**:
   - `n_components` (int): 主成分数量
   - `contamination` (float): 异常比例

6. **Statistical**:
   - `method` (str): 'iqr' 或 'zscore'
   - `contamination` (float): 异常比例
   - `threshold_factor` (float): 阈值因子

##### `get_outlier_scores()`
获取异常分数
```python
scores = model.get_outlier_scores()
# scores: {algorithm_name: array of scores [0,1]}
```

**返回**：
- `Dict[str, np.ndarray]`: 各算法的异常分数
  - 分数范围[0, 1]
  - 分数越高越异常

##### `get_range_df()`
获取特征范围统计
```python
range_df = model.get_range_df()
```

**返回字段**：
- 每个特征的：最小值、25%分位、中位数、75%分位、最大值
- 基于正常样本计算

##### `plot_anomaly_scores(save_path)`
可视化异常分数
```python
model.plot_anomaly_scores(save_path='anomaly_scores.png')
```

##### `plot_feature_distributions(save_path)`
绘制特征分布图
```python
model.plot_feature_distributions(save_path='distributions.png')
```

##### `save_model(file_path)`
保存模型
```python
model.save_model('anomaly_model.pkl')
```

##### `load_model(file_path)`
加载模型（静态方法）
```python
model = AnomalyDetectionModel.load_model('anomaly_model.pkl')
```

#### 各算法详解

##### 1. Isolation Forest（孤立森林）
**原理**：通过随机森林隔离异常点

**优点**：
- 速度快，适合大数据
- 无需假设数据分布
- 对高维数据效果好

**适用场景**：
- 大规模数据集
- 异常点分散且明显

**推荐参数**：
```python
contamination=0.1,    # 预期异常比例
n_estimators=100,     # 树的数量
max_samples=256       # 每棵树的样本数
```

##### 2. One-Class SVM（单类支持向量机）
**原理**：学习正常样本的边界

**优点**：
- 理论基础扎实
- 可处理非线性边界
- 适合低维数据

**适用场景**：
- 正常数据分布紧密
- 特征数量较少(<20)

**推荐参数**：
```python
nu=0.1,              # 异常比例上界
kernel='rbf',        # 径向基核
gamma='scale'        # 自动计算gamma
```

##### 3. Local Outlier Factor（局部异常因子）
**原理**：基于局部密度的异常检测

**优点**：
- 可检测局部异常
- 对不同密度区域敏感
- 无需全局阈值

**适用场景**：
- 数据密度不均匀
- 局部异常检测

**推荐参数**：
```python
n_neighbors=20,      # 邻居数量
contamination=0.1    # 异常比例
```

##### 4. DBSCAN（基于密度的聚类）
**原理**：将低密度区域标记为异常

**优点**：
- 无需指定异常比例
- 可发现任意形状的簇
- 对噪声鲁棒

**适用场景**：
- 簇形状不规则
- 存在噪声数据

**推荐参数**：
```python
eps=0.5,            # 邻域半径
min_samples=5       # 最小样本数
```

##### 5. PCA Anomaly（基于PCA）
**原理**：检测重构误差大的样本

**优点**：
- 可降维
- 计算快速
- 可解释性强

**适用场景**：
- 高维数据
- 特征相关性强

**推荐参数**：
```python
n_components=5,      # 主成分数量
contamination=0.1    # 异常比例
```

##### 6. Statistical（统计方法）
**原理**：基于IQR或Z-score

**优点**：
- 简单直观
- 计算极快
- 易于理解

**适用场景**：
- 数据近似正态分布
- 单变量异常检测

**推荐参数**：
```python
method='iqr',           # 'iqr' 或 'zscore'
threshold_factor=1.5    # IQR倍数
```

### 使用示例

**示例1：基础异常检测**
```python
import pandas as pd
from JayttleProcess.Algorithm.AnomalyDetectionModel import AnomalyDetectionModel

# 准备数据
df = pd.DataFrame({
    'batch': ['b1', 'b2', 'b3', 'b4', 'b5'],
    'temp': [100, 102, 101, 150, 103],      # b4异常
    'pressure': [50, 51, 49, 45, 50],
    'flow': [10, 11, 10.5, 9, 10.2]
})

# 创建模型
model = AnomalyDetectionModel(
    feature_df=df,
    model_corpus=['isolation_forest', 'lof'],
    patch_col='batch'
)

# 预处理
model.preprocess_data(scaler_type='Standard')

# 检测
results = model.fit_predict(contamination=0.2)

# 查看结果
print("检测结果:")
for algo, preds in results.items():
    print(f"{algo}: {preds}")
    print(f"  异常数量: {sum(preds)}")
```

**示例2：多算法对比**
```python
# 使用所有算法
model = AnomalyDetectionModel(
    feature_df=df,
    model_corpus=[
        'isolation_forest',
        'one_class_svm',
        'lof',
        'dbscan',
        'pca_anomaly',
        'statistical'
    ],
    patch_col='batch'
)

model.preprocess_data()
results = model.fit_predict()

# 统计各样本被标记为异常的次数
anomaly_votes = sum(results.values())
print("异常投票数:")
print(anomaly_votes)

# 找出所有算法都认为异常的样本
unanimous_anomalies = anomaly_votes == len(model.model_corpus)
print(f"\n所有算法一致认为异常的样本: {sum(unanimous_anomalies)}")
```

**示例3：异常分数分析**
```python
# 执行检测
model.fit_predict()

# 获取异常分数
scores = model.get_outlier_scores()

# 分析每个算法的分数
for algo, score_array in scores.items():
    print(f"\n{algo}:")
    print(f"  平均分数: {score_array.mean():.3f}")
    print(f"  最大分数: {score_array.max():.3f}")
    print(f"  最小分数: {score_array.min():.3f}")
    
    # 找出异常分数最高的样本
    top_anomaly_idx = score_array.argmax()
    print(f"  最异常样本索引: {top_anomaly_idx}")
    print(f"  其特征值: {df.iloc[top_anomaly_idx].to_dict()}")
```

**示例4：可视化**
```python
# 执行检测
model.fit_predict()

# 绘制异常分数图
model.plot_anomaly_scores(save_path='scores.png')

# 绘制特征分布图
model.plot_feature_distributions(save_path='distributions.png')

print("可视化图表已保存")
```

**示例5：模型保存与加载**
```python
# 训练模型
model.preprocess_data()
model.fit_predict()

# 保存模型
model.save_model('my_anomaly_model.pkl')

# 加载模型
loaded_model = AnomalyDetectionModel.load_model('my_anomaly_model.pkl')

# 使用加载的模型预测新数据
new_data = pd.DataFrame({
    'batch': ['new1'],
    'temp': [105],
    'pressure': [52],
    'flow': [10.8]
})
# 注意：需要使用相同的预处理步骤
```

---

## 📊 BaselineModel.py

### 功能说明
能源基线建模，用于建立工业能源消耗的正常基线范围，支持当前基线和历史基线的加权融合。

### BaselineModel 类

**双基线能源模型（当前+历史）**

#### 初始化
```python
from JayttleProcess.Algorithm.BaselineModel import BaselineModel
import pandas as pd

# 准备当前数据（近期1个月）
current_df = pd.DataFrame({
    'recipename': ['b1', 'b2', 'b3'],
    'total_steam': [100, 105, 102],
    'total_energy': [50, 52, 51],
    'temperature': [80, 82, 81]
})

# 准备历史数据（过去3个月）
history_df = pd.DataFrame({
    'recipename': ['h1', 'h2', 'h3', 'h4', 'h5'],
    'total_steam': [98, 103, 101, 104, 100],
    'total_energy': [49, 51, 50, 52, 50],
    'temperature': [79, 81, 80, 82, 80]
})

model = BaselineModel(
    current_df=current_df,
    history_df=history_df,
    model_corpus=['isolation_forest', 'lof'],
    feature_cols=['total_steam', 'total_energy', 'temperature'],
    patch_col='recipename',
    feature_weights=None,
    baseline_weights=(0.7, 0.3),  # 当前70%，历史30%
    seed=42
)
```

**参数**：
- `current_df` (pd.DataFrame): 当前数据（近期）
- `history_df` (pd.DataFrame): 历史数据
- `model_corpus` (list): 异常检测算法列表
- `feature_cols` (list): 参与建模的特征列
- `patch_col` (str): 批次标识列
- `feature_weights` (dict, 可选): 特征权重字典
- `baseline_weights` (tuple): (当前权重, 历史权重)，默认(0.5, 0.5)
- `seed` (int): 随机种子

#### 核心方法

##### `exec_ADModel(df, feature_data)`
执行异常检测模型
```python
result, normal_samples, anomaly_samples = model.exec_ADModel(df, feature_data)
```

**返回**：
- `result` (pd.DataFrame): 完整结果（原始数据+检测结果）
- `normal_samples` (pd.DataFrame): 所有算法都认为正常的样本
- `anomaly_samples` (pd.DataFrame): 所有算法都认为异常的样本

**处理流程**：
1. 创建AnomalyDetectionModel实例
2. 数据预处理
3. 执行异常检测
4. 筛选全正常和全异常样本

##### `process_nengyuan_baseline(device_name, module)`
生成能源基线数据
```python
baseline_df = model.process_nengyuan_baseline(
    device_name='Device_A',
    module='Module_1'
)
```

**返回**：
- `pd.DataFrame`: 包含3行基线数据
  - 第1行：当前基线（baseline_mode='current'）
  - 第2行：历史基线（baseline_mode='history'）
  - 第3行：融合基线（baseline_mode='merged'）

**基线字段**：
```python
{
    'record_time': 记录时间,
    'device_name': 设备名称,
    'module': 模块名称,
    
    # 每个特征的上下限
    'total_steam_lower': 蒸汽下限,
    'total_steam_upper': 蒸汽上限,
    'duration_lower': 持续时间下限,
    'duration_upper': 持续时间上限,
    'temperature_lower': 温度下限,
    'temperature_upper': 温度上限,
    'humidity_lower': 湿度下限,
    'humidity_upper': 湿度上限,
    # ... 其他特征
    
    'baseline_mode': 'current'/'history'/'merged',
    'is_pushed': False
}
```

**基线计算方法**：
1. **当前/历史基线**：使用正常样本的最小值和最大值
2. **融合基线**：按权重计算加权平均
   ```
   merged_lower = w_current * current_lower + w_history * history_lower
   merged_upper = w_current * current_upper + w_history * history_upper
   ```

##### `save_to_tdengine(baseline_df, device_name, td_config_path)`
保存基线到TDengine数据库
```python
success = model.save_to_tdengine(
    baseline_df=baseline_df,
    device_name='Device_A',
    td_config_path='tdengine_config.json'
)
```

### 使用示例

**示例1：基础基线建模**
```python
import pandas as pd
from JayttleProcess.Algorithm.BaselineModel import BaselineModel

# 准备数据
current_df = pd.DataFrame({
    'batch': ['c1', 'c2', 'c3', 'c4', 'c5'],
    'steam': [100, 102, 101, 103, 101],
    'energy': [50, 51, 50, 52, 50],
    'temp': [80, 81, 80, 82, 80]
})

history_df = pd.DataFrame({
    'batch': ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8'],
    'steam': [98, 100, 99, 101, 100, 99, 102, 100],
    'energy': [49, 50, 49, 51, 50, 49, 51, 50],
    'temp': [79, 80, 79, 81, 80, 79, 81, 80]
})

# 创建模型（当前数据权重更高）
model = BaselineModel(
    current_df=current_df,
    history_df=history_df,
    model_corpus=['isolation_forest', 'lof', 'one_class_svm'],
    feature_cols=['steam', 'energy', 'temp'],
    patch_col='batch',
    baseline_weights=(0.7, 0.3)  # 当前70%，历史30%
)

# 生成基线
baseline_df = model.process_nengyuan_baseline(
    device_name='Boiler_A',
    module='Production_Line_1'
)

# 查看基线
print(baseline_df)
```

**示例2：分析正常与异常样本**
```python
# 执行异常检测
current_result, current_normal, current_anomaly = model.exec_ADModel(
    current_df, 
    current_df[model.feature_cols]
)

print("当前数据分析:")
print(f"总样本数: {len(current_result)}")
print(f"正常样本数: {len(current_normal)}")
print(f"异常样本数: {len(current_anomaly)}")

print("\n正常样本统计:")
print(current_normal[model.feature_cols].describe())

print("\n异常样本:")
print(current_anomaly)
```

**示例3：特征权重配置**
```python
# 为重要特征设置更高权重
model = BaselineModel(
    current_df=current_df,
    history_df=history_df,
    model_corpus=['isolation_forest'],
    feature_cols=['steam', 'energy', 'temp'],
    patch_col='batch',
    feature_weights={
        'steam': 2.0,      # 蒸汽最重要
        'energy': 1.5,     # 能源次之
        'temp': 1.0        # 温度正常权重
    },
    baseline_weights=(0.6, 0.4)
)

baseline_df = model.process_nengyuan_baseline('Device_A', 'Module_1')
```

**示例4：保存到数据库**
```python
# 生成基线
baseline_df = model.process_nengyuan_baseline('Device_A', 'Module_1')

# 保存到TDengine
success = model.save_to_tdengine(
    baseline_df=baseline_df,
    device_name='Device_A',
    td_config_path='config.json'
)

if success:
    print("基线数据已成功保存到TDengine")
else:
    print("保存失败")
```

**示例5：基线对比分析**
```python
# 生成基线
baseline_df = model.process_nengyuan_baseline('Device_A', 'Module_1')

# 提取三种基线
current_baseline = baseline_df[baseline_df['baseline_mode'] == 'current']
history_baseline = baseline_df[baseline_df['baseline_mode'] == 'history']
merged_baseline = baseline_df[baseline_df['baseline_mode'] == 'merged']

# 对比分析
features = ['total_steam', 'total_energy', 'temperature']
for feature in features:
    print(f"\n{feature}:")
    print(f"  当前基线: [{current_baseline[f'{feature}_lower'].values[0]:.2f}, "
          f"{current_baseline[f'{feature}_upper'].values[0]:.2f}]")
    print(f"  历史基线: [{history_baseline[f'{feature}_lower'].values[0]:.2f}, "
          f"{history_baseline[f'{feature}_upper'].values[0]:.2f}]")
    print(f"  融合基线: [{merged_baseline[f'{feature}_lower'].values[0]:.2f}, "
          f"{merged_baseline[f'{feature}_upper'].values[0]:.2f}]")
```

---

## 🔧 依赖安装

### 基础依赖
```bash
pip install numpy pandas
pip install scikit-learn
pip install scipy
pip install matplotlib seaborn
```

### 可选依赖

#### 时序预测（PredictiveModel）
```bash
pip install statsmodels  # ARIMA, Holt-Winters等
```

#### 数据库支持
```bash
pip install taosws  # TDengine数据库
```

#### 模型持久化
```bash
pip install joblib  # 模型保存与加载
```

### 完整安装
```bash
pip install numpy pandas scikit-learn scipy matplotlib seaborn statsmodels taosws joblib
```

---

## 📦 配置文件

### TDengine配置（tdengine_config.json）
```json
{
    "TDengine_config": {
        "host": "localhost",
        "user": "root",
        "password": "taosdata",
        "database": "energy_db",
        "port": 6030
    }
}
```

---

## 🎯 应用场景

### 1. 工业能源预测
使用PredictiveModel预测能源消耗趋势
- 蒸汽消耗预测
- 电能消耗预测
- 多步超前预测

### 2. 设备异常检测
使用AnomalyDetectionModel检测设备异常状态
- 温度异常
- 压力异常
- 振动异常
- 能耗异常

### 3. 生产基线建立
使用BaselineModel建立生产正常范围
- 能耗基线
- 质量指标基线
- 工艺参数基线

### 4. 分类任务
使用MachineLearning进行数据分类
- 设备状态分类
- 产品质量分类
- 故障类型分类

### 5. 在线监控
结合预测和异常检测实现实时监控
- 实时预测下一时刻状态
- 实时检测异常情况
- 自动告警

---

## 💡 最佳实践

### 1. 数据准备
```python
# 确保数据质量
df = df.dropna()  # 删除缺失值
df = df.drop_duplicates()  # 删除重复
df = df[df['value'] > 0]  # 删除异常值
```

### 2. 算法选择

**预测算法选择**：
- 平稳数据 → SMA, WMA
- 有趋势数据 → EMA, Holt-Winters
- 季节性数据 → Holt-Winters
- 复杂数据 → ARIMA

**异常检测算法选择**：
- 大规模数据 → Isolation Forest
- 局部异常 → LOF
- 高维数据 → PCA Anomaly
- 快速检测 → Statistical

### 3. 参数调优
```python
# 预测窗口大小
window_size = min(20, len(data) // 4)

# 异常比例估计
contamination = 0.05  # 5%异常率较为合适

# 基线权重
if recent_data_quality_good:
    weights = (0.7, 0.3)  # 更信任当前数据
else:
    weights = (0.5, 0.5)  # 平衡
```

### 4. 结果验证
```python
# 预测结果验证
mae = calculate_metrics(actual, predicted, 'MAE')
if mae < threshold:
    print("预测效果良好")

# 异常检测验证
anomaly_ratio = sum(predictions) / len(predictions)
if 0.01 < anomaly_ratio < 0.20:
    print("异常比例合理")
```

---

## ⚠️ 注意事项

1. **数据量要求**：
   - 预测模型：至少10个历史数据点
   - 异常检测：至少20个样本
   - 基线建模：至少30个正常样本

2. **算法限制**：
   - ARIMA计算较慢，大数据时考虑其他算法
   - One-Class SVM不适合高维数据
   - DBSCAN需要手动调整eps参数

3. **内存使用**：
   - 孤立森林：O(n * n_estimators)
   - SVM：O(n²) 到 O(n³)
   - PCA：O(n * p²)，p为特征数

4. **异常比例**：
   - contamination参数需要根据实际情况调整
   - 设置过高会将正常样本标记为异常
   - 设置过低会遗漏真实异常

5. **特征选择**：
   - 移除常数特征
   - 处理高相关性特征
   - 特征缩放很重要

---

## 📝 更新日志

- **v1.0.0** (2024-01)
  - 初始版本发布
  - 包含4个核心算法模块
  - 支持机器学习、时序预测、异常检测、基线建模

---

## 👥 贡献

欢迎提交Issue和Pull Request来改进这些算法！

---

**最后更新**: 2024年  
**模块版本**: 1.0.0

