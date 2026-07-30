# 故障排查指南（TROUBLESHOOTING）

如果你在项目运行过程中遇到了报错或异常，请先查阅一下常见问题列表。本文档旨在帮助你快速定位并解决问题

## 常见报错与解决方案
### 1. [WinError 126] 找不到指定的模块
- **报错** : `OSError: [WinError 126] 找不到指定的模块。Error loading "C:\...\pianke\.venv\Lib\site-packages\torch\lib\c10.dll" or one of its dependencies.`
- **现象描述**：使用 专家模式 进行依赖校验时提示报错信息。
- **可能原因**：
  1. dll未正确安装
  2. 项目未更新到最新版
- **解决方案**：
  1. 安装最新版 Microsoft Visual C++ Redistributable https://aka.ms/vc14/vc_redist.x64.exe
  2. 将项目更新至最新版
  3. 详见 [issue](https://github.com/zhaoyue4810/pianke/issues/15)

### 2. [WinError 1114] 动态链接库(DLL)初始化例程失败
- **报错**：`OSError: [WinError 1114] 动态链接库(DLL)初始化例程失败。 Error loading "C:\...\spianke\.venv\Lib\site-packages\torch\lib\c10.dll" or one of its dependencies.`
- **现象描述**：使用 专家模式 进行依赖校验时提示报错信息。
- **可能原因**：[同1.](#1-winerror-126-找不到指定的模块)
- **解决方案**：[同1.](#1-winerror-126-找不到指定的模块)

### 3. [ImportError]: 找不到指定的模块 _rawpy
- **报错**：`ImportError: DLL load failed while importing _rawpy: 找不到指定的模块。`
- **现象描述**：读取RAW格式文件后提示`RuntimeError: 发现 1 个 RAW 文件没有同名 JPG，必须安装 rawpy 才能处理：pip install 'rawpy>=0.18'。`
- **可能原因**：[同1.](#1-winerror-126-找不到指定的模块)
- **解决方案**：[同1.](#1-winerror-126-找不到指定的模块)

---
## 若以上问题皆无法帮助到你
若以上问题皆无法帮助到你，请提交一份 issue ，附上报错内容或日志。如可以，描述复现步骤

### 日志位置
你读取照片的位置\\_pic_selecter\log.txt