# LLM-Werewolf

一个由大语言模型驱动的狼人杀项目。

## 快速上手

先将项目克隆到本地：

```bash
git clone https://github.com/RaptorValley
```

然后打开`call.py`配置模型供应商、名称、API Key等。为方便启用，程序已内置部分常见模型及`base_url`，如下图：

![image-20250809192711639](C:\Users\VICTUS\Desktop\H\Project\LLM-Werewolf\assets\image-20250809192711639.png)

然后运行如下命令（Windows 环境）：

```bash
cd LLM-Werewolf
python main.py <YOUR-LLM-PROVIDER> <YOUR-LLM-INDEX>
```

参数说明：

- `<YOUR-LLM-PROVIDER>`是你模型的提供商，须在`call.py`中先行配置后才会生效；
- `<YOUR-LLM-INDEX>`是你选择模型在`model_list`列表中的索引。