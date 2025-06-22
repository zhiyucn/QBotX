# 修复中文乱码问题
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 | Out-Null

# 安装流程
Write-Host "开始安装QBotX" -ForegroundColor Cyan
Write-Host "任务完成请继续" -ForegroundColor Green
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
Set-Content -Path run.bat -Value "uv run main.py" -Encoding UTF8

# 完成提示
Write-Host "QBotX 已经安装完毕！" -ForegroundColor Green
Write-Host "请配置 config.toml 文件" -ForegroundColor Yellow
Write-Host "配置完成后，你可以使用 run.bat 文件启动QBotX" -ForegroundColor Cyan
Read-Host -Prompt "按Enter退出"