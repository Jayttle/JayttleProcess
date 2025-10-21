NENGYUAN_PERIOD_ANALYSIS_SQL_SCRIPT ="""
SELECT 
	TODAY() as record_date,
    device_name,
	module, 
	period,
	COUNT(*) AS period_count,
	AVG(duration_seconds) AS duration_seconds,
   	SUM(total_steam * duration_seconds) / SUM(duration_seconds) AS total_steam,
    SUM(total_tob * duration_seconds) / SUM(duration_seconds) AS total_tob,
    SUM(total_energy * duration_seconds) / SUM(duration_seconds) AS total_energy,
    SUM(temperature * duration_seconds) / SUM(duration_seconds) AS temperature,
    SUM(humidity * duration_seconds) / SUM(duration_seconds) AS humidity,
    SUM(steam_mafl * duration_seconds) / SUM(duration_seconds) AS steam_mafl,
    SUM(steam_flow * duration_seconds) / SUM(duration_seconds) AS steam_flow,
    SUM(steam_press_aft * duration_seconds) / SUM(duration_seconds) AS steam_press_aft,
    SUM(steam_press_bef * duration_seconds) / SUM(duration_seconds) AS steam_press_bef,
    SUM(proc_air_valve * duration_seconds) / SUM(duration_seconds) AS proc_air_valve,
    SUM(proc_air_temp * duration_seconds) / SUM(duration_seconds) AS proc_air_temp,
    SUM(cyl_temp * duration_seconds) / SUM(duration_seconds) AS cyl_temp,
    SUM(tob_mafl * duration_seconds) / SUM(duration_seconds) AS tob_mafl 
FROM (
	SELECT 
    	device_name,
        recipename,
        module,
        period,
        sum(duration_seconds) AS duration_seconds,
        SUM(total_steam * duration_seconds) / SUM(duration_seconds) AS total_steam,
        SUM(total_tob * duration_seconds) / SUM(duration_seconds) AS total_tob,
        SUM(total_energy * duration_seconds) / SUM(duration_seconds) AS total_energy,
        SUM(temperature * duration_seconds) / SUM(duration_seconds) AS temperature,
        SUM(humidity * duration_seconds) / SUM(duration_seconds) AS humidity,
        SUM(steam_mafl * duration_seconds) / SUM(duration_seconds) AS steam_mafl,
        SUM(steam_flow * duration_seconds) / SUM(duration_seconds) AS steam_flow,
        SUM(steam_press_aft * duration_seconds) / SUM(duration_seconds) AS steam_press_aft,
        SUM(steam_press_bef * duration_seconds) / SUM(duration_seconds) AS steam_press_bef,
        SUM(proc_air_valve * duration_seconds) / SUM(duration_seconds) AS proc_air_valve,
        SUM(proc_air_temp * duration_seconds) / SUM(duration_seconds) AS proc_air_temp,
        SUM(cyl_temp * duration_seconds) / SUM(duration_seconds) AS cyl_temp,
        SUM(tob_mafl * duration_seconds) / SUM(duration_seconds) AS tob_mafl 
	FROM (
		SELECT
			device_name,
		    recipename,
		    CASE 
		        WHEN module_task LIKE '%01' 
		            THEN CONCAT(module, 'A')
		        ELSE CONCAT(module, 'B')
		    END AS module,
		    period,
		    timediff(period_end_time, period_start_time, 1s) AS duration_seconds,
		    total_steam,
		    total_tob,
		    total_energy,
		    temperature,
		    humidity,
		    steam_mafl,
		    steam_flow,
		    steam_press_aft,
		    steam_press_bef,
		    proc_air_valve,
		    proc_air_temp,
		    cyl_temp,
		    tob_mafl
		FROM things_energy.nengyuan_period
	)
	AS first_agg
	GROUP BY device_name, recipename, module, period
)
AS final_agg
GROUP BY device_name, module, period
ORDER BY device_name, module, period
"""

NENGYUAN_PERIOD_ANALYSIS_COLUMNS_MAPPING = {
    "record_date": "记录日期",
    "device_name": "设备名",
    "module": "牌号",
    "period": "阶段",
    "period_count": "阶段累计数",
    "duration_seconds": "持续时间",
    "total_steam": "蒸汽能耗",
    "total_tob": "烟丝物料总量",
    "total_energy": "电能能耗",
    "temperature": "温度",
    "humidity": "湿度",
    "steam_mafl": "蒸汽流量阀门开度实际值",
    "steam_flow": "蒸汽流量",
    "steam_press_aft": "蒸汽压力(阀后)",
    "steam_press_bef": "蒸汽压力(阀前)",
    "proc_air_valve": "风门开度实际值",
    "proc_air_temp": "热风温度",
    "cyl_temp": "筒壁温度",
    "tob_mafl": "烟丝物料流量"
}
# NENGYUAN_PERIOD_ANALYSIS_SQL_SCRIPT 数据样例：
# record_date	module	period	period_count	duration_seconds	total_steam	total_tob	total_energy	temperature	humidity	steam_mafl	steam_flow	steam_press_aft	steam_press_bef	proc_air_valve	proc_air_temp	cyl_temp	tob_mafl
# 0	2025-09-28	D38A	interrupt	1	1182.0	0.000000	0.000000	3.142149	29.231479	69.028360	NaN	NaN	None	None	51.404399	32.417048	None	NaN
# 1	2025-09-28	D38A	preheat	1	1850.0	111.902760	4.412586	12.325778	29.416398	67.818481	NaN	261.563449	None	None	64.154269	63.504850	None	626.993726
# 2	2025-09-28	D38A	production	1	4073.0	709.147217	6138.464844	39.169998	29.609278	66.793137	85.139107	630.287292	None	None	60.000000	67.792961	None	5978.166016
# 3	2025-09-28	D38B	preheat	1	492.0	0.763522	3.700613	2.276931	29.793759	65.170080	NaN	68.594067	None	None	60.000000	71.137386	None	329.574748
# 4	2025-09-28	D38B	production	1	4069.0	616.354980	6140.649414	38.220001	29.777550	65.134293	84.675140	552.116150	None	None	60.000000	67.984169	None	5987.319336

