echo "��ʼ��װQBotX"
echo "�����������"
Read-Host -Prompt "Press Enter to continue"
# ��¡QBotX�ֿ⵽����
git clone https://github.com/zhiyucn/QBotX.git
# ��װuv������
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
cd ./QBotX
uv add -r ./requirements.txt
copy ./templates_config.toml ./config.toml
echo "uv run main.py" > run.bat
echo "QBotX �Ѿ���װ��ϣ�"
echo "������config.toml�ļ�"
echo "������ɺ������ʹ��run.bat�ļ�����QBotX"
echo "�����������"
Read-Host -Prompt "Press Enter to continue"
