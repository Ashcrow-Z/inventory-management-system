import pandas as pd
import numpy as np
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import json
import os
from config import MODEL_CONFIG, DATA_FILES

class CompactReportGenerator:
    def __init__(self):
        """初始化简洁报告生成器"""
        from prompts import (
            ANALYST_SYSTEM_MESSAGE, 
            STRATEGY_SYSTEM_MESSAGE, 
            REPORT_SYSTEM_MESSAGE,
            format_strategy_prompt,
            format_report_prompt
        )
        
        self.llm = ChatOpenAI(
            model_name=MODEL_CONFIG["model_name"],
            openai_api_base=MODEL_CONFIG["openai_api_base"],
            openai_api_key=MODEL_CONFIG["openai_api_key"],
            temperature=MODEL_CONFIG["temperature"]
        )
        
        self.analyst_system_message = ANALYST_SYSTEM_MESSAGE
        self.strategy_system_message = STRATEGY_SYSTEM_MESSAGE
        self.report_system_message = REPORT_SYSTEM_MESSAGE
        self.format_strategy_prompt = format_strategy_prompt
        self.format_report_prompt = format_report_prompt
        
        # 加载数据
        self.load_data()
        
    def load_data(self):
        """加载所有数据文件"""
        try:
            self.inventory_df = pd.read_csv(DATA_FILES['inventory'])
            self.products_df = pd.read_csv(DATA_FILES['products'])
            self.sales_df = pd.read_csv(DATA_FILES['sales_records'])
            
            # 合并数据
            self.merged_df = self.inventory_df.merge(
                self.products_df, on='product_id', how='left'
            )
            
            # 计算销售统计
            self.sales_stats = self.sales_df.groupby('product_id').agg({
                'quantity_sold': ['mean', 'max', 'sum', 'count']
            }).round(2)
            self.sales_stats.columns = ['avg_daily_sales', 'max_daily_sales', 'total_sales', 'sales_days']
            
            print("✅ 数据加载成功")
            
        except Exception as e:
            print(f"❌ 数据加载失败: {e}")
            raise
    
    def generate_compact_report(self):
        """生成简洁的库存管理报告"""
        print("🚀 开始生成简洁库存管理报告...")
        
        # 1. 分析数据
        low_stock_df = self.merged_df[self.merged_df['current_stock'] < self.merged_df['safety_stock']].copy()
        high_stock_df = self.merged_df[self.merged_df['current_stock'] > self.merged_df['safety_stock'] * 2].copy()
        
        # 计算风险指数
        low_stock_df['out_of_stock_risk'] = ((low_stock_df['safety_stock'] - low_stock_df['current_stock']) / 
                                            low_stock_df['safety_stock'] * 100)
        high_stock_df['overstock_risk'] = ((high_stock_df['current_stock'] - high_stock_df['safety_stock']) / 
                                          high_stock_df['safety_stock'] * 100)
        
        # 2. 生成报告内容
        report_content = self._generate_report_content(low_stock_df, high_stock_df)
        
        # 3. 保存报告
        with open('compact_inventory_report.md', 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print("✅ 简洁报告已保存到 compact_inventory_report.md")
        return report_content
    
    def _generate_report_content(self, low_stock_df, high_stock_df):
        """生成报告内容"""
        
        # 统计信息
        total_products = len(self.merged_df)
        low_stock_count = len(low_stock_df)
        high_stock_count = len(high_stock_df)
        critical_low = len(low_stock_df[low_stock_df['out_of_stock_risk'] > 70])
        critical_high = len(high_stock_df[high_stock_df['overstock_risk'] > 200])
        
        # 生成低库存表格
        low_stock_table = self._generate_low_stock_table(low_stock_df)
        
        # 生成高库存表格
        high_stock_table = self._generate_high_stock_table(high_stock_df)
        
        # 生成补货建议
        replenishment_table = self._generate_replenishment_table(low_stock_df)
        
        # 生成促销建议
        promotion_table = self._generate_promotion_table(high_stock_df)
        
        # 组装完整报告
        report = f"""# 库存管理报告

## 执行摘要

### 总体库存状况
当前库存健康状况显示为"需要关注"。本报告周期内，我们发现{low_stock_count}个商品低于安全库存水平，其中{critical_low}个商品的缺货风险高于70%，表明这些商品存在较高的断货风险。同时，有{high_stock_count}个商品库存积压严重，其中{critical_high}个商品积压超过安全库存2倍。

### 关键发现与建议
- **低库存商品**：立即对缺货风险高于70%的商品进行紧急补货，以避免断货和销售损失。
- **高库存商品**：考虑采取促销活动以减少库存积压，同时分析销售趋势，调整采购计划。
- **库存结构**：整体库存结构存在不平衡，需要根据销量和季节性因素优化库存水平。

## 详细库存分析

### 低库存商品分析

{low_stock_table}

### 高库存商品分析

{high_stock_table}

## 补货与促销策略

### 补货建议

{replenishment_table}

### 促销策略

{promotion_table}

## 总结

本报告基于实时数据分析，提供了详细的库存状况和相应的管理建议。建议管理层根据报告内容制定相应的补货和促销策略，以优化库存结构，提高资金使用效率。
"""
        
        return report
    
    def _generate_low_stock_table(self, low_stock_df):
        """生成低库存商品表格"""
        if len(low_stock_df) == 0:
            return "**无低库存商品**"
        
        # 按缺货风险排序
        low_stock_df = low_stock_df.sort_values('out_of_stock_risk', ascending=False)
        
        table_rows = []
        for _, row in low_stock_df.iterrows():
            risk_level = "🔴" if row['out_of_stock_risk'] > 70 else "🟡" if row['out_of_stock_risk'] > 40 else "🟢"
            table_rows.append(f"| {row['product_id']} | {row['name']} | {row['current_stock']} | {row['safety_stock']:.1f} | {row['out_of_stock_risk']:.1f}% | {row['category']} | {risk_level} |")
        
        table_content = "\n".join(table_rows)
        
        return f"""| 商品编号 | 商品名称 | 当前库存 | 安全库存 | 缺货风险 | 类别 | 风险等级 |
|----------|----------|----------|----------|----------|------|----------|
{table_content}

**说明**：🔴 高风险(>70%)，🟡 中风险(40-70%)，🟢 低风险(<40%)"""
    
    def _generate_high_stock_table(self, high_stock_df):
        """生成高库存商品表格"""
        if len(high_stock_df) == 0:
            return "**无高库存商品**"
        
        # 按积压风险排序
        high_stock_df = high_stock_df.sort_values('overstock_risk', ascending=False)
        
        table_rows = []
        for _, row in high_stock_df.iterrows():
            risk_level = "🔴" if row['overstock_risk'] > 200 else "🟡" if row['overstock_risk'] > 100 else "🟢"
            table_rows.append(f"| {row['product_id']} | {row['name']} | {row['current_stock']} | {row['safety_stock']:.1f} | {row['overstock_risk']:.1f}% | {row['category']} | {risk_level} |")
        
        table_content = "\n".join(table_rows)
        
        return f"""| 商品编号 | 商品名称 | 当前库存 | 安全库存 | 积压风险 | 类别 | 风险等级 |
|----------|----------|----------|----------|----------|------|----------|
{table_content}

**说明**：🔴 高风险(>200%)，🟡 中风险(100-200%)，🟢 低风险(<100%)"""
    
    def _generate_replenishment_table(self, low_stock_df):
        """生成补货建议表格"""
        if len(low_stock_df) == 0:
            return "**无需补货**"
        
        # 筛选需要补货的商品（缺货风险>40%）
        replenishment_df = low_stock_df[low_stock_df['out_of_stock_risk'] > 40].copy()
        replenishment_df = replenishment_df.sort_values('out_of_stock_risk', ascending=False)
        
        table_rows = []
        for _, row in replenishment_df.iterrows():
            priority = "🔴 紧急" if row['out_of_stock_risk'] > 70 else "🟡 高" if row['out_of_stock_risk'] > 50 else "🟢 中"
            amount = int((row['safety_stock'] - row['current_stock']) * 1.2)  # 建议补货量
            timeline = "48小时内" if row['out_of_stock_risk'] > 70 else "7天内" if row['out_of_stock_risk'] > 50 else "14天内"
            
            table_rows.append(f"| {row['product_id']} | {row['name']} | {amount} | {priority} | {timeline} | 缺货风险{row['out_of_stock_risk']:.1f}% |")
        
        table_content = "\n".join(table_rows)
        
        return f"""| 商品编号 | 商品名称 | 建议补货量 | 优先级 | 补货时间 | 补货原因 |
|----------|----------|------------|--------|----------|----------|
{table_content}"""
    
    def _generate_promotion_table(self, high_stock_df):
        """生成促销建议表格"""
        if len(high_stock_df) == 0:
            return "**无需促销**"
        
        # 筛选需要促销的商品（积压风险>100%）
        promotion_df = high_stock_df[high_stock_df['overstock_risk'] > 100].copy()
        promotion_df = promotion_df.sort_values('overstock_risk', ascending=False)
        
        table_rows = []
        for _, row in promotion_df.iterrows():
            priority = "🔴 紧急" if row['overstock_risk'] > 200 else "🟡 高" if row['overstock_risk'] > 150 else "🟢 中"
            discount = "30%" if row['overstock_risk'] > 200 else "20%" if row['overstock_risk'] > 150 else "15%"
            duration = "立即" if row['overstock_risk'] > 200 else "1周内" if row['overstock_risk'] > 150 else "2周内"
            
            table_rows.append(f"| {row['product_id']} | {row['name']} | 限时折扣 | {discount} | {duration} | 积压风险{row['overstock_risk']:.1f}% |")
        
        table_content = "\n".join(table_rows)
        
        return f"""| 商品编号 | 商品名称 | 促销方式 | 折扣率 | 促销时间 | 促销原因 |
|----------|----------|----------|--------|----------|----------|
{table_content}"""

def main():
    """主函数"""
    generator = CompactReportGenerator()
    report = generator.generate_compact_report()
    print("\n📊 简洁报告生成完成！")
    print("="*50)
    print(report[:500] + "..." if len(report) > 500 else report)

if __name__ == "__main__":
    main()

