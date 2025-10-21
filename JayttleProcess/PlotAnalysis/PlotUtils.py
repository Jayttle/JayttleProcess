import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import matplotlib.ticker as mticker
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from scipy import stats
import statsmodels.formula.api as smf
import seaborn as sns
import matplotlib.dates as mdates
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from matplotlib.colors import ListedColormap
from sklearn.inspection import DecisionBoundaryDisplay
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import ticker
import os

COLOR_MAP = {0: 'blue', 1: 'red', 2: 'green', 3: 'orange'}

plt.rcParams['font.sans-serif'] = ['Kaiti']
plt.rcParams['axes.unicode_minus'] = False #用来正常显示负

def plot_dataframe_scatter_with_boxplt(df: pd.DataFrame, 
                                        x_target_col: str,
                                        y_target_col: str,
                                        groupby_col: str,
                                        title: str=None, 
                                        set_ylabel: str = 'Value', 
                                        save_path=None):
    """
    绘制分组散点图和箱线图
    参数:
    - df: 包含数据的DataFrame
    - x_target_col: 散点图x轴数据列名
    - y_target_col: 散点图y轴数据列名
    - groupby_col: 分组依据的列名
    - title: 图表标题
    - set_ylabel: y轴标签
    - save_path: 保存路径
    """
    # 计算 x_target_col 和 y_target_col 的 25% 分位数 (Q1) 和 75% 分位数 (Q3)
    unique_phase_Q1 = df[x_target_col].quantile(0.25)
    unique_phase_Q3 = df[x_target_col].quantile(0.75)
    range_Q1 = df[y_target_col].quantile(0.25)
    range_Q3 = df[y_target_col].quantile(0.75)
    
    # 计算 IQR
    unique_phase_IQR = unique_phase_Q3 - unique_phase_Q1
    range_IQR = range_Q3 - range_Q1
    
    # 计算上下范围 (Q3 + 1.5 * IQR 和 Q1 - 1.5 * IQR)
    unique_phase_upper_bound = round(unique_phase_Q3 + 1.5 * unique_phase_IQR, 4)
    unique_phase_lower_bound = round(unique_phase_Q1 - 1.5 * unique_phase_IQR, 4) if unique_phase_Q1 - 1.5 * unique_phase_IQR >= 0 else 0
    range_upper_bound = round(range_Q3 + 1.5 * range_IQR, 4)
    range_lower_bound = round(range_Q1 - 1.5 * range_IQR, 4) if range_Q1 - 1.5 * range_IQR >= 0 else 0
    
    # 输出基于 IQR 设置的范围
    print(f'基于 IQR 设置的范围:')
    print(f'持续时间: {unique_phase_lower_bound} ~ {unique_phase_upper_bound}')
    print(f'能耗: {range_lower_bound} ~ {range_upper_bound}')
    
    # 判断哪些数据超出范围
    out_of_counts_idx = df[df[x_target_col] > unique_phase_upper_bound].index
    out_of_range_idx = df[(df[y_target_col] > range_upper_bound) | (df[y_target_col] < range_lower_bound)].index

    # 找出三种情况的数据
    both_out_of_bounds = df.loc[out_of_counts_idx.intersection(out_of_range_idx)]
    only_out_of_range = df.loc[out_of_range_idx.difference(out_of_counts_idx)]
    only_out_of_counts = df.loc[out_of_counts_idx.difference(out_of_range_idx)]

    # **新增散点图：横坐标为持续时间，纵坐标为总能耗**
    # 根据 batch_status 来设置散点图的颜色
    unique_batch_status = df[groupby_col].unique()
    color_palette = sns.color_palette("Set1", len(unique_batch_status))  # Set1 颜色调色板
    batch_status_color_map = dict(zip(unique_batch_status, color_palette))  # 创建一个 batch_status -> 颜色的映射
    
    scatter_colors = [batch_status_color_map[status] for status in df[groupby_col]]
    
    # 创建图表
    fig = plt.figure(figsize=(16, 10), dpi=150)
    grid = plt.GridSpec(5, 8, hspace=0.5, wspace=0.2)

    # 定义子图
    ax_main = fig.add_subplot(grid[:-1, :-1])
    ax_right = fig.add_subplot(grid[:-1, -1], xticklabels=[], yticklabels=[])
    ax_bottom = fig.add_subplot(grid[-1, 0:-1], xticklabels=[], yticklabels=[])
    ax_bottom_right = fig.add_subplot(grid[-1, -1])  # 右下角子图

    # 绘制散点图，使用 batch_status 来设置颜色
    sns.scatterplot(x=df[x_target_col], y=df[y_target_col],
                    hue=df[groupby_col], palette=batch_status_color_map, marker="D", ax=ax_main)

    # 在右侧添加箱型图 (hwy)，将 boxplot 宽度设置为 0.5
    sns.boxplot(df[y_target_col], ax=ax_right, orient="v", width=0.5)

    # 在底部添加箱型图 (displ)，将 boxplot 宽度设置为 0.5
    sns.boxplot(df[x_target_col], ax=ax_bottom, orient="h", width=0.5)
    # 隐藏坐标轴标题
    ax_right.set_xlabel('')  # 去除右侧箱型图的 x 轴标题
    ax_right.set_ylabel('')  # 去除右侧箱型图的 y 轴标题
    ax_bottom.set_xlabel('')  # 去除底部箱型图的 x 轴标题
    ax_bottom.set_ylabel('')  # 去除底部箱型图的 y 轴标题
    # 去除右侧箱型图和底部箱型图的坐标轴刻度线
    ax_right.set_xticks([])
    ax_right.set_yticks([])
    ax_bottom.set_xticks([])
    ax_bottom.set_yticks([])

    # 设置标题和标签
    ax_main.set(xlabel=x_target_col, ylabel=y_target_col, title=title)

    text_info = f"""
    持续时间范围: {unique_phase_lower_bound} ~ {unique_phase_upper_bound}
    能耗范围: {range_lower_bound} ~ {range_upper_bound}
    """

    # 在右下角添加文本信息，设置文本位置
    ax_main.text(0.95, -0.1, text_info, transform=ax_main.transAxes, fontsize=12,
                verticalalignment='top', horizontalalignment='right',
                bbox=dict(facecolor='white', alpha=0.8, edgecolor='black', boxstyle='round,pad=0.3'))
    
    # 文本信息
    text_info = f"""
    时间: {unique_phase_lower_bound} ~ {unique_phase_upper_bound}
    能耗: {range_lower_bound} ~ {range_upper_bound}
    """
    # 在右下角子图 ax_bottom_right 内部居中添加文本信息
    ax_bottom_right.text(0.4, 0.5, text_info,
                        transform=ax_bottom_right.transAxes,  # 使用子图的坐标系
                        fontsize=10,
                        verticalalignment='center',  # 垂直居中
                        horizontalalignment='center')  # 水平居中

    # 设置轴标签和标题（可选）
    ax_bottom_right.set_xticks([])  # 不显示 x 轴刻度
    ax_bottom_right.set_yticks([])  # 不显示 y 轴刻度


    # 设置最终的纵轴标签
    ax_main.set_ylabel(set_ylabel)

    # 显示图表
    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()

    return both_out_of_bounds, only_out_of_range, only_out_of_counts
