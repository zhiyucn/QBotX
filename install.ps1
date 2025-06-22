# 修复乱码的核心设置 - 必须放在脚本最开头
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 | Out-Null  # 设置控制台代码页为UTF-8

# 安装流程
echo "开始安装QBotX"
echo "按任意键继续"
Read-Host -Prompt "按Enter继续"

# 克隆仓库
git clone https://github.com/zhiyucn/QBotX.git

# 安装UV管理器
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 设置环境
cd ./QBotX
uv add -r ./requirements.txt
copy ./templates_config.toml ./config.toml

# 创建启动脚本
echo "uv run main.py" > run.bat

# 完成提示
echo "QBotX 已经安装完毕！"
echo "请配置 config.toml 文件"
echo "配置完成后，你可以使用 run.bat 文件启动QBotX"
Read-Host -Prompt "按Enter退出"