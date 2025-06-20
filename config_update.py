import os
import shutil
import toml
CONFIG_VERSION_ID = 2
print("欢迎使用 QBotX 配置工具")
print("该工具会将您的旧版配置进行升级处理")
print("注意，由于使用配置工具升级会导致注释缺失，我们更建议复制一份模板配置文件重新配置")
result = input("这是一次警告，使用配置工具升级会导致注释缺失，我们更建议复制一份模板配置文件重新配置，您确认要继续吗？(Y/n)")
if result == "n" or result == "N":
    print("您选择了不继续，所以我们不会升级您的配置文件")
    exit(0)
elif result == "Y" or result == "y":
    print("您选择了升级")
else:
    print("您输入了错误的指令")
    exit(0)

if not os.path.exists("config.toml"):
    print("所以你压根没有一个配置文件，所以我们会复制一份模板")
    shutil.copyfile("template_config.toml", "config.toml")
    print("配置文件复制完成")
    exit(0)
else:
    print("发现您有一个旧版配置文件")
    print("我们会将您的旧版配置文件备份一份")
    import time
    timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
    shutil.copyfile("config.toml", f"config_{timestamp}_old.toml")
    print("配置文件备份完成")

with open("config.toml", "r", encoding="utf-8") as f:
    config = toml.load(f)

if config == {}:
    print("您的配置文件为空，可能是您没有配置过")
    exit(0)
if config["config"]["version_id"] == CONFIG_VERSION_ID:
    print("您的配置文件版本号与当前版本号一致，不需要升级")
    exit(0)

if config["config"]["version_id"] < CONFIG_VERSION_ID:
    print("您的配置文件版本号低于当前版本号，需要升级")
    print("我们会将您的旧版配置文件升级为最新版本")
    config["config"]["version_id"] = CONFIG_VERSION_ID
    config["config"]["version"] = "0.0.2"
    # 添加experiment项
    config["experiment"] = {}
    config["experiment"]["adapter_custom"] = False
    config["experiment"]["adapter_custom_path"] = "onebot"
    with open("config.toml", "w", encoding="utf-8") as f:
        toml.dump(config, f)

print("""██████╗ ███████╗██████╗ ███████╗███████╗████████╗ ██████╗████████╗██╗
██╔══██╗██╔════╝██╔══██╗██╔════╝██╔════╝╚══██╔══╝██╔════╝╚══██╔══╝██║
██████╔╝█████╗  ██████╔╝█████╗  █████╗     ██║   ██║        ██║   ██║
██╔═══╝ ██╔══╝  ██╔══██╗██╔══╝  ██╔══╝     ██║   ██║        ██║   ╚═╝
██║     ███████╗██║  ██║██║     ███████╗   ██║   ╚██████╗   ██║   ██╗
╚═╝     ╚══════╝╚═╝  ╚═╝╚═╝     ╚══════╝   ╚═╝    ╚═════╝   ╚═╝   ╚═╝
                                                                     """)
print("升级完成，您可以根据提示配置您的机器人了")