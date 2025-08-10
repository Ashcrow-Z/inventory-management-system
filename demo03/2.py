from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# 配置DeepSeek Chat模型
try:
    llm = ChatOpenAI(
        model_name="deepseek-chat",
        openai_api_base="https://api.deepseek.com/v1",
        openai_api_key="xxxxx",  # 👈 替换成你的真实API Key
        max_tokens=200,
        temperature=0.7
    )
    
    # 创建测试消息
    messages = [HumanMessage(content="你好！请用中文回答：'API测试成功'")]
    
    # 调用模型
    response = llm.invoke(messages)
    
    # 打印结果
    print("✅ API 测试成功！")
    print("🤖 模型回复:", response.content)
    print("🔍 完整响应对象类型:", type(response))
    
except Exception as e:
    print(f"❌ 发生错误: {str(e)}")
    print("可能的原因：")
    print("1. API Key 无效或过期")
    print("2. 网络连接问题")
    print("3. DeepSeek API 服务不可用")
    print("4. 库版本不兼容（需要langchain-openai>=0.1.0）")
