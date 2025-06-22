chcp 65001
echo "开始安装QBotX"
echo "按任意键继续"
Read-Host -Prompt "Press Enter to continue"
# 克隆QBotX仓库到本地
git clone https://github.com/zhiyucn/QBotX.git
# 安装uv管理器
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
cd ./QBotX
uv add -r ./requirements.txt
copy ./templates_config.toml ./config.toml
echo "uv run main.py" > run.bat
echo "QBotX 已经安装完毕！"
echo "请配置config.toml文件"
echo "配置完成后，你可以使用run.bat文件启动QBotX"
echo "按任意键继续"
Read-Host -Prompt "Press Enter to continue"