NENGYUAN_DEVICE_MODULE_ANALYSIS_SQL_SCRIPT = """
SELECT
    module_with_suffix as 牌号,
    count(*) AS 个数,
    AVG(CASE WHEN device_name = 'A_HT' THEN total_steam END) AS A路HT回潮机,
    AVG(CASE WHEN device_name = 'B_HT' THEN total_steam END) AS B路HT回潮机,
    AVG(CASE WHEN device_name = 'TT1142' THEN total_steam END) AS A路薄板式烘丝机,
    AVG(CASE WHEN device_name = 'TT1153' THEN total_steam END) AS B路薄板式烘丝机,
    AVG(CASE WHEN device_name = 'HT' THEN total_steam END) AS 烟片HT回潮机,
    AVG(CASE WHEN device_name = 'TBL' THEN total_steam END) AS 松散回潮机,
    sum(total_steam) AS 小计
FROM (
    SELECT
        device_name,
        CASE 
            WHEN SUBSTR(module_task, -2, 2) = '01' THEN CONCAT(module, 'A') 
            ELSE CONCAT(module, 'B') 
        END AS module_with_suffix,
        total_steam
    FROM things_energy.nengyuan_recipe
) AS subquery
GROUP BY module_with_suffix
"""

# 4.牌号生产平均用能表格查询结果
# 牌号	个数	A_HT	B_HT	A路烘丝	B路烘丝	小计
# D19	7	162.19	636.31	174.01	622.81	1595.32
# D28	5	206.85	917.52	224.03	840.74	2189.14
# D29	1	201.38	1019.43	223.45	883.99	2328.25
# D38	43	196.26	765.47	208.26	710.2	1880.19
# D98	4	204.18	704.19	217.04	663.64	1789.05

NENGYUAN_BASELINE_SQL_SCRIPT ="""
SELECT 
    module AS module,
    device_name AS device_name,
    LAST(record_time) AS record_time,
    LAST(total_steam_lower) AS total_steam_lower,
    LAST(total_steam_upper) AS total_steam_upper,
    LAST(duration_lower) AS duration_lower,
    LAST(duration_upper) AS duration_upper,
    LAST(temperature_lower) AS temperature_lower,
    LAST(temperature_upper) AS temperature_upper,
    LAST(humidity_lower) AS humidity_lower,
    LAST(humidity_upper) AS humidity_upper,
    LAST(steam_mafl_lower) AS steam_mafl_lower,
    LAST(steam_mafl_upper) AS steam_mafl_upper,
    LAST(steam_flow_lower) AS steam_flow_lower,
    LAST(steam_flow_upper) AS steam_flow_upper,
    LAST(steam_press_aft_lower) AS steam_press_aft_lower,
    LAST(steam_press_aft_upper) AS steam_press_aft_upper,
    LAST(steam_press_bef_lower) AS steam_press_bef_lower,
    LAST(steam_press_bef_upper) AS steam_press_bef_upper,
    LAST(proc_air_valve_lower) AS proc_air_valve_lower,
    LAST(proc_air_valve_upper) AS proc_air_valve_upper,
    LAST(proc_air_temp_lower) AS proc_air_temp_lower,
    LAST(proc_air_temp_upper) AS proc_air_temp_upper,
    LAST(cyl_temp_lower) AS cyl_temp_lower,
    LAST(cyl_temp_upper) AS cyl_temp_upper,
    LAST(tob_mafl_lower) AS tob_mafl_lower,
    LAST(tob_mafl_upper) AS tob_mafl_upper,
    LAST(total_tob_lower) AS total_tob_lower,
    LAST(total_tob_upper) AS total_tob_upper,
    LAST(total_energy_lower) AS total_energy_lower,
    LAST(total_energy_upper) AS total_energy_upper
FROM things_energy.nengyuan_baseline 
GROUP BY module, device_name
order by device_name, module
"""
# """
# SELECT 
#     module AS 牌号,
#     device_name AS 设备,
#     LAST(record_time) AS 记录时间,
#     LAST(total_steam_lower) AS 总蒸汽量下限,
#     LAST(total_steam_upper) AS 总蒸汽量上限,
#     LAST(duration_lower) AS 持续时间下限,
#     LAST(duration_upper) AS 持续时间上限,
#     LAST(temperature_lower) AS 温度下限,
#     LAST(temperature_upper) AS 温度上限,
#     LAST(humidity_lower) AS 湿度下限,
#     LAST(humidity_upper) AS 湿度上限,
#     LAST(steam_mafl_lower) AS 蒸汽阀门开度下限,
#     LAST(steam_mafl_upper) AS 蒸汽阀门开度上限,
#     LAST(steam_flow_lower) AS 蒸汽流量下限,
#     LAST(steam_flow_upper) AS 蒸汽流量上限,
#     LAST(steam_press_aft_lower) AS 蒸汽阀后压力下限,
#     LAST(steam_press_aft_upper) AS 蒸汽阀后压力上限,
#     LAST(steam_press_bef_lower) AS 蒸汽阀前压力下限,
#     LAST(steam_press_bef_upper) AS 蒸汽阀前压力上限,
#     LAST(proc_air_valve_lower) AS 风门开度下限,
#     LAST(proc_air_valve_upper) AS 风门开度上限,
#     LAST(proc_air_temp_lower) AS 热风温度下限,
#     LAST(proc_air_temp_upper) AS 热风温度上限,
#     LAST(cyl_temp_lower) AS 筒壁温度下限,
#     LAST(cyl_temp_upper) AS 筒壁温度上限,
#     LAST(tob_mafl_lower) AS 烟丝物料流量下限,
#     LAST(tob_mafl_upper) AS 烟丝物料流量上限,
#     LAST(total_tob_lower) AS 烟丝物料累积量下限,
#     LAST(total_tob_upper) AS 烟丝物料累积量上限,
#     LAST(total_energy_lower) AS 总电量下限,
#     LAST(total_energy_upper) AS 总电量上限
# FROM things_energy.nengyuan_baseline 
# GROUP BY module, device_name
# """

