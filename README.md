# 库存管理系统

本项目旨在打造一款基于 AI 的智能库存管理系统。该系统借助多个 AI Agent 的协同合作，能够完成数据分析、策略制定以及报告生成等一系列任务。系统采用模块化设计理念，可支持 Web 界面、命令行、报告生成器等多种使用方式，为用户提供灵活便捷的操作选择。

## 项目结构

```
crewai-uv/
├── 1.py                           # 数据生成模块
├── 2.py                           # API测试程序
├── qa_system.py                   # 智能问答系统 
├── web_qa.py                      # Web界面
├── test_qa.py                     # 问答系统测试脚本
├── test_data_accuracy.py          # 数据准确性测试脚本
├── simple_report_generator.py     # 简洁报告生成器（推荐）
├── manual_llm_test.py            # 手动LLM测试脚本
├── prompts.py                     # 提示词配置文件
├── config.py                      # 系统配置文件
├── requirements.txt               # 依赖包列表
├── README.md                     # 项目说明文档
├── charts/                        # 图表输出目录
│   └── inventory_distribution.png # 库存分布图表
├── inventory.csv                  # 库存数据
├── products.csv                   # 商品信息数据
├── sales_records.csv              # 销售记录数据
└── simple_inventory_report.md     # 生成的库存管理报告
```

## 功能特性

- **数据分析师Agent**: 分析库存数据，识别低库存商品
- **策略顾问Agent**: 制定补货和促销策略
- **报告生成器Agent**: 生成完整的库存管理报告
- **智能问答系统**: 支持自然语言问答，自动生成图表
- **配置化管理**: 提示词和系统参数可独立配置

## 快速开始

### 1. 安装环境:
pip install uv\n
uv venv .venv\n
.\.venv\Scripts\activate\n
uv pip install -r requirements.txt\n
uv pip install langchain-openai\n

### 2. 获取报告或交互式问答

#### 方法一：Web界面（推荐）
```bash
# 1. 安装依赖
uv pip install streamlit matplotlib seaborn

# 2. 启动Web界面
uv run streamlit run web_qa.py

# 3. 打开浏览器访问 http://localhost:8501
```

#### 方法二：命令行
```bash
# 1. 安装依赖
uv pip install -r requirements.txt

# 2. 配置API密钥
# 编辑 config.py 文件中的 MODEL_CONFIG，替换为你的真实API密钥

# 3. 运行库存分析
uv run python simple_report_generator.py

# 4. 或运行问答系统
uv run python qa_system.py
```

## 详细使用说明

### Web界面使用
1. 启动后，在浏览器中打开显示的地址（通常是 http://localhost:8501）
2. 在输入框中输入您的问题，如：
   - "我们的库存状况如何？"
   - "哪些商品销售最好？"
   - "有哪些商品库存不足？"
   - "各类别的销售情况如何？"
3. 点击"发送"按钮，系统会自动分析数据并生成相关图表
4. 支持多轮对话，可以连续提问

### 命令行使用
- 运行 `uv run python qa_system.py` 进入交互式问答模式
- 运行 `uv run python test_qa.py` 进行系统测试

### 示例问题
系统支持多种类型的问题，包括但不限于：

**库存相关：**
- "哪些商品库存不足？"
- "我们的库存分布情况如何？"
- "哪些商品需要补货？"

**销售相关：**
- "最近30天的销售趋势如何？"
- "哪些商品销售最好？"
- "各类别的销售占比如何？"

**利润相关：**
- "我们的利润率怎么样？"
- "哪些类别的利润最高？"

**综合分析：**
- "给我一个库存和销售的综合分析"
- "哪些商品需要重点关注？"

## 配置说明

### 提示词配置 (prompts.py)

包含所有AI Agent的提示词模板：
- `ANALYST_PROMPT_TEMPLATE`: 数据分析师提示词
- `STRATEGY_PROMPT_TEMPLATE`: 策略顾问提示词  
- `REPORT_PROMPT_TEMPLATE`: 报告生成器提示词

### 系统配置 (config.py)

- `MODEL_CONFIG`: 大模型配置（API密钥、模型名称等）
- `DATA_FILES`: 数据文件路径配置
- `SAFETY_STOCK_CONFIG`: 安全库存计算参数
- `SAMPLE_DATA_CONFIG`: 示例数据生成参数
- `REPORT_CONFIG`: 报告生成配置

## 工作流程

### 库存分析工作流
1. **数据加载**: 系统加载库存、销售和商品数据文件
2. **数据分析**: 使用pandas进行准确的数据计算和筛选
   - 识别低库存商品：当前库存 < 安全库存
   - 识别高库存商品：当前库存 > 安全库存 × 2
   - 计算缺货风险指数和积压风险指数
3. **策略制定**: 基于分析结果制定补货和促销策略
4. **报告生成**: 生成完整的库存管理报告，包含所有商品详情

### 智能问答系统
1. **数据加载**: 系统加载所有库存、销售和商品数据
2. **问题分析**: 根据用户问题自动识别需要生成的图表类型
3. **图表生成**: 自动生成相关的可视化图表
4. **智能回答**: 结合数据和图表提供详细的文字回答

### Web界面功能
- **多轮对话**: 支持连续提问，保持对话上下文
- **实时图表**: 自动生成并展示相关图表
- **简洁界面**: 基于Streamlit的现代化Web界面
- **响应式设计**: 适配不同屏幕尺寸

## 输出文件

### 库存分析工作流
- `simple_inventory_report.md`: 简洁版库存管理报告（推荐）
- 控制台输出: 显示分析进度和统计信息

### 智能问答系统
- `charts/`: 图表输出目录，包含各种可视化图表
- 控制台输出: 显示问答过程和生成的图表信息

### Web界面
- 浏览器访问: 默认地址为 http://localhost:8501
- 实时交互: 支持多轮对话和图表展示
- 自动保存: 对话历史和图表自动保存

### 数据验证
- `test_data_accuracy.py`: 数据准确性测试脚本
- 控制台输出: 显示详细的库存分析结果和验证信息

## 注意事项

### 数据准确性
- 系统使用pandas进行准确的数据计算，确保分析结果可靠
- 低库存商品：当前库存 < 安全库存
- 高库存商品：当前库存 > 安全库存 × 2
- 所有商品都会在报告中完整列出，不会使用省略号

### 报告生成
- 使用 `simple_report_generator.py` 生成简洁准确的报告
- 报告文件会覆盖之前的版本
- 生成格式：Markdown格式的完整库存管理报告

### 系统配置
- 请确保API密钥配置正确（config.py中的MODEL_CONFIG）
- Web界面需要安装streamlit: `uv pip install streamlit`
- 首次运行可能需要下载依赖包，请耐心等待

### 数据验证
- 可使用 `test_data_accuracy.py` 验证数据准确性
- 系统会自动计算并显示详细的统计信息
- 支持风险等级分类：🔴高风险、🟡中风险、🟢低风险 
