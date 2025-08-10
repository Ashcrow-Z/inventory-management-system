import pandas as pd
import numpy as np
from config import DATA_FILES

def generate_simple_report():
    """生成简单的库存管理报告"""
    print("🚀 开始生成简单库存管理报告...")
    
    # 加载数据
    inventory_df = pd.read_csv(DATA_FILES['inventory'])
    products_df = pd.read_csv(DATA_FILES['products'])
    sales_df = pd.read_csv(DATA_FILES['sales_records'])
    
    # 合并数据
    merged_df = inventory_df.merge(products_df, on='product_id', how='left')
    
    # 计算销售统计
    sales_stats = sales_df.groupby('product_id').agg({
        'quantity_sold': ['mean', 'max', 'sum', 'count']
    }).round(2)
    sales_stats.columns = ['avg_daily_sales', 'max_daily_sales', 'total_sales', 'sales_days']
    
    # 识别低库存商品
    low_stock_df = merged_df[merged_df['current_stock'] < merged_df['safety_stock']].copy()
    low_stock_df = low_stock_df.merge(sales_stats, left_index=True, right_index=True, how='left')
    low_stock_df['out_of_stock_risk'] = ((low_stock_df['safety_stock'] - low_stock_df['current_stock']) / 
                                        low_stock_df['safety_stock'] * 100)
    
    # 识别高库存商品
    high_stock_df = merged_df[merged_df['current_stock'] > merged_df['safety_stock'] * 2].copy()
    high_stock_df = high_stock_df.merge(sales_stats, left_index=True, right_index=True, how='left')
    high_stock_df['overstock_risk'] = ((high_stock_df['current_stock'] - high_stock_df['safety_stock']) / 
                                      high_stock_df['safety_stock'] * 100)
    
    # 按风险排序
    low_stock_df = low_stock_df.sort_values('out_of_stock_risk', ascending=False)
    high_stock_df = high_stock_df.sort_values('overstock_risk', ascending=False)
    
    # 生成报告
    report = f"""# 库存管理报告

## 执行摘要

### 总体库存状况
当前库存健康状况显示为"需要关注"。本报告周期内，我们发现{len(low_stock_df)}个商品低于安全库存水平，其中{len(low_stock_df[low_stock_df['out_of_stock_risk'] > 70])}个商品的缺货风险高于70%，表明这些商品存在较高的断货风险。同时，有{len(high_stock_df)}个商品库存积压严重，其中{len(high_stock_df[high_stock_df['overstock_risk'] > 200])}个商品积压超过安全库存2倍。

### 关键发现与建议
- **低库存商品**：立即对缺货风险高于70%的商品进行紧急补货，以避免断货和销售损失。
- **高库存商品**：考虑采取促销活动以减少库存积压，同时分析销售趋势，调整采购计划。
- **库存结构**：整体库存结构存在不平衡，需要根据销量和季节性因素优化库存水平。

## 详细库存分析

### 低库存商品分析 (共{len(low_stock_df)}个商品)

| 商品编号 | 商品名称 | 当前库存 | 安全库存 | 缺货风险 | 类别 | 风险等级 |
|----------|----------|----------|----------|----------|------|----------|
"""
    
    # 添加低库存商品
    for _, row in low_stock_df.iterrows():
        risk_level = "🔴" if row['out_of_stock_risk'] > 70 else "🟡" if row['out_of_stock_risk'] > 40 else "🟢"
        report += f"| {row['product_id']} | {row['name']} | {row['current_stock']} | {row['safety_stock']:.1f} | {row['out_of_stock_risk']:.1f}% | {row['category']} | {risk_level} |\n"
    
    report += f"""

**说明**：🔴 高风险(>70%)，🟡 中风险(40-70%)，🟢 低风险(<40%)

### 高库存商品分析 (共{len(high_stock_df)}个商品)

| 商品编号 | 商品名称 | 当前库存 | 安全库存 | 积压风险 | 类别 | 风险等级 |
|----------|----------|----------|----------|----------|------|----------|
"""
    
    # 添加高库存商品
    for _, row in high_stock_df.iterrows():
        risk_level = "🔴" if row['overstock_risk'] > 200 else "🟡" if row['overstock_risk'] > 100 else "🟢"
        report += f"| {row['product_id']} | {row['name']} | {row['current_stock']} | {row['safety_stock']:.1f} | {row['overstock_risk']:.1f}% | {row['category']} | {risk_level} |\n"
    
    report += f"""

**说明**：🔴 高风险(>200%)，🟡 中风险(100-200%)，🟢 低风险(<100%)

## 补货与促销策略

### 补货建议

| 商品编号 | 商品名称 | 建议补货量 | 优先级 | 补货时间 | 补货原因 |
|----------|----------|------------|--------|----------|----------|
"""
    
    # 生成补货建议
    replenishment_df = low_stock_df[low_stock_df['out_of_stock_risk'] > 40].copy()
    for _, row in replenishment_df.iterrows():
        priority = "🔴 紧急" if row['out_of_stock_risk'] > 70 else "🟡 高" if row['out_of_stock_risk'] > 50 else "🟢 中"
        amount = int((row['safety_stock'] - row['current_stock']) * 1.2)
        timeline = "48小时内" if row['out_of_stock_risk'] > 70 else "7天内" if row['out_of_stock_risk'] > 50 else "14天内"
        report += f"| {row['product_id']} | {row['name']} | {amount} | {priority} | {timeline} | 缺货风险{row['out_of_stock_risk']:.1f}% |\n"
    
    report += f"""

### 促销策略

| 商品编号 | 商品名称 | 促销方式 | 折扣率 | 促销时间 | 促销原因 |
|----------|----------|----------|--------|----------|----------|
"""
    
    # 生成促销建议
    promotion_df = high_stock_df[high_stock_df['overstock_risk'] > 100].copy()
    for _, row in promotion_df.iterrows():
        priority = "🔴 紧急" if row['overstock_risk'] > 200 else "🟡 高" if row['overstock_risk'] > 150 else "🟢 中"
        discount = "30%" if row['overstock_risk'] > 200 else "20%" if row['overstock_risk'] > 150 else "15%"
        duration = "立即" if row['overstock_risk'] > 200 else "1周内" if row['overstock_risk'] > 150 else "2周内"
        report += f"| {row['product_id']} | {row['name']} | 限时折扣 | {discount} | {duration} | 积压风险{row['overstock_risk']:.1f}% |\n"
    
    report += f"""

## 总结

本报告基于实时数据分析，提供了详细的库存状况和相应的管理建议。建议管理层根据报告内容制定相应的补货和促销策略，以优化库存结构，提高资金使用效率。

**关键数据统计：**
- 总商品数：{len(merged_df)}
- 低库存商品：{len(low_stock_df)}个
- 高库存商品：{len(high_stock_df)}个
- 高风险低库存：{len(low_stock_df[low_stock_df['out_of_stock_risk'] > 70])}个
- 高风险高库存：{len(high_stock_df[high_stock_df['overstock_risk'] > 200])}个
"""
    
    # 保存报告
    with open('simple_inventory_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ 简单报告已保存到 simple_inventory_report.md")
    print(f"📊 统计：{len(low_stock_df)}个低库存商品，{len(high_stock_df)}个高库存商品")
    
    return report

if __name__ == "__main__":
    generate_simple_report()