# 牌号	设备	记录时间	总蒸汽量下限	总蒸汽量上限	持续时间下限	持续时间上限	温度下限	温度上限	湿度下限	湿度上限	蒸汽阀门开度下限	蒸汽阀门开度上限	蒸汽流量下限	蒸汽流量上限	蒸汽阀后压力下限	蒸汽阀后压力上限	蒸汽阀前压力下限	蒸汽阀前压力上限	风门开度下限	风门开度上限	热风温度下限	热风温度上限	筒壁温度下限	筒壁温度上限	烟丝物料流量下限	烟丝物料流量上限	烟丝物料累积量下限	烟丝物料累积量上限	总电量下限	总电量上限
# D38B	HT	2025-10-09 16:47:53.000	294.50208	301.90588	4560	5022	30.526836	31.423843	64.059746	66.211945	32.979557	33.518803			0.74406785	0.80609983	6.7370768	6.829262							6676.7627	6688.077	6676.1094	6698.3403	14.29	14.845
# D38B	TT1153	2025-10-09 16:47:53.000	611.49005	782.15515	3480	4759	29.566944	30.366678	55.21886	61.58512			591.75275	632.3298					64.951866	65.693245	120.00385	120.10223	128.18513	132.0666	3191.8247	3200.1587	3080.994	3555.886	40.87	48.9
# D38B	TBL	2025-10-09 16:47:53.000	618.50653	733.3154	4505	4832	29.77932	31.334648	60.489937	65.13813	84.34534	88.90266	548.42444	653.409					58.064804	60.0	68.267746	68.69277			5859.1025	5940.2627	6139.534	6151.3145	42.22	45.08
# D38B	A_HT	2025-10-09 16:47:52.000	160.88777	193.71521	3480	4759	29.566944	30.366678	55.21886	61.58512	39.301727	41.725082			0.5515075	0.5968507	5.7282147	6.826027							3194.0513	3199.991	3089.989	3654.9617	40.87	48.9
# D38B	TT1142	2025-10-09 16:47:52.000	622.3163	789.63086	3480	4759	29.566944	30.366678	55.21886	61.58512			597.3436	643.7793					56.204433	56.82614	119.993484	120.03408	129.91252	134.33456	3194.0513	3199.991	3089.989	3654.9617	40.87	48.9
# D38B	B_HT	2025-10-09 16:47:53.000	172.17067	200.01541	3480	4759	29.566944	30.366678	55.21886	61.58512	45.014618	45.36512			0.36644995	0.44590884	6.0584106	6.088312							3191.8247	3200.1587	3080.994	3555.886	40.87	48.9

NENGYUAN_PREDICT_SQL_SCRIPT ="""
SELECT 
    last(record_time) as record_time,
    device_name AS device_name,
    last(module) as module,
    last(total_steam) as total_steam,
    last(total_tob) as total_tob,
    last(total_energy) as total_energy,
    last(is_pushed) as is_pushed
from things_energy.nengyuan_predict
group by module, device_name
order by device_name, module
"""