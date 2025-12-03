# 项目结构说明

本文档详细说明了项目的目录结构和各文件的作用。

## 📁 完整目录结构

```
real-time-stock-mcp-service/
├── mcp_server.py              # MCP服务器主文件
├── pyproject.toml             # 项目配置文件
├── README.md                  # 项目说明文档
├── .env                       # 环境变量配置（需自行创建）
└── src/
    ├── data_source_interface.py    # 数据源接口定义
    ├── stock_data_source.py     # stockapi.com.cn数据源实现
    ├── utils.py                    # 通用工具函数
    ├── formatting/
    │   └── markdown_formatter.py   # Markdown格式化工具（废弃）
    └── tools/  # 工具模块

```

## 📝 核心文件说明

### 根目录文件

#### `mcp_server.py` - 主服务器文件
- **作用**: MCP服务器的入口点
- **功能**:
  - 初始化数据源
  - 注册所有工具模块
  - 启动MCP服务器
  - 处理服务器生命周期
- **关键代码**:
  ```python
  active_data_source = StockAPIDataSource()
  app = FastMCP(...)
  app.run(transport='stdio')
  ```

#### `pyproject.toml` - 项目配置
- **作用**: 定义项目元数据和依赖
- **包含**:
  - 项目名称、版本、描述
  - Python版本要求
  - 依赖包列表
  - 构建系统配置

#### `test_basic.py` - 测试脚本
- **作用**: 验证基本功能是否正常
- **测试项目**:
  - 数据源初始化
  - 股票搜索
  - 获取股票信息
  - K线数据获取

### src/ 目录

#### `data_source_interface.py` - 数据源接口
- **作用**: 定义数据源的抽象接口
- **包含方法**:
  - `get_stock_search()` - 搜索股票
  - `get_historical_k_data()` - 获取K线数据
  - `get_technical_indicators()` - 获取技术指标
  - 等等...  

- **设计模式**: 抽象基类 (ABC)

#### `stock_data_source.py` - 数据源实现
- **作用**: 实现 StockAPI 数据源
- **功能**:
  - 实现所有接口方法
  - HTTP API 调用
  - 数据解析和转换
  - 错误处理
- **关键方法**:
  - `_make_request()` - 统一API请求处理
  - `_normalize_stock_code()` - 标准化股票代码

#### `utils.py` - 工具函数
- **作用**: 提供通用工具函数
- **功能**:
  - 日志配置
  - 日期格式化
  - 数字格式化
  - 类型转换

### src/tools/ 目录

每个工具模块都遵循相同的模式：

#### `basic_data.py` - 股票基础信息
- **工具**:
  - `search()` - 搜索股票


## 🔄 数据流

```
用户请求 (Claude Desktop)
    ↓
MCP Server (mcp_server.py)
    ↓
工具函数 (tools/*.py)
    ↓
数据源实例 (stock_data_source.py.py)
    ↓
StockAPI HTTP API
    ↓
返回给用户
```

## 🎯 设计模式

### 1. 依赖注入
- 数据源通过构造函数注入到工具模块
- 易于测试和替换实现

### 2. 策略模式
- 通过接口定义行为
- 不同数据源可以有不同实现

### 3. 单一职责原则
- 每个模块只负责一类功能
- 便于维护和扩展

### 4. 开闭原则
- 对扩展开放（添加新工具）
- 对修改关闭（不需要改动核心代码）

## 📦 依赖关系

```
mcp_server.py
    ├─→ data_source_interface.py
    ├─→ stock_data_source.py
    ├─→ utils.py
    └─→ tools/
         ├─→ search.py
         ├─→ kline_data.py
         └─→ ...

tools/*.py
    ├─→ data_source_interface.py (接口依赖)
    └─→ utils.py

stock_data_source.py
    └─→ data_source_interface.py (实现接口)
```

## 🚀 扩展点

### 添加新数据源
1. 创建新文件实现 `StockDataSource` 接口
2. 在 `mcp_server.py` 中切换数据源

### 添加新工具
1. 在 `src/tools/` 创建新模块
2. 实现 `register_*_tools()` 函数
3. 在 `mcp_server.py` 中注册

### 添加新格式化器
1. 在 `src/formatting/` 添加新格式化类
2. 在工具中使用

## 📊 代码统计

- **Python 文件**: 15+
- **工具函数**: 20+
- **代码行数**: 2000+
- **文档行数**: 1000+

## 💡 最佳实践

1. ✅ 所有工具函数都有详细的 docstring
2. ✅ 使用类型提示 (Type Hints)
3. ✅ 统一的错误处理
4. ✅ 完善的日志记录
5. ✅ Markdown格式化输出
6. ✅ 清晰的模块划分

## 📚 相关文档

- [README.md](README.md) - 项目概述
- [QUICKSTART.md](QUICKSTART.md) - 快速开始
- [DEVELOPMENT.md](DEVELOPMENT.md) - 开发指南

---

**提示**: 这个项目结构设计使得添加新功能非常简单，只需要：
1. 定义接口方法
2. 实现数据获取
3. 创建工具函数
4. 注册到主服务器

无需修改现有代码！