def plot_dataframe_column_vlines_v2(df: pd.DataFrame, target_col: str, groupby_col: str, 
                                set_ylim: tuple = None, save_path: str = None, set_xlabel: str = 'Index', 
                                set_ylabel: str = 'Value', data_label: str = 'Data', 
                                vline_color: str = 'gray', vline_style: str = '--',
                                bar_width: float = 0.8):
    """
    绘制带季节分隔线的柱状图（修改为柱状图版本）
    
    参数:
    - vlines: 季节变化的x轴位置列表（分隔线位于柱子右侧）
    - xticklabels: 季节标签列表（长度需比vlines多1）
    - bar_width: 柱状图宽度（0-1）
    - bar_color: 柱状图颜色
    """
    # 校验目标列是否存在
    if target_col not in df.columns:
        raise KeyError(f"DataFrame中未找到目标列: {target_col}")

    # 数据准备
    data = df[target_col].values
    x_index = np.arange(len(data))  # 生成柱状图x坐标
    
    season_changes = df[groupby_col] != df[groupby_col].shift(1)
    vlines = np.where(season_changes)[0].tolist()

    fig, ax = plt.subplots(figsize=(14, 6))

    bar_color = (78/255, 171/255, 144/255) # 柱状图颜色
    # 绘制柱状图（调整边框样式）
    bars = ax.bar(x_index, data, 
                width=bar_width, 
                color=bar_color,
                edgecolor=bar_color,  # 边框颜色与填充一致
                linewidth=0.5, 
                alpha=0.7, 
                label=data_label)

    # 计算季节刻度位置
    boundaries = vlines + [len(df)]  # 添加末段边界
    season_midpoints = [(boundaries[i] + boundaries[i+1])/2 for i in range(len(boundaries)-1)]
    
    # 设置季节标签
    xticklabels = [ '冬季', '春季']
    ax.set_xticks(season_midpoints)
    ax.set_xticklabels(xticklabels)
    
    # 绘制季节分隔线（微调位置避免与柱子重叠）
    for x in vlines:
        ax.axvline(x=x - 0.5 + bar_width/2,  # 对齐柱子右侧
                color=vline_color, 
                linestyle=vline_style, 
                linewidth=1.2, 
                alpha=0.9)

    # 坐标轴样式优化
    ax.set_xlabel(set_xlabel, fontsize=12)
    ax.set_ylabel(set_ylabel, fontsize=12)
    ax.set_xlim(-0.5, len(data)-0.5)  # 精确控制x轴范围
    
    # 隐藏原始刻度线
    ax.tick_params(axis='x', which='both', length=0)  # 隐藏x轴小刻度
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')  # 旋转标签
    
    # 自动调整y轴范围
    if set_ylim:
        ax.set_ylim(set_ylim)
    else:
        y_max = data.max() * 1.15  # 自动留白15%
        ax.set_ylim(0, y_max if not np.isnan(y_max) else 1)

    # 边框和网格优化
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    for spine in ['right', 'top']:
        ax.spines[spine].set_visible(False)
    ax.spines['left'].set_position(('outward', 0))
    ax.spines['bottom'].set_position(('outward', 0))
    
    # 图例和布局
    ax.legend(loc='upper right', frameon=False)
    plt.tight_layout()

    # 输出控制
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=120)
    else:
        plt.show()
    plt.close()

def plot_dataframe_distributed_dots(df: pd.DataFrame, target_col: str, groupby_col: str, 
                            set_xlim: tuple = None, save_path: str = None,
                            set_xlabel: str = 'Value', set_ylabel: str = 'Group',
                            median_color: str = 'firebrick', dot_alpha: float = 0.7):
    """
    绘制分组分布点图，显示每个组的单变量分布和组中位数
    
    参数:
    df -- 包含数据的DataFrame
    target_col -- 要分析的目标列名
    groupby_col -- 分组依据的列名
    set_xlim -- 横坐标范围 (默认自动调整)
    save_path -- 图片保存路径 (默认不保存)
    set_xlabel -- 横坐标标签 (默认'Value')
    set_ylabel -- 纵坐标标签 (默认'Group')
    median_color -- 中位数点颜色 (默认'firebrick')
    dot_alpha -- 数据点透明度 (默认0.7)
    """
    # 检查列是否存在
    if target_col not in df.columns or groupby_col not in df.columns:
        raise KeyError(f"DataFrame中未找到目标列或分组列")

    # 准备数据
    df = df[[target_col, groupby_col]].copy()
    df.dropna(inplace=True)  # 删除缺失值
    
    # 按分组排序
    grouped = df.groupby(groupby_col)[target_col]
    df_median = grouped.median().sort_values(ascending=False)
    groups = df_median.index.tolist()
    
    # 创建图形
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # 绘制水平参考线
    ax.hlines(y=np.arange(len(groups)), 
            xmin=df[target_col].min()-1, 
            xmax=df[target_col].max()+1, 
            color='gray', alpha=0.3, linewidth=0.5, 
            linestyles='dashdot')

    # 绘制数据点
    for y_idx, group in enumerate(groups):
        group_data = df[df[groupby_col] == group][target_col]
        # 添加抖动效果防止点重叠
        jitter = np.random.normal(loc=0, scale=0.05, size=len(group_data))
        ax.scatter(x=group_data, 
                y=y_idx + jitter,
                s=40, edgecolors='gray', 
                facecolors='white', alpha=dot_alpha,
                linewidths=0.5)

    # 绘制中位数点
    ax.scatter(x=df_median.values, 
            y=np.arange(len(groups)),
            s=80, color=median_color, 
            zorder=3, label='Median')

    # 装饰图形
    ax.set_title(f'Distribution of {target_col} by {groupby_col}', fontsize=14)
    ax.set_xlabel(set_xlabel, fontsize=12)
    ax.set_ylabel(set_ylabel, fontsize=12)
    ax.set_yticks(np.arange(len(groups)))
    ax.set_yticklabels([str(g).title() for g in groups], fontsize=10)
    
    # 设置坐标轴范围
    if set_xlim:
        ax.set_xlim(set_xlim)
    else:
        buffer = (df[target_col].max() - df[target_col].min()) * 0.1
        ax.set_xlim(df[target_col].min()-buffer, df[target_col].max()+buffer)

    # 设置坐标轴样式
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.grid(axis='x', alpha=0.4, linestyle='--')
    
    # 添加图例
    ax.legend(loc='upper right', frameon=False)

    # 调整布局
    plt.tight_layout()
    
    # 保存或显示
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    else:
        plt.show()
        
    plt.close()

def plot_dataframe_lollipop_compare(df: pd.DataFrame,
                                    target_col: str,
                                    groupby_col: str,
                                    sort_values: bool = True,
                                    color: str = '#4E79A7',
                                    title: str = None,
                                    set_ylim: tuple = None,
                                    save_path: str = None,
                                    figsize: tuple = (12, 8),
                                    label_size: int = 12):
    """
    绘制分类均值对比棒棒糖图

    参数:
    - groupby_col: 分类列名（如厂商、季节等）
    - sort_values: 是否按目标列值排序
    - color: 主色系
    - annot_offset: 数值标签偏移量
    """
    # 校验数据列
    if target_col not in df.columns:
        raise KeyError(f"目标列 {target_col} 不存在")
    if groupby_col not in df.columns:
        raise KeyError(f"分类列 {groupby_col} 不存在")

    def trimmed_mean(x):
        if len(x) >= 20:  # 确保数据量足够进行剔除操作
            sorted_x = sorted(x)
            n = len(sorted_x)
            start = int(n * 0.05)
            end = int(n * 0.95)
            trimmed_x = sorted_x[start:end]
            return sum(trimmed_x) / len(trimmed_x)
        return x.mean()

    # 准备数据
    df_group = df.groupby(groupby_col, observed=True)[target_col].apply(trimmed_mean).reset_index()
    df_counts = df[groupby_col].value_counts().reset_index(name='counts')
    df_group = pd.merge(df_group, df_counts, on=groupby_col)

    # 排序
    if sort_values:
        df_group.sort_values(target_col, inplace=True, ascending=False)

    # 创建索引
    df_group['x_index'] = range(len(df_group))

    # 创建画布
    fig, ax = plt.subplots(figsize=figsize)

    # 绘制棒棒糖主体
    ax.vlines(x=df_group['x_index'],
                ymin=0,
                ymax=df_group[target_col],
                color=color,
                alpha=0.7,
                linewidth=2.5)

    # 绘制端点圆点
    ax.scatter(df_group['x_index'],
                df_group[target_col],
                s=200,  # 点的大小
                color=color,
                alpha=0.7,
                edgecolor='white',
                zorder=3)

    # 计算动态偏移量
    annot_offset = df_group[target_col].max() * 0.02  # 根据数据高度动态计算

    # 添加数值标签
    for idx, row in df_group.iterrows():
        ax.text(row['x_index'],
                row[target_col] + annot_offset,
                f"{row[target_col]:.2f}",
                ha='center',
                va='bottom',
                fontsize=label_size,
                color=color)

    # 设置坐标轴
    ax.set_xticks(df_group['x_index'])
    ax.set_xticklabels(df_group[groupby_col].str.upper(),
                        rotation=45,
                        ha='right',
                        fontsize=label_size)

    # 标题设置
    title = title or f"{target_col} 的 {groupby_col} 对比"
    ax.set_title(title, fontsize=label_size + 4, pad=20)

    # 坐标轴标签
    ax.set_xlabel('')  # 分类标签已显示在x轴刻度
    ax.set_ylabel(target_col, fontsize=label_size)

    # 范围设置
    y_max = df_group[target_col].max() * 1.15
    ax.set_ylim(0, set_ylim[1] if set_ylim else y_max)

    # 边框优化
    for spine in ['right', 'top']:
        ax.spines[spine].set_visible(False)
    ax.spines['left'].set_position(('outward', 5))
    ax.spines['bottom'].set_position(('outward', 5))

    # 网格线
    ax.grid(axis='y', alpha=0.3, linestyle='--', zorder=0)

    # 添加图例
    for idx, row in df_group.iterrows():
        ax.scatter([], [], color=color, s=200, alpha=0.7, edgecolor='white',
                    label=f"{row[groupby_col]} (n={row['counts']})")
    ax.legend(title='数据样本量',
                loc='upper right',
                fontsize=label_size - 2)

    plt.tight_layout()

    # 输出控制
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
    else:
        plt.show()
    plt.close()
    

