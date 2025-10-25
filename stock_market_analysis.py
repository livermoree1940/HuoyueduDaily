# stock_market_analysis.py
import akshare as ak
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta

# 中文环境
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


# ---------------------------- 数据获取 ---------------------------- #
def fetch_market_activity_data():
    """获取当日市场赚钱效应数据"""
    try:
        df = ak.stock_market_activity_legu()
        return df
    except Exception as e:
        print("获取数据失败：", e)
        return None


# ---------------------------- 数据存储 ---------------------------- #
def save_to_csv(df, filename=None):
    """保存到 CSV（自动追加）"""
    if filename is None:
        filename = f"market_activity_{datetime.now():%Y%m%d}.csv"

    df = df.copy()
    df['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    df['date'] = datetime.now().strftime('%Y-%m-%d')

    if os.path.exists(filename):
        old = pd.read_csv(filename)
        df = pd.concat([old, df], ignore_index=True)

    df.to_csv(filename, index=False, encoding='utf-8-sig')
    return filename


# ---------------------------- 数据加载 ---------------------------- #
def load_recent_data(days=60):
    """加载最近 N 天数据并做类型清洗"""
    files = [f for f in os.listdir('.') if f.startswith('market_activity_') and f.endswith('.csv')]
    if not files:
        return None

    latest = max(files, key=os.path.getmtime)
    try:
        df = pd.read_csv(latest)
        df['date'] = pd.to_datetime(df['date'])
        # 统一清洗：去 % 并转数值
        df['value'] = df['value'].astype(str).str.replace('%', '', regex=False)
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        cutoff = datetime.now() - timedelta(days=days)
        return df[df['date'] >= cutoff].copy()
    except Exception as e:
        print("加载历史数据失败：", e)
        return None


# ---------------------------- 可视化 ---------------------------- #
def create_visualizations(df, days=60):
    """画三张折线图：活跃度、上涨家数、真实涨停家数"""
    if df is None or df.empty:
        print("无数据可视化")
        return None

    df = df.sort_values('date')
    fig, axes = plt.subplots(3, 1, figsize=(12, 15))

    items = [
        ('活跃度', '市场活跃度 (%)', '#FF6B6B'),
        ('上涨', '上涨家数', '#4ECDC4'),
        ('真实涨停', '真实涨停家数', '#45B7D1')
    ]

    for ax, (item, ylabel, color) in zip(axes, items):
        sub = df[df['item'] == item].copy()
        if not sub.empty:
            ax.plot(sub['date'], sub['value'], marker='o', linewidth=2, markersize=4, color=color)
            ax.set_title(f'近{days}天{item}变化趋势', fontsize=14, fontweight='bold')
            ax.set_ylabel(ylabel)
            ax.grid(alpha=0.3)
            ax.tick_params(axis='x', rotation=45)

    plt.tight_layout()
    plot_file = f'market_activity_trends_{days}days.png'
    plt.savefig(plot_file, dpi=300, bbox_inches='tight')
    plt.close()
    return plot_file


# ---------------------------- 情绪分析 ---------------------------- #
def analyze_market_sentiment(df):
    """基于最新数据给出市场情绪"""
    if df is None or df.empty:
        return None

    latest = df[df['date'] == df['date'].max()]
    analysis = {
        'date': df['date'].max().strftime('%Y-%m-%d'),
        'total_stocks': 0,
        'rise_ratio': 0.,
        'activity_level': 0.,
        'limit_up_count': 0,
        'sentiment': '中性'
    }

    try:
        rise = int(latest[latest['item'] == '上涨']['value'].iloc[0])
        fall = int(latest[latest['item'] == '下跌']['value'].iloc[0])
        flat = int(latest[latest['item'] == '平盘']['value'].iloc[0])
        suspension = int(latest[latest['item'] == '停牌']['value'].iloc[0])
        total = rise + fall + flat + suspension
        analysis['total_stocks'] = total
        analysis['rise_ratio'] = round(rise / total * 100, 2) if total else 0.

        activity = latest[latest['item'] == '活跃度']['value']
        if not activity.empty:
            analysis['activity_level'] = round(float(activity.iloc[0]), 2)

        limit_up = latest[latest['item'] == '真实涨停']['value']
        if not limit_up.empty:
            analysis['limit_up_count'] = int(limit_up.iloc[0])

        # 情绪判定
        rr = analysis['rise_ratio']
        lu = analysis['limit_up_count']
        if rr > 60 and lu > 50:
            analysis['sentiment'] = '强势看多'
        elif rr > 50 and lu > 30:
            analysis['sentiment'] = '温和看多'
        elif rr < 40 and lu < 20:
            analysis['sentiment'] = '谨慎看空'
        else:
            analysis['sentiment'] = '中性震荡'
    except Exception as e:
        print("情绪分析出错：", e)
    return analysis


# ---------------------------- 主流程 ---------------------------- #
def main():
    print("开始获取赚钱效应数据...")
    df = fetch_market_activity_data()
    if df is None:
        print("数据获取失败，退出")
        return

    print(df.head())
    csv_file = save_to_csv(df)
    print("已保存 →", csv_file)

    recent_df = load_recent_data(60)
    if recent_df is not None:
        plot_file = create_visualizations(recent_df, 60)
        print("可视化已生成 →", plot_file)

        analysis = analyze_market_sentiment(recent_df)
        if analysis:
            print("\n=== 市场情绪分析 ===")
            print(f"分析日期: {analysis['date']}")
            print(f"总股票数: {analysis['total_stocks']}")
            print(f"上涨比例: {analysis['rise_ratio']}%")
            print(f"市场活跃度: {analysis['activity_level']}%")
            print(f"真实涨停家数: {analysis['limit_up_count']}")
            print(f"市场情绪: {analysis['sentiment']}")
    else:
        print("历史数据不足，仅保存当日数据")


# ---------------------------- 入口 ---------------------------- #
if __name__ == "__main__":
    main()