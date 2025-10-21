import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from JayttleProcess.Algorithm.AnomalyDetectionModel import AnomalyDetectionModel

class BaselineModel:
    def __init__(self, current_df: pd.DataFrame, 
                 history_df: pd.DataFrame, 
                 model_corpus: list, 
                 feature_cols: list,
                 patch_col: str,
                 feature_weights: Optional[Dict[str, float]] = None,
                 baseline_weights: tuple = (0.5, 0.5),
                 seed: int = 42):
        self.current_df = current_df.copy()
        self.history_df = history_df.copy()
        self.model_corpus = model_corpus
        self.feature_cols = feature_cols
        self.patch_col = patch_col
        self.feature_weights = AnomalyDetectionModel._process_feature_weights(feature_weights)
        self.baseline_weights = baseline_weights
        self.seed = seed
        self.current_feature = self.current_df[self.feature_cols].copy()
        self.history_feature = self.history_df[self.feature_cols].copy()


    def exec_ADModel(self, df: pd.DataFrame, feature_data: pd.DataFrame) -> tuple:
        """执行异常检测模型并返回结果
        
        Args:
            df: 原始数据框
            feature_data: 特征数据
        
        Returns:
            tuple: (完整结果, 全正常样本, 全异常样本)
        """
        ADModel = AnomalyDetectionModel(
            feature_data.dropna(axis=1, how='all'), 
            self.model_corpus, 
            self.patch_col, 
            self.feature_weights
        )
        ADModel.preprocess_data()
        ADModel.fit_predict()
        
        # 合并原始数据和模型结果
        result = pd.concat([df, pd.DataFrame(ADModel.results)], axis=1)
        # 筛选全正常和全异常样本
        normal_samples = result[(result[self.model_corpus] == 0).all(axis=1)]
        anomaly_samples = result[(result[self.model_corpus] == 1).all(axis=1)]
        return result, normal_samples, anomaly_samples
    def process_nengyuan_baseline(self, device_name: str, module: str):
        # 用于存储所有基线数据的列表
        baseline_data = []
        # 处理当前数据
        current_result, current_normaly, current_anomaly = self.exec_ADModel(
            self.current_df, self.current_feature
        )
         # 当前数据的基线行
        current_baseline_row = {
            'record_time': pd.Timestamp.now().floor('S'),  # 精确到秒
            'device_name': device_name,
            'module': module,
            # 特征上下限值 - 使用 current_normaly
            'total_steam_lower': current_normaly['total_steam'].min() if 'total_steam' in current_normaly else np.nan,
            'total_steam_upper': current_normaly['total_steam'].max() if 'total_steam' in current_normaly else np.nan,
            'duration_lower': current_normaly['duration'].min() if 'duration' in current_normaly else np.nan,
            'duration_upper': current_normaly['duration'].max() if 'duration' in current_normaly else np.nan,
            'temperature_lower': current_normaly['temperature'].min() if 'temperature' in current_normaly else np.nan,
            'temperature_upper': current_normaly['temperature'].max() if 'temperature' in current_normaly else np.nan,
            'humidity_lower': current_normaly['humidity'].min() if 'humidity' in current_normaly else np.nan,
            'humidity_upper': current_normaly['humidity'].max() if 'humidity' in current_normaly else np.nan,
            'steam_mafl_lower': current_normaly['steam_mafl'].min() if 'steam_mafl' in current_normaly else np.nan,
            'steam_mafl_upper': current_normaly['steam_mafl'].max() if 'steam_mafl' in current_normaly else np.nan,
            'steam_flow_lower': current_normaly['steam_flow'].min() if 'steam_flow' in current_normaly else np.nan,
            'steam_flow_upper': current_normaly['steam_flow'].max() if 'steam_flow' in current_normaly else np.nan,
            'steam_press_aft_lower': current_normaly['steam_press_aft'].min() if 'steam_press_aft' in current_normaly else np.nan,
            'steam_press_aft_upper': current_normaly['steam_press_aft'].max() if 'steam_press_aft' in current_normaly else np.nan,
            'steam_press_bef_lower': current_normaly['steam_press_bef'].min() if 'steam_press_bef' in current_normaly else np.nan,
            'steam_press_bef_upper': current_normaly['steam_press_bef'].max() if 'steam_press_bef' in current_normaly else np.nan,
            'proc_air_valve_lower': current_normaly['proc_air_valve'].min() if 'proc_air_valve' in current_normaly else np.nan,
            'proc_air_valve_upper': current_normaly['proc_air_valve'].max() if 'proc_air_valve' in current_normaly else np.nan,
            'proc_air_temp_lower': current_normaly['proc_air_temp'].min() if 'proc_air_temp' in current_normaly else np.nan,
            'proc_air_temp_upper': current_normaly['proc_air_temp'].max() if 'proc_air_temp' in current_normaly else np.nan,
            'cyl_temp_lower': current_normaly['cyl_temp'].min() if 'cyl_temp' in current_normaly else np.nan,
            'cyl_temp_upper': current_normaly['cyl_temp'].max() if 'cyl_temp' in current_normaly else np.nan,
            'tob_mafl_lower': current_normaly['tob_mafl'].min() if 'tob_mafl' in current_normaly else np.nan,
            'tob_mafl_upper': current_normaly['tob_mafl'].max() if 'tob_mafl' in current_normaly else np.nan,
            'total_tob_lower': current_normaly['total_tob'].min() if 'total_tob' in current_normaly else np.nan,
            'total_tob_upper': current_normaly['total_tob'].max() if 'total_tob' in current_normaly else np.nan,
            'total_energy_lower': current_normaly['total_energy'].min() if 'total_energy' in current_normaly else np.nan,
            'total_energy_upper': current_normaly['total_energy'].max() if 'total_energy' in current_normaly else np.nan,
            'baseline_mode': 'current',
            'is_pushed': False,
        }
        baseline_data.append(current_baseline_row)

        # 处理历史数据
        history_result, history_normaly, history_anomaly = self.exec_ADModel(
            self.history_df, self.history_feature
        )
        
        # 历史数据的基线行
        history_baseline_row = {
            'record_time': pd.Timestamp.now().floor('S'),  # 精确到秒
            'device_name': device_name,
            'module': module,
            # 特征上下限值 - 使用 history_normaly
            'total_steam_lower': history_normaly['total_steam'].min() if 'total_steam' in history_normaly else np.nan,
            'total_steam_upper': history_normaly['total_steam'].max() if 'total_steam' in history_normaly else np.nan,
            'duration_lower': history_normaly['duration'].min() if 'duration' in history_normaly else np.nan,
            'duration_upper': history_normaly['duration'].max() if 'duration' in history_normaly else np.nan,
            'temperature_lower': history_normaly['temperature'].min() if 'temperature' in history_normaly else np.nan,
            'temperature_upper': history_normaly['temperature'].max() if 'temperature' in history_normaly else np.nan,
            'humidity_lower': history_normaly['humidity'].min() if 'humidity' in history_normaly else np.nan,
            'humidity_upper': history_normaly['humidity'].max() if 'humidity' in history_normaly else np.nan,
            'steam_mafl_lower': history_normaly['steam_mafl'].min() if 'steam_mafl' in history_normaly else np.nan,
            'steam_mafl_upper': history_normaly['steam_mafl'].max() if 'steam_mafl' in history_normaly else np.nan,
            'steam_flow_lower': history_normaly['steam_flow'].min() if 'steam_flow' in history_normaly else np.nan,
            'steam_flow_upper': history_normaly['steam_flow'].max() if 'steam_flow' in history_normaly else np.nan,
            'steam_press_aft_lower': history_normaly['steam_press_aft'].min() if 'steam_press_aft' in history_normaly else np.nan,
            'steam_press_aft_upper': history_normaly['steam_press_aft'].max() if 'steam_press_aft' in history_normaly else np.nan,
            'steam_press_bef_lower': history_normaly['steam_press_bef'].min() if 'steam_press_bef' in history_normaly else np.nan,
            'steam_press_bef_upper': history_normaly['steam_press_bef'].max() if 'steam_press_bef' in history_normaly else np.nan,
            'proc_air_valve_lower': history_normaly['proc_air_valve'].min() if 'proc_air_valve' in history_normaly else np.nan,
            'proc_air_valve_upper': history_normaly['proc_air_valve'].max() if 'proc_air_valve' in history_normaly else np.nan,
            'proc_air_temp_lower': history_normaly['proc_air_temp'].min() if 'proc_air_temp' in history_normaly else np.nan,
            'proc_air_temp_upper': history_normaly['proc_air_temp'].max() if 'proc_air_temp' in history_normaly else np.nan,
            'cyl_temp_lower': history_normaly['cyl_temp'].min() if 'cyl_temp' in history_normaly else np.nan,
            'cyl_temp_upper': history_normaly['cyl_temp'].max() if 'cyl_temp' in history_normaly else np.nan,
            'tob_mafl_lower': history_normaly['tob_mafl'].min() if 'tob_mafl' in history_normaly else np.nan,
            'tob_mafl_upper': history_normaly['tob_mafl'].max() if 'tob_mafl' in history_normaly else np.nan,
            'total_tob_lower': history_normaly['total_tob'].min() if 'total_tob' in history_normaly else np.nan,
            'total_tob_upper': history_normaly['total_tob'].max() if 'total_tob' in history_normaly else np.nan,
            'total_energy_lower': history_normaly['total_energy'].min() if 'total_energy' in history_normaly else np.nan,
            'total_energy_upper': history_normaly['total_energy'].max() if 'total_energy' in history_normaly else np.nan,
            'baseline_mode': 'history',
            'is_pushed': False,
        }
        baseline_data.append(history_baseline_row)
        
                # 合并两个基线行
        merge_baseline_row = {
            'record_time': pd.Timestamp.now().floor('S'),  # 精确到秒
            'device_name': device_name,
            'module': module,
            'baseline_mode': 'merged',
            'is_pushed': False,
        }
        
        # 提取权重
        w_current, w_history = self.baseline_weights
        
        # 定义特征列表
        features = [
            'total_steam', 'duration', 'temperature', 'humidity', 
            'steam_mafl', 'steam_flow', 'steam_press_aft', 'steam_press_bef',
            'proc_air_valve', 'proc_air_temp', 'cyl_temp', 'tob_mafl',
            'total_tob', 'total_energy'
        ]
        
        # 对每个特征计算加权后的上下限
        for feature in features:
            lower_key = f"{feature}_lower"
            upper_key = f"{feature}_upper"
            
            # 获取当前基线值
            current_lower = current_baseline_row.get(lower_key, np.nan)
            current_upper = current_baseline_row.get(upper_key, np.nan)
            
            # 获取历史基线值
            history_lower = history_baseline_row.get(lower_key, np.nan)
            history_upper = history_baseline_row.get(upper_key, np.nan)
            
            # 计算加权合并值
            if not np.isnan(current_lower) and not np.isnan(history_lower):
                merged_lower = w_current * current_lower + w_history * history_lower
            elif not np.isnan(current_lower):
                merged_lower = current_lower
            elif not np.isnan(history_lower):
                merged_lower = history_lower
            else:
                merged_lower = np.nan
                
            if not np.isnan(current_upper) and not np.isnan(history_upper):
                merged_upper = w_current * current_upper + w_history * history_upper
            elif not np.isnan(current_upper):
                merged_upper = current_upper
            elif not np.isnan(history_upper):
                merged_upper = history_upper
            else:
                merged_upper = np.nan
                
            # 添加到合并行
            merge_baseline_row[lower_key] = merged_lower
            merge_baseline_row[upper_key] = merged_upper
        
        baseline_data.append(merge_baseline_row)
        return pd.DataFrame(baseline_data)