def plot_seasonal_kde_comparison(df: pd.DataFrame, target_col: str, groupby_col: str,
                                palette: list = None, alpha: float = 0.7, 
                                show_stats: bool = True, save_path: str = None,
                                figsize: tuple = (12, 6), legend_pos: str = 'upper right',
                                bw_method: float = None):
    """
    绘制不同季节的概率密度分布对比图
    
    参数:
    - palette: 季节颜色列表，默认使用预设配色
    - alpha: 曲线透明度
    - show_stats: 是否显示均值/分位点标记
    - bw_method: 核密度估计的带宽方法
    """
    # 校验数据列
    if target_col not in df.columns:
        raise KeyError(f"DataFrame中未找到目标列: {target_col}")
    if groupby_col not in df.columns:
        raise KeyError(f"DataFrame中未找到季节列: {groupby_col}")

    # 准备数据
    seasons = df[groupby_col].unique()
    season_data = [df[df[groupby_col]==s][target_col].dropna() for s in seasons]
    
    # ========== 新增颜色选择逻辑 ==========
    # 定义定制颜色（RGB格式，数值范围0-1）
    custom_colors = [
        (191/255, 30/255, 46/255),    # 深红色
        (115/255, 186/255, 214/255),   # 浅蓝色
        (250/255, 134/255, 0/255),     # 橙色
        (2/255, 38/255, 62/255),       # 深蓝色
    ]
    # 备用默认颜色（Hex格式）
    default_palette = ['#4C72B0', '#55A868', '#C44E52', '#8172B2', '#CCB974', '#64B5CD']
    
    # 智能选择颜色方案
    if palette is None:
        if len(seasons) <= 4:
            palette = custom_colors[:len(seasons)]  # 使用定制色板
        else:
            palette = default_palette[:len(seasons)]  # 使用备用默认色板
    else:
        palette = palette[:len(seasons)]  # 使用用户自定义色板
    # ========== 颜色逻辑结束 ==========

    # 创建画布
    fig, ax = plt.subplots(figsize=figsize)
    
    # 绘制KDE曲线
    max_density = 0
    for i, (data, color) in enumerate(zip(season_data, palette)):
        if len(data) < 5:
            print(f"警告: 季节'{seasons[i]}'数据量不足({len(data)})，已跳过")
            continue
            
        # 计算KDE
        kde = stats.gaussian_kde(data, bw_method=bw_method)
        x = np.linspace(data.min(), data.max(), 500)
        y = kde(x)

        # 计算分位数边界（95%范围）
        q_low, q_high = np.percentile(data, [2.5, 97.5])
        
        # 生成分段掩码
        full_mask = (x >= data.min()) & (x <= data.max())
        main_mask = (x >= q_low) & (x <= q_high)
        tail_mask = ~main_mask & full_mask

        # 绘制曲线
        line = ax.plot(x, y, color=color, lw=2.5, 
                    label=f'{seasons[i]} (n={len(data)})')
        
        # ========== 分区域填充 ==========
        # 中间95%区域（实色填充）
        ax.fill_between(x, y, where=main_mask,
                    color=color, alpha=0.7, zorder=3)
        
        # 尾部区域（斜线填充）
        ax.fill_between(x, y, where=tail_mask,
                    color=color, alpha=0.3, 
                    hatch='////', edgecolor='white',
                    linewidth=0.8, zorder=2)
        
        # 记录最大密度值
        max_density = max(max_density, y.max())
        
        
        # # 添加统计标记
        # if show_stats:
        #     mean = data.mean()
        #     q1, median, q3 = data.quantile([0.25, 0.5, 0.75])
            
        #     # 绘制均值和分位点
        #     ax.axvline(mean, color=color, linestyle='--', alpha=alpha*0.7, lw=1)
        #     ax.scatter([q1, median, q3], kde([q1, median, q3]), 
        #             color=color, marker='o', s=50, alpha=alpha, 
        #             edgecolor='white', zorder=5)

    # 样式设置（保持不变）
    ax.set_xlabel(target_col, fontsize=12)
    ax.set_ylabel('概率密度', fontsize=12)
    ax.set_title('季节分布对比', fontsize=14, pad=20)
    
    # 边框和网格
    ax.grid(True, alpha=0.3, linestyle='--')
    for spine in ['right', 'top']:
        ax.spines[spine].set_visible(False)
    ax.spines['left'].set_position(('outward', 0))
    ax.spines['bottom'].set_position(('outward', 0))
    
    # 图例
    ax.legend(loc=legend_pos, frameon=False, fontsize=10)
    
    # 调整坐标轴范围
    ax.set_ylim(0, max_density*1.1)
    
    plt.tight_layout()
    
    # 输出控制
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
    else:
        plt.show()
    plt.close()


