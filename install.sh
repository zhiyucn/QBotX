#!/bin/bash
echo "开始安装QBotX"
echo "按任意键继续"
read -n 1 -s
# 克隆QBotX仓库到本地
git clone https://github.com/zhiyucn/QBotX.git
# 安装uv管理器
curl -sS https://astral.sh/uv/install.sh | bash
cd ./QBotX
uv add -r ./requirements.txt
cp ./templates_config.toml ./config.toml
echo "uv run main.py" > run.sh
echo "QBotX 已经安装完毕！"
echo "请配置config.toml文件"
echo "配置完成后，你可以使用run.sh文件启动QBotX"
echo "按任意键继续"
read -n 1 -s