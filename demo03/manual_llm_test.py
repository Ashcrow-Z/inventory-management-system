from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import json

# 配置 Moonshot 大模型
llm = ChatOpenAI(
    model_name="moonshot-v1-8k",
    openai_api_base="https://api.moonshot.cn/v1",
    openai_api_key="sk-iw52Xktj1kqdKIICxd5tX6WQBYtW94yznBRy37RodQET03Cj",
    temperature=0.7
)

def manual_crewai_simulation():
    """手动模拟 crewai 的工作流程"""
    
    # 模拟 Agent 1: 数据分析师
    print("🤖 Agent 1: 数据分析师开始工作...")
    
    # 构建数据分析师的任务提示
    analyst_prompt = """
    你是一位经验丰富的数据分析师。请分析以下库存数据并识别低库存商品。

    数据文件信息：
    - 销售记录: sales_records.csv (3000行数据)
    - 商品信息: products.csv (100个商品)
    - 库存数据: inventory.csv (100个商品库存)

    请返回JSON格式的分析结果，结构如下：
    {
        "low_stock_products": [
            {
                "product_id": "P001",
                "name": "商品名称",
                "current_stock": 50,
                "safety_stock": 100,
                "days_of_inventory": 5.2,
                "out_of_stock_risk": 50.0
            }
        ],
        "overall_health": "不佳",
        "key_findings": "发现10个商品低于安全库存水平，其中3个商品缺货风险高于70%"
    }
    """
    
    try:
        # 手动调用 LLM，只传递必要的参数
        messages = [
            SystemMessage(content="你是一个专业的数据分析师，擅长分析库存数据。"),
            HumanMessage(content=analyst_prompt)
        ]
        
        response1 = llm.invoke(messages)
        print("✅ Agent 1 分析完成")
        print("分析结果:", response1.content)
        
        # 模拟 Agent 2: 策略顾问
        print("\n🤖 Agent 2: 策略顾问开始工作...")
        
        # 使用 Agent 1 的结果作为输入
        strategy_prompt = f"""
        你是一位资深的库存策略顾问。根据数据分析师的分析结果：
        
        {response1.content}
        
        请为低库存商品制定具体的补货建议和促销策略。
        
        请返回JSON格式的策略建议，结构如下：
        {{
            "replenishment_strategies": [
                {{
                    "product_id": "P001",
                    "replenishment_amount": 200,
                    "timeline": "紧急补货（48小时内）",
                    "reason": "高缺货风险且销售趋势上升"
                }}
            ],
            "promotion_strategies": [
                {{
                    "product_id": "P045",
                    "promotion_method": "限时折扣",
                    "discount_rate": 15,
                    "duration": "2周"
                }}
            ],
            "overall_recommendations": "建议优化安全库存计算公式并建立自动补货系统"
        }}
        """
        
        messages2 = [
            SystemMessage(content="你是一个专业的库存策略顾问，擅长制定补货和促销策略。"),
            HumanMessage(content=strategy_prompt)
        ]
        
        response2 = llm.invoke(messages2)
        print("✅ Agent 2 策略制定完成")
        print("策略建议:", response2.content)
        
        # 模拟 Agent 3: 报告生成器
        print("\n🤖 Agent 3: 报告生成器开始工作...")
        
        report_prompt = f"""
        你是一位专业的报告撰写专家。根据以下分析结果和策略建议，撰写一份全面的库存管理报告：

        数据分析结果：
        {response1.content}

        策略建议：
        {response2.content}

        请生成一份完整的Markdown格式库存管理报告，包含：
        1. 执行摘要
        2. 详细库存分析
        3. 具体补货和促销策略
        4. 实施计划和时间表
        5. 预期效果和ROI分析
        """
        
        messages3 = [
            SystemMessage(content="你是一个专业的报告撰写专家，擅长将复杂信息整理成清晰的报告。"),
            HumanMessage(content=report_prompt)
        ]
        
        response3 = llm.invoke(messages3)
        print("✅ Agent 3 报告生成完成")
        
        # 保存最终报告
        with open('manual_inventory_report.md', 'w', encoding='utf-8') as f:
            f.write(response3.content)
        
        print("\n🎉 手动工作流执行成功！")
        print("📄 报告已保存到: manual_inventory_report.md")
        print("\n" + "="*50)
        print("最终报告预览:")
        print("="*50)
        print(response3.content[:500] + "..." if len(response3.content) > 500 else response3.content)
        
        return True
        
    except Exception as e:
        print(f"❌ 手动工作流执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 开始手动模拟 CrewAI 工作流...")
    print("="*50)
    manual_crewai_simulation() 