def plot_seasonal_kde_comparison(df: pd.DataFrame, target_col: str, groupby_col: str,
                                palette: list = None, alpha: float = 0.7, 
                                show_stats: bool = True, save_path: str = None,
                                figsize: tuple = (12, 6), legend_pos: str = 'upper right',
                                bw_method: float = None):
    """
    绘制不同季节的概率密度分布对比图
    
    参数:
    - palette: 季节颜色列表，默认使用预设配色
    - alpha: 曲线透明度
    - show_stats: 是否显示均值/分位点标记
    - bw_method: 核密度估计的带宽方法
    """
    # 校验数据列
    if target_col not in df.columns:
        raise KeyError(f"DataFrame中未找到目标列: {target_col}")
    if groupby_col not in df.columns:
        raise KeyError(f"DataFrame中未找到季节列: {groupby_col}")

    # 准备数据
    seasons = df[groupby_col].unique()
    season_data = [df[df[groupby_col]==s][target_col].dropna() for s in seasons]
    
    # ========== 新增颜色选择逻辑 ==========
    # 定义定制颜色（RGB格式，数值范围0-1）
    custom_colors = [
        (191/255, 30/255, 46/255),    # 深红色
        (115/255, 186/255, 214/255),   # 浅蓝色
        (250/255, 134/255, 0/255),     # 橙色
        (2/255, 38/255, 62/255),       # 深蓝色
    ]
    # 备用默认颜色（Hex格式）
    default_palette = ['#4C72B0', '#55A868', '#C44E52', '#8172B2', '#CCB974', '#64B5CD']
    
    # 智能选择颜色方案
    if palette is None:
        if len(seasons) <= 4:
            palette = custom_colors[:len(seasons)]  # 使用定制色板
        else:
            palette = default_palette[:len(seasons)]  # 使用备用默认色板
    else:
        palette = palette[:len(seasons)]  # 使用用户自定义色板
    # ========== 颜色逻辑结束 ==========

    # 创建画布
    fig, ax = plt.subplots(figsize=figsize)
    
    # 绘制KDE曲线
    max_density = 0
    for i, (data, color) in enumerate(zip(season_data, palette)):
        if len(data) < 5:
            print(f"警告: 季节'{seasons[i]}'数据量不足({len(data)})，已跳过")
            continue
            
        # 计算KDE
        kde = stats.gaussian_kde(data, bw_method=bw_method)
        x = np.linspace(data.min(), data.max(), 500)
        y = kde(x)

        # 计算分位数边界（95%范围）
        q_low, q_high = np.percentile(data, [2.5, 97.5])
        
        # 生成分段掩码
        full_mask = (x >= data.min()) & (x <= data.max())
        main_mask = (x >= q_low) & (x <= q_high)
        tail_mask = ~main_mask & full_mask

        # 绘制曲线
        line = ax.plot(x, y, color=color, lw=2.5, 
                    label=f'{seasons[i]} (n={len(data)})')
        
        # ========== 分区域填充 ==========
        # 中间95%区域（实色填充）
        ax.fill_between(x, y, where=main_mask,
                    color=color, alpha=0.7, zorder=3)
        
        # 尾部区域（斜线填充）
        ax.fill_between(x, y, where=tail_mask,
                    color=color, alpha=0.3, 
                    hatch='////', edgecolor='white',
                    linewidth=0.8, zorder=2)
        
        # 记录最大密度值
        max_density = max(max_density, y.max())
        
        
        # # 添加统计标记
        # if show_stats:
        #     mean = data.mean()
        #     q1, median, q3 = data.quantile([0.25, 0.5, 0.75])
            
        #     # 绘制均值和分位点
        #     ax.axvline(mean, color=color, linestyle='--', alpha=alpha*0.7, lw=1)
        #     ax.scatter([q1, median, q3], kde([q1, median, q3]), 
        #             color=color, marker='o', s=50, alpha=alpha, 
        #             edgecolor='white', zorder=5)

    # 样式设置（保持不变）
    ax.set_xlabel(target_col, fontsize=12)
    ax.set_ylabel('概率密度', fontsize=12)
    ax.set_title('季节分布对比', fontsize=14, pad=20)
    
    # 边框和网格
    ax.grid(True, alpha=0.3, linestyle='--')
    for spine in ['right', 'top']:
        ax.spines[spine].set_visible(False)
    ax.spines['left'].set_position(('outward', 0))
    ax.spines['bottom'].set_position(('outward', 0))
    
    # 图例
    ax.legend(loc=legend_pos, frameon=False, fontsize=10)
    
    # 调整坐标轴范围
    ax.set_ylim(0, max_density*1.1)
    
    plt.tight_layout()
    
    # 输出控制
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
    else:
        plt.show()
    plt.close()



def plot_forecast_with_history(history_data: np.ndarray, 
                                pred_data: np.ndarray,
                                history_length: int = 20,
                                set_ylim: tuple = None,
                                save_path: str = None,
                                set_xlabel: str = '时间步',
                                set_ylabel: str = '蒸汽能耗累积量',
                                labels: tuple = ('历史观测', '模型预测'),
                                x_labels: list = None):
        """
        柱状图可视化预测结果（优化网格线+标签样式）
        
        参数：
            history_data: 历史数据数组（训练集最后部分）
            pred_data: 预测数据数组
            history_length: 显示的历史数据点数（默认20）
            set_ylim: 手动设置纵轴范围（可选）
            save_path: 图片保·存路径（None时显示）
            set_xlabel: x轴标签文本
            set_ylabel: y轴标签文本
            labels: 图例标签（历史标签，预测标签）
        """
        # 数据预处理
        actual_hist_len = min(history_length, len(history_data))
        history_tail = history_data[-actual_hist_len:]
        
        # 颜色配置
        HIST_COLOR = '#2A609D'  # 历史色
        PRED_COLOR = '#6A6A6A'  # 预测色
        
        # 创建组合数据
        combined_data = np.concatenate([history_tail, pred_data])
        total_points = len(combined_data)
        
        # 创建画布
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # 创建柱状图位置索引
        x_pos = np.arange(total_points)
        
        # 绘制历史柱状图
        hist_bars = ax.bar(x_pos[:actual_hist_len], history_tail,
                        width=0.6,
                        color=HIST_COLOR,
                        edgecolor='#1A406D',
                        linewidth=1.2,
                        label=labels[0])
        
        # 绘制预测柱状图
        if len(pred_data) > 0:
            pred_bars = ax.bar(x_pos[actual_hist_len:], pred_data,
                            width=0.6,
                            color=PRED_COLOR,
                            edgecolor='#4A4A4A',
                            linewidth=1.2,
                            label=labels[1])
        
        # 添加分界线（红色虚线）
        split_line_x = actual_hist_len - 0.5
        ax.axvline(x=split_line_x, 
                color='#FF6B6B',
                linestyle='--',
                linewidth=2.5,
                zorder=2)
        
        # 智能注释
        if len(pred_data) > 0:
            annot_text = f"预测分界\n历史窗口: {actual_hist_len}步\n预测窗口: {len(pred_data)}步"
            max_height = max(combined_data) * 1.15
            ax.annotate(annot_text,
                        xy=(split_line_x, max_height*0.8),
                        xytext=(split_line_x + 3, max_height*0.83),
                        arrowprops=dict(arrowstyle="->",
                                    color='#606060',
                                    linewidth=1.8,
                                    connectionstyle="angle3,angleA=0,angleB=90"),
                        fontsize=11,
                        bbox=dict(boxstyle="round",
                                facecolor='white',
                                alpha=0.95,
                                edgecolor='#CCCCCC'))
            
        # 坐标轴设置
        ax.set_xlabel(set_xlabel, fontsize=12, labelpad=12)
        ax.set_ylabel(set_ylabel, fontsize=12, labelpad=12)
        
        # 设置x轴刻度位置和标签
        ax.set_xticks(x_pos)  # 右移半个柱宽
        
        # 标签生成逻辑
        if x_labels is not None:
            if len(x_labels) != total_points:
                raise ValueError(f"x_labels长度需与总数据点一致（当前：{len(x_labels)}，需要：{total_points}）")
            xtick_labels = x_labels
        else:
            xtick_labels = [f"H-{actual_hist_len-i}" if i < actual_hist_len 
                        else f"F+{i-actual_hist_len+1}" 
                        for i in range(total_points)]
        
        # 设置标签样式（关键修改）
        ax.set_xticklabels(xtick_labels,
                        rotation=0,
                        ha='center',  # 左对齐
                        va='top',
                        color='#333333',
                        fontsize=10,)  # 向下偏移3%
        
        # 调整x轴显示范围
        ax.set_xlim(-0.5, total_points - 0.5)

        # 智能Y轴范围（保持10的倍数）
        data_min = np.nanmin(combined_data)
        data_max = np.nanmax(combined_data)
        y_min = np.floor(data_min / 10) * 10
        y_max = np.ceil(data_max / 10) * 10
        ax.set_ylim(set_ylim if set_ylim else (y_min, y_max))

        # 生成均匀5个刻度（关键修改部分）
        y_ticks = np.linspace(start=y_min, stop=y_max, num=5)
        y_ticks = np.round(y_ticks).astype(int)  # 转为整数
        ax.yaxis.set_major_locator(mticker.FixedLocator(y_ticks))
        
        # 配置网格线
        ax.grid(axis='y', 
            linestyle=':', 
            linewidth=1, 
            alpha=0.6,
            color='#CCCCCC')
        
        # 添加柱顶数值标签（水平显示）
        def add_labels(bars):
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., 
                        height + (y_max - y_min)*0.01,  # 动态偏移
                        f'{height:.0f}',
                        ha='center',
                        va='bottom',
                        fontsize=10,  # 8号字体
                        color='#333333',
                        rotation=0)  # 水平显示
        
        # 添加历史数据标签
        add_labels(hist_bars)
        
        # 添加预测数据标签（如果存在）
        if len(pred_data) > 0 and 'pred_bars' in locals():
            add_labels(pred_bars)
        
        # 图例样式
        legend = ax.legend(frameon=True,
                        loc='upper right',
                        framealpha=0.95,
                        edgecolor='#333333',
                        fontsize=10)
        legend.get_frame().set_linewidth(1.5)
        
        # 边框样式
        for spine in ax.spines.values():
            spine.set_linewidth(1.5)
            spine.set_color('#333333')
        
        # 输出控制
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"图表已保存至：{save_path}")
        else:
            plt.show()
        plt.close()

