from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
from prompts import (
    format_analyst_prompt, 
    format_strategy_prompt, 
    format_report_prompt,
    ANALYST_SYSTEM_MESSAGE,
    STRATEGY_SYSTEM_MESSAGE,
    REPORT_SYSTEM_MESSAGE
)
from config import MODEL_CONFIG, DATA_FILES, SAFETY_STOCK_CONFIG, SAMPLE_DATA_CONFIG, REPORT_CONFIG

# 使用配置创建LLM实例
llm = ChatOpenAI(
    model_name=MODEL_CONFIG["model_name"],
    openai_api_base=MODEL_CONFIG["openai_api_base"],
    openai_api_key=MODEL_CONFIG["openai_api_key"],
    temperature=MODEL_CONFIG["temperature"]
)

# 修正后的示例数据生成函数（使用numpy代替pd.np）
def generate_sample_data():
    # 创建销售记录数据
    products = [f"P{i:03d}" for i in range(1, SAMPLE_DATA_CONFIG['num_products'] + 1)]
    dates = pd.date_range(end=pd.Timestamp.now(), periods=SAMPLE_DATA_CONFIG['date_range_days'], freq='D')
    
    sales_data = []
    for product in products:
        avg_sales = np.random.randint(5, 100)
        volatility = np.random.uniform(0.2, 0.8)
        for date in dates:
            sales = max(0, np.random.normal(avg_sales, avg_sales * volatility))
            sales_data.append({
                'product_id': product,
                'date': date.strftime('%Y-%m-%d'),
                'quantity_sold': round(sales)
            })
    
    sales_df = pd.DataFrame(sales_data)
    sales_df.to_csv(DATA_FILES['sales_records'], index=False)
    
    # 创建商品信息数据
    categories = SAMPLE_DATA_CONFIG['categories']
    product_info = []
    
    for product in products:
        category = np.random.choice(categories)
        cost = round(np.random.uniform(5, 200), 2)
        price = round(cost * np.random.uniform(1.2, 3), 2)
        supplier_lead_time = np.random.randint(3, 15)
        
        product_info.append({
            'product_id': product,
            'name': f'{category}商品{product[1:]}',
            'category': category,
            'cost_price': cost,
            'selling_price': price,
            'supplier_lead_time': supplier_lead_time
        })
    
    products_df = pd.DataFrame(product_info)
    products_df.to_csv(DATA_FILES['products'], index=False)
    
    # 创建库存数据
    inventory_data = []
    
    for product in products:
        recent_sales = sales_df[sales_df['product_id'] == product].tail(30)
        avg_daily_sales = recent_sales['quantity_sold'].mean()
        max_daily_sales = recent_sales['quantity_sold'].max()
        
        # 随机确定商品类型（稳定或波动）
        is_stable = np.random.choice([True, False])
        safety_stock = avg_daily_sales * SAFETY_STOCK_CONFIG['stable_product_multiplier'] if is_stable else max_daily_sales * SAFETY_STOCK_CONFIG['volatile_product_multiplier']
        
        # 让一些商品处于低库存状态
        if np.random.random() < SAMPLE_DATA_CONFIG['low_stock_probability']:
            current_stock = np.random.randint(0, int(safety_stock * 0.7))
        else:
            current_stock = np.random.randint(int(safety_stock * 1.2), int(safety_stock * 3))
        
        inventory_data.append({
            'product_id': product,
            'current_stock': current_stock,
            'safety_stock': safety_stock,
            'last_updated': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    inventory_df = pd.DataFrame(inventory_data)
    inventory_df.to_csv(DATA_FILES['inventory'], index=False)
    
    print("示例数据已生成")

if __name__ == "__main__":
    # 生成示例数据
    generate_sample_data()