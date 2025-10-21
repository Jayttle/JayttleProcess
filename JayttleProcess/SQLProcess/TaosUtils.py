import taosws
import numpy as np
import pandas as pd
import time
import json
from datetime import datetime, timedelta
from typing import Union, Optional
from config.tdengine_config import *
class TDengineUse:
    def __init__(self, config_path: str = None) -> None:
        self.CONFIG: dict = {}
        if config_path is not None:
            self.load_config(config_path)
        
    def load_config(self, config_path: str) -> None:
        try:
            with open(config_path, 'r') as file:
                data = json.load(file)
                
            config = data.get('TDengine_config', {})
            self.CONFIG['host'] = config.get('host')
            self.CONFIG['user'] = config.get('user')
            self.CONFIG['password'] = config.get('password')
            self.CONFIG['database'] = config.get('database')
            port = config.get('port', 6030)
            self.CONFIG['port'] = int(port)

        except FileNotFoundError:
            print(f"文件 {config_path} 未找到。")
        except json.JSONDecodeError:
            print("文件内容不是有效的 JSON 格式。文件内容不是有效的 JSON 格式。")
        except Exception as e:
            print(f"发生错误：{e}")

    def input_config(self, host: str, user: str, password: str, database: str, port: int = 6030):
        self.CONFIG['host'] = host
        self.CONFIG['user'] = user
        self.CONFIG['password'] = password
        self.CONFIG['database'] = database
        self.CONFIG['port'] = port

    def check_config(self) -> None:
        print('-----配置检查------')
        print(f"host: {self.CONFIG.get('host')}")
        print(f"user: {self.CONFIG.get('user')}")
        print(f"password: {self.CONFIG.get('password')}")
        print(f"database: {self.CONFIG.get('database')}")
        print(f"port: {self.CONFIG.get('port')}")

    def connect(self):
        """建立TDengine连接"""
        try:
            conn = taosws.connect(
                host=self.CONFIG['host'],
                user=self.CONFIG['user'],
                password=self.CONFIG['password'],
                port=self.CONFIG['port'],
                database=self.CONFIG['database']  # 添加database参数
            )
            return conn
        except Exception as e:
            print(f"连接TDengine失败: {e}")
            return None


    def execute_sql(self, sql_statement: str) -> Union[str, list[tuple]]:
        """执行SQL查询或命令"""
        conn = self.connect()
        if conn is None:
            return "连接失败"
            
        cursor = conn.cursor()
        
        try:
            cursor.execute(sql_statement)
            
            if sql_statement.strip().upper().startswith("SELECT"):
                results = cursor.fetchall()
                return results
            else:
                conn.commit()
                return "SQL语句执行成功"
                
        except Exception as e:
            conn.rollback()
            return f"执行SQL语句出错: {e}"
            
        finally:
            cursor.close()
            conn.close()


    def execute_sql_and_save_to_txt(self, sql_statement: str, file_path: str):
        """执行SQL查询并将结果保存到文本文件"""
        conn = self.connect()
        if conn is None:
            return "连接失败"
            
        cursor = conn.cursor()
        
        try:
            cursor.execute(sql_statement)
            
            if sql_statement.strip().upper().startswith("SELECT"):
                results = cursor.fetchall()
                with open(file_path, 'w') as f:
                    for row in results:
                        f.write(','.join(map(str, row)) + '\n')
                return f"查询执行成功，结果已保存到 {file_path}"
            else:
                conn.commit()
                return "SQL语句执行成功"
                
        except Exception as e:
            conn.rollback()
            return f"执行SQL语句出错: {e}"
            

    def get_min_max_time(self, table_name: str) -> tuple:
        """获取时间列的最小值和最大值"""
        query = f"SELECT MIN(ts) AS min_time, MAX(ts) AS max_time FROM {table_name}"
        result = self.execute_sql(query)
        return result[0] if isinstance(result, list) and len(result) > 0 else None

    def list_tables(self) -> list[str]:
        """列出数据库中的所有表"""
        result = self.execute_sql("SHOW TABLES")
        return [table[0] for table in result] if isinstance(result, list) else []

    def describe_table(self, table_name: str) -> Union[str, list[tuple]]:
        """查看表结构"""
        query = f"DESCRIBE {table_name}"
        return self.execute_sql(query)
    
    def create_database(self, database_name: str):
        """建立TDengine连接"""
        try:
            # 先连接到系统数据库创建目标数据库
            sys_conn = taosws.connect(
                host=self.CONFIG['host'],
                user=self.CONFIG['user'],
                password=self.CONFIG['password'],
                port=self.CONFIG['port']
            )
            sys_cursor = sys_conn.cursor()
            
            # 创建数据库（如果不存在）
            create_db_query = f"CREATE DATABASE IF NOT EXISTS {database_name}"
            sys_cursor.execute(create_db_query)
            print(f"数据库 '{database_name}' 创建成功或已存在")
            
            sys_cursor.close()
            sys_conn.close()
            
            # 连接到目标数据库
            conn = taosws.connect(
                host=self.CONFIG['host'],
                user=self.CONFIG['user'],
                password=self.CONFIG['password'],
                port=self.CONFIG['port'],
                database=f"{database_name}"  # 连接到新创建的数据库
            )
            return conn
        except Exception as e:
            print(f"连接TDengine失败: {e}")
            return None
    def create_table(self, table_name: str, columns: list) -> str:
        """创建TDengine表"""
        # TDengine创建表语法与MySQL不同
        column_defs = ", ".join(columns)
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_defs})"
        return self.execute_sql(sql)

    def create_stable(self, stable_name: str, columns: list, tags: list) -> str:
        """创建超级表"""
        column_defs = ", ".join(columns)
        tag_defs = ", ".join(tags)
        sql = f"CREATE STABLE IF NOT EXISTS {stable_name} ({column_defs}) TAGS ({tag_defs})"
        return self.execute_sql(sql)

    def create_super_tables(self):
        """使用全局变量动态创建所有超级表"""
        conn = self.connect()
        if conn is None:
            print("连接失败，无法创建超级表")
            return False
        try:
            cursor = conn.cursor()
            # 定义超级表配置
            super_tables = [
                ("nengyuan_real", REAL_DATA_FIELDS),
                ("nengyuan_events", RECIPE_EVENTS_FIELDS),
                ("nengyuan_period", PERIOD_DATA_FIELDS),
                ("nengyuan_recipe", RECIPE_DATA_FIELDS),
                ("nengyuan_baseline", BASELINE_DATA_FIELDS),
                ("nengyuan_predict", PREDICT_DATA_FIELDS),
                ("nengyuan_anomaly", ANOMALY_DATA_FILEDS)
            ]
            for table_name, fields in super_tables:
                # 从字段列表中移除标签字段
                columns = [f for f in fields if f != "device_name"]
                
                # 生成字段定义
                column_defs = []
                for field in columns:
                    # 获取字段类型，默认为NCHAR(100)
                    field_type = FIELD_TYPES.get(field, FIELD_TYPES["default"])
                    column_defs.append(f"{field} {field_type}")
                
                # 构建SQL语句
                sql = f"""
                CREATE STABLE IF NOT EXISTS {table_name} (
                    {", ".join(column_defs)}
                ) TAGS (device_name {FIELD_TYPES['device_name']})
                """
                # 执行SQL
                cursor.execute(sql)
                print(f"创建超级表 {table_name} 成功")
            
            cursor.close()
            print("所有超级表创建完成！")
            return True
            
        except Exception as e:
            print(f"创建超级表失败: {e}")
            return False
        finally:
            conn.close()

    def create_subtables(self):
        """为每个超表创建6个设备的子表"""
        conn = self.connect()
        if conn is None:
            print("连接失败，无法创建子表")
            return False
        try:
            cursor = conn.cursor()
            
            # 设备列表
            devices = ["A_HT", "B_HT", "TT1142", "TT1153", "HT", "TBL"]
            
            # 超表列表
            super_tables = [
                "nengyuan_real",
                "nengyuan_events", 
                "nengyuan_period",
                "nengyuan_recipe",
                "nengyuan_baseline",
                "nengyuan_predict",
                "nengyuan_anomaly",
            ]
            
            # 为每个超表创建每个设备的子表
            for stable in super_tables:
                for device in devices:
                    # 子表命名规则：超表名_设备名
                    subtable_name = f"{stable}_{device}"
                    
                    # 创建子表的SQL语句
                    sql = f"CREATE TABLE IF NOT EXISTS {subtable_name} USING {stable} TAGS ('{device}')"
                    
                    try:
                        cursor.execute(sql)
                        print(f"创建子表 {subtable_name} 成功")
                    except Exception as e:
                        print(f"创建子表 {subtable_name} 失败: {e}")
            
            cursor.close()
            print("所有子表创建完成！")
            return True
            
        except Exception as e:
            print(f"创建子表过程中出错: {e}")
            return False
        finally:
            conn.close()
    def batch_insert_real_data(self, data_df, device_name):
        """
        优化后的批量插入函数，使用一次性构建大SQL语句的方式
        
        参数:
            data_df: 聚合后的数据DataFrame
            device_name: 设备名称
        
        返回:
            插入是否成功
        """
        # 子表名
        subtable_name = f"nengyuan_real_{device_name}"
        
        # 获取字段列表（不包括device_name，因为它是标签）
        fields = [
            'datetime', 'recipename', 'module', 'module_task', 'shift', 'team', 'phase',
            'temperature', 'humidity', 'total_steam', 'steam_mafl', 'steam_flow',
            'steam_press_aft', 'steam_press_bef', 'proc_air_valve', 'proc_air_temp',
            'cyl_temp', 'tob_mafl', 'total_tob', 'total_energy', 'is_pushed'
        ]
        
        # 确保DataFrame中有所有需要的字段
        for field in fields:
            if field not in data_df.columns:
                data_df[field] = None
        
        # 只保留需要的字段
        data_df = data_df[fields]
        
        # 连接到数据库
        conn = self.connect()
        if conn is None:
            print("数据库连接失败")
            return False
        
        try:
            cursor = conn.cursor()
            
            # 生成VALUES字符串
            value_rows = []
            for _, row in data_df.iterrows():
                values = []
                for field in fields:
                    val = row[field]
                    
                    # 处理特殊值
                    if pd.isna(val):
                        values.append("NULL")
                    elif isinstance(val, (np.int64, np.int32, int)):
                        values.append(str(int(val)))
                    elif isinstance(val, (np.float64, float)):
                        values.append(str(float(val)))
                    elif isinstance(val, bool):
                        values.append("1" if val else "0")
                    elif isinstance(val, str):
                        # 转义单引号
                        val = val.replace("'", "''")
                        values.append(f"'{val}'")
                    elif isinstance(val, (datetime, pd.Timestamp)):
                        # 格式化为TDengine接受的格式
                        values.append(f"'{val.strftime('%Y-%m-%d %H:%M:%S')}'")
                    elif val is None:
                        values.append("NULL")
                    else:
                        values.append(f"'{str(val)}'")
                
                value_rows.append(f"({','.join(values)})")
            
            # 构建完整SQL
            columns_str = ",".join(fields)
            values_str = ",".join(value_rows)
            sql = f"INSERT INTO {subtable_name} ({columns_str}) VALUES {values_str}"
            
            # 执行插入
            cursor.execute(sql)
            print(f"成功批量插入 {len(data_df)} 条数据到 {subtable_name}")
            return True
            
        except Exception as e:
            print(f"批量插入到 {subtable_name} 失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            conn.close()
    
    def batch_insert_recipe_data(self, recipe_df, device_name):
        """
        将批次级别的数据插入到数据库
        
        参数:
            recipe_df: 批次级别的聚合数据
            device_name: 设备名称
        
        返回:
            插入是否成功
        """
        # 子表名
        subtable_name = f"nengyuan_recipe_{device_name}"
        
        # 获取字段列表
        fields = [
            'recipe_start_time', 'recipe_end_time', 'recipename', 'module', 'module_task', 
            'shift', 'team', 'temperature', 'humidity', 'total_steam', 'steam_mafl', 
            'steam_flow', 'steam_press_aft', 'steam_press_bef', 'proc_air_valve', 
            'proc_air_temp', 'cyl_temp', 'tob_mafl', 'total_tob', 'total_energy', 'is_pushed'
        ]
        
        # 确保DataFrame中有所有需要的字段
        for field in fields:
            if field not in recipe_df.columns:
                recipe_df[field] = None
        
        # 只保留需要的字段
        recipe_df = recipe_df[fields]
        
        # 连接到数据库
        conn = self.connect()
        if conn is None:
            print("数据库连接失败")
            return False
        
        try:
            cursor = conn.cursor()
            
            # 生成VALUES字符串
            value_rows = []
            for _, row in recipe_df.iterrows():
                values = []
                for field in fields:
                    val = row[field]
                    
                    # 处理特殊值
                    if pd.isna(val):
                        values.append("NULL")
                    elif isinstance(val, (np.int64, np.int32, int)):
                        values.append(str(int(val)))
                    elif isinstance(val, (np.float64, float)):
                        values.append(str(float(val)))
                    elif isinstance(val, bool):
                        values.append("1" if val else "0")
                    elif isinstance(val, str):
                        # 转义单引号
                        val = val.replace("'", "''")
                        values.append(f"'{val}'")
                    elif isinstance(val, (datetime, pd.Timestamp)):
                        # 格式化为TDengine接受的格式
                        values.append(f"'{val.strftime('%Y-%m-%d %H:%M:%S')}'")
                    elif val is None:
                        values.append("NULL")
                    else:
                        values.append(f"'{str(val)}'")
                
                value_rows.append(f"({','.join(values)})")
            
            # 构建完整SQL
            columns_str = ",".join(fields)
            values_str = ",".join(value_rows)
            sql = f"INSERT INTO {subtable_name} ({columns_str}) VALUES {values_str}"
            
            # 执行插入
            cursor.execute(sql)
            print(f"成功批量插入 {len(recipe_df)} 条批次数据到 {subtable_name}")
            return True
            
        except Exception as e:
            print(f"插入批次数据到 {subtable_name} 失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            conn.close()


    def batch_insert_period_data(self, recipe_df, device_name):
        """
        将批次级别的数据插入到数据库
        
        参数:
            recipe_df: 批次级别的聚合数据
            device_name: 设备名称
        
        返回:
            插入是否成功
        """
        # 子表名
        subtable_name = f"nengyuan_period_{device_name}"
        
        # 获取字段列表
        fields = [
            'period_start_time', 'period_end_time', 'period', 'recipename','module', 'module_task', 
            'shift', 'team', 'temperature', 'humidity', 'total_steam', 'steam_mafl', 
            'steam_flow', 'steam_press_aft', 'steam_press_bef', 'proc_air_valve', 
            'proc_air_temp', 'cyl_temp', 'tob_mafl', 'total_tob', 'total_energy', 'is_pushed'
        ]
        
        # 确保DataFrame中有所有需要的字段
        for field in fields:
            if field not in recipe_df.columns:
                recipe_df[field] = None
        
        # 只保留需要的字段
        recipe_df = recipe_df[fields]
        
        # 连接到数据库
        conn = self.connect()
        if conn is None:
            print("数据库连接失败")
            return False
        
        try:
            cursor = conn.cursor()
            
            # 生成VALUES字符串
            value_rows = []
            for _, row in recipe_df.iterrows():
                values = []
                for field in fields:
                    val = row[field]
                    
                    # 处理特殊值
                    if pd.isna(val):
                        values.append("NULL")
                    elif isinstance(val, (np.int64, np.int32, int)):
                        values.append(str(int(val)))
                    elif isinstance(val, (np.float64, float)):
                        values.append(str(float(val)))
                    elif isinstance(val, bool):
                        values.append("1" if val else "0")
                    elif isinstance(val, str):
                        # 转义单引号
                        val = val.replace("'", "''")
                        values.append(f"'{val}'")
                    elif isinstance(val, (datetime, pd.Timestamp)):
                        # 格式化为TDengine接受的格式
                        values.append(f"'{val.strftime('%Y-%m-%d %H:%M:%S')}'")
                    elif val is None:
                        values.append("NULL")
                    else:
                        values.append(f"'{str(val)}'")
                
                value_rows.append(f"({','.join(values)})")
            
            # 构建完整SQL
            columns_str = ",".join(fields)
            values_str = ",".join(value_rows)
            sql = f"INSERT INTO {subtable_name} ({columns_str}) VALUES {values_str}"
            
            # 执行插入
            cursor.execute(sql)
            print(f"成功批量插入 {len(value_rows)} 条批次数据到 {subtable_name}")
            return True
            
        except Exception as e:
            print(f"插入批次数据到 {subtable_name} 失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            conn.close()
    
    def batch_insert_predict_data(self, recipe_df, device_name):
        """
        将批次级别的数据插入到数据库
        
        参数:
            recipe_df: 批次级别的聚合数据
            device_name: 设备名称
        
        返回:
            插入是否成功
        """
        # 子表名
        subtable_name = f"nengyuan_predict_{device_name}"
        
        # 获取字段列表
        fields = [
            'record_time', 'module', 'total_steam',  'total_tob', 'total_energy', 'is_pushed'
        ]
        
        # 确保DataFrame中有所有需要的字段
        for field in fields:
            if field not in recipe_df.columns:
                recipe_df[field] = None
        
        # 只保留需要的字段
        recipe_df = recipe_df[fields]
        
        # 连接到数据库
        conn = self.connect()
        if conn is None:
            print("数据库连接失败")
            return False
        
        try:
            cursor = conn.cursor()
            
            # 生成VALUES字符串
            value_rows = []
            for _, row in recipe_df.iterrows():
                values = []
                for field in fields:
                    val = row[field]
                    
                    # 处理特殊值
                    if pd.isna(val):
                        values.append("NULL")
                    elif isinstance(val, (np.int64, np.int32, int)):
                        values.append(str(int(val)))
                    elif isinstance(val, (np.float64, float)):
                        values.append(str(float(val)))
                    elif isinstance(val, bool):
                        values.append("1" if val else "0")
                    elif isinstance(val, str):
                        # 转义单引号
                        val = val.replace("'", "''")
                        values.append(f"'{val}'")
                    elif isinstance(val, (datetime, pd.Timestamp)):
                        # 格式化为TDengine接受的格式
                        values.append(f"'{val.strftime('%Y-%m-%d %H:%M:%S')}'")
                    elif val is None:
                        values.append("NULL")
                    else:
                        values.append(f"'{str(val)}'")
                
                value_rows.append(f"({','.join(values)})")
            
            # 构建完整SQL
            columns_str = ",".join(fields)
            values_str = ",".join(value_rows)
            sql = f"INSERT INTO {subtable_name} ({columns_str}) VALUES {values_str}"
            
            # 执行插入
            cursor.execute(sql)
            print(f"成功批量插入 {len(value_rows)} 条批次数据到 {subtable_name}")
            return True
            
        except Exception as e:
            print(f"插入批次数据到 {subtable_name} 失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            conn.close()

    def batch_insert_baseline_data(self, baseline_df, device_name):
        """
        将基线数据插入到数据库中的 nengyuan_baseline 表
        
        参数:
            baseline_df: 包含基线数据的DataFrame
            device_name: 设备名称
        
        返回:
            插入是否成功
        """
        # 子表名
        subtable_name = f"nengyuan_baseline_{device_name}"
        
        # 获取字段列表（与表结构一致）
        fields = [
            'record_time', 'module',
            'duration_lower', 'duration_upper',
            'temperature_lower', 'temperature_upper',
            'humidity_lower', 'humidity_upper',
            'total_steam_lower', 'total_steam_upper',
            'steam_mafl_lower', 'steam_mafl_upper',
            'steam_flow_lower', 'steam_flow_upper',
            'steam_press_aft_lower', 'steam_press_aft_upper',
            'steam_press_bef_lower', 'steam_press_bef_upper',
            'proc_air_valve_lower', 'proc_air_valve_upper',
            'proc_air_temp_lower', 'proc_air_temp_upper',
            'cyl_temp_lower', 'cyl_temp_upper',
            'tob_mafl_lower', 'tob_mafl_upper',
            'total_tob_lower', 'total_tob_upper',
            'total_tob_lower', 'total_tob_upper',
            'total_energy_lower', 'total_energy_upper', 'baseline_mode', 'is_pushed'
        ]
        
        # 确保DataFrame中有所有需要的字段
        for field in fields:
            if field not in baseline_df.columns:
                baseline_df[field] = None
        
        # 只保留需要的字段
        baseline_df = baseline_df[fields]
        
        # 连接到数据库
        conn = self.connect()
        if conn is None:
            print("数据库连接失败")
            return False
        
        try:
            cursor = conn.cursor()
            
            # 生成VALUES字符串
            value_rows = []
            for _, row in baseline_df.iterrows():
                values = []
                for field in fields:
                    val = row[field]
                    
                    # 处理特殊值
                    if pd.isna(val):
                        values.append("NULL")
                    elif isinstance(val, (np.int64, np.int32, int)):
                        values.append(str(int(val)))
                    elif isinstance(val, (np.float64, float)):
                        values.append(str(float(val)))
                    elif isinstance(val, bool):
                        values.append("1" if val else "0")
                    elif isinstance(val, str):
                        # 转义单引号
                        val = val.replace("'", "''")
                        values.append(f"'{val}'")
                    elif isinstance(val, (datetime, pd.Timestamp)):
                        # 格式化为TDengine接受的格式
                        values.append(f"'{val.strftime('%Y-%m-%d %H:%M:%S')}'")
                    elif val is None:
                        values.append("NULL")
                    else:
                        values.append(f"'{str(val)}'")
                
                value_rows.append(f"({','.join(values)})")
            
            # 构建完整SQL
            columns_str = ",".join(fields)
            values_str = ",".join(value_rows)
            sql = f"INSERT INTO {subtable_name} ({columns_str}) VALUES {values_str}"
            
            # 执行插入
            cursor.execute(sql)
            print(f"成功批量插入 {len(value_rows)} 条基线数据到 {subtable_name}")
            return True
            
        except Exception as e:
            print(f"插入基线数据到 {subtable_name} 失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            conn.close()

    def batch_insert_anomaly_data(self, anomaly_df, device_name):
        """
        将基线数据插入到数据库中的 nengyuan_anomaly 表
        
        参数:
            anomaly_df: 包含基线数据的DataFrame
            device_name: 设备名称
        
        返回:
            插入是否成功
        """
        # 子表名
        subtable_name = f"nengyuan_anomaly_{device_name}"
        
        # 获取字段列表（与表结构一致）
        fields = [
                "record_time",              # 记录时间 
                "recipename",               # 批次号" 
                "module",                   # 模块
                "total_steam",              # 蒸汽累积量
                "total_tob",                # 物料累积量
                "total_energy",             # 电能累积量
                "anomaly_info",             # 异常信息
                "is_pushed"
        ]
        
        # 确保DataFrame中有所有需要的字段
        for field in fields:
            if field not in anomaly_df.columns:
                anomaly_df[field] = None
        
        # 只保留需要的字段
        anomaly_df = anomaly_df[fields]
        
        # 连接到数据库
        conn = self.connect()
        if conn is None:
            print("数据库连接失败")
            return False
        
        try:
            cursor = conn.cursor()
            
            # 生成VALUES字符串
            value_rows = []
            for _, row in anomaly_df.iterrows():
                values = []
                for field in fields:
                    val = row[field]
                    
                    # 处理特殊值
                    if pd.isna(val):
                        values.append("NULL")
                    elif isinstance(val, (np.int64, np.int32, int)):
                        values.append(str(int(val)))
                    elif isinstance(val, (np.float64, float)):
                        values.append(str(float(val)))
                    elif isinstance(val, bool):
                        values.append("1" if val else "0")
                    elif isinstance(val, str):
                        # 转义单引号
                        val = val.replace("'", "''")
                        values.append(f"'{val}'")
                    elif isinstance(val, (datetime, pd.Timestamp)):
                        # 格式化为TDengine接受的格式
                        values.append(f"'{val.strftime('%Y-%m-%d %H:%M:%S')}'")
                    elif val is None:
                        values.append("NULL")
                    else:
                        values.append(f"'{str(val)}'")
                
                value_rows.append(f"({','.join(values)})")
            
            # 构建完整SQL
            columns_str = ",".join(fields)
            values_str = ",".join(value_rows)
            sql = f"INSERT INTO {subtable_name} ({columns_str}) VALUES {values_str}"
            
            # 执行插入
            cursor.execute(sql)
            print(f"成功批量插入 {len(value_rows)} 条基线数据到 {subtable_name}")
            return True
            
        except Exception as e:
            print(f"插入基线数据到 {subtable_name} 失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            conn.close()
    def execute_sql_and_return_dataframe(self, sql_statement: str):
        """执行SQL查询并返回DataFrame"""
        conn = self.connect()
        if conn is None:
            return "连接失败"
            
        cursor = conn.cursor()
        
        try:
            cursor.execute(sql_statement)
            
            # 如果是查询语句，则将结果转换为DataFrame
            if sql_statement.strip().upper().startswith("SELECT"):
                # 获取列名
                column_names = [desc[0] for desc in cursor.description]
                
                # 获取所有数据
                results = cursor.fetchall()
                
                # 转换为DataFrame
                df = pd.DataFrame(results, columns=column_names)
                
                return df
            else:
                # 提交更改
                conn.commit()
                return "SQL语句执行成功"
                
        except Exception as e:
            # 发生错误时回滚
            conn.rollback()
            return f"执行SQL语句出错: {e}"
            
        finally:
            # 关闭游标和数据库连接
            cursor.close()
            conn.close()
    def nengyuan_select_sql_execute(self, start_time: datetime, end_time: datetime, column_names: list) -> pd.DataFrame:
        """
        分批执行SQL查询以避免数据库压力过大
        
        Args:
            start_time (str): 查询开始时间，格式为 'YYYY-MM-DD HH:MM:SS'
            end_time (str): 查询结束时间，格式为 'YYYY-MM-DD HH:MM:SS'
            column_names (list): 需要查询的列名列表
                
        Returns:
            pd.DataFrame: 合并后的查询结果
        """
        # 检查时间范围是否有效
        if start_time >= end_time:
            raise ValueError("开始时间必须早于结束时间")
            
        # 初始化结果列表
        all_results = []
        
        # 以30分钟为间隔进行分割
        current_start = start_time
        interval = timedelta(minutes=30)
        
        print(f"开始分批执行查询，时间范围: {start_time} 到 {end_time}")
        batch_count = 0
        while current_start < end_time:
            # 计算当前批次的结束时间
            current_end = min(current_start + interval, end_time)
            current_start_str = current_start.strftime('%Y-%m-%d %H:%M:%S')
            current_end_str = current_end.strftime('%Y-%m-%d %H:%M:%S')
            
            # 构建列名字符串
            column_str = ",".join([f"'{col}'" for col in column_names])
            
            # 构建完整的SQL查询
            sql = f"""
            SELECT * FROM ts_kv 
            WHERE device_id = '100a995b-984e-f26d-075a-4fe1b48c93b5' 
            AND k IN ({column_str})
            AND ts >= '{current_start_str}' AND ts <= '{current_end_str}';
            """
            
            print(f"执行批次 {batch_count + 1}: {current_start_str} 到 {current_end_str}")
            
            # 执行SQL查询
            result = self.execute_sql_and_return_dataframe(sql)
            
            # 如果查询成功，将结果添加到列表中
            if isinstance(result, pd.DataFrame):
                all_results.append(result)
                print(f"  成功获取 {len(result)} 条记录")
            else:
                print(f"  查询失败: {result}")
            
            # 更新下一批次的开始时间
            current_start = current_end
            batch_count += 1
            
            # 添加短暂延迟以减轻数据库压力
            time.sleep(0.1)
        
        # 合并所有结果
        if all_results:
            final_result = pd.concat(all_results, ignore_index=True)
            print(f"查询完成，总共执行 {batch_count} 个批次，获取 {len(final_result)} 条记录")
            return final_result
        else:
            print("查询完成，但未获取到任何数据")
            return pd.DataFrame()
            
    def create_tables(self):
        """创建三张数据表（ZS12、HT、TBL）"""
        conn = self.connect()
        if not conn:
            print("无法创建表：数据库连接失败")
            return False

        try:
            cursor = conn.cursor()
            
            # 创建ZS12表
            zs12_table_sql = """
            CREATE TABLE IF NOT EXISTS zs12_data (
                `datetime` TIMESTAMP,
                `recipename` NCHAR(100),
                `module` NCHAR(50),
                `module_task` NCHAR(50),
                `shift` NCHAR(20),
                `team` NCHAR(20),
                `A_HT_steam_total_blend` FLOAT,
                `A_HT_phase` NCHAR(20),
                `A_HT_SteamMaFl` FLOAT,
                `A_HT_SteamPressAft` FLOAT,
                `A_HT_SteamPressBef` FLOAT,
                `TT1142_steam_total_blend` FLOAT,
                `TT1142_phase` NCHAR(20),
                `TT1142_Steam_flow` FLOAT,
                `TT1142_SteamMaFl` FLOAT,
                `TT1142_ProcAirValve` FLOAT,
                `TT1142_ProcAirTemp` FLOAT,
                `TT1142_CylTemp` FLOAT,
                `A_HT_TT1142_TobMaFl` FLOAT,
                `A_HT_TT1142_TotalTob` FLOAT,
                `B_HT_steam_total_blend` FLOAT,
                `B_HT_phase` NCHAR(20),
                `B_HT_SteamMaFl` FLOAT,
                `B_HT_SteamPressAft` FLOAT,
                `B_HT_SteamPressBef` FLOAT,
                `TT1153_Steam_total_2` FLOAT,
                `TT1153_phase` NCHAR(20),
                `TT1153_Steam_flow` FLOAT,
                `TT1153_SteamMaFl` FLOAT,
                `TT1153_ProcAirValve` FLOAT,
                `TT1153_ProcAirTemp` FLOAT,
                `TT1153_CylTemp` FLOAT,
                `B_HT_TT1153_TobMaFl` FLOAT,
                `B_HT_TT1153_TotalTob` FLOAT,
                `Temperature_Kld_Area` FLOAT,
                `Humidity_Kld_Area` FLOAT,
                `line_energy_total` FLOAT,
                `line_energy_total_blend` FLOAT
            ) 
            TAGS (dummy_tag BOOL);
            """
            
            # 创建HT表
            ht_table_sql = """
            CREATE TABLE IF NOT EXISTS ht_data (
                `datetime` TIMESTAMP,
                `HT_recipename` NCHAR(100),
                `HT_module` NCHAR(50),
                `HT_module_task` NCHAR(50),
                `HT_shift` NCHAR(20),
                `HT_team` NCHAR(20),
                `HT_steam_total` FLOAT,
                `HT_steam_total_blend` FLOAT,
                `HT_phase` NCHAR(20),
                `HT_temperature` FLOAT,
                `HT_humidity` FLOAT,
                `HT_SteamMaFI_CV` FLOAT,
                `HT_SteamPressAft` FLOAT,
                `HT_SteamPressBef` FLOAT,
                `HT_CurrentFlow` FLOAT,
                `HT_CurrentCumulativeFlow` FLOAT,
                `HT_energy_total` FLOAT,
                `HT_energy_total_blend` FLOAT
            ) 
            TAGS (dummy_tag BOOL);
            """
            
            # 创建TBL表
            tbl_table_sql = """
            CREATE TABLE IF NOT EXISTS tbl_data (
                `datetime` TIMESTAMP,
                `TBL_recipename` NCHAR(100),
                `TBL_module` NCHAR(50),
                `TBL_module_task` NCHAR(50),
                `TBL_shift` NCHAR(20),
                `TBL_team` NCHAR(20),
                `TBL_steam_flow` FLOAT,
                `TBL_steam_total` FLOAT,
                `TBL_steam_total_blend` FLOAT,
                `TBL_phase` NCHAR(20),
                `TBL_temperature` FLOAT,
                `TBL_humidity` FLOAT,
                `TBL_ProcAirTemp` FLOAT,
                `TBL_SteamMafl` FLOAT,
                `TBL_ProcAirFlap_CV` FLOAT,
                `TBL_SteamMafl_CV` FLOAT,
                `TBL_ProcAirTemp_CV` FLOAT,
                `TBL_TobMaFl` FLOAT,
                `TBL_TotalTob` FLOAT,
                `TBL_energy_total` FLOAT,
                `TBL_energy_total_blend` FLOAT
            ) 
            TAGS (dummy_tag BOOL);
            """
            
            # 执行建表语句
            cursor.execute(zs12_table_sql)
            cursor.execute(ht_table_sql)
            cursor.execute(tbl_table_sql)
            
            # 创建具体子表（TDengine要求必须基于超级表创建子表）
            cursor.execute("CREATE TABLE IF NOT EXISTS zs12_child USING zs12_data TAGS (true);")
            cursor.execute("CREATE TABLE IF NOT EXISTS ht_child USING ht_data TAGS (true);")
            cursor.execute("CREATE TABLE IF NOT EXISTS tbl_child USING tbl_data TAGS (true);")
            
            print("三张数据表创建成功")
            return True
            
        except Exception as e:
            print(f"建表过程中发生错误: {e}")
            return False
        finally:
            conn.close()

    def ensure_child_tables(self):
        """确保子表存在，不存在则创建"""
        conn = self.connect()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS zs12_child 
            USING zs12_data TAGS (true)
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS ht_child 
            USING ht_data TAGS (true)
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS tbl_child 
            USING tbl_data TAGS (true)
            """)
            print("子表校验/创建完成")
            return True
        except Exception as e:
            print(f"子表创建失败: {e}")
            return False
        finally:
            conn.close()
    
    def batch_insert(self, df, table_name, columns=None):
        """
        批量插入数据到指定子表 (兼容TDengine语法)
        :param df: 待插入的DataFrame
        :param table_name: 目标表名
        :param columns: 指定列顺序
        """
        if df.empty:
            print(f"警告: 尝试插入空DataFrame到 {table_name}")
            return False
        
        conn = self.connect()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            
            # 获取有效列
            cols = columns if columns else df.columns.tolist()
            all_cols = self.get_table_columns(table_name)
            valid_cols = [col for col in cols if col in all_cols]
            
            # 生成VALUES字符串
            value_rows = []
            for _, row in df.iterrows():
                values = []
                for col in valid_cols:
                    val = row[col]
                    
                    # 处理特殊值
                    if pd.isna(val):
                        values.append("NULL")
                    elif isinstance(val, (np.int64, np.int32, int)):
                        values.append(str(int(val)))
                    elif isinstance(val, (np.float64, float)):
                        values.append(str(float(val)))
                    elif isinstance(val, str):
                        # 转义单引号
                        val = val.replace("'", "''")
                        values.append(f"'{val}'")
                    elif isinstance(val, (datetime, pd.Timestamp)):
                        values.append(f"'{val.strftime('%Y-%m-%d %H:%M:%S')}'")
                    else:
                        values.append(f"'{str(val)}'")
                
                value_rows.append(f"({','.join(values)})")
            
            # 构建完整SQL
            columns_str = ",".join(valid_cols)
            values_str = ",".join(value_rows)
            sql = f"INSERT INTO {table_name} ({columns_str}) VALUES {values_str}"
            
            # 执行插入
            cursor.execute(sql)
            print(f"成功批量插入 {len(df)} 条数据到 {table_name}")
            return True
            
        except Exception as e:
            print(f"批量插入到 {table_name} 失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            conn.close()
    
    def get_table_columns(self, table_name):
        """获取指定表的列名列表"""
        conn = self.connect()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            cursor.execute(f"DESCRIBE {table_name}")
            result = cursor.fetchall()
            return [row[0] for row in result if row[0] not in ["dummy_tag", "ts"]]
        except:
            return []
        finally:
            conn.close()