def plot_true_and_forecast_with_history(history_data: np.ndarray, 
                                        pred_data: np.ndarray,
                                        true_data: np.ndarray,
                                        history_length: int = 20,
                                        set_ylim: tuple = None,
                                        save_path: str = None,
                                        set_xlabel: str = '时间步',
                                        set_ylabel: str = '蒸汽能耗累积量',
                                        labels: tuple = ('历史数据', '预测值', '真实值')):
    """
    可视化预测结果（修正预测起始位置）

    参数：
        history_data: 历史数据数组（训练集最后部分）
        pred_data: 预测数据数组
        true_data: 真实值数组
        history_length: 显示的历史数据点数（默认20）
        set_ylim: 纵轴范围
        save_path: 保存路径
        set_xlabel: x轴标签
        set_ylabel: y轴标签
        labels: 图例标签
    """
    # 数据预处理
    actual_history_length = min(history_length, len(history_data))
    history_tail = history_data[-actual_history_length:]

    # 创建时间轴（重要修改点）
    full_index = np.arange(actual_history_length + len(pred_data))

    # 合并数据序列（保持原始结构）
    combined_pred = np.concatenate([history_tail, pred_data])
    combined_true = np.concatenate([history_tail, true_data])

    # 创建画布
    fig, ax = plt.subplots(figsize=(12, 6))

    # 绘制预测趋势（交换标签顺序）
    ax.plot(full_index, combined_pred, 
            color='#4E79A7', linewidth=2, linestyle='--', 
            marker='o', markersize=6, label=labels[0])  # 预测值标签改为labels[1]

    # 绘制真实数据
    ax.plot(full_index, combined_true,
            color='#E15759', linewidth=2, 
            marker='s', markersize=6, label=labels[1])

    # 关键修改点：调整预测起始线位置
    connection_point = actual_history_length  # 使用历史数据长度作为分界点
    ax.axvline(x=connection_point,  # 精确对齐预测起始位置
                color='#79706E', 
                linestyle=':', 
                linewidth=1.5)

    # 智能注释系统调整
    annotation_text = f"预测起点\n历史窗口: {actual_history_length}步\n预测窗口: {len(pred_data)}步"
    # 使用预测首值作为锚点高度
    annotation_y = pred_data[0] * 0.95 if len(pred_data) > 0 else history_tail[-1] 

    ax.annotate(annotation_text,
                xy=(connection_point, pred_data[0]),  # 锚点指向预测第一个数据点
                xytext=(connection_point + 1.5, annotation_y - 0.5),
                arrowprops=dict(arrowstyle="->", 
                                color='#606060',
                                lw=1.5,
                                connectionstyle="arc3,rad=0.2"),
                fontsize=10,
                bbox=dict(boxstyle="round", 
                            facecolor='white', 
                            alpha=0.9,
                            edgecolor='#DDDDDD'))

    # 坐标轴标签设置
    ax.set_xlabel(set_xlabel, fontsize=12, labelpad=10)
    ax.set_ylabel(set_ylabel, fontsize=12, labelpad=10)

    # 保持其他样式不变
    ax.grid(False)
    legend = ax.legend(frameon=True, loc='upper left',
                        framealpha=0.9, edgecolor='#333333')
    legend.get_frame().set_linewidth(1.2)

    for spine in ax.spines.values():
        spine.set_linewidth(1.5)
        spine.set_color('#333333')

    # 创建嵌套子图
    inset_ax = inset_axes(ax, width="30%", height="30%", loc='lower left')
    # 创建NYmodel实例
    _insert_plot_two_data(inset_ax, pred_data, true_data)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    else:
        plt.show()
    plt.close()

def _insert_plot_two_data(ax, to_plt_numpy1: np.ndarray, to_plt_numpy2: np.ndarray, 
                            set_ylim: tuple = None):
    
    print('to_plt_numpy1:', to_plt_numpy1)
    print('to_plt_numpy2:', to_plt_numpy2)
    # 绘制第一条数据
    ax.plot(to_plt_numpy1, color='#9ACF80', linewidth=1)  # 设置颜色为蓝色并设置线宽为1
    ax.scatter(np.arange(len(to_plt_numpy1)), to_plt_numpy1, color='#9ACF80', marker='s', s=20)  # 黑色方块点

    # 绘制第二条数据
    ax.plot(to_plt_numpy2, color='#899CD6', linewidth=1, linestyle='--')  # 设置颜色为红色，线宽为1，虚线
    ax.scatter(np.arange(len(to_plt_numpy2)), to_plt_numpy2, color='#899CD6', marker='o', s=20)  # 红色圆点

    if set_ylim is not None:
        ax.set_ylim(set_ylim)

    # 取消网格线
    ax.grid(False)
    ax.tick_params(axis='x', which='both', 
                labelbottom=False,  # 隐藏x轴标签
                bottom=False)  # 保留刻度线

    # 设置主要和次要刻度线方向
    ax.yaxis.set_tick_params(which='major', direction='in')  # Y轴主要刻度
    ax.yaxis.set_tick_params(which='minor', direction='in') # Y轴次要刻度

    # 设置轴交叉点
    ax.spines['left'].set_position(('outward', 0))   # 设置y轴位置
    ax.spines['bottom'].set_position(('outward', 0))  # 设置x轴位置
    ax.spines['right'].set_linewidth(1)    # 设置右侧边框宽度
    ax.spines['top'].set_linewidth(1)      # 设置顶部边框宽度

    # 设置图形区域背景为白色
    ax.set_facecolor('white')

    # 设置坐标轴线宽
    ax.spines['left'].set_linewidth(1)
    ax.spines['bottom'].set_linewidth(1)

    # 设置横坐标刻度数量
    num_ticks = min(5, len(to_plt_numpy1))  # 确保最多5个刻度线，且不超过数据长度
    ax.xaxis.set_major_locator(MaxNLocator(nbins=num_ticks))  # 设置横坐标最大刻度数量

    # 取消横纵坐标标签
    ax.set_xlabel('')
    ax.set_ylabel('')

def plot_grouped_trends(grouped_df, groupby_col, params_to_plot, figsize=(15, 8)):
    """
    根据分组结果绘制多参数趋势图
    
    参数:
        grouped_df (DataFrame): groupby_table_result 的输出结果
        groupby_col (str): 分组列名（如日期、设备等）
        params_to_plot (list): 需要绘制的参数基础名称列表（如 ['SteamMaFl', 'SteamPressAft']）
        figsize (tuple): 图表尺寸
    """
    # 参数校验
    if groupby_col not in grouped_df.columns:
        print(f"错误: 分组列 {groupby_col} 不存在")
        return
    
    # 自动识别相关设备参数
    valid_columns = []
    equipment_labels = []
    for param in params_to_plot:
        # 匹配所有设备相关列 (格式: 设备名_参数)
        param_cols = [col for col in grouped_df.columns 
                     if col.endswith(f'_{param}') and not col.startswith('ZS12')]
        valid_columns.extend(param_cols)
        equipment_labels.extend([col.split('_')[0] for col in param_cols])
    
    # 去重并保留顺序
    valid_columns = list(dict.fromkeys(valid_columns))
    equipment_labels = list(dict.fromkeys(equipment_labels))
    
    # 创建画布
    n_plots = len(params_to_plot)
    fig, axes = plt.subplots(n_plots, 1, figsize=(figsize[0], figsize[1]*n_plots))
    if n_plots == 1:
        axes = [axes]  # 统一为列表格式
    
    # 颜色配置
    color_palette = plt.cm.tab10.colors
    date_format = "%Y-%m" if pd.api.types.is_datetime64_any_dtype(grouped_df[groupby_col]) else None
    
    # 遍历每个参数绘制子图
    for idx, (param, ax) in enumerate(zip(params_to_plot, axes)):
        # 获取当前参数相关列
        param_cols = [col for col in valid_columns if col.endswith(f'_{param}')]
        
        # 绘制每条趋势线
        for i, col in enumerate(param_cols):
            equipment = col.split('_')[0]
            ax.plot(grouped_df[groupby_col], 
                   grouped_df[col], 
                   label=f'{equipment}',
                   color=color_palette[i % 10],
                   marker='o',
                   linestyle='--' if i > 4 else '-')
            
        # 坐标轴格式化
        if date_format:
            ax.xaxis.set_major_formatter(mdates.DateFormatter(date_format))
        
        # 添加辅助元素
        ax.set_title(f"参数趋势: {param}", pad=20)
        ax.set_ylabel("参数值")
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1), borderaxespad=0)
        
        # 自动旋转日期标签
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

    # 共享x轴标签
    axes[-1].set_xlabel(groupby_col)
    plt.tight_layout()
    plt.show()

