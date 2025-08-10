#!/usr/bin/env python3
"""
问答系统测试脚本
"""

from qa_system import InventoryQASystem

def test_qa_system():
    """测试问答系统"""
    print("🧪 开始测试问答系统...")
    
    # 初始化系统
    qa_system = InventoryQASystem()
    
    # 测试问题列表
    test_questions = [
        "我们的库存状况如何？",
        "哪些商品销售最好？",
        "有哪些商品库存不足？",
        "各类别的销售情况如何？",
        "我们的利润率怎么样？"
    ]
    
    print(f"📝 将测试 {len(test_questions)} 个问题")
    print("="*60)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n🔍 测试 {i}/{len(test_questions)}")
        print(f"问题: {question}")
        print("-" * 40)
        
        try:
            # 获取回答
            text_response, charts_info = qa_system.ask_question(question)
            
            # 验证回答
            if text_response and len(text_response) > 50:
                print("✅ 回答生成成功")
            else:
                print("❌ 回答内容过短")
            
            # 验证图表
            if charts_info:
                print(f"✅ 生成了 {len(charts_info)} 个图表")
                for chart in charts_info:
                    print(f"   - {chart['type']}: {chart['path']}")
            else:
                print("⚠️  没有生成图表")
                
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
        
        print("-" * 40)
    
    print("\n🎉 测试完成！")

if __name__ == "__main__":
    test_qa_system() 