from JayttleProcess.SQLProcess.TaosUtils import TDengineUse
from datetime import timedelta

def nengyuan_split_data(data_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    分割能源数据为当前数据和历史数据
    
    参数:
        data_df: 包含能源数据的DataFrame，必须包含'recipe_start_time'列
        
    返回:
        tuple: (current_df, history_df)
    """
    # 确保数据按时间排序
    data_df = data_df.sort_values('recipe_start_time', ascending=False)
    
    # 获取最新时间点
    latest_time = data_df['recipe_start_time'].max()
    
    # 计算一个月前的时间点（按30天计算）
    one_month_ago = latest_time - timedelta(days=30)
    
    # 划分当前数据和历史数据
    current_df = data_df[data_df['recipe_start_time'] >= one_month_ago].copy()
    history_df = data_df[data_df['recipe_start_time'] < one_month_ago].copy()
    
    # 如果当前数据少于20个，从历史数据中补充
    if len(current_df) < 20:
        # 获取历史数据中最新的部分
        supplement = history_df.head(20 - len(current_df))
        # 添加到当前数据
        current_df = pd.concat([current_df, supplement])
        # 从历史数据中移除已补充的部分
        history_df = history_df.iloc[len(supplement):]
    
    # 如果历史数据少于15个，进行随机复制
    if len(history_df) < 15 and len(history_df) > 0:
        # 计算需要复制的样本数量
        samples_needed = 15 - len(history_df)
        
        # 随机选择要复制的样本（有放回抽样）
        random_samples = history_df.sample(n=samples_needed, replace=True, random_state=42)
        
        # 将复制的样本添加到历史数据中
        history_df = pd.concat([history_df, random_samples])
    
    return current_df, history_df

def run_BlModel(TDdb_use: TDengineUse, device_name: str, module: str):
    # 定义特征权重字典
    FEATURE_WEIGHTS = {
        'total_steam': 2.0,
        'duration': 1,
        'steam_flow': 0.8,
        'tob_mafl': 0.8,
        'total_tob': 1.2,
        'total_energy': 1.2,
    }
    sql_script = f"""
SELECT 
    last(recipe_start_time) AS recipe_start_time,
    last(recipe_end_time) AS recipe_end_time,
    last(recipename) AS recipename,
    last(module) AS module,
    last(module_task) AS module_task,
    last(shift) AS shift,
    last(team) AS team,
    last(temperature) AS temperature,
    last(humidity) AS humidity,
    last(total_steam) AS total_steam,
    last(steam_mafl) AS steam_mafl,
    last(steam_flow) AS steam_flow,
    last(steam_press_aft) AS steam_press_aft,
    last(steam_press_bef) AS steam_press_bef,
    last(proc_air_valve) AS proc_air_valve,
    last(proc_air_temp) AS proc_air_temp,
    last(cyl_temp) AS cyl_temp,
    last(tob_mafl) AS tob_mafl,
    last(total_tob) AS total_tob,
    last(total_energy) AS total_energy,
    last(is_pushed) AS is_pushed,
    last(device_name) AS device_name
FROM (
    SELECT 
        *,
        CASE 
            WHEN SUBSTR(module_task, -2, 2) = '01' THEN CONCAT(module, 'A') 
            ELSE CONCAT(module, 'B') 
        END AS module_with_suffix
    FROM nengyuan_recipe
    WHERE device_name = '{device_name}'
) AS subquery
WHERE module_with_suffix = '{module}' 
GROUP BY recipename
order by recipe_start_time desc 
    """
    data = TDdb_use.execute_sql_and_return_dataframe(sql_script)
    current_df, history_df = nengyuan_split_data(data)
    baseline_model = BaselineModel(current_df=current_df, 
                                   history_df=history_df,
                                   model_corpus=['isolation_forest'], 
                                   feature_cols=['recipename'] + list(FEATURE_WEIGHTS.keys()),
                                   patch_col='recipename', 
                                   feature_weights=FEATURE_WEIGHTS,
                                   baseline_weights=(0.7, 0.3),
                                   seed=42)
    
    baseline_df = baseline_model.process_nengyuan_baseline(device_name, module)
    TDdb_use.t
    TDdb_use.batch_insert_baseline_data(baseline_df, device_name)
