# 迭代三：最终发布（FinalRelease）

> 本目录归档「构造迭代 / 最终验收」的成果。实际文件存放于仓库对应位置，此处列出成果清单与映射关系。

## 成果清单（验收成果）

| 成果项 | 说明 | 仓库位置 |
|--------|------|---------|
| Vision 文档 | 项目前景文档 | 小组另存为 docx（桌面） |
| 软件架构文档 | 分层架构 + MVC | `../docs/02_软件架构文档.md` |
| UML 模型 | 用例模型 + 设计模型 | `../docs/用例模型.md`、`../docs/设计模型.md` |
| 软件代码 | 源码 + 可执行 | `../app.py`、`../algorithms.py`、`../database.py`、`../templates/`、`../static/` |
| 单元测试 | pytest 测试代码 + 报告 | `../tests/`、`../docs/单元测试报告.md` |
| 系统测试 | 测试用例 + 报告 | `../docs/系统测试报告.md` |
| 项目总结报告 | 项目总结 | `../docs/项目总结报告.md` |
| 用户手册 | 使用说明 | `../docs/05_用户手册.md` |
| 验收答辩 PPT | 答辩材料 | 小组另存（桌面） |

## 部署运行

```bash
# 安装依赖
python -m pip install -r requirements.txt

# 启动
python app.py
# 浏览器访问 http://127.0.0.1:5000
```

或双击 `../start.bat`（首次先双击 `../install.bat`）。
