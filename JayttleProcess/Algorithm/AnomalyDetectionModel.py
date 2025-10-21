import pandas as pd
import numpy as np
import warnings
import pickle
import joblib
import os
from typing import Dict, List, Any, Optional, Tuple
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.neighbors import LocalOutlierFactor
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, calinski_harabasz_score
import matplotlib.pyplot as plt
import seaborn as sns
from JayttleProcess.SQLProcess.TaosUtils import TDengineUse
warnings.filterwarnings('ignore')

#TODO: 、
# 1. 做一个加权重的，近一个月的module 占比70%，超过一个月的module 占比30%，作为基线；都要保存，一个作为历史基线，一个作为近期基线，通过基线的变化也能得到分析；
# 其中要加条件：满足 足量的批次数据 + 满足 没有维修记录，如果有维修记录则重新计算近期基线，同时历史基线只到 该维修记录到上上个维修记录期间的数据作为历史，过去的则不计算

class AnomalyDetectionModel:
    """
    高度封装的无监督故障识别类
    支持多种无监督异常检测算法, 可根据model_corpus自动选择和使用指定模型
    
    支持的算法：
    - isolation_forest: 孤立森林
    - one_class_svm: 单类支持向量机
    - local_outlier_factor (lof): 局部异常因子
    - dbscan: 基于密度的聚类
    - autoencoder: 自编码器 (需要TensorFlow)
    - pca_anomaly: 基于PCA的异常检测
    - statistical: 统计学方法 (IQR, Z-score)
    """
    def __init__(self, 
                feature_df: pd.DataFrame, 
                model_corpus: List[str],
                patch_col: str,
                seed: int = 42):
        
        """
        初始化异常检测类
        Args:
            feature_df: 特征数据框
            model_corpus: 可用模型列表，如['isolation_forest', 'one_class_svm', 'lof', 'dbscan', 'autoencoder']
            patch_col: 批次列名，用于标识不同批次的数据
            feature_weights: 特征权重字典，键为特征名，值为权重值（0-1之间，默认1.0）
                           例如：{'feature1': 2.0, 'feature2': 0.5} 表示feature1重要性是feature2的4倍
            seed: 随机种子
        """
        # 类型检查
        if not isinstance(feature_df, pd.DataFrame):
            raise TypeError("feature_df必须是pandas DataFrame")
        if not isinstance(model_corpus, list):
            raise TypeError("model_corpus必须是列表")
        if not isinstance(patch_col, str):
            raise TypeError("patch_col必须是字符串")
            
        self.feature_df = feature_df.copy()
        self.model_corpus = model_corpus
        self.patch_col = patch_col
        self.seed = seed
        self.models = {}
        self.scalers = {}
        self.results = {}
        self.result_df = None
        self.outlier_scores = {}  # 存储异常分数
        self.processed_data = None
        self.range_df = None
        
        # 验证批次列是否存在
        if patch_col not in feature_df.columns:
            raise ValueError(f"批次列 '{patch_col}' 不存在于数据中")
        self.patch_values = feature_df[patch_col].copy()  # 保存批次信息
        print(f"检测到 {len(self.patch_values.unique())} 个不同批次")
        # 设置随机种子
        np.random.seed(seed)
        # 支持的算法映射
        self.algorithm_map = {
            'isolation_forest': self._isolation_forest,
            'one_class_svm': self._one_class_svm,
            'local_outlier_factor': self._local_outlier_factor,
            'lof': self._local_outlier_factor,
            'dbscan': self._dbscan,
            'pca_anomaly': self._pca_anomaly,
            'statistical': self._statistical_anomaly
        }
        print(f"初始化完成，可用算法: {list(self.algorithm_map.keys())}")
        print(f"指定使用算法: {self.model_corpus}")


    def _filter_algorithm_params(self, algorithm_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        为不同算法过滤合适的参数
        
        Args:
            algorithm_name: 算法名称
            params: 输入参数字典
            
        Returns:
            过滤后的参数字典
        """
        # 定义每个算法支持的参数
        algorithm_params = {
            'isolation_forest': ['contamination', 'n_estimators', 'max_samples', 'max_features', 'bootstrap'],
            'one_class_svm': ['nu', 'kernel', 'gamma', 'degree', 'coef0', 'tol', 'shrinking', 'cache_size'],
            'local_outlier_factor': ['n_neighbors', 'contamination', 'algorithm', 'leaf_size', 'metric', 'p'],
            'lof': ['n_neighbors', 'contamination', 'algorithm', 'leaf_size', 'metric', 'p'],
            'dbscan': ['eps', 'min_samples', 'metric', 'algorithm', 'leaf_size', 'p'],
            'autoencoder': ['encoding_dim', 'epochs', 'batch_size', 'contamination', 'learning_rate', 'validation_split'],
            'pca_anomaly': ['n_components', 'contamination', 'whiten', 'svd_solver'],
            'statistical': ['method', 'contamination', 'threshold_factor']
        }
        
        if algorithm_name not in algorithm_params:
            return params
        
        # 过滤参数
        supported_params = algorithm_params[algorithm_name]
        filtered = {k: v for k, v in params.items() if k in supported_params}
        
        return filtered
    
    def _normalize_scores(self, scores: np.ndarray) -> np.ndarray:
        """
        将异常分数标准化到[0,1]范围，0表示正常，1表示最异常
        
        Args:
            scores: 原始异常分数
            
        Returns:
            标准化后的分数
        """
        min_score = np.min(scores)
        max_score = np.max(scores)
        if max_score > min_score:
            return (scores - min_score) / (max_score - min_score)
        else:
            return np.zeros_like(scores)
    
    def fit_predict(self, **kwargs) -> Dict[str, np.ndarray]:
        """
        根据model_corpus拟合并预测所有指定算法
        
        Args:
            **kwargs: 传递给各算法的参数
            
        Returns:
            各算法的预测结果字典
        """
        if self.processed_data is None:
            print("数据未预处理，使用默认预处理...")
            self.preprocess_data()
        
        print(f"\n开始训练和预测，使用算法: {self.model_corpus}")
        
        for model_name in self.model_corpus:
            if model_name in self.algorithm_map:
                print(f"\n正在执行: {model_name}")
                try:
                    # 为每个算法过滤合适的参数
                    filtered_kwargs = self._filter_algorithm_params(model_name, kwargs)
                    predictions = self.algorithm_map[model_name](**filtered_kwargs)
                    self.results[model_name] = predictions
                    print(f"{model_name} 完成，异常点数量: {np.sum(predictions == 1)}")
                except Exception as e:
                    print(f"{model_name} 执行失败: {str(e)}")
                    print(f"错误详情: {type(e).__name__}")
            else:
                print(f"警告: 未知算法 '{model_name}'，跳过")

        self.result_df = pd.concat([self.feature_df, pd.DataFrame(self.results)], axis=1)  # 横向合并
        return self.results
    def _isolation_forest(self, 
                         contamination: float = 0.1,
                         n_estimators: int = 100,
                         **kwargs) -> np.ndarray:
        """Isolation Forest算法"""
        model = IsolationForest(
            contamination=contamination,
            n_estimators=n_estimators,
            random_state=self.seed,
            **kwargs
        )
        predictions = model.fit_predict(self.processed_data)
        
        # 获取异常分数（decision_function返回的值越小越异常）
        raw_scores = model.decision_function(self.processed_data)
        # 转换为正值，分数越高越异常，并进行标准化
        outlier_scores = self._normalize_scores(-raw_scores)
        self.outlier_scores['isolation_forest'] = outlier_scores
        
        self.models['isolation_forest'] = model
        # 转换为0（正常）和1（异常）格式
        predictions = np.where(predictions == -1, 1, 0)
        return predictions
    
    def _one_class_svm(self, 
                      nu: float = 0.1,
                      kernel: str = 'rbf',
                      gamma: str = 'scale',
                      **kwargs) -> np.ndarray:
        """One-Class SVM算法"""
        model = OneClassSVM(
            nu=nu,
            kernel=kernel,
            gamma=gamma,
            **kwargs
        )
        predictions = model.fit_predict(self.processed_data)
        
        # 获取异常分数（decision_function返回的值越小越异常）
        raw_scores = model.decision_function(self.processed_data)
        # 转换为正值，分数越高越异常，并进行标准化
        outlier_scores = -raw_scores
        # 标准化到[0,1]范围
        min_score = np.min(outlier_scores)
        max_score = np.max(outlier_scores)
        if max_score > min_score:
            outlier_scores = (outlier_scores - min_score) / (max_score - min_score)
        else:
            outlier_scores = np.zeros_like(outlier_scores)
        self.outlier_scores['one_class_svm'] = outlier_scores
        
        self.models['one_class_svm'] = model
        # 转换为0（正常）和1（异常）格式
        predictions = np.where(predictions == -1, 1, 0)
        return predictions
    
    def _local_outlier_factor(self, 
                             n_neighbors: int = 20,
                             contamination: float = 0.1,
                             **kwargs) -> np.ndarray:
        """Local Outlier Factor算法"""
        model = LocalOutlierFactor(
            n_neighbors=n_neighbors,
            contamination=contamination,
            **kwargs
        )
        predictions = model.fit_predict(self.processed_data)
        
        # 获取异常分数（negative_outlier_factor_越小越异常）
        raw_scores = -model.negative_outlier_factor_
        # 标准化到[0,1]范围
        min_score = np.min(raw_scores)
        max_score = np.max(raw_scores)
        if max_score > min_score:
            outlier_scores = (raw_scores - min_score) / (max_score - min_score)
        else:
            outlier_scores = np.zeros_like(raw_scores)
        self.outlier_scores['local_outlier_factor'] = outlier_scores
        
        self.models['local_outlier_factor'] = model
        # 转换为0（正常）和1（异常）格式
        predictions = np.where(predictions == -1, 1, 0)
        return predictions
    
    def _dbscan(self, 
               eps: float = 0.5,
               min_samples: int = 5,
               **kwargs) -> np.ndarray:
        """DBSCAN聚类算法"""
        model = DBSCAN(
            eps=eps,
            min_samples=min_samples,
            **kwargs
        )
        cluster_labels = model.fit_predict(self.processed_data)
        
        # 为DBSCAN计算异常分数（优化版本，使用KDTree）
        outlier_scores = np.zeros(len(cluster_labels))
        
        # 获取非噪声点
        non_noise_indices = np.where(cluster_labels != -1)[0]
        
        if len(non_noise_indices) > 0:
            from sklearn.neighbors import NearestNeighbors
            # 使用最近邻算法优化距离计算
            nn = NearestNeighbors(n_neighbors=1, algorithm='kd_tree')
            non_noise_data = self.processed_data.iloc[non_noise_indices]
            nn.fit(non_noise_data)
            
            # 计算所有点到最近非噪声点的距离
            distances, _ = nn.kneighbors(self.processed_data)
            outlier_scores = distances.flatten()
            
            # 对于非噪声点，计算与同簇点的平均距离
            for i, label in enumerate(cluster_labels):
                if label != -1:  # 非噪声点
                    same_cluster_indices = np.where(cluster_labels == label)[0]
                    if len(same_cluster_indices) > 1:
                        same_cluster_data = self.processed_data.iloc[same_cluster_indices]
                        # 计算与同簇点的平均距离
                        cluster_distances = []
                        for j in same_cluster_indices:
                            if i != j:
                                dist = np.linalg.norm(self.processed_data.iloc[i] - self.processed_data.iloc[j])
                                cluster_distances.append(dist)
                        if cluster_distances:
                            outlier_scores[i] = np.mean(cluster_distances)
        else:
            # 如果没有非噪声点，所有点都是异常
            outlier_scores = np.ones(len(cluster_labels))
        
        # 标准化DBSCAN异常分数到[0,1]范围
        min_score = np.min(outlier_scores)
        max_score = np.max(outlier_scores)
        if max_score > min_score:
            outlier_scores = (outlier_scores - min_score) / (max_score - min_score)
        else:
            outlier_scores = np.zeros_like(outlier_scores)
        
        self.outlier_scores['dbscan'] = outlier_scores
        
        # 将噪声点(-1)视为异常，其他聚类点视为正常
        predictions = np.where(cluster_labels == -1, 1, 0)
        self.models['dbscan'] = model
        return predictions
    def _pca_anomaly(self, 
                    n_components: float = 0.95,
                    contamination: float = 0.1,
                    **kwargs) -> np.ndarray:
        """基于PCA的异常检测"""
        pca = PCA(n_components=n_components, random_state=self.seed)
        transformed = pca.fit_transform(self.processed_data)
        reconstructed = pca.inverse_transform(transformed)
        
        # 计算重构误差
        mse = np.mean(np.power(self.processed_data.values - reconstructed, 2), axis=1)
        
        # 保存异常分数（重构误差），标准化到[0,1]范围
        min_score = np.min(mse)
        max_score = np.max(mse)
        if max_score > min_score:
            normalized_mse = (mse - min_score) / (max_score - min_score)
        else:
            normalized_mse = np.zeros_like(mse)
        self.outlier_scores['pca_anomaly'] = normalized_mse
        
        # 基于重构误差阈值判断异常
        threshold = np.percentile(mse, (1 - contamination) * 100)
        predictions = np.where(mse > threshold, 1, 0)
        
        # 保存模型和阈值
        self.models['pca_anomaly'] = pca
        self.models['pca_anomaly_threshold'] = threshold
        
        return predictions


    def evaluate_results(self) -> pd.DataFrame:
        """评估各算法结果"""
        if not self.results:
            print("没有可评估的结果，请先运行fit_predict()")
            return pd.DataFrame()
        
        evaluation_metrics = []
        
        for model_name, predictions in self.results.items():
            metrics = {
                'algorithm': model_name,
                'total_samples': len(predictions),
                'anomaly_count': np.sum(predictions == 1),
                'anomaly_ratio': np.sum(predictions == 1) / len(predictions),
                'normal_count': np.sum(predictions == 0)
            }
            
            # 如果可能，计算聚类质量指标
            try:
                if len(np.unique(predictions)) > 1:
                    metrics['silhouette_score'] = silhouette_score(self.processed_data, predictions)
                    metrics['calinski_harabasz_score'] = calinski_harabasz_score(self.processed_data, predictions)
            except:
                metrics['silhouette_score'] = np.nan
                metrics['calinski_harabasz_score'] = np.nan
            
            evaluation_metrics.append(metrics)
        
        evaluation_df = pd.DataFrame(evaluation_metrics)
        print("\n算法评估结果:")
        print(evaluation_df.to_string(index=False))
        return evaluation_df
    
    def _statistical_anomaly(self, 
                           method: str = 'iqr',
                           contamination: float = 0.1,
                           **kwargs) -> np.ndarray:
        """统计学方法异常检测"""
        if method == 'iqr':
            # 使用IQR方法
            Q1 = self.processed_data.quantile(0.25, axis=0)
            Q3 = self.processed_data.quantile(0.75, axis=0)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            # 计算异常分数（超出边界的程度）
            deviations = np.maximum(
                (lower_bound - self.processed_data).clip(lower=0),
                (self.processed_data - upper_bound).clip(lower=0)
            )
            raw_scores = np.max(deviations, axis=1)
            # 标准化到[0,1]范围
            min_score = np.min(raw_scores)
            max_score = np.max(raw_scores)
            if max_score > min_score:
                outlier_scores = (raw_scores - min_score) / (max_score - min_score)
            else:
                outlier_scores = np.zeros_like(raw_scores)
            self.outlier_scores['statistical'] = outlier_scores
            
            # 检查每个样本是否在正常范围内
            is_outlier = ((self.processed_data < lower_bound) | 
                         (self.processed_data > upper_bound)).any(axis=1)
            predictions = np.where(is_outlier, 1, 0)
            
        elif method == 'zscore':
            # 使用Z-score方法
            z_scores = np.abs((self.processed_data - self.processed_data.mean()) / self.processed_data.std())
            # 异常分数为最大的z-score，标准化到[0,1]范围
            raw_scores = np.max(z_scores, axis=1)
            min_score = np.min(raw_scores)
            max_score = np.max(raw_scores)
            if max_score > min_score:
                outlier_scores = (raw_scores - min_score) / (max_score - min_score)
            else:
                outlier_scores = np.zeros_like(raw_scores)
            self.outlier_scores['statistical'] = outlier_scores
            
            is_outlier = (z_scores > 3).any(axis=1)
            predictions = np.where(is_outlier, 1, 0)
        
        return predictions
        
    def save_models(self, save_dir: str = "saved_models") -> None:
        """
        保存所有训练好的模型和预处理器
        
        Args:
            save_dir: 保存目录路径
        """
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        # 保存模型
        for model_name, model in self.models.items():
            model_path = os.path.join(save_dir, f"{model_name}_model.pkl")
            joblib.dump(model, model_path)
            print(f"已保存 {model_name} 模型到: {model_path}")
        
        # 保存预处理器
        for scaler_name, scaler in self.scalers.items():
            scaler_path = os.path.join(save_dir, f"{scaler_name}.pkl")
            joblib.dump(scaler, scaler_path)
            print(f"已保存预处理器 {scaler_name} 到: {scaler_path}")
        
        # 保存模型配置信息
        feature_columns = [col for col in self.feature_df.columns if col != self.patch_col]
        config = {
            'model_corpus': self.model_corpus,
            'patch_col': self.patch_col,
            'seed': self.seed,
            'feature_columns': feature_columns,
            'feature_weights': self.feature_weights,
            'processed_data_shape': self.processed_data.shape if self.processed_data is not None else None
        }
        config_path = os.path.join(save_dir, "model_config.pkl")
        with open(config_path, 'wb') as f:
            pickle.dump(config, f)
        print(f"已保存模型配置到: {config_path}")
        
        print(f"\n所有模型已保存到目录: {save_dir}")
    
    @classmethod
    def load_models(cls, save_dir: str = "saved_models", feature_df: Optional[pd.DataFrame] = None):
        """
        加载保存的模型和预处理器
        
        Args:
            save_dir: 模型保存目录
            feature_df: 特征数据框（可选，用于初始化）
            
        Returns:
            AnomalyDetection实例
        """
        if not os.path.exists(save_dir):
            raise FileNotFoundError(f"模型目录不存在: {save_dir}")
        
        # 加载配置
        config_path = os.path.join(save_dir, "model_config.pkl")
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"模型配置文件不存在: {config_path}")
        
        with open(config_path, 'rb') as f:
            config = pickle.load(f)
        
        print(f"加载模型配置: {config}")
        
        # 创建实例
        if feature_df is None:
            # 创建空的DataFrame作为占位符，包含patch_col
            feature_df = pd.DataFrame({config['patch_col']: []})
        
        # 从配置中获取特征权重
        feature_weights = config.get('feature_weights', None)
        detector = cls(feature_df, config['model_corpus'], config['patch_col'], feature_weights, config['seed'])
        
        # 加载模型
        for model_name in config['model_corpus']:
            model_path = os.path.join(save_dir, f"{model_name}_model.pkl")
            if os.path.exists(model_path):
                detector.models[model_name] = joblib.load(model_path)
                print(f"已加载 {model_name} 模型")
    
        # 加载预处理器
        scaler_files = [f for f in os.listdir(save_dir) if f.endswith('.pkl') and f != 'model_config.pkl' and not f.endswith('_model.pkl')]
        for scaler_file in scaler_files:
            scaler_name = scaler_file.replace('.pkl', '')
            scaler_path = os.path.join(save_dir, scaler_file)
            detector.scalers[scaler_name] = joblib.load(scaler_path)
            print(f"已加载预处理器 {scaler_name}")
        
        print(f"\n模型加载完成，共加载 {len(detector.models)} 个模型")
        return detector

        
    def _process_feature_weights(self, feature_weights: Optional[Dict[str, float]]) -> Dict[str, float]:
        """
        处理特征权重，确保所有特征都有权重值
        
        Args:
            feature_weights: 特征权重字典
            
        Returns:
            处理后的特征权重字典
        """
        if feature_weights is None:
            return {}
        
        # 获取所有数值特征列（排除批次列）
        numeric_columns = self.feature_df.select_dtypes(include=[np.number]).columns
        if self.patch_col in numeric_columns:
            numeric_columns = numeric_columns.drop(self.patch_col)
        
        processed_weights = {}
        
        # 为每个特征设置权重
        for col in numeric_columns:
            if col in feature_weights:
                weight = feature_weights[col]
                if weight <= 0:
                    raise ValueError(f"特征 '{col}' 的权重必须大于0，当前值: {weight}")
                processed_weights[col] = weight
            else:
                # 未指定的特征使用默认权重1.0
                processed_weights[col] = 1.0
        
        # 检查是否有无效的特征名
        invalid_features = set(feature_weights.keys()) - set(numeric_columns)
        if invalid_features:
            print(f"警告: 以下特征在数据中不存在，将被忽略: {invalid_features}")
        
        return processed_weights
 
def analyze_anomaly_data(feature_fileds: list[str], anomaly_row: pd.Series, baseline_row: dict) -> tuple:
    """
    分析异常数据，生成详细的异常信息报告
    
    参数:
        anomaly_row: 包含异常数据的Series
        baseline_row: 包含基线范围数据的字典
        
    返回:
        anomalies_list: 包含异常详细信息的字典列表
        anomaly_level: 异常严重等级
    """
    if anomaly_row.empty:
        return [], 0
    
    # 存储异常信息的列表
    anomalies_list = []
    
    # 检查每个特征是否超出基线范围
    for feature in feature_fileds:
        # 获取特征值
        value = anomaly_row.get(feature)
        
        # 获取基线范围
        lower_key = f"{feature}_lower"
        upper_key = f"{feature}_upper"
        lower_bound = baseline_row.get(lower_key)
        upper_bound = baseline_row.get(upper_key)
        
        # 跳过缺失值或无效范围
        if pd.isna(value) or pd.isna(lower_bound) or pd.isna(upper_bound):
            continue
        
        anomaly_info = ""
        # 检查是否低于下限
        if value < lower_bound:
            deviation = lower_bound - value
            deviation_percent = (deviation / lower_bound) * 100
            anomaly_info = f"{value:.2f} 低于下限 {lower_bound:.2f}, 偏低 {deviation:.2f}, {deviation_percent:.1f}%"
        
        # 检查是否高于上限
        elif value > upper_bound:
            deviation = value - upper_bound
            deviation_percent = (deviation / upper_bound) * 100
            anomaly_info = f"{value:.2f} 高于上限 {upper_bound:.2f}, 偏高 {deviation:.2f}, {deviation_percent:.1f}%"
        
        # 如果有异常信息，添加到列表
        if anomaly_info:
            anomalies_list.append({
                'anomaly_field': feature,
                'anomaly_info': anomaly_info
            })
    
    # 计算异常等级
    num_anomalies = len(anomalies_list)
    if num_anomalies > 5:
        anomaly_level = 2
    elif num_anomalies >= 2:
        anomaly_level = 1
    else:
        anomaly_level = 0
    
    return anomalies_list, anomaly_level


def preprocess_data(self, 
            scaler_type: str = 'standard',
            handle_missing: str = 'drop',
            pca_components: Optional[int] = None) -> pd.DataFrame:
    """
    数据预处理
    
    Args:
        scaler_type: 缩放方法 ('standard', 'minmax', 'robust')
        handle_missing: 缺失值处理 ('drop', 'fill_mean', 'fill_median')
        pca_components: PCA降维组件数，None表示不降维
        
    Returns:
        处理后的数据
    """
    print("开始数据预处理...")
    data = self.feature_df.copy()
    
    # 处理缺失值
    original_indices = data.index
    if handle_missing == 'drop':
        data = data.dropna()
        # 更新批次列，保持索引一致
        self.patch_values = self.patch_values.loc[data.index]
    elif handle_missing == 'fill_mean':
        data = data.fillna(data.mean())
    elif handle_missing == 'fill_median':
        data = data.fillna(data.median())
    
    # 只保留数值列，排除批次列
    numeric_columns = data.select_dtypes(include=[np.number]).columns
    # 如果批次列是数值类型，也要排除
    if self.patch_col in numeric_columns:
        numeric_columns = numeric_columns.drop(self.patch_col)
    data = data[numeric_columns]
    
    # 数据缩放
    if scaler_type == 'standard':
        scaler = StandardScaler()
    elif scaler_type == 'minmax':
        scaler = MinMaxScaler()
    elif scaler_type == 'robust':
        scaler = RobustScaler()
    else:
        raise ValueError("scaler_type必须是'standard', 'minmax', 或'robust'之一")
    
    scaled_data = scaler.fit_transform(data)
    self.scalers['data_scaler'] = scaler
    
    # 应用特征权重（在PCA之前应用）
    if self.feature_weights:
        # 创建权重矩阵
        weights_array = np.array([self.feature_weights.get(col, 1.0) for col in numeric_columns])
        # 对每个样本的每个特征应用权重
        weighted_data = scaled_data * weights_array
        scaled_data = weighted_data
    
    # PCA降维
    if pca_components:
        pca = PCA(n_components=pca_components, random_state=self.seed)
        scaled_data = pca.fit_transform(scaled_data)
        self.scalers['pca'] = pca
        print(f"PCA降维至{pca_components}维，解释方差比: {pca.explained_variance_ratio_.sum():.3f}")
    
    self.processed_data = pd.DataFrame(scaled_data)
    return self.processed_data
    
def run_ADModel(TDdb_use: TDengineUse, device_name: str, module: str):
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
    last(device_name) AS device_name,
    last(module_with_suffix) as module_with_suffix
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
    keep_cols = ['recipename'] + list(FEATURE_WEIGHTS.keys())
    model_corpus = ['isolation_forest']
    patch_col = 'recipename'
    data['module'] = data['module_with_suffix']
    data.drop(columns='module_with_suffix', inplace=True)
    data['duration'] = (data['recipe_end_time'] - data['recipe_start_time']).dt.total_seconds().astype(int)
    # 用于存储所有基线数据的列表
    baseline_data = []
    anomaly_info = []
    ADModel = AnomalyDetectionModel(data[keep_cols].dropna(axis=1, how='all'), model_corpus, patch_col, FEATURE_WEIGHTS)
    ADModel.preprocess_data()
    ADModel.fit_predict()
    result_df = pd.concat([data, pd.DataFrame(ADModel.results)], axis=1)
    normal_data = result_df[result_df['isolation_forest'] == 0]
    anomaly_data = result_df[result_df['isolation_forest'] == 1]
    # 如果没有正常样本，跳过
    if normal_data.empty:
        print(f"警告: 设备 {device_name} 模块 {data} 没有正常样本")
    # 准备一行基线数据
    baseline_row = {
        'record_time': pd.Timestamp.now().floor('S'),  # 精确到秒
        'device_name': device_name,
        'module': module,
        # 特征上下限值
        'total_steam_lower': normal_data['total_steam'].min() if 'total_steam' in normal_data else np.nan,
        'total_steam_upper': normal_data['total_steam'].max() if 'total_steam' in normal_data else np.nan,
        'duration_lower': normal_data['duration'].min() if 'duration' in normal_data else np.nan,
        'duration_upper': normal_data['duration'].max() if 'duration' in normal_data else np.nan,
        'temperature_lower': normal_data['temperature'].min() if 'temperature' in normal_data else np.nan,
        'temperature_upper': normal_data['temperature'].max() if 'temperature' in normal_data else np.nan,
        'humidity_lower': normal_data['humidity'].min() if 'humidity' in normal_data else np.nan,
        'humidity_upper': normal_data['humidity'].max() if 'humidity' in normal_data else np.nan,
        'steam_mafl_lower': normal_data['steam_mafl'].min() if 'steam_mafl' in normal_data else np.nan,
        'steam_mafl_upper': normal_data['steam_mafl'].max() if 'steam_mafl' in normal_data else np.nan,
        'steam_flow_lower': normal_data['steam_flow'].min() if 'steam_flow' in normal_data else np.nan,
        'steam_flow_upper': normal_data['steam_flow'].max() if 'steam_flow' in normal_data else np.nan,
        'steam_press_aft_lower': normal_data['steam_press_aft'].min() if 'steam_press_aft' in normal_data else np.nan,
        'steam_press_aft_upper': normal_data['steam_press_aft'].max() if 'steam_press_aft' in normal_data else np.nan,
        'steam_press_bef_lower': normal_data['steam_press_bef'].min() if 'steam_press_bef' in normal_data else np.nan,
        'steam_press_bef_upper': normal_data['steam_press_bef'].max() if 'steam_press_bef' in normal_data else np.nan,
        'proc_air_valve_lower': normal_data['proc_air_valve'].min() if 'proc_air_valve' in normal_data else np.nan,
        'proc_air_valve_upper': normal_data['proc_air_valve'].max() if 'proc_air_valve' in normal_data else np.nan,
        'proc_air_temp_lower': normal_data['proc_air_temp'].min() if 'proc_air_temp' in normal_data else np.nan,
        'proc_air_temp_upper': normal_data['proc_air_temp'].max() if 'proc_air_temp' in normal_data else np.nan,
        'cyl_temp_lower': normal_data['cyl_temp'].min() if 'cyl_temp' in normal_data else np.nan,
        'cyl_temp_upper': normal_data['cyl_temp'].max() if 'cyl_temp' in normal_data else np.nan,
        'tob_mafl_lower': normal_data['tob_mafl'].min() if 'tob_mafl' in normal_data else np.nan,
        'tob_mafl_upper': normal_data['tob_mafl'].max() if 'tob_mafl' in normal_data else np.nan,
        'total_tob_lower': normal_data['total_tob'].min() if 'total_tob' in normal_data else np.nan,
        'total_tob_upper': normal_data['total_tob'].max() if 'total_tob' in normal_data else np.nan,
        'total_energy_lower': normal_data['total_energy'].min() if 'total_energy' in normal_data else np.nan,
        'total_energy_upper': normal_data['total_energy'].max() if 'total_energy' in normal_data else np.nan,
        'is_pushed': False,
    }
    # 添加到数据列表
    baseline_data.append(baseline_row)
    # 将所有基线数据转换为DataFrame
    if baseline_data:
        baseline_df = pd.DataFrame(baseline_data)
        TDdb_use.truncate_table(f"nengyuan_baseline_{device_name}", module)
        TDdb_use.batch_insert_baseline_data(baseline_df, device_name)
    else:
        print("警告: 没有生成任何基线数据")

    # 定义特征列表（与基线字典中的键对应）
    feature_fileds = [
        'total_steam', 'duration', 'temperature', 'humidity',
        'steam_mafl', 'steam_flow', 'steam_press_aft', 'steam_press_bef',
        'proc_air_valve', 'proc_air_temp', 'cyl_temp', 'tob_mafl',
        'total_tob', 'total_energy'
    ]
    
    for index, anomaly in anomaly_data.iterrows():
        # 生成异常信息报告
        anomalies_list, anomaly_level = ADModel.analyze_anomaly_data(feature_fileds, anomaly, baseline_row)
        # 如果没有异常，跳过
        if not anomalies_list:
            continue
        
        # 为每个异常字段创建一条记录
        for anomaly_item in anomalies_list:
            anomaly_info.append({
                'record_time': pd.Timestamp.now().floor('S'),
                'recipename': anomaly.get('recipename', ''),  # 添加批次号
                'device_name': device_name,
                'module': module,
                'total_steam': anomaly['total_steam'],
                'total_tob': anomaly['total_tob'],
                'total_energy': anomaly['total_energy'],
                'anomaly_field': anomaly_item['anomaly_field'],  # 异常字段名
                'anomaly_info': anomaly_item['anomaly_info'],  # 该字段的异常信息
                'anomaly_level': anomaly_level,
                'is_pushed': False
            })

    # 将所有异常数据转换为DataFrame
    if anomaly_info:
        anomaly_info_df = pd.DataFrame(anomaly_info)
        # 清空表并插入新数据
        TDdb_use.truncate_table(f"nengyuan_anomaly_{device_name}", module)
        TDdb_use.batch_insert_anomaly_data(anomaly_info_df, device_name)