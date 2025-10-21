import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
import warnings
from scipy import stats
from scipy.optimize import minimize
from JayttleProcess.SQLProcess.TaosUtils import TDengineUse
# 尝试导入statsmodels，如果没有安装则使用内置实现
try:
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.stattools import adfuller
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    warnings.warn("statsmodels未安装，将使用内置的Holt-Winters和ARIMA实现")

class EnergyPredictModel:
    def __init__(self, df: pd.DataFrame, patch_col: str, model_corpus: list, step_num: int) -> None:
        """
        初始化能耗预测模型
        
        Args:
            df: 输入数据框
            patch_col: 不参与预测的列名
            model_corpus: 预测算法列表，支持 ['SMA', 'WMA', 'EMA', 'Holt-Winters', 'ARIMA']
            step_num: 预测步数
        """
        self.df = df.copy()
        self.patch_col = patch_col
        self.model_corpus = model_corpus
        self.step_num = step_num

        # 获取数值列（除了patch_col）
        self.numeric_cols = self._get_numeric_columns()
        
        # 验证model_corpus
        self._validate_model_corpus()
    
    def _get_numeric_columns(self) -> List[str]:
        """获取所有数值列（除了patch_col）"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if self.patch_col in numeric_cols:
            numeric_cols.remove(self.patch_col)
        return numeric_cols
    
    def _validate_model_corpus(self):
        """验证model_corpus中的方法是否支持"""
        supported_methods = ['SMA', 'WMA', 'EMA', 'Holt-Winters', 'ARIMA']
        for method in self.model_corpus:
            if method not in supported_methods:
                raise ValueError(f"不支持的预测算法: {method}. 支持的方法: {supported_methods}")
                
    def _analyze_data_characteristics(self, series: pd.Series) -> Dict[str, Any]:
        """分析数据特征，用于算法选择"""
        characteristics = {}
        
        # 平稳性检验
        try:
            if STATSMODELS_AVAILABLE:
                adf_result = adfuller(series.dropna())
                characteristics['is_stationary'] = adf_result[1] < 0.05
            else:
                # 简单的平稳性检验：检查均值和方差的稳定性
                mid_point = len(series) // 2
                first_half = series[:mid_point]
                second_half = series[mid_point:]
                
                mean_diff = abs(first_half.mean() - second_half.mean()) / series.std()
                var_ratio = first_half.var() / second_half.var()
                
                characteristics['is_stationary'] = mean_diff < 0.5 and 0.5 < var_ratio < 2.0
        except:
            characteristics['is_stationary'] = True
            
        # 趋势检验
        x = np.arange(len(series))
        slope, _, r_value, p_value, _ = stats.linregress(x, series)
        characteristics['has_trend'] = abs(r_value) > 0.3 and p_value < 0.05
        characteristics['trend_strength'] = abs(r_value)
        
        # 季节性检验（简单的周期性检验）
        if len(series) >= 24:  # 至少需要24个数据点
            autocorr = np.correlate(series - series.mean(), series - series.mean(), mode='full')
            autocorr = autocorr[autocorr.size // 2:]
            autocorr = autocorr / autocorr[0]
            
            # 检查是否存在显著的周期性
            peaks = []
            for i in range(2, min(len(autocorr), 24)):
                if autocorr[i] > 0.3:  # 阈值可调整
                    peaks.append((i, autocorr[i]))
            
            characteristics['has_seasonality'] = len(peaks) > 0
            characteristics['seasonal_period'] = peaks[0][0] if peaks else None
        else:
            characteristics['has_seasonality'] = False
            characteristics['seasonal_period'] = None
            
        return characteristics
    
    def _sma_predict(self, series: pd.Series, window: int = 5, steps: int = 1) -> List[float]:
        """简单移动平均 (SMA) - 适用于平稳数据"""
        if len(series) < window:
            window = len(series)
        
        predictions = []
        extended_series = series.copy()
        
        for _ in range(steps):
            # 使用最近window个值的平均值作为预测
            pred_value = extended_series.tail(window).mean()
            predictions.append(pred_value)
            
            # 将预测值添加到序列中用于下一步预测
            extended_series = pd.concat([extended_series, pd.Series([pred_value])])
        
        return predictions
    
    def _wma_predict(self, series: pd.Series, window: int = 5, steps: int = 1) -> List[float]:
        """加权移动平均 (WMA) - 强调近期数据"""
        if len(series) < window:
            window = len(series)
        
        predictions = []
        extended_series = series.copy()
        
        for _ in range(steps):
            recent_data = extended_series.tail(window)
            # 线性递增权重，最近的数据权重最大
            weights = np.arange(1, len(recent_data) + 1)
            weights = weights / weights.sum()
            
            pred_value = np.sum(recent_data * weights)
            predictions.append(pred_value)
            
            extended_series = pd.concat([extended_series, pd.Series([pred_value])])
        
        return predictions
    
    def _ema_predict(self, series: pd.Series, alpha: float = 0.3, steps: int = 1) -> List[float]:
        """指数移动平均 (EMA) - 适用于大多数时间序列"""
        if len(series) == 0:
            return [0] * steps
        if len(series) == 1:
            return [series.iloc[0]] * steps
        
        # 计算当前EMA值
        ema = series.iloc[0]
        for i in range(1, len(series)):
            ema = alpha * series.iloc[i] + (1 - alpha) * ema
        
        # 对于多步预测，我们需要考虑趋势
        # 计算最近的趋势
        if len(series) >= 3:
            recent_trend = (series.iloc[-1] - series.iloc[-3]) / 2
        else:
            recent_trend = 0
        
        # 生成多步预测，考虑趋势衰减
        predictions = []
        current_ema = ema
        
        for step in range(steps):
            # 趋势随步数衰减
            trend_factor = np.exp(-0.1 * step)  # 指数衰减
            adjusted_trend = recent_trend * trend_factor
            
            # 预测值 = 当前EMA + 调整后的趋势
            pred_value = current_ema + adjusted_trend
            predictions.append(pred_value)
            
            # 更新EMA（假设预测值作为新的观测值）
            current_ema = alpha * pred_value + (1 - alpha) * current_ema
        
        return predictions
    
    def _holt_winters_predict(self, series: pd.Series, steps: int = 1, seasonal_period: int = None) -> List[float]:
        """Holt-Winters三重指数平滑 - 处理趋势和季节性"""
        if len(series) < 4:
            # 数据太少，回退到简单平均
            return [series.mean()] * steps
        
        if STATSMODELS_AVAILABLE and len(series) >= 10:
            try:
                # 使用statsmodels的实现
                if seasonal_period and len(series) >= 2 * seasonal_period:
                    model = ExponentialSmoothing(
                        series, 
                        trend='add', 
                        seasonal='add', 
                        seasonal_periods=seasonal_period
                    ).fit()
                else:
                    model = ExponentialSmoothing(series, trend='add').fit()
                
                forecast = model.forecast(steps)
                return forecast.tolist()
            except:
                pass
        
        # 内置简化的Holt-Winters实现
        return self._simple_holt_winters(series, steps, seasonal_period)
    
    def _simple_holt_winters(self, series: pd.Series, steps: int, seasonal_period: int = None) -> List[float]:
        """简化的Holt-Winters实现"""
        data = series.values
        n = len(data)
        
        if n < 4:
            return [np.mean(data)] * steps
        
        # 初始化参数
        alpha, beta, gamma = 0.3, 0.1, 0.1
        
        # 初始化level和trend
        level = np.mean(data[:4])
        trend = (np.mean(data[2:4]) - np.mean(data[:2])) / 2
        
        # 如果有季节性
        seasonal = None
        if seasonal_period and n >= 2 * seasonal_period:
            seasonal = []
            for i in range(seasonal_period):
                seasonal.append(np.mean([data[j] for j in range(i, n, seasonal_period)]) - level)
        
        # Holt-Winters更新
        for i in range(n):
            if seasonal:
                seasonal_component = seasonal[i % seasonal_period]
                new_level = alpha * (data[i] - seasonal_component) + (1 - alpha) * (level + trend)
            else:
                new_level = alpha * data[i] + (1 - alpha) * (level + trend)
            
            new_trend = beta * (new_level - level) + (1 - beta) * trend
            
            if seasonal:
                seasonal[i % seasonal_period] = gamma * (data[i] - new_level) + (1 - gamma) * seasonal[i % seasonal_period]
            
            level, trend = new_level, new_trend
        
        # 生成预测
        predictions = []
        for i in range(steps):
            if seasonal:
                pred = level + (i + 1) * trend + seasonal[i % seasonal_period]
            else:
                pred = level + (i + 1) * trend
            predictions.append(pred)
        
        return predictions
    
    def _arima_predict(self, series: pd.Series, steps: int = 1, order: Tuple[int, int, int] = (1, 1, 1)) -> List[float]:
        """ARIMA自回归积分滑动平均模型 - 处理复杂时间模式"""
        if len(series) < 5:
            # 数据太少，使用简单的线性趋势预测
            if len(series) >= 2:
                trend = (series.iloc[-1] - series.iloc[0]) / (len(series) - 1)
                return [series.iloc[-1] + trend * (i + 1) for i in range(steps)]
            else:
                return [series.mean()] * steps
        
        if STATSMODELS_AVAILABLE:
            try:
                # 使用statsmodels的ARIMA实现
                model = ARIMA(series, order=order).fit()
                forecast = model.forecast(steps)
                return forecast.tolist()
            except:
                pass
        
        # 内置简化的ARIMA实现 - 使用改进的AR模型
        return self._improved_ar_predict(series, steps)
    
    def _simple_ar_predict(self, series: pd.Series, steps: int) -> List[float]:
        """简化的AR(1)模型实现"""
        data = series.values
        n = len(data)
        
        if n < 3:
            return [np.mean(data)] * steps
        
        # 估计AR(1)参数：y_t = c + phi * y_{t-1} + epsilon_t
        y = data[1:]
        y_lag = data[:-1]
        
        # 使用最小二乘估计参数
        X = np.column_stack([np.ones(len(y_lag)), y_lag])  # 添加常数项
        try:
            # 求解 [c, phi] = (X'X)^(-1)X'y
            params = np.linalg.lstsq(X, y, rcond=None)[0]
            c, phi = params[0], params[1]
        except:
            # 如果矩阵求解失败，使用简单方法
            phi = np.corrcoef(y, y_lag)[0, 1] * 0.8  # 使用相关系数的80%作为phi
            c = np.mean(y) * (1 - phi)
        
        # 限制phi在稳定区间内
        phi = max(-0.99, min(0.99, phi))
        
        # 计算最近几个观测值的变化趋势
        if n >= 3:
            recent_changes = []
            for i in range(max(1, n-5), n):
                if i > 0:
                    recent_changes.append(data[i] - data[i-1])
            avg_change = np.mean(recent_changes) if recent_changes else 0
        else:
            avg_change = 0
        
        # 生成预测
        predictions = []
        last_value = data[-1]
        
        for step in range(steps):
            # AR(1)基础预测：y_t = c + phi * y_{t-1}
            base_pred = c + phi * last_value
            
            # 添加趋势衰减项
            # 趋势影响随着预测步数增加而衰减
            trend_factor = np.exp(-0.2 * step)  # 指数衰减
            trend_adjustment = avg_change * trend_factor
            
            # 最终预测值
            pred = base_pred + trend_adjustment
            
            predictions.append(pred)
            last_value = pred
        
        return predictions
    
    def _improved_ar_predict(self, series: pd.Series, steps: int) -> List[float]:
        """改进的AR预测实现，确保产生不同的预测值"""
        data = series.values
        n = len(data)
        
        if n < 3:
            return [np.mean(data)] * steps
        
        # 使用更复杂的AR模型 - AR(2)或AR(1)
        if n >= 5:
            # AR(2)模型: y_t = c + phi1 * y_{t-1} + phi2 * y_{t-2} + epsilon_t
            y = data[2:]
            y_lag1 = data[1:-1]
            y_lag2 = data[:-2]
            
            X = np.column_stack([np.ones(len(y)), y_lag1, y_lag2])
            try:
                params = np.linalg.lstsq(X, y, rcond=None)[0]
                c, phi1, phi2 = params[0], params[1], params[2]
                
                # 确保模型稳定性
                if abs(phi1 + phi2) >= 1 or abs(phi2) >= 1:
                    phi1 = max(-0.8, min(0.8, phi1))
                    phi2 = max(-0.3, min(0.3, phi2))
                    
            except:
                # 回退到AR(1)
                return self._simple_ar_predict(series, steps)
            
            # AR(2)预测
            predictions = []
            last_val1 = data[-1]
            last_val2 = data[-2] if n > 1 else data[-1]
            
            for step in range(steps):
                pred = c + phi1 * last_val1 + phi2 * last_val2
                predictions.append(pred)
                
                # 更新滞后值
                last_val2 = last_val1
                last_val1 = pred
                
            return predictions
        
        else:
            # 对于数据较少的情况，使用改进的AR(1)
            return self._simple_ar_predict(series, steps)
    
    def _apply_prediction_algorithm(self, series: pd.Series, method: str, steps: int = 1, window: int = 5) -> List[float]:
        """应用指定的预测算法"""
        # 分析数据特征
        characteristics = self._analyze_data_characteristics(series)
        
        if method == 'SMA':
            return self._sma_predict(series, window, steps)
        elif method == 'WMA':
            return self._wma_predict(series, window, steps)
        elif method == 'EMA':
            return self._ema_predict(series, steps=steps)
        elif method == 'Holt-Winters':
            seasonal_period = characteristics.get('seasonal_period')
            return self._holt_winters_predict(series, steps, seasonal_period)
        elif method == 'ARIMA':
            return self._arima_predict(series, steps)
        else:
            raise ValueError(f"未知的预测算法: {method}")
    
    def _recommend_algorithm(self, series: pd.Series) -> str:
        """基于数据特征推荐最适合的算法"""
        characteristics = self._analyze_data_characteristics(series)
        
        # 根据数据特征推荐算法
        if characteristics.get('has_seasonality', False) and characteristics.get('has_trend', False):
            return 'Holt-Winters'  # 有趋势和季节性
        elif characteristics.get('has_trend', False):
            return 'EMA'  # 有趋势但无明显季节性
        elif not characteristics.get('is_stationary', True):
            return 'ARIMA'  # 非平稳数据
        elif characteristics.get('trend_strength', 0) > 0.5:
            return 'WMA'  # 强调近期数据
        else:
            return 'SMA'  # 平稳数据，简单应用
    
    def get_algorithm_info(self) -> Dict[str, Dict[str, str]]:
        """获取算法信息表"""
        return {
            'SMA': {
                'name': '简单移动平均',
                '适用场景': '平稳数据，简单应用',
                '复杂度': '低',
                '准确性': '高'
            },
            'WMA': {
                'name': '加权移动平均',
                '适用场景': '需要强调近期数据',
                '复杂度': '低',
                '准确性': '高'
            },
            'EMA': {
                'name': '指数移动平均',
                '适用场景': '大多数时间序列',
                '复杂度': '中',
                '准确性': '高'
            },
            'Holt-Winters': {
                'name': 'Holt-Winters三重指数平滑',
                '适用场景': '有趋势和季节性',
                '复杂度': '中',
                '准确性': '中'
            },
            'ARIMA': {
                'name': '自回归积分滑动平均模型',
                '适用场景': '复杂时间模式',
                '复杂度': '高',
                '准确性': '低'
            }
        }
    
    def predict_next_step(self, window: int = 5) -> Dict[str, Any]:
        """
        预测下一步的值
        
        Args:
            window: 滑动窗口大小
            
        Returns:
            Dict[str, Any]: 每列的预测值和算法信息
        """
        predictions = {}
        
        for col in self.numeric_cols:
            col_predictions = []
            algorithm_results = {}
            
            # 对每种预测算法进行预测
            for method in self.model_corpus:
                try:
                    pred_values = self._apply_prediction_algorithm(self.df[col], method, steps=1, window=window)
                    pred_value = pred_values[0] if pred_values else self.df[col].mean()
                    col_predictions.append(pred_value)
                    algorithm_results[method] = pred_value
                except Exception as e:
                    # 如果算法失败，使用均值作为备选
                    fallback_value = self.df[col].mean()
                    col_predictions.append(fallback_value)
                    algorithm_results[method] = fallback_value
                    print(f"算法 {method} 对列 {col} 预测失败，使用均值: {e}")
            
            # 计算所有方法的平均值作为最终预测
            final_prediction = np.mean(col_predictions)
            
            # 推荐最佳算法
            recommended_algorithm = self._recommend_algorithm(self.df[col])
            
            predictions[col] = {
                'final_prediction': final_prediction,
                'algorithm_results': algorithm_results,
                'recommended_algorithm': recommended_algorithm,
                'data_characteristics': self._analyze_data_characteristics(self.df[col])
            }
        
        return predictions
    
    def predict_multi_steps(self, window: int = 5) -> Dict[str, Any]:
        """
        进行多步预测
        
        Args:
            window: 滑动窗口大小
            
        Returns:
            Dict[str, Any]: 包含预测结果、算法性能等信息
        """
        results = {
            'predictions': [],
            'algorithm_performance': {},
            'recommended_algorithms': {},
            'data_analysis': {}
        }
        
        # 对每列进行多步预测
        for col in self.numeric_cols:
            col_results = {}
            algorithm_predictions = {}
            
            # 分析数据特征
            characteristics = self._analyze_data_characteristics(self.df[col])
            results['data_analysis'][col] = characteristics
            
            # 推荐算法
            recommended_algo = self._recommend_algorithm(self.df[col])
            results['recommended_algorithms'][col] = recommended_algo
            
            # 对每种算法进行多步预测
            for method in self.model_corpus:
                try:
                    pred_values = self._apply_prediction_algorithm(
                        self.df[col], method, steps=self.step_num, window=window
                    )
                    algorithm_predictions[method] = pred_values
                except Exception as e:
                    # 失败时使用简单预测
                    fallback_values = [self.df[col].mean()] * self.step_num
                    algorithm_predictions[method] = fallback_values
                    print(f"算法 {method} 对列 {col} 多步预测失败: {e}")
            
            col_results['algorithm_predictions'] = algorithm_predictions
            
            # 计算集成预测（所有算法的平均）
            ensemble_predictions = []
            for step in range(self.step_num):
                step_predictions = [algorithm_predictions[method][step] 
                                 for method in self.model_corpus 
                                 if step < len(algorithm_predictions[method])]
                ensemble_predictions.append(np.mean(step_predictions))
            
            col_results['ensemble_predictions'] = ensemble_predictions
            results['algorithm_performance'][col] = col_results
        
        # 构建预测数据框
        predictions_df_data = []
        for step in range(self.step_num):
            step_data = {'step': step + 1}
            
            for col in self.numeric_cols:
                # 集成预测
                step_data[f'{col}_ensemble'] = results['algorithm_performance'][col]['ensemble_predictions'][step]
                
                # 各算法预测
                for method in self.model_corpus:
                    if step < len(results['algorithm_performance'][col]['algorithm_predictions'][method]):
                        step_data[f'{col}_{method}'] = results['algorithm_performance'][col]['algorithm_predictions'][method][step]
                
                # 推荐算法预测
                recommended_method = results['recommended_algorithms'][col]
                if recommended_method in self.model_corpus:
                    if step < len(results['algorithm_performance'][col]['algorithm_predictions'][recommended_method]):
                        step_data[f'{col}_recommended'] = results['algorithm_performance'][col]['algorithm_predictions'][recommended_method][step]
            
            predictions_df_data.append(step_data)
        
        results['predictions'] = pd.DataFrame(predictions_df_data)
        return results
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        info = {
            'numeric_columns': self.numeric_cols,
            'patch_column': self.patch_col,
            'model_methods': self.model_corpus,
            'prediction_steps': self.step_num,
            'data_shape': self.df.shape,
            'algorithm_info': self.get_algorithm_info(),
            'data_analysis': {}
        }
        
        # 为每列添加数据分析
        for col in self.numeric_cols:
            info['data_analysis'][col] = self._analyze_data_characteristics(self.df[col])
            info['data_analysis'][col]['recommended_algorithm'] = self._recommend_algorithm(self.df[col])
        
        return info
    
    def evaluate_algorithms(self, test_ratio: float = 0.2) -> Dict[str, Any]:
        """评估不同算法的性能"""
        if len(self.df) < 10:
            return {"error": "数据量太少，无法进行算法评估"}
        
        # 分割数据
        split_point = int(len(self.df) * (1 - test_ratio))
        train_data = self.df.iloc[:split_point].copy()
        test_data = self.df.iloc[split_point:].copy()
        
        evaluation_results = {}
        
        for col in self.numeric_cols:
            col_results = {}
            train_series = train_data[col]
            test_series = test_data[col]
            
            for method in self.model_corpus:
                try:
                    # 创建临时模型用于训练
                    temp_model = EnergyPredictModel(
                        train_data, self.patch_col, [method], len(test_data)
                    )
                    
                    # 进行预测
                    predictions = temp_model._apply_prediction_algorithm(
                        train_series, method, steps=len(test_data)
                    )
                    
                    # 计算误差指标
                    if len(predictions) == len(test_series):
                        mse = np.mean((np.array(predictions) - test_series.values) ** 2)
                        mae = np.mean(np.abs(np.array(predictions) - test_series.values))
                        mape = np.mean(np.abs((test_series.values - np.array(predictions)) / test_series.values)) * 100
                        
                        col_results[method] = {
                            'MSE': mse,
                            'MAE': mae,
                            'MAPE': mape,
                            'predictions': predictions[:5],  # 只保存前5个预测值
                            'actual': test_series.values[:5].tolist()
                        }
                    else:
                        col_results[method] = {"error": "预测长度不匹配"}
                        
                except Exception as e:
                    col_results[method] = {"error": str(e)}
            
            evaluation_results[col] = col_results
        
        return evaluation_results
    
def run_EPModel(TDdb_use: TDengineUse, device_name: str, module: str):
    sql_script = f"""
    SELECT *
    FROM (
        SELECT 
            recipename,
            device_name,
            CASE 
                WHEN SUBSTR(module_task, -2, 2) = '01' THEN CONCAT(module, 'A') 
                ELSE CONCAT(module, 'B') 
            END AS module,
            total_steam,
            total_tob,
            total_energy
        FROM nengyuan_recipe
        WHERE 
            device_name = '{device_name}'
    ) AS subquery
    WHERE module = '{module}'
    """
    data = TDdb_use.execute_sql_and_return_dataframe(sql_script)
    model_corpus = ['SMA', 'WMA', 'EMA', 'Holt-Winters', 'ARIMA']
    patch_col = 'recipename'
    step_num = 1
    predict_data = []
    for device_name in data['device_name'].unique():
        temp = data[data['device_name'] == device_name]
        for module in temp['module'].unique():
            module_data = temp[temp['module'] == module]
            EPModel = EnergyPredictModel(module_data, patch_col, model_corpus, step_num)
            results = EPModel.predict_multi_steps()
            predict_row = {
                'record_time': pd.Timestamp.now().floor('S'),  # 精确到秒
                'device_name': device_name,
                'module': module,
                'total_steam': results['predictions']['total_steam_recommended'][0] if 'total_steam_recommended' in results['predictions'] else None,
                'total_tob': results['predictions']['total_tob_recommended'][0] if 'total_tob_recommended' in results['predictions'] else None,
                'total_energy': results['predictions']['total_energy_recommended'][0] if 'total_energy_recommended' in results['predictions'] else None,
                'is_pushed': False,
            }
            predict_data.append(predict_row)
    if predict_data:
        baseline_df = pd.DataFrame(predict_data)
        TDdb_use.batch_insert_predict_data(baseline_df, device_name)