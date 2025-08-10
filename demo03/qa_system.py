import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import json
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class InventoryQASystem:
    def __init__(self):
        """初始化问答系统"""
        from config import MODEL_CONFIG
        from prompts import QA_SYSTEM_MESSAGE, QA_PROMPT_TEMPLATE
        
        self.llm = ChatOpenAI(
            model_name=MODEL_CONFIG["model_name"],
            openai_api_base=MODEL_CONFIG["openai_api_base"],
            openai_api_key=MODEL_CONFIG["openai_api_key"],
            temperature=MODEL_CONFIG["temperature"]
        )
        
        self.system_message = QA_SYSTEM_MESSAGE
        self.prompt_template = QA_PROMPT_TEMPLATE
        
        # 加载数据
        self.load_data()
        
    def load_data(self):
        """加载所有数据文件"""
        from config import DATA_FILES
        
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
    
    def analyze_data(self, question):
        """分析数据并生成回复"""
        # 准备数据摘要
        data_summary = self._prepare_data_summary()
        
        # 生成图表
        charts_info = self._generate_charts(question)
        
        # 构建提示词
        prompt = self.prompt_template.format(
            question=question,
            data_summary=data_summary,
            charts_info=charts_info
        )
        
        # 调用LLM
        messages = [
            SystemMessage(content=self.system_message),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content, charts_info
    
    def _prepare_data_summary(self):
        """准备数据摘要"""
        summary = f"""
        数据概览：
        - 总商品数：{len(self.products_df)}
        - 商品类别：{', '.join(self.products_df['category'].unique())}
        - 销售记录数：{len(self.sales_df)}
        - 销售日期范围：{self.sales_df['date'].min()} 到 {self.sales_df['date'].max()}
        
        库存状况：
        - 低库存商品（当前库存 < 安全库存）：{len(self.merged_df[self.merged_df['current_stock'] < self.merged_df['safety_stock']])}个
        - 缺货商品（当前库存 = 0）：{len(self.merged_df[self.merged_df['current_stock'] == 0])}个
        - 平均库存水平：{self.merged_df['current_stock'].mean():.0f}
        
        销售统计：
        - 平均日销量：{self.sales_df['quantity_sold'].mean():.1f}
        - 最高日销量：{self.sales_df['quantity_sold'].max()}
        - 总销量：{self.sales_df['quantity_sold'].sum()}
        """
        return summary
    
    def _generate_charts(self, question):
        """根据问题生成相关图表"""
        charts_info = []
        
        # 创建图表目录
        os.makedirs('charts', exist_ok=True)
        
        # 根据问题关键词生成不同类型的图表
        question_lower = question.lower()
        
        # 1. 库存分布图
        if any(keyword in question_lower for keyword in ['库存', 'stock', '分布', 'distribution']):
            chart_path = self._create_inventory_distribution_chart()
            charts_info.append({
                'type': '库存分布',
                'path': chart_path,
                'description': '显示各商品的当前库存与安全库存对比'
            })
        
        # 2. 销售趋势图
        if any(keyword in question_lower for keyword in ['销售', 'sale', '趋势', 'trend', '销量']):
            chart_path = self._create_sales_trend_chart()
            charts_info.append({
                'type': '销售趋势',
                'path': chart_path,
                'description': '显示过去30天的销售趋势'
            })
        
        # 3. 类别分析图
        if any(keyword in question_lower for keyword in ['类别', 'category', '分类']):
            chart_path = self._create_category_analysis_chart()
            charts_info.append({
                'type': '类别分析',
                'path': chart_path,
                'description': '按商品类别分析库存和销售情况'
            })
        
        # 4. 低库存商品图
        if any(keyword in question_lower for keyword in ['低库存', '缺货', 'out of stock', '不足']):
            chart_path = self._create_low_stock_chart()
            charts_info.append({
                'type': '低库存商品',
                'path': chart_path,
                'description': '显示库存低于安全库存的商品'
            })
        
        # 5. 利润率分析图
        if any(keyword in question_lower for keyword in ['利润', 'profit', '收益', '收入']):
            chart_path = self._create_profit_analysis_chart()
            charts_info.append({
                'type': '利润率分析',
                'path': chart_path,
                'description': '分析各商品的利润率情况'
            })
        
        # 如果没有匹配的关键词，生成综合图表
        if not charts_info:
            chart_path = self._create_overview_chart()
            charts_info.append({
                'type': '综合概览',
                'path': chart_path,
                'description': '显示库存和销售的综合情况'
            })
        
        return charts_info
    
    def _create_inventory_distribution_chart(self):
        """创建库存分布图"""
        plt.figure(figsize=(12, 6))
        
        # 选择前20个商品进行展示
        sample_df = self.merged_df.head(20)
        
        x = range(len(sample_df))
        width = 0.35
        
        plt.bar([i - width/2 for i in x], sample_df['current_stock'], 
                width, label='当前库存', alpha=0.8, color='skyblue')
        plt.bar([i + width/2 for i in x], sample_df['safety_stock'], 
                width, label='安全库存', alpha=0.8, color='lightcoral')
        
        plt.xlabel('商品')
        plt.ylabel('库存数量')
        plt.title('库存分布对比图')
        plt.legend()
        plt.xticks(x, sample_df['product_id'], rotation=45)
        plt.tight_layout()
        
        chart_path = 'charts/inventory_distribution.png'
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def _create_sales_trend_chart(self):
        """创建销售趋势图"""
        plt.figure(figsize=(12, 6))
        
        # 按日期汇总销售数据
        daily_sales = self.sales_df.groupby('date')['quantity_sold'].sum().reset_index()
        daily_sales['date'] = pd.to_datetime(daily_sales['date'])
        daily_sales = daily_sales.sort_values('date')
        
        plt.plot(daily_sales['date'], daily_sales['quantity_sold'], 
                marker='o', linewidth=2, markersize=4)
        plt.xlabel('日期')
        plt.ylabel('日销量')
        plt.title('销售趋势图')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        chart_path = 'charts/sales_trend.png'
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def _create_category_analysis_chart(self):
        """创建类别分析图"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # 按类别统计库存
        category_inventory = self.merged_df.groupby('category').agg({
            'current_stock': 'sum',
            'safety_stock': 'sum'
        }).reset_index()
        
        # 库存对比
        x = range(len(category_inventory))
        width = 0.35
        ax1.bar([i - width/2 for i in x], category_inventory['current_stock'], 
                width, label='当前库存', alpha=0.8, color='skyblue')
        ax1.bar([i + width/2 for i in x], category_inventory['safety_stock'], 
                width, label='安全库存', alpha=0.8, color='lightcoral')
        ax1.set_xlabel('商品类别')
        ax1.set_ylabel('库存数量')
        ax1.set_title('各类别库存对比')
        ax1.legend()
        ax1.set_xticks(x)
        ax1.set_xticklabels(category_inventory['category'], rotation=45)
        
        # 按类别统计销量
        category_sales = self.sales_df.merge(self.products_df[['product_id', 'category']], 
                                           on='product_id').groupby('category')['quantity_sold'].sum()
        
        ax2.pie(category_sales.values, labels=category_sales.index, autopct='%1.1f%%')
        ax2.set_title('各类别销量占比')
        
        plt.tight_layout()
        
        chart_path = 'charts/category_analysis.png'
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def _create_low_stock_chart(self):
        """创建低库存商品图"""
        plt.figure(figsize=(12, 6))
        
        # 找出低库存商品
        low_stock_df = self.merged_df[self.merged_df['current_stock'] < self.merged_df['safety_stock']].head(15)
        
        # 计算缺货风险
        low_stock_df['stockout_risk'] = ((low_stock_df['safety_stock'] - low_stock_df['current_stock']) / 
                                        low_stock_df['safety_stock'] * 100)
        
        # 按缺货风险排序
        low_stock_df = low_stock_df.sort_values('stockout_risk', ascending=False)
        
        colors = ['red' if risk > 70 else 'orange' if risk > 40 else 'yellow' 
                 for risk in low_stock_df['stockout_risk']]
        
        bars = plt.bar(range(len(low_stock_df)), low_stock_df['stockout_risk'], 
                      color=colors, alpha=0.8)
        
        plt.xlabel('商品')
        plt.ylabel('缺货风险 (%)')
        plt.title('低库存商品缺货风险分析')
        plt.xticks(range(len(low_stock_df)), low_stock_df['product_id'], rotation=45)
        
        # 添加数值标签
        for i, bar in enumerate(bars):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%', ha='center', va='bottom')
        
        plt.tight_layout()
        
        chart_path = 'charts/low_stock_analysis.png'
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def _create_profit_analysis_chart(self):
        """创建利润率分析图"""
        plt.figure(figsize=(12, 6))
        
        # 计算利润率
        self.merged_df['profit_margin'] = ((self.merged_df['selling_price'] - self.merged_df['cost_price']) / 
                                          self.merged_df['selling_price'] * 100)
        
        # 按类别统计平均利润率
        category_profit = self.merged_df.groupby('category')['profit_margin'].mean().sort_values(ascending=False)
        
        bars = plt.bar(range(len(category_profit)), category_profit.values, 
                      color='lightgreen', alpha=0.8)
        
        plt.xlabel('商品类别')
        plt.ylabel('平均利润率 (%)')
        plt.title('各类别平均利润率')
        plt.xticks(range(len(category_profit)), category_profit.index, rotation=45)
        
        # 添加数值标签
        for i, bar in enumerate(bars):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%', ha='center', va='bottom')
        
        plt.tight_layout()
        
        chart_path = 'charts/profit_analysis.png'
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def _create_overview_chart(self):
        """创建综合概览图"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # 1. 库存vs安全库存散点图
        ax1.scatter(self.merged_df['safety_stock'], self.merged_df['current_stock'], 
                   alpha=0.6, color='blue')
        ax1.plot([0, self.merged_df['safety_stock'].max()], 
                [0, self.merged_df['safety_stock'].max()], 'r--', alpha=0.8)
        ax1.set_xlabel('安全库存')
        ax1.set_ylabel('当前库存')
        ax1.set_title('库存vs安全库存')
        
        # 2. 销量分布直方图
        ax2.hist(self.sales_df['quantity_sold'], bins=30, alpha=0.7, color='green')
        ax2.set_xlabel('日销量')
        ax2.set_ylabel('频次')
        ax2.set_title('销量分布')
        
        # 3. 类别商品数量
        category_counts = self.products_df['category'].value_counts()
        ax3.pie(category_counts.values, labels=category_counts.index, autopct='%1.1f%%')
        ax3.set_title('商品类别分布')
        
        # 4. 库存状态饼图
        low_stock_count = len(self.merged_df[self.merged_df['current_stock'] < self.merged_df['safety_stock']])
        normal_stock_count = len(self.merged_df) - low_stock_count
        
        ax4.pie([low_stock_count, normal_stock_count], 
                labels=['低库存', '正常库存'], autopct='%1.1f%%',
                colors=['orange', 'lightblue'])
        ax4.set_title('库存状态分布')
        
        plt.tight_layout()
        
        chart_path = 'charts/overview.png'
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def ask_question(self, question):
        """主问答接口"""
        print(f"🤔 问题: {question}")
        print("="*50)
        
        try:
            # 分析数据并生成回复
            text_response, charts_info = self.analyze_data(question)
            
            # 输出文字回复
            print("📝 回答:")
            print(text_response)
            print("\n" + "="*50)
            
            # 输出图表信息
            if charts_info:
                print("📊 生成的图表:")
                for chart in charts_info:
                    print(f"  - {chart['type']}: {chart['path']}")
                    print(f"    描述: {chart['description']}")
            
            return text_response, charts_info
            
        except Exception as e:
            error_msg = f"❌ 处理问题时出错: {str(e)}"
            print(error_msg)
            return error_msg, []

def main():
    """主函数 - 交互式问答"""
    print("🚀 库存管理智能问答系统")
    print("="*50)
    print("系统已加载，您可以询问关于库存、销售、商品等任何问题！")
    print("输入 'quit' 或 'exit' 退出系统")
    print("="*50)
    
    qa_system = InventoryQASystem()
    
    while True:
        try:
            question = input("\n💬 请输入您的问题: ").strip()
            
            if question.lower() in ['quit', 'exit', '退出']:
                print("👋 感谢使用，再见！")
                break
            
            if not question:
                print("❌ 请输入有效的问题")
                continue
            
            # 处理问题
            qa_system.ask_question(question)
            
        except KeyboardInterrupt:
            print("\n👋 感谢使用，再见！")
            break
        except Exception as e:
            print(f"❌ 系统错误: {str(e)}")

if __name__ == "__main__":
    main() 