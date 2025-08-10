# 库存管理系统配置文件
import os

# 环境变量配置（如果需要从环境变量读取，可以取消注释下面的代码）
# from dotenv import load_dotenv
# load_dotenv()

# 模型配置
MODEL_CONFIG = {
    "model_name": "moonshot-v1-8k",
    "openai_api_base": "https://api.moonshot.cn/v1",
    "openai_api_key": "xxxxxxx",  # 请替换成你的真实API Key
    "temperature": 0.7
}

# 数据文件配置
DATA_FILES = {
    "sales_records": "sales_records.csv",
    "products": "products.csv", 
    "inventory": "inventory.csv",
    "report_output": "inventory_management_report.md"
}

# 安全库存配置
SAFETY_STOCK_CONFIG = {
    "stable_product_multiplier": 5,  # 稳定商品：平均日销量 * 5
    "volatile_product_multiplier": 3,  # 波动商品：最高日销量 * 3
    "analysis_period_days": 30  # 分析周期（天）
}

# 示例数据生成配置
SAMPLE_DATA_CONFIG = {
    "num_products": 100,
    "date_range_days": 30,
    "low_stock_probability": 0.3,  # 30%的商品处于低库存状态
    "categories": ['电子产品', '服装', '食品', '家居', '运动', '书籍', '玩具', '美妆', '电器', '文具']
}

# 报告配置
REPORT_CONFIG = {
    "max_preview_length": 500,  # 控制台预览的最大字符数
    "encoding": "utf-8"
} 
