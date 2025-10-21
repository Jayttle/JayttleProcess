import pymysql
import functools
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import time
import json
from datetime import datetime, timedelta
from typing import Union, Optional

class SQLUseType:
    def __init__(self, SQL_config_path: str = None) -> None:
        self.SQL_CONFIG: dict = {}
        if SQL_config_path is not None:
            self.load_SQLConfig(SQL_config_path)
        
    def load_SQLConfig(self, SQL_config_path: str) -> None:
        try:
            with open(SQL_config_path, 'r') as file:
                data = json.load(file)
                
            SQL_config = data.get('SQL_tianmeng_config', {})
            self.SQL_CONFIG['host'] = SQL_config.get('host')
            self.SQL_CONFIG['user']  = SQL_config.get('user')
            self.SQL_CONFIG['password']  = SQL_config.get('password')
            self.SQL_CONFIG['database'] = SQL_config.get('database')

            if not all([self.SQL_CONFIG.get('host'), self.SQL_CONFIG.get('user'), self.SQL_CONFIG.get('password'), self.SQL_CONFIG.get('database')]):
                print("警告:SQL 配置中的某些信息缺失。")
        
        except FileNotFoundError:
            print(f"文件 {SQL_config_path} 未找到。")
        except json.JSONDecodeError:
            print("文件内容不是有效的 JSON 格式。")
        except Exception as e:
            print(f"发生错误：{e}")

    def input_emailInfo(self, host: str, user: str, password: str, database: str):
        self.SQL_CONFIG['host'] = host
        self.SQL_CONFIG['user']  = user
        self.SQL_CONFIG['password']  = password
        self.SQL_CONFIG['database'] = database


    def check_SQLInfo(self) -> None:
        print('-----check------')
        print(f"Host: {self.SQL_CONFIG.get('host')}")
        print(f"User: {self.SQL_CONFIG.get('user')}")
        print(f"Password: {self.SQL_CONFIG.get('password')}")
        print(f"Database: {self.SQL_CONFIG.get('database')}")


    def execute_sql(self, sql_statement: str) -> Union[str, list[tuple]]:
        # 建立数据库连接
        conn = pymysql.connect(**self.SQL_CONFIG)
        cursor = conn.cursor()
        
        try:
            # 执行输入的 SQL 语句
            cursor.execute(sql_statement)
            
            # 如果是查询语句，则返回查询结果
            if sql_statement.strip().upper().startswith("SELECT"):
                results = cursor.fetchall()
                return results
            else:
                # 提交更改
                conn.commit()
                return "SQL statement executed successfully!"

        except Exception as e:
            # 发生错误时回滚
            conn.rollback()
            return "Error executing SQL statement: " + str(e)

        finally:
            # 关闭游标和数据库连接
            cursor.close()
            conn.close()

    def execute_sql_and_save_to_txt(self, sql_statement: str, file_path: str):
        # 建立数据库连接
        conn = pymysql.connect(**self.SQL_CONFIG)
        cursor = conn.cursor()
        
        try:
            # 执行输入的 SQL 语句
            cursor.execute(sql_statement)
            
            # 如果是查询语句，则将查询结果写入到 txt 文件中
            if sql_statement.strip().upper().startswith("SELECT"):
                results = cursor.fetchall()
                with open(file_path, 'w') as f:
                    for row in results:
                        f.write(','.join(map(str, row)) + '\n')
                return "Query executed successfully. Results saved to " + file_path
            else:
                # 提交更改
                conn.commit()
                return "SQL statement executed successfully!"

        except Exception as e:
            # 发生错误时回滚
            conn.rollback()
            return "Error executing SQL statement: " + str(e)

        finally:
            # 关闭游标和数据库连接
            cursor.close()
            conn.close()

    
    def get_min_max_time(self, listName: str) -> tuple:
        # 查询 Time 列的最小值和最大值
        query = "SELECT MIN(Time) AS min_time, MAX(Time) AS max_time FROM {0};".format(listName)
        conn = pymysql.connect(**self.SQL_CONFIG)
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            result = cursor.fetchone()
            return result
        except Exception as e:
            print("Error executing SQL statement:", e)
            return None
        finally:
            cursor.close()
            conn.close()

    def query_time_difference(self, listName: str, StartTime: datetime, EndTime: datetime) -> tuple:
        # 构建带有参数的查询语句
        sql_statement = """
        WITH TimeDiffCTE AS (
            SELECT
                time,
                LAG(time) OVER (ORDER BY time) AS PreviousTime,
                TIMESTAMPDIFF(SECOND, LAG(time) OVER (ORDER BY time), time) AS TimeDifference
            FROM
                {0}
            WHERE
                time >= '{1}' AND time <= '{2}'
        )
        SELECT
            PreviousTime,
            time AS CurrentTime,
            TimeDifference
        FROM
            TimeDiffCTE
        WHERE
            (TimeDifference > 100 OR PreviousTime IS NULL)
            AND PreviousTime IS NOT NULL 
        ORDER BY
            time ASC;
        """.format(listName, StartTime, EndTime)

        # 执行 SQL 查询
        conn = pymysql.connect(**self.SQL_CONFIG)
        cursor = conn.cursor()
        try:
            cursor.execute(sql_statement)
            results = cursor.fetchall()  # 获取查询结果
            return results  # 返回结果
        except Exception as e:
            print("Error executing SQL statement:", e)
            return None
        finally:
            cursor.close()
            conn.close()
    
    def count_records_in_table(self, table_name: str) -> int:
        """查看数据库中的表有多少个数据"""
        # 建立数据库连接
        conn = pymysql.connect(**self.SQL_CONFIG)
        cursor = conn.cursor()

        try:
            # 构建 SQL 查询语句，统计表中的数据行数
            sql_statement = f"SELECT COUNT(*) FROM {table_name}"
            
            # 执行 SQL 查询
            cursor.execute(sql_statement)
            
            # 获取查询结果
            result = cursor.fetchone()  # fetchone() 用于获取单行结果
            if result:
                record_count = result[0]  # 查询结果是一个包含一个元素的 tuple，获取第一个元素即数据行数
                return record_count  # 返回数据行数

            else:
                return 0  # 如果结果为空，则返回 0 条数据

        except Exception as e:
            # 发生错误时回滚
            conn.rollback()
            raise e  # 将异常抛出，由调用者处理

        finally:
            # 关闭游标和数据库连接
            cursor.close()
            conn.close()

    def count_time_differences(self, tableName: list, startTime: datetime, stopTime: datetime) -> dict[float, int]:
        # 构造查询 SQL 语句
        sql_statement = f"SELECT Time FROM {tableName} WHERE Time >= %s AND Time <= %s"

        # 建立数据库连接
        conn = pymysql.connect(**self.SQL_CONFIG)
        cursor = conn.cursor()

        try:
            # 执行 SQL 查询
            cursor.execute(sql_statement, (startTime, stopTime))

            # 获取查询结果
            results = cursor.fetchall()

            # 计算相邻时间差并统计
            time_list = [row[0] for row in results]
            time_list.sort()  # 将时间列表排序

            # 计算相邻时间差
            time_diffs = [(time_list[i + 1] - time_list[i]).total_seconds() for i in range(len(time_list) - 1)]

            # 统计不同时间差的个数
            diff_count = {}
            for diff in time_diffs:
                diff_count[diff] = diff_count.get(diff, 0) + 1

            return diff_count

        except Exception as e:
            # 发生错误时回滚
            conn.rollback()
            print("Error executing SQL statement:", str(e))
            return None

        finally:
            # 关闭游标和数据库连接
            cursor.close()
            conn.close()


if __name__ == '__main__':
    config_path = r'C:\Users\32315\OneDrive\PyPackages\config.json'
    sql_use = SQLUseType(config_path)
    sql_use.check_SQLInfo()

    # 自定义时间段：2024年12月1日中午12点（1小时数据）
    start_time = datetime(2024, 12, 1, 12, 0, 0)  # 2024-12-01 12:00:00
    end_time = start_time + timedelta(hours=1)  # 2024-12-01 13:00:00
    
    # 格式化时间字符串
    start_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
    end_str = end_time.strftime('%Y-%m-%d %H:%M:%S')
    
    # 构建查询语句
    query = f"SELECT * FROM avr WHERE time >= '{start_str}' AND time < '{end_str}'"
    
    print(f"查询时间段: {start_str} 至 {end_str}")
    print(f"SQL查询语句: {query}")
    
    # 执行查询并保存到文件
    file_path = f'avr_data_{start_time.strftime("%Y%m%d%H%M%S")}.txt'
    result = sql_use.execute_sql_and_save_to_txt(query, file_path)
    
    print(f"数据已保存至: {file_path}")