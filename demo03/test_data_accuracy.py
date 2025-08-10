import pandas as pd
import numpy as np
from config import DATA_FILES

def test_data_accuracy():
    """测试数据准确性"""
    print("🔍 测试数据准确性...")
    
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
    
    # 1. 识别低库存商品
    low_stock_df = merged_df[merged_df['current_stock'] < merged_df['safety_stock']].copy()
    low_stock_df = low_stock_df.merge(sales_stats, left_index=True, right_index=True, how='left')
    
    # 计算缺货风险
    low_stock_df['out_of_stock_risk'] = ((low_stock_df['safety_stock'] - low_stock_df['current_stock']) / 
                                        low_stock_df['safety_stock'] * 100)
    
    # 2. 识别高库存商品
    high_stock_df = merged_df[merged_df['current_stock'] > merged_df['safety_stock'] * 2].copy()
    high_stock_df = high_stock_df.merge(sales_stats, left_index=True, right_index=True, how='left')
    
    # 计算积压风险
    high_stock_df['overstock_risk'] = ((high_stock_df['current_stock'] - high_stock_df['safety_stock']) / 
                                      high_stock_df['safety_stock'] * 100)
    
    print(f"\n📊 数据准确性测试结果:")
    print(f"总商品数: {len(merged_df)}")
    print(f"低库存商品数: {len(low_stock_df)}")
    print(f"高库存商品数: {len(high_stock_df)}")
    print(f"缺货风险>70%的商品数: {len(low_stock_df[low_stock_df['out_of_stock_risk'] > 70])}")
    print(f"积压风险>200%的商品数: {len(high_stock_df[high_stock_df['overstock_risk'] > 200])}")
    
    print(f"\n🔴 高风险低库存商品 (缺货风险>70%):")
    critical_low = low_stock_df[low_stock_df['out_of_stock_risk'] > 70].sort_values('out_of_stock_risk', ascending=False)
    for _, row in critical_low.head(10).iterrows():
        print(f"  {row['product_id']}: {row['name']} - 当前库存:{row['current_stock']}, 安全库存:{row['safety_stock']:.1f}, 缺货风险:{row['out_of_stock_risk']:.1f}%")
    
    print(f"\n🟡 高库存商品 (积压风险>100%):")
    critical_high = high_stock_df[high_stock_df['overstock_risk'] > 100].sort_values('overstock_risk', ascending=False)
    for _, row in critical_high.head(10).iterrows():
        print(f"  {row['product_id']}: {row['name']} - 当前库存:{row['current_stock']}, 安全库存:{row['safety_stock']:.1f}, 积压风险:{row['overstock_risk']:.1f}%")
    
    # 验证P005是否被错误分类
    p005_data = merged_df[merged_df['product_id'] == 'P005'].iloc[0]
    print(f"\n🔍 P005验证:")
    print(f"  当前库存: {p005_data['current_stock']}")
    print(f"  安全库存: {p005_data['safety_stock']}")
    print(f"  是否低库存: {p005_data['current_stock'] < p005_data['safety_stock']}")
    print(f"  是否高库存: {p005_data['current_stock'] > p005_data['safety_stock'] * 2}")
    
    return len(low_stock_df), len(high_stock_df)

if __name__ == "__main__":
    test_data_accuracy()