def plot_period_statistics(period_stats_df, stats_cols, col_names, 
                           figsize=(14, 8), dpi=150, bins=30, 
                           color='lightcoral', save_path=None):
    """
    绘制周期统计特征的直方图
    
    参数:
        period_stats_df (DataFrame): 包含周期统计量的数据框
        stats_cols (list): 需要绘制的数值列名列表
        col_names (list): 对应的显示名称列表（与stats_cols顺序一致）
        figsize (tuple): 图表尺寸，默认(14, 8)
        dpi (int): 图像分辨率，默认150
        bins (int): 直方图的分箱数量，默认30
        color (str): 直方图颜色，默认'lightcoral'
        save_path (str): 图片保存路径（可选），默认None不保存
    """
    # 参数校验
    missing_cols = [col for col in stats_cols if col not in period_stats_df.columns]
    if missing_cols:
        print(f"错误: 以下列不存在 - {missing_cols}")
        return
    
    if len(stats_cols) != len(col_names):
        print("错误: 数值列名列表与显示名称列表长度不一致")
        return
    
    # 创建图表
    n_stats = len(stats_cols)
    plt.figure(figsize=figsize, dpi=dpi)
    
    # 计算子图布局 (行数固定为2)
    n_rows = 2
    n_cols = int(np.ceil(n_stats / n_rows))
    
    # 绘制每个统计特征的直方图
    for i, (col, name) in enumerate(zip(stats_cols, col_names)):
        plt.subplot(n_rows, n_cols, i+1)
        plt.hist(period_stats_df[col], bins=bins, rwidth=0.9, color=color)
        plt.title(name, fontsize=12)
        plt.grid(True, alpha=0.3)
    
    # 调整布局并保存/显示
    plt.tight_layout(pad=3.0)
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图片已保存至: {save_path}")
    else:
        plt.show()

def ax_plot_residuals(ax, x_data, resid_data, x_label, title, resid_lb, resid_ub):
    """
    在指定轴上绘制残差图
    
    参数:
        ax (matplotlib.axes.Axes): 要绘制残差图的轴对象
        x_data (pd.Series): 自变量数据
        resid_data (pd.Series): 残差数据
        x_label (str): X轴标签
        title (str): 图表标题
        resid_lb (float): 残差下边界
        resid_ub (float): 残差上边界
    """
    # 绘制残差散点图 - 使用珊瑚色
    ax.scatter(
        x=x_data,
        y=resid_data,
        color="coral",  # 使用珊瑚色
        alpha=0.5,      # 降低透明度
        zorder=3        # 确保数据点在网格线上方
    )
    
    # 添加异常值边界线 - 使用红色和蓝色
    ax.axhline(y=resid_lb, ls='--', color='r', linewidth=1.5, zorder=2)  # 红色下边界
    ax.axhline(y=resid_ub, ls='--', color='b', linewidth=1.5, zorder=2)  # 蓝色上边界
    
    # 添加标题
    ax.set_title(title, fontsize=12)
    ax.set_xlabel(x_label)
    ax.set_ylabel("回归残差")
    
    # 设置残差图的白色网格线（在底层）
    ax.grid(True, color='white', linestyle='-', linewidth=1.0, alpha=0.8, zorder=1)


def plot_column_relationship(df: pd.DataFrame, 
                            x_col: str,
                            y_col: str,
                            figsize: tuple = (12, 8),
                            dpi: int = 150,
                            group_col: str = None) -> pd.DataFrame:
    """
    分析并可视化任意两列之间的关系，进行回归分析和异常值检测
    
    参数:
        df (pd.DataFrame): 输入数据框
        x_col (str): 自变量列名
        y_col (str): 因变量列名
        figsize (tuple): 图表尺寸 (宽, 高)
        dpi (int): 图表分辨率
        group_col (str): 可选，分组列名（如周期等）
    
    返回:
        pd.DataFrame: 包含计算字段和异常值标记的增强数据框
    """
    # 创建数据副本以避免修改原始数据
    df_copy = df.copy()
    
    # 1. 检查列是否存在
    missing_cols = []
    if x_col not in df_copy.columns:
        missing_cols.append(x_col)
    if y_col not in df_copy.columns:
        missing_cols.append(y_col)
    
    if missing_cols:
        raise ValueError(f"以下列不存在于数据框中: {', '.join(missing_cols)}")
    
    # 2. 检查数据类型是否为数值型
    if not pd.api.types.is_numeric_dtype(df_copy[x_col]):
        raise ValueError(f"列 '{x_col}' 不是数值类型")
    
    if not pd.api.types.is_numeric_dtype(df_copy[y_col]):
        raise ValueError(f"列 '{y_col}' 不是数值类型")
    
    # 3. 检查是否有足够的数据点
    valid_data = df_copy[[x_col, y_col]].dropna()
    if len(valid_data) < 10:  # 至少需要10个数据点
        raise ValueError(f"有效数据点不足 ({len(valid_data)} 个)，至少需要10个非缺失值")
    
    # 4. 如果指定了分组列，检查是否存在于数据框
    if group_col and group_col not in df_copy.columns:
        raise ValueError(f"分组列 '{group_col}' 不存在于数据框中")
    
    # 5. 创建绘图区域 - 使用2个子图并设置灰色背景
    fig = plt.figure(figsize=(figsize[0], figsize[1] * 1.5), dpi=dpi)
    fig.set_facecolor('#F0F0F0')  # 设置整个图形的背景色为浅灰色
    gs = fig.add_gridspec(2, 1, height_ratios=[3, 2])  # 主图3份高度，残差图2份高度
    
    # 创建主图区域
    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor('#F0F0F0')  # 设置主图背景色
    
    # 6. 绘制两列关系图 - 使用橙色
    sns.scatterplot(
        x=x_col, 
        y=y_col, 
        data=df_copy,
        color="orange",  # 使用橙色
        alpha=0.8,       # 提高透明度
        edgecolor='k',   # 黑色边缘
        ax=ax1,
        zorder=3         # 确保数据点在网格线上方
    )
    ax1.set_title(f"{y_col} 与 {x_col} 的关系", fontsize=12)
    ax1.set_xlabel(x_col)
    ax1.set_ylabel(y_col)
    
    # 7. 计算和展示相关系数
    corr_coef = valid_data.corr().iloc[0, 1]
    ax1.text(0.95, 0.05, f'相关系数: {corr_coef:.3f}', 
            transform=ax1.transAxes, 
            ha='right', 
            bbox=dict(facecolor='white', alpha=0.8),
            zorder=4)  # 确保文本在数据点上方
    
    # 8. 拟合回归模型（使用有效数据）
    formula = f'{y_col} ~ {x_col}'
    ols_model = smf.ols(formula=formula, data=valid_data).fit()
    
    # 添加回归线
    x_min = valid_data[x_col].min()
    x_max = valid_data[x_col].max()
    x_range = np.linspace(x_min, x_max, 100)
    y_pred = ols_model.predict(exog={x_col: x_range})
    ax1.plot(x_range, y_pred, 'r--', linewidth=1.5, zorder=2)  # 回归线在网格线上方但在数据点下方
    
    # 设置主图的白色网格线（在底层）
    ax1.grid(True, color='white', linestyle='-', linewidth=1.0, alpha=0.8, zorder=1)
    
    # 9. 残差分析和异常值检测
    # 将残差结果合并回原始数据框
    df_copy = df_copy.merge(valid_data.assign(resid=ols_model.resid), 
                           on=[x_col, y_col], how='left')
    
    # 计算残差边界 - 使用与consistency_speed_position相同的计算方法
    resid_mean = df_copy['resid'].mean()
    resid_std = df_copy['resid'].std()
    resid_lb = resid_mean - 3 * resid_std
    resid_ub = resid_mean + 3 * resid_std
    df_copy['outlier'] = (np.abs(df_copy['resid']) >= resid_ub)  # 使用绝对值和上界
    
    # 10. 绘制残差图 - 在第二个子图中
    ax2 = fig.add_subplot(gs[1])
    ax2.set_facecolor('#F0F0F0')  # 设置残差图背景色
    
    # 准备残差图标题
    title = "残差分布与异常值检测"
    if group_col:
        title += f" (按 {group_col} 分组)"
    
    # 使用独立函数绘制残差图
    ax_plot_residuals(
        ax=ax2,
        x_data=df_copy[x_col],
        resid_data=df_copy['resid'],
        x_label=x_col,
        title=title,
        resid_lb=resid_lb,
        resid_ub=resid_ub
    )
    
    # 调整布局
    plt.tight_layout()
    
    # 在整个图表周围添加填充
    fig.subplots_adjust(left=0.08, right=0.95, top=0.93, bottom=0.08, hspace=0.25)
    
    plt.show()
    
    # 打印统计摘要
    print("\n" + "="*50)
    print(f"{y_col}与{x_col}关系回归分析摘要")
    print("="*50)
    print(ols_model.summary())

