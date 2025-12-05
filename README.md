# 实时股票 MCP 服务

这是一个实时股票数据服务的MCP（Model Context Protocol）服务器。它通过东方财富网获取金融数据，并将这些数据以工具的形式暴露给支持MCP的AI模型。

## 功能特性

- 📊 查找股票
- 📈 K线数据查询（日线、周线、月线等）
- 📉 计算技术指标
- 待开发...
## 环境要求

- Python 3.12+
- Windows/Linux/MacOS
- uv 包管理器

## 安装步骤

### 1. 安装 uv 包管理器

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Linux/MacOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 克隆或下载项目

```bash
git clone https://github.com/DannyWongIsAvailable/real-time-stock-mcp-service.git
cd real-time-stock-mcp-service
```

### 3. 使用 uv 安装依赖

```bash
uv sync
```


## 使用方法

### 直接运行服务器

```bash
uv run mcp_server.py
```

### client 中配置

编辑 Claude Desktop 的配置文件：

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`  
**MacOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`  

添加以下配置：

```json
{
  "mcpServers": {
    "stock-data": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\path\\to\\real-time-stock-mcp-service",
        "run",
        "mcp_server.py"
      ]
    }
  }
}
```

注意：将路径替换为你的实际项目路径。

## 项目结构

```
real-time-stock-mcp-service/
├── mcp_server.py              # MCP服务器主文件
├── pyproject.toml             # 项目配置文件
├── README.md                  # 项目说明文档
├── .env                       # 环境变量配置（需自行创建）
└── src/
    ├── crawler/               # 网络爬虫模块
    │   ├── base_crawler.py       # 爬虫基类
    │   ├── basic_data.py         # 基础数据爬虫（股票搜索、交易日信息）
    │   ├── real_time_data.py     # 实时数据爬虫（来自雪球）
    │   ├── technical_data.py     # 技术数据爬虫（K线数据）
    │   └── ...              
    ├── data_source_interface.py  # 数据源接口定义
    ├── stock_data_source.py      # 数据源实现
    ├── mcp_tools/                # 各个MCP工具模块
    │   ├── kline_data.py         # K线数据工具
    │   ├── real_time_data.py     # 实时数据工具
    │   └── ...
    └── utils/                    # 工具模块
        ├── markdown_formatter.py # Markdown格式化工具
        └── utils.py              # 通用工具
```

## 核心设计

本项目采用**依赖注入**设计模式：

1. `crawler` 模块获取数据
2. `data_source_interface.py` 定义抽象数据源接口
3. `stock_data_source.py` 提供具体实现
4. 各工具模块通过依赖注入获取数据源实例

这种设计使得：
- ✅ 易于扩展新功能
- ✅ 可以轻松切换不同数据源
- ✅ 便于单元测试
- ✅ 代码解耦，维护性强



## 开发指南

详情请查看[开发指南](DEVELOPMENT.md)  

## 注意事项

⚠️ **重要提醒**：
1. 本服务提供的数据仅供参考，不构成投资建议
2. 请遵守数据使用协议和相关法律法规

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题，请提交 Issue 或联系项目开发者。