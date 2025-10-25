# stock_market_analysis.py
import akshare as ak
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from datetime import datetime, timedelta
import os
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def fetch_market_activity_data():
    """获取赚钱效应分析数据"""
    try:
        df = ak.stock_market_activity_legu()
        return df
    except Exception as e:
        print(f"获取数据失败: {e}")
        return None

def save_to_csv(df, filename=None):
    """保存数据到CSV文件"""
    if filename is None:
        filename = f"market_activity_{datetime.now().strftime('%Y%m%d')}.csv"
    
    # 添加时间戳
    df['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    df['date'] = datetime.now().strftime('%Y-%m-%d')
    
    # 如果文件已存在，则追加数据
    if os.path.exists(filename):
        existing_df = pd.read_csv(filename)
        combined_df = pd.concat([existing_df, df], ignore_index=True)
        combined_df.to_csv(filename, index=False, encoding='utf-8-sig')
    else:
        df.to_csv(filename, index=False, encoding='utf-8-sig')
    
    return filename
def load_recent_data(days=60, filename_pattern="market_activity_*.csv"):
    """加载最近N天的数据（修复版本）"""
    csv_files = [f for f in os.listdir('.') if f.startswith('market_activity_') and f.endswith('.csv')]
    
    if not csv_files:
        return None
    
    latest_file = max(csv_files, key=os.path.getmtime)
    
    try:
        df = pd.read_csv(latest_file)
        
        # 确保日期列正确转换[7](@ref)
        df['date'] = pd.to_datetime(df['date'])
        
        # 处理数值数据：移除百分比符号并转换为数值
        df['value'] = df['value'].astype(str).str.replace('%', '')
        # 使用to_numeric安全转换，错误值设为NaN[8](@ref)
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        
        # 获取最近N天的数据
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_df = df[df['date'] >= cutoff_date].copy()
        
        return recent_df
    except Exception as e:
        print(f"加载数据失败: {e}")
        return None

def create_visualizations(df, days=60):
    """创建三种指标的折线图"""
    if df is None or df.empty:
        print("没有可用的数据进行可视化")
        return
    
    # 确保数据按日期排序
    df = df.sort_values('date')
    
    # 创建三个子图
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 15))
    
    # 1. 活跃度折线图
    activity_data = df[df['item'] == '活跃度'].copy()
    if not activity_data.empty:
        activity_data['value'] = activity_data['value'].str.rstrip('%').astype(float)
        ax1.plot(activity_data['date'], activity_data['value'], 
                marker='o', linewidth=2, markersize=4, color='#FF6B6B')
        ax1.set_title(f'近{days}天市场活跃度变化趋势', fontsize=14, fontweight='bold')
        ax1.set_ylabel('活跃度 (%)')
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
    
    # 2. 上涨家数折线图
    rise_data = df[df['item'] == '上涨'].copy()
    if not rise_data.empty:
        ax2.plot(rise_data['date'], rise_data['value'], 
                marker='s', linewidth=2, markersize=4, color='#4ECDC4')
        ax2.set_title(f'近{days}天上涨家数变化趋势', fontsize=14, fontweight='bold')
        ax2.set_ylabel('上涨家数')
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(axis='x', rotation=45)
    
    # 3. 涨停家数折线图（真实涨停）
    limit_up_data = df[df['item'] == '真实涨停'].copy()
    if not limit_up_data.empty:
        ax3.plot(limit_up_data['date'], limit_up_data['value'], 
                marker='^', linewidth=2, markersize=4, color='#45B7D1')
        ax3.set_title(f'近{days}天真实涨停家数变化趋势', fontsize=14, fontweight='bold')
        ax3.set_ylabel('涨停家数')
        ax3.set_xlabel('日期')
        ax3.grid(True, alpha=0.3)
        ax3.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    
    # 保存图片
    plot_filename = f'market_activity_trends_{days}days.png'
    plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    return plot_filename