def plot_correlation_heatmap(df, stats_cols, figsize=(16, 14), dpi=100,
                             cmap='coolwarm', annot=True, fmt='.2f',
                             linewidths=.5, cbar_kws={'shrink': 0.8},
                             save_path=None):
    """
    绘制完整数值列的相关性热图（无掩码）
    
    参数:
        df (pd.DataFrame): 包含数据的DataFrame
        stats_cols (list): 需要分析的数值列名列表
        figsize (tuple): 图表尺寸，默认(16, 14)
        dpi (int): 图像分辨率，默认100
        cmap (str): 热图颜色，默认'coolwarm'
        annot (bool): 是否显示相关系数值，默认True
        fmt (str): 数值格式，默认'.2f'(保留两位小数)
        linewidths (float): 格子间线宽，默认0.5
        cbar_kws (dict): 颜色条参数，默认缩小20%
        save_path (str): 图片保存路径(可选)，默认None不保存
    
    返回:
        相关系数矩阵DataFrame (如果成功绘制)
    """
    # 1. 参数校验
    # 检查必备列是否存在
    missing_cols = [col for col in stats_cols if col not in df.columns]
    if missing_cols:
        print(f"错误: 以下列不存在 - {missing_cols}")
        return None
        
    # 检查列数量是否足够
    if len(stats_cols) < 2:
        print("错误: 至少需要两个数值列")
        return None
    
    # 检查是否有非数值列
    non_numeric_cols = [col for col in stats_cols if not np.issubdtype(df[col].dtype, np.number)]
    if non_numeric_cols:
        print(f"警告: 以下列为非数值类型 - {non_numeric_cols}")
        # 尝试自动转换为数值类型
        for col in non_numeric_cols:
            try:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            except Exception as e:
                print(f"转换列 {col} 失败: {str(e)}")
    
    # 2. 提取所需列并计算相关系数
    corr_df = df[stats_cols].corr()
    
    # 3. 创建完整热图（无掩码）
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    
    # 绘制完整热图（显示全部对称矩阵）
    # 关键修改：将annot_kws设置为居中对齐
    heatmap = sns.heatmap(
        corr_df,
        cmap=cmap,
        annot=annot,
        fmt=fmt,
        annot_kws={"fontsize": 10, "va": "center", "ha": "center"},  # 文字居中对齐
        linewidths=linewidths,
        vmin=-1, vmax=1,  # 固定颜色范围[-1,1]
        cbar_kws=cbar_kws,
        square=True,  # 保持格子为正方形
        ax=ax
    )
    
    # 4. 设置标题和标签
    plt.title('Complete Correlation Matrix', fontsize=18, pad=20)
    
    # 优化标签显示 - 使刻度线与方块居中对齐
    # 关键修改：调整刻度位置到方块中心
    ax.set_xticks(np.arange(len(stats_cols)) + 0.5)
    ax.set_xticklabels(
        stats_cols,
        rotation=55,
        ha='right',
        rotation_mode='anchor',  # 围绕锚点旋转
        fontsize=10
    )
    
    ax.set_yticks(np.arange(len(stats_cols)) + 0.5)
    ax.set_yticklabels(
        stats_cols,
        rotation=0,
        fontsize=10,
        va='center'  # 垂直居中
    )
    
    # 微调布局
    plt.tight_layout()
    
    # 5. 保存或显示
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
        print(f"图片已保存至: {save_path}")
    else:
        plt.show()
    
    return corr_df


def boxplot_with_regression_line(x, y, x_label='X', y_label='Y', bins=5):
    """
    绘制分箱后的 X-Y 箱线图，并拟合中位数上的回归线。

    参数:
        x (array-like): 自变量数据。
        y (array-like): 因变量数据。
        x_label (str): 横轴标签名称。
        y_label (str): 纵轴标签名称。
        bins (int): 分箱数量。
    """
    df = pd.DataFrame({x_label: x, y_label: y}).dropna()
    df['x_bin'] = pd.cut(df[x_label], bins=bins)

    grouped = df.groupby('x_bin', observed=True).agg({x_label: 'median', y_label: 'median'}).reset_index()
    grouped['x_bin_center'] = grouped['x_bin'].apply(lambda x: x.mid)

    model = LinearRegression()
    model.fit(grouped[['x_bin_center']], grouped[y_label])
    y_pred = model.predict(grouped[['x_bin_center']])
    r2 = r2_score(grouped[y_label], y_pred)

    # 回归系数与方程
    slope = model.coef_[0]
    intercept = model.intercept_
    eq_text = f'$y = {slope:.2f}x + {intercept:.2f}$'

    # 设置字体与绘图
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df, x='x_bin', y=y_label, color='lightgreen')

    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    plt.plot(grouped['x_bin'].astype(str), grouped[y_label], 'o', color='red', label='中位数')
    plt.plot(grouped['x_bin'].astype(str), y_pred, '--', color='blue', label='回归线')

    # 显示回归方程和R²
    plt.text(0.05, max(df[y_label])*0.95, f'$R^2 = {r2:.2f}$', fontsize=12, color='red')
    plt.text(0.05, max(df[y_label])*0.88, eq_text, fontsize=12, color='darkblue')

    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(f'{x_label} vs {y_label}')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    return model

