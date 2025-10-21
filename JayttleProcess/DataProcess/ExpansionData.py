
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import os


class DataExpansion:
    def __init__(self, data: pd.DataFrame, 
                 key_col: str,
                 target_cols: list, 
                 class_col: str, 
                 coef_dict: dict, 
                 expand_ratio: float, 
                 random_seed = 42):
        """
        data: 需要膨胀的原始数据
        key_col: 样本主键列
        target_cols: 需要进行数据膨胀的列
        class_col: 样本类别列
        coef_dict: 样本类别与数据膨胀系数的映射字典
        expand_ratio: 样本膨胀的数据比例
        random_seed: 随机数种子
        """
        self.data = data
        self.key_col = key_col
        self.target_cols = target_cols
        self.class_col = class_col
        self.coef_dict = coef_dict
        self.expand_ratio = expand_ratio
        self.data_expanded = None
        self.random_seed = random_seed
    def __str__(self):
        """返回类的摘要信息"""
        summary = [
            f"DataExpansion Summary:",
            f"  Key Column: '{self.key_col}'",
            f"  Target Columns: {self.target_cols}",
            f"  Class Column: '{self.class_col}'",
            f"  Expansion Ratio: {self.expand_ratio:.2%}",
            f"  Random Seed: {self.random_seed}",
            f"  Coefficient Mapping:"
        ]
        
        # 添加系数映射的详细信息
        for class_val, coef in self.coef_dict.items():
            summary.append(f"    - Class '{class_val}': {coef:.4f}")
        
        # 添加数据状态信息
        if self.data_expanded is None:
            summary.append("  Status: Data not expanded yet")
            summary.append(f"  Original Samples: {len(self.data)}")
        else:
            expansion_count = len(self.data_expanded) - len(self.data)
            summary.append("  Status: Data expansion completed")
            summary.append(f"  Original Samples: {len(self.data)}")
            summary.append(f"  Expanded Samples: {expansion_count}")
            summary.append(f"  Total Samples: {len(self.data_expanded)}")
        
        return "\n".join(summary)

    def expand_data(self):
        """
        数据膨胀 - 按 period_type 分组进行膨胀
        """
        corrupted_samples = []
        np.random.seed(self.random_seed)
        self.data_expanded = self.data.copy()
        
        # 清空之前的坏样本信息
        self.corrupted_samples_info = []
        
        # 按 period_type 分组处理
        grouped = self.data_expanded.groupby('period_type')
        
        # 存储所有被选中的原始数据
        selected_data_frames = []
        
        for period_type, group in grouped:
            # 获取当前 period_type 的所有唯一 period_code
            unique_period_codes = group[self.key_col].unique()
            
            # 计算当前 period_type 需要膨胀的数量
            n = max(1, int(self.expand_ratio * len(unique_period_codes)))
            
            # 随机选择 period_code
            selected_codes = np.random.choice(unique_period_codes, size=n, replace=False)
            
            # 存储被选中的原始数据
            selected_df = group[group[self.key_col].isin(selected_codes)].copy()
            selected_data_frames.append(selected_df)
            
            # 处理每个被选中的 period_code
            for period_code in selected_codes:
                # 获取当前 period_code 的所有样本
                code_data = group[group[self.key_col] == period_code].copy()
                
                # 为新的 period_code 添加后缀
                new_period_code = f"{period_code}BAD"
                code_data[self.key_col] = new_period_code
                
                # 存储原始数据用于可视化
                original_data = group[group[self.key_col] == period_code].copy()
                
                # 为每个样本计算膨胀系数
                for idx, row in code_data.iterrows():
                    # 获取当前样本的相位值
                    class_value = row[self.class_col]
                    coef = self.coef_dict[class_value]  # 使用字典中的系数
                    
                    # 膨胀振动信号
                    for col in self.target_cols:
                        if col == 'ABB2_SE04_peak':
                            code_data.at[idx, col] = row[col] * (coef + 2)
                        else:
                            code_data.at[idx, col] = row[col] * coef
                        
                    
                    # 记录使用的相位值和系数
                    code_data.at[idx, 'class_value'] = class_value
                    code_data.at[idx, 'coef'] = coef
                
                # 标记为坏样本
                code_data['is_corrupted'] = 1
                
                # 添加到结果列表
                corrupted_samples.append(code_data)
                
                # 存储信息用于可视化
                self.corrupted_samples_info.append({
                    'original_period_code': period_code,
                    'new_period_code': new_period_code,
                    'original_data': original_data,
                    'corrupted_data': code_data.copy()
                })
        
        # 合并所有被选中的原始数据
        self.selected_df = pd.concat(selected_data_frames)
        
        # 合并所有生成的坏样本
        if corrupted_samples:
            corrupted_df = pd.concat(corrupted_samples)
            corrupted_df.reset_index(drop=True, inplace=True)
            
            # 将坏样本添加到原始数据中
            self.data_expanded = pd.concat([self.data_expanded, corrupted_df], ignore_index=True)
            
        return self.data_expanded

    def expand_data_types(self):
        """
        数据膨胀 - 按故障类型分组进行膨胀
        """
        corrupted_samples = []
        np.random.seed(self.random_seed)
        self.data_expanded = self.data.copy()
        
        # 清空之前的坏样本信息
        self.corrupted_samples_info = []
        
        # 按 period_type 分组处理
        grouped = self.data_expanded.groupby('period_type')
        
        # 存储所有被选中的原始数据
        selected_data_frames = []
        
        # 定义故障类型和对应的膨胀规则
        fault_types = [
            {
                'name': '左侧两个从动轮坏',
                'description': 'SE01坏，SE02坏',
                'target_cols': ['ABB2_SE01_peak', 'ABB2_SE02_peak']
            },
            {
                'name': '从动轮带动主动轮坏',
                'description': 'SE01坏，SE03坏',
                'target_cols': ['ABB2_SE01_peak', 'ABB2_SE03_peak']
            },
            {
                'name': '从动轮带动主动轮坏',
                'description': 'SE02坏，SE03坏',
                'target_cols': ['ABB2_SE02_peak', 'ABB2_SE03_peak']
            },
            {
                'name': '只有主动轮坏',
                'description': 'SE03坏',
                'target_cols': ['ABB2_SE03_peak']
            },
            {
                'name': '右侧两个轮子坏',
                'description': 'SE03坏，SE04坏',
                'target_cols': ['ABB2_SE03_peak', 'ABB2_SE04_peak']
            }
        ]
        
        for period_type, group in grouped:
            # 获取当前 period_type 的所有唯一 period_code
            unique_period_codes = group[self.key_col].unique()
            
            # 计算当前 period_type 需要膨胀的总数量
            total_n = max(4, int(self.expand_ratio * len(unique_period_codes)))
            
            # 计算每组故障类型的样本数量（平均分配）
            n_per_fault = max(1, total_n // len(fault_types))
            
            # 随机选择 period_code
            selected_codes = np.random.choice(unique_period_codes, size=total_n, replace=False)
            
            # 存储被选中的原始数据
            selected_df = group[group[self.key_col].isin(selected_codes)].copy()
            selected_data_frames.append(selected_df)
            
            # 将选中的 period_code 分配到不同的故障类型组
            for i, fault_type in enumerate(fault_types):
                # 获取当前故障类型组的 period_code
                start_idx = i * n_per_fault
                end_idx = min((i + 1) * n_per_fault, len(selected_codes))
                fault_codes = selected_codes[start_idx:end_idx]
                
                # 处理当前故障类型组的每个 period_code
                for period_code in fault_codes:
                    # 获取当前 period_code 的所有样本
                    code_data = group[group[self.key_col] == period_code].copy()
                    
                    # 为新的 period_code 添加后缀
                    new_period_code = f"{period_code}BAD"
                    code_data[self.key_col] = new_period_code
                    
                    # 存储原始数据用于可视化
                    original_data = group[group[self.key_col] == period_code].copy()
                    
                    # 为每个样本计算膨胀系数
                    for idx, row in code_data.iterrows():
                        # 获取当前样本的相位值
                        class_value = row[self.class_col]
                        coef = self.coef_dict[class_value]  # 使用字典中的系数
                        
                        # 膨胀振动信号 - 只膨胀当前故障类型对应的列
                        for col in fault_type['target_cols']:
                            code_data.at[idx, col] = row[col] * coef
                        
                        # 记录使用的相位值和系数
                        code_data.at[idx, 'class_value'] = class_value
                        code_data.at[idx, 'coef'] = coef
                        code_data.at[idx, 'fault_type'] = fault_type['name']
                    
                    # 标记为坏样本
                    code_data['is_corrupted'] = 1
                    
                    # 添加到结果列表
                    corrupted_samples.append(code_data)
                    
                    # 存储信息用于可视化
                    self.corrupted_samples_info.append({
                        'original_period_code': period_code,
                        'new_period_code': new_period_code,
                        'original_data': original_data,
                        'corrupted_data': code_data.copy(),
                        'fault_type': fault_type['name']
                    })
        
        # 合并所有被选中的原始数据
        self.selected_df = pd.concat(selected_data_frames)
        
        # 合并所有生成的坏样本
        if corrupted_samples:
            corrupted_df = pd.concat(corrupted_samples)
            corrupted_df.reset_index(drop=True, inplace=True)
            
            # 将坏样本添加到原始数据中
            self.data_expanded = pd.concat([self.data_expanded, corrupted_df], ignore_index=True)
            
        return self.data_expanded
        
    def adjust_imbalance(self, target_bad_ratio=0.01):
        """
        调整数据不平衡，使坏样本 period_code 占比达到目标比例
        
        参数:
            target_bad_ratio: 目标坏样本比例 (默认为1%)
        """
        if self.data_expanded is None:
            print("请先调用 expand_data() 方法进行数据膨胀")
            return self.data
        
        # 计算当前坏样本 period_code 比例
        # 获取所有唯一的 period_code
        all_period_codes = self.data_expanded[self.key_col].unique()
        
        # 获取坏样本的 period_code
        bad_period_codes = self.data_expanded[
            self.data_expanded['is_corrupted'] == 1
        ][self.key_col].unique()
        
        # 获取好样本的 period_code
        good_period_codes = self.data_expanded[
            self.data_expanded['is_corrupted'] == 0
        ][self.key_col].unique()
        
        # 计算当前比例
        current_bad_count = len(bad_period_codes)
        current_good_count = len(good_period_codes)
        total_periods = len(all_period_codes)
        
        # 计算目标坏样本 period_code 数量
        target_bad_count = current_bad_count
        target_total_periods = target_bad_count / target_bad_ratio
        target_good_count = int(target_total_periods - target_bad_count)
        
        # 计算需要补充的好样本 period_code 数量
        supplement_count = max(0, target_good_count - current_good_count)
        
        if supplement_count == 0:
            current_ratio = current_bad_count / total_periods
            print(f"当前坏样本 period_code 比例: {current_ratio:.2%}, 已达到目标比例 {target_bad_ratio:.0%}")
            return self.data_expanded
        
        current_ratio = current_bad_count / total_periods
        print(f"目前好样本 period_code 数量: {current_good_count}")
        print(f"目前总样本 period_code 数量: {total_periods}")
        print(f"当前坏样本 period_code 比例: {current_ratio:.2%}")
        print(f"目标坏样本 period_code 比例: {target_bad_ratio:.0%}")
        print(f"需要补充 {supplement_count} 个好样本 period_code")
        
        # 复制好样本 period_code 并修改 key_col
        np.random.seed(self.random_seed)
        supplement_samples = []
        
        # 随机选择要复制的 period_code
        selected_codes = np.random.choice(good_period_codes, size=supplement_count, replace=True)
        
        # 复制样本并修改 period_code
        for i, period_code in enumerate(selected_codes):
            # 获取原始样本
            original_samples = self.data_expanded[
                (self.data_expanded[self.key_col] == period_code) &
                (self.data_expanded['is_corrupted'] == 0)
            ].copy()
            
            # 创建新的 period_code
            new_period_code = f"{period_code}_COPY{i+1}"
            original_samples[self.key_col] = new_period_code
            
            # 添加到补充样本列表
            supplement_samples.append(original_samples)
        
        # 合并所有补充样本
        if supplement_samples:
            supplement_df = pd.concat(supplement_samples)
            supplement_df.reset_index(drop=True, inplace=True)
            
            # 将补充样本添加到数据中
            self.data_expanded = pd.concat([self.data_expanded, supplement_df], ignore_index=True)
            
            # 更新统计信息
            new_good_count = current_good_count + supplement_count
            new_total = new_good_count + current_bad_count
            new_ratio = current_bad_count / new_total
            
            print(f"补充后坏样本 period_code 比例: {new_ratio:.2%}")
        
        return self.data_expanded