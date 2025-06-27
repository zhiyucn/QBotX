# 修复中文乱码问题
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 | Out-Null

# 安装流程
Write-Host "开始安装QBotX" -ForegroundColor Cyan
Read-Host -Prompt "按Enter继续"

# 检查git是否安装
if (!(Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "git未安装，开始安装" -ForegroundColor Yellow
    Write-Host "请注意，我们使用winget安装，所以会比较慢"
    winget install --id Git.Git -e --source winget
}


Write-Host "我们需要一些信息" -ForegroundColor Yellow
Write-Host "你希望在何处安装QBotX？"
$installPath = Read-Host "请输入路径（例如：C:\QBotX 默认为D:/QBotX）"

if ($installPath -eq "") {
    $installPath = "D:/QBotX"
}

# 克隆仓库
git clone https://github.com/zhiyucn/QBotX.git $installPath

Write-Host "开始安装uv，这可能需要很长时间" -ForegroundColor Green
# 安装UV管理器
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
# 刷新环境变量
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
# 设置环境
Set-Location $installPath
uv add -r ./requirements.txt
Copy-Item ./templates_config.toml ./config.toml

# 创建启动脚本
Set-Content -Path run.bat -Value "uv run main.py" -Encoding UTF8
explorer .
# 完成提示
Write-Host "QBotX 已经安装完毕！" -ForegroundColor Green
Write-Host "请配置 config.toml 文件" -ForegroundColor Yellow
Write-Host "配置完成后，你可以使用 run.bat 文件启动QBotX" -ForegroundColor Cyan
Read-Host -Prompt "按Enter退出"