def plot_selected_device_correlation_heatmap(recipe_tab: pd.DataFrame, phase_tab: pd.DataFrame, selected_devices: list):
    """
    仅绘制所选设备相关字段与全局字段的相关性热力图。

    参数:
    - recipe_tab: 包含 recipe 参数的 DataFrame。
    - phase_tab: 包含 phase 参数（带有 _deltaE, _deltaT, _deltaET 后缀）的 DataFrame。
    - selected_devices: 你想查看的设备列表，例如 ['A_HT', 'TT1142']。
    """

    # 所有可能的设备（控制排序）
    full_device_order = ['A_HT', 'B_HT', 'TT1142', 'TT1153']

    # phase字段原始结构
    phase_base = ['A_HT_phase1_2', 'A_HT_phase3_4', 'A_HT_phase5_6',
                  'B_HT_phase1_2', 'B_HT_phase3_4', 'B_HT_phase5_6',
                  'TT1142_phase1_3', 'TT1142_phase4_6', 'TT1142_phase7_8',
                  'TT1153_phase1_3', 'TT1153_phase4_6', 'TT1153_phase7_8']

    # 扩展成 deltaE, deltaT, deltaET
    phase_fields_all = [f"{name}_{suffix}" for name in phase_base for suffix in ['deltaE', 'deltaT', 'deltaET']]

    # 按设备过滤 phase 字段
    phase_fields = [f for f in phase_fields_all if any(f.startswith(dev) for dev in selected_devices)]

    # recipe 字段（设备相关 + 全局字段）
    recipe_fields_all = [
        'A_HT_SteamMaFl', 'A_HT_SteamPressAft', 'A_HT_SteamPressBef',
        'TT1142_Steam_flow', 'TT1142_SteamMaFl', 'TT1142_ProcAirValve',
        'TT1142_ProcAirTemp', 'TT1142_CylTemp',
        'B_HT_SteamMaFl', 'B_HT_SteamPressAft', 'B_HT_SteamPressBef',
        'TT1153_Steam_flow', 'TT1153_SteamMaFl', 'TT1153_ProcAirValve',
        'TT1153_ProcAirTemp', 'TT1153_CylTemp'
    ]
    global_fields = ['Temperature_Kld_Area', 'Humidity_Kld_Area', 'line_total_energy']

    # 按设备过滤 recipe 字段
    recipe_fields = [f for f in recipe_fields_all if any(f.startswith(dev) for dev in selected_devices)]

    # 合并字段
    selected_fields = phase_fields + recipe_fields + global_fields

    # 合并 DataFrame
    merged_df = pd.concat([recipe_tab, phase_tab], axis=1)

    # 保证字段存在
    valid_fields = [f for f in selected_fields if f in merged_df.columns]

    # 排序逻辑：设备顺序 + global 固定最后
    def sort_key(f):
        for i, dev in enumerate(full_device_order):
            if f.startswith(dev):
                return (i, f)
        return (len(full_device_order), f)  # global 参数

    sorted_fields = sorted(valid_fields, key=sort_key)

    # 相关性矩阵
    corr_matrix = merged_df[sorted_fields].corr()

    # 绘图
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置黑体
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
    plt.figure(figsize=(max(10, len(sorted_fields) * 0.4), max(8, len(sorted_fields) * 0.4)))
    sns.heatmap(corr_matrix, annot=True, fmt=".1f", cmap='coolwarm', center=0,
                linewidths=0.3, square=True, cbar_kws={"shrink": 0.6})
    plt.xticks(rotation=90, fontsize=8)
    plt.yticks(rotation=0, fontsize=8)
    plt.title(f"相关性热力图 - 已选择设备: {', '.join(selected_devices)}", fontsize=14)
    plt.tight_layout()
    plt.show()
    #plot_selected_device_correlation_heatmap(recipe_tab, phase_tab, selected_devices=['A_HT', 'TT1142'])


def plot_cluster_lines(
    ax,
    df,
    feature_names,
    label_column='cluster_label',
    color_map=COLOR_MAP,
    title=None,
    y_max=4500
):
    subset = df.dropna(subset=feature_names + [label_column]).sort_index()
    if subset.empty:
        ax.set_title(title or '')
        return

    x = subset.index.to_numpy()

    for c in feature_names:
        y = subset[c].to_numpy(dtype=float)
        if len(y) < 2:
            continue
        points = np.column_stack([x, y])
        segments = np.stack([points[:-1], points[1:]], axis=1)
        seg_labels = subset[label_column].astype(int).to_numpy()[:-1]
        seg_colors = [color_map.get(lbl, 'gray') for lbl in seg_labels]
        lc = LineCollection(segments, colors=seg_colors, linewidths=1.5, alpha=0.95, zorder=2)
        ax.add_collection(lc)

    labels_present = sorted(subset[label_column].dropna().astype(int).unique())
    legend_handles = [
        Line2D([0], [0], color=color_map.get(lab, 'gray'), lw=2, label=f'label={lab}')
        for lab in labels_present
    ]
    ax.legend(handles=legend_handles, loc='upper left', fontsize=12)

    ax.grid(True, alpha=0.3)
    ax.set_title(title or '', fontsize=18)
    ax.tick_params(axis='y', labelsize=14)
    ax.tick_params(axis='x', labelsize=12)
    if y_max is not None:
        ax.set_ylim(0, y_max)
    ax.autoscale(enable=True, axis='x', tight=False)

def pdf_plot_cluster_lines(
	features_df,
	period_types_set,
	feature_names,
	filename,
	prob_threshold=0.5
):
	all_result_df = pd.DataFrame()
	with PdfPages(filename) as pdf:
		for target_period_type in period_types_set:
			query_df = features_df.query(f"period_type == '{target_period_type}'").reset_index(drop=True)
			fig, axes = plt.subplots(3, 1, figsize=(16, 14), sharex=False)
			plot_cluster_lines(
				ax=axes[0],
				df=query_df,
				feature_names=feature_names,
				label_column='cluster_label',
				title=f'周期类型：{target_period_type}',
				y_max=4500
			)

			plt.tight_layout(pad=2.0)
			pdf.savefig(fig, bbox_inches='tight')
			plt.close(fig)
	all_result_df.to_excel('LR_result.xlsx', index=False)
	print(f"PDF保存成功：{filename}")

def plot_comparison_with_markers(df, plt_cols, mark_col, mark_vals=None, 
                                 figsize=(16, 9), title_suffix=None):
    """
    通用数据对比图绘制函数，可标记指定值
    
    参数:
    df (pd.DataFrame): 包含数据的DataFrame
    plt_cols (list): 要绘制的数据列名列表
    mark_col (str): 用于标记的列名
    mark_vals (list): 需要标记的值列表
    figsize (tuple): 图表尺寸，默认为(16, 9)
    title_suffix (str): 图表标题后缀
    
    返回:
    str: 保存的文件路径或None
    """
    # 设置中文字体和图表清晰度
    plt.rcParams['font.sans-serif'] = ['Noto Sans CJK JP', 'SimHei', 'Microsoft YaHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['figure.dpi'] = 300
    
    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)
    
    # 为每条数据线绘制折线
    markers = ['o', 's', '^', 'd', 'v', '<', '>', 'p', '*', 'h']
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
              '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    
    for i, col in enumerate(plt_cols):
        ax.plot(
            range(len(df)), 
            df[col], 
            marker=markers[i % len(markers)], 
            label=col, 
            linewidth=2,
            color=colors[i % len(colors)],
            markersize=6,
            alpha=0.8
        )
    
    # 标记指定的值
    if mark_vals:
        # 获取要标记的值在DataFrame中的索引位置
        mark_indices = df[df[mark_col].isin(mark_vals)].index
        
        # 计算y轴范围，用于智能放置标注
        y_min, y_max = ax.get_ylim()
        y_range = y_max - y_min
        
        # 为每个标记点添加垂直参考线和标注
        for idx in mark_indices:
            # 添加垂直参考线
            ax.axvline(x=idx, color='red', linestyle='--', alpha=0.5, linewidth=1.5)
            
            # 添加标注文本
            mark_value = df.loc[idx, mark_col]
            
            # 计算标注位置 - 交替在图表上方和下方放置
            text_y_pos = y_max - (y_range * 0.05 * (idx % 2 + 1))
            
            ax.text(
                x=idx, 
                y=text_y_pos, 
                s=f"{mark_col}: {mark_value}", 
                rotation=45, 
                ha='center', 
                va='bottom' if idx % 2 == 0 else 'top',
                fontsize=9,
                fontweight='bold',
                bbox=dict(facecolor='yellow', alpha=0.9, edgecolor='red', boxstyle='round,pad=0.3')
            )
            
            # 在每条线上标记点
            for col in plt_cols:
                ax.plot(
                    idx, 
                    df.loc[idx, col], 
                    marker='*', 
                    markersize=14, 
                    color='gold',
                    markeredgecolor='black',
                    markeredgewidth=1.5,
                    zorder=10  # 确保标记点在最上层
                )
    
    # 设置图表标题和标签
    title = f"数据对比图 - {title_suffix}" if title_suffix else "数据对比图"
    ax.set_title(title, fontsize=16, fontweight='bold')
    ax.set_xlabel('样本索引', fontsize=12)
    ax.set_ylabel('数值', fontsize=12)
    
    # 添加图例和网格
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=len(plt_cols))
    ax.grid(True, alpha=0.3)
    
    # 调整x轴刻度，避免过于密集
    if len(df) > 20:
        ax.xaxis.set_major_locator(ticker.MaxNLocator(20))
    
    plt.tight_layout()
    
    # 保存图表
    if title_suffix:
        # 创建文件夹保存图表
        output_dir = 'data_plots'
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成文件名
        filename = f"{output_dir}/data_comparison_{title_suffix.replace(' ', '_')}.png"
        plt.savefig(filename, bbox_inches='tight', dpi=300)
        print(f"图表已保存为: {filename}")
    else:
        filename = None
    
    # 关闭图表，避免内存泄漏
    plt.close(fig)
    
    return filename