def analyze_market_sentiment(df):
    """分析市场情绪（修复版本）"""
    if df is None or df.empty:
        return None
    
    # 确保使用最新数据
    latest_data = df[df['date'] == df['date'].max()]
    
    analysis = {
        'date': df['date'].max().strftime('%Y-%m-%d'),
        'total_stocks': 0,
        'rise_ratio': 0,
        'activity_level': 0,
        'limit_up_count': 0,
        'sentiment': '中性'
    }
    
    try:
        # 首先确保数据类型正确
        # 将数值列从字符串转换为浮点数[6](@ref)[8](@ref)
        for col in ['value']:
            if col in latest_data.columns:
                # 移除百分比符号并转换为数值
                latest_data.loc[:, 'value'] = latest_data['value'].astype(str).str.replace('%', '').astype(float)
        
        # 分别提取各项数据
        rise_data = latest_data[latest_data['item'] == '上涨']['value']
        fall_data = latest_data[latest_data['item'] == '下跌']['value']
        flat_data = latest_data[latest_data['item'] == '平盘']['value']
        suspension_data = latest_data[latest_data['item'] == '停牌']['value']
        
        # 确保数据不为空再进行计算
        if not rise_data.empty and not fall_data.empty and not flat_data.empty and not suspension_data.empty:
            rise = float(rise_data.iloc
            fall = float(fall_data.iloc
            flat = float(flat_data.iloc
            suspension = float(suspension_data.iloc
            
            total = rise + fall + flat + suspension
            analysis['total_stocks'] = total
            analysis['rise_ratio'] = round(rise / total * 100, 2) if total > 0 else 0
        
        # 获取活跃度（处理百分比）
        activity_data = latest_data[latest_data['item'] == '活跃度']['value']
        if not activity_data.empty:
            analysis['activity_level'] = float(activity_data.iloc
        
        # 获取涨停家数
        limit_up_data = latest_data[latest_data['item'] == '真实涨停']['value']
        if not limit_up_data.empty:
            analysis['limit_up_count'] = float(limit_up_data.iloc
        
        # 基于修复后的数据判断市场情绪
        if analysis['rise_ratio'] > 60 and analysis['limit_up_count'] > 50:
            analysis['sentiment'] = '强势看多'
        elif analysis['rise_ratio'] > 50 and analysis['limit_up_count'] > 30:
            analysis['sentiment'] = '温和看多'
        elif analysis['rise_ratio'] < 40 and analysis['limit_up_count'] < 20:
            analysis['sentiment'] = '谨慎看空'
        else:
            analysis['sentiment'] = '中性震荡'
            
    except Exception as e:
        print(f"分析市场情绪时出错: {e}")
        # 打印详细错误信息便于调试
        import traceback
        traceback.print_exc()
    
    return analysis

def main():
    """主函数"""
    print("开始获取赚钱效应分析数据...")
    
    # 获取当前数据
    df = fetch_market_activity_data()
    if df is not None:
        print("数据获取成功!")
        print(df)
        
        # 保存数据
        csv_file = save_to_csv(df)
        print(f"数据已保存到: {csv_file}")
        
        # 加载最近60天数据
        recent_df = load_recent_data(60)
        
        if recent_df is not None:
            # 创建可视化图表
            plot_file = create_visualizations(recent_df, 60)
            print(f"可视化图表已保存到: {plot_file}")
            
            # 分析市场情绪
            analysis = analyze_market_sentiment(recent_df)
            if analysis:
                print("\n=== 市场情绪分析 ===")
                print(f"分析日期: {analysis['date']}")
                print(f"总股票数量: {analysis['total_stocks']}")
                print(f"上涨比例: {analysis['rise_ratio']}%")
                print(f"市场活跃度: {analysis['activity_level']}")
                print(f"真实涨停家数: {analysis['limit_up_count']}")
                print(f"市场情绪: {analysis['sentiment']}")
        else:
            print("没有足够的历史数据进行可视化分析")
    else:
        print("数据获取失败，请检查网络连接或接口状态")

if __name__ == "__main__":
    main()
