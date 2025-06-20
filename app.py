# ANSI蓝色和红色
BLUE = '\033[94m'
RED = '\033[91m'
RESET = '\033[0m'
print(f"""{BLUE} ██████╗ ██████╗  ██████╗ ████████╗██╗  ██╗
██╔═══██╗██╔══██╗██╔═══██╗╚══██╔══╝╚██╗██╔╝
██║   ██║██████╔╝██║   ██║   ██║    ╚███╔╝ {RED}
██║▄▄ ██║██╔══██╗██║   ██║   ██║    ██╔██╗ 
╚██████╔╝██████╔╝╚██████╔╝   ██║   ██╔╝ ██╗
 ╚══▀▀═╝ ╚═════╝  ╚═════╝    ╚═╝   ╚═╝  ╚═╝{RESET}
A Simple QQ Bot  󰭹 
zhiyuHD 制作""")

print("本软件在字体采用Nerd Font时效果最佳！")
print("在这里下载Nerd Font --> https://www.nerdfonts.com/font-downloads")
import datetime
import tomli
import websockets
import asyncio
import json
import requests
import base64
import openai
import logging
from sqlalchemy.orm import sessionmaker
from model import Memory, engine, Base
from decode import decode_array
import requests
import logger as lg
logger = lg.get_logger(__name__)
with open("config.toml", "rb") as f:
    config = tomli.load(f)

VERSION_ID = 2
VERSION_NAME = "0.0.2"
logger.info("检查更新......")
logger.info(f"当前版本为 {VERSION_NAME}")
resp = requests.get("https://qbotx.zhiyuxl.workers.dev/")
if resp.status_code == 200:
    release = resp.json()
    latest_version = release["app_version_id"]
    if latest_version > VERSION_ID:
        logger.info(f"发现新版本: {release["app_version"]}")
        logger.info(f"更新内容：\n{release['update']}")
    else:
        logger.info("当前已是最新版本")
else:
    logger.error("检查更新失败，你可能无法连接到Cloudflare Worker")

client = openai.OpenAI(
    api_key=config["api_service"]["api_key"],
    base_url=config["api_service"]["base_url"],
)

group_message = {}  # 临时记忆
async def handler(websocket):
    async for message in websocket:
        
        message = json.loads(message)
        # 提取出消息
        # print(message)  # 打印消息，方便调试
        if "meta_event_type" in message and message["meta_event_type"] == "lifecycle":
            continue
        if "message" not in message:
            continue
        group_id = message["group_id"]
        if group_id not in group_message:
            group_message[group_id] = []
        nick_name = message["sender"]["nickname"]
        q_message = message["message"]
        q_message = decode_array(q_message)
        str_message = f"{nick_name}:"
        # 构建为字符串
        for item in q_message:
            if item["type"] == "text":
                str_message += item["text"]
            elif item["type"] == "image":
                logger.info(f"图片识别中: {item['url']}")
                import requests
                # 下载图片并转为 data:image/png;base64 格式
                response = requests.get(item["url"])
                image_data = base64.b64encode(response.content).decode("utf-8")
                # 调用识图模型
                response = client.chat.completions.create(
                    model=config["image_vlm"]["model"],
                    messages=[
                        {
                            "role": "system",
                            "content": "你是一个专业的图片识别助手，你可以识别图片中的内容，并且给出简略的描述，你必须回复中文，禁用Markdown格式。"
                        },
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{image_data}",
                                        "detail": "high"
                                    }
                                }
                            ]
                        }
                    ],
                    max_tokens=128,
                )
                # 提取出识别结果
                image_description = response.choices[0].message.content
                str_message += f"[图片:{image_description}]"
                # 如果SubType=1，说明是表情，检查是否开启表情包小偷功能
                print(item)
                if item["subtype"] == "1":
                    logger.info(f"表情识别中: {image_description}")
                    if config["emoji"]["emoji_stolen"]:
                        import random
                        if random.random() < config["emoji"]["emoji_stolen_need"]:
                            # 偷取并存入数据库
                            # 检查emoji表中是否存在该表情
                            from model import Emoji, engine, Base, sessionmaker
                            Session = sessionmaker(bind=engine)
                            session = Session()
                            import os
                            emoji = session.query(Emoji).filter_by(file_name = item["file"]).first()
                            if emoji is None:
                                # 不存在，插入
                                emoji = Emoji(message=image_description, file_name=item["file"])
                                session.add(emoji)
                                session.commit()
                                response = requests.get(item["url"])
                                if item["file"].endswith(".image"):
                                    item["file"] = item["file"].replace(".image", ".png")
                                if not os.path.exists(os.path.join(os.getcwd(),"emoji")):
                                    os.makedirs(os.path.join(os.getcwd(),"emoji"))
                                with open(os.path.join(os.getcwd(),"emoji", item['file']), "wb") as f:
                                    f.write(response.content)
                                logger.info(f"偷取表情: {image_description}，文件名: {item['file']}")
                            
            elif item["type"] == "at":
                # 获取用户信息
                user_id = item["user_id"]
                # 调用get_group_member_info
                logger.info(f"Group ID: {group_id}")
                payload = json.dumps(
                {
                    "action": "get_group_member_info",
                    "params": {"group_id": group_id, "user_id": user_id, "no_cache": False},
                }
                )
                try:
                    await websocket.send(payload)
                    socket_response = await asyncio.wait_for(websocket.recv(), timeout=10)
                    socket_response = json.loads(socket_response)
                    str_message += f"@{socket_response['data']['nickname']}"
                except TimeoutError:
                    logger.warning(f"获取成员信息超时，群号: {group_id}, 用户ID: {user_id}")
                    str_message += f"@{user_id}(获取名称失败：TimeoutError)"
                    return None
                except Exception as e:
                    logger.error(f"获取成员信息失败: {e}")
                    str_message += f"@{user_id}(获取名称失败：{e})"
                    return None
            elif item["type"] == "reply":
                # 获取回复消息
                message_id = item["message_id"]
                # 调用get_msg
                payload = json.dumps(
                {
                    "action": "get_msg",
                    "params": {"message_id": message_id},
                }
                )
                try:
                    await websocket.send(payload)
                    socket_response = await asyncio.wait_for(websocket.recv(), timeout=10)
                    socket_response = json.loads(socket_response)
                    str_message += f"[引用消息:{socket_response['data']['message']}]"
                except TimeoutError:
                    logger.warning(f"获取消息超时，消息ID: {message_id}")
                    str_message += f"[引用消息:获取消息失败：TimeoutError]"
                    return None
                except Exception as e:
                    logger.error(f"获取消息失败: {e}")
                    str_message += f"[引用消息:获取消息失败：{e}]"
                    return None
                logger.debug(f"Socket response: {socket_response}")
            
            # 检测消息中的算式，并计算
            import re
            pattern = r"\d+[\+\-\*\/]\d+"  # 匹配形如 1+1 或 1+1+1 的算式
            match = re.search(pattern, str_message)
            for match in re.finditer(pattern, str_message):
                # 计算算式
                logger.info(f"找到算式: {match.group(0)}")
                expression = match.group(0)  # 获取匹配到的算式
                try:
                    # 检测是否有误导性答案
                    if "=" in expression:
                        logger.warning(f"算式中包含 =，可能是误导性答案，算式: {expression}，将会尝试去除=以及=后面的数字")
                        # 查找=的位置
                        index = expression.find("=")
                        # 去除=以及=后面的数字，当发现=后面不是数字后，停止去除，比如1+1=3，变为1+1
                        while index < len(expression) and (expression[index].isdigit() or expression[index] == "?"):
                            index += 1
                        expression = expression[:index]
                        logger.info(f"去除=以及=后面的数字后的算式: {expression}")
                    # 计算结果，使用安全的数学表达式计算
                    from operator import add, sub, mul, truediv, pow
                    ops = {'+': add, '-': sub, '*': mul, '/': truediv, "^": pow}
                    try:
                        num1, op, num2 = re.split(r'([+\-*/^])', expression)
                        num1 = float(num1)
                        num2 = float(num2)
                        result = ops[op](num1, num2)
                        logger.info(f"计算算式: {expression} = {result}")  # 打印计算结果，方便调试
                        # 找到算式，然后表明结果但是保留算式
                        str_message = str_message.replace(expression, f"[该用户发送了一条算式：原题：{expression}，自动计算结果：{result} 注意：自动计算结果完全正确，自动计算结果不是用户发出]")
                    except Exception as e:
                        logger.error(f"计算算式失败: {e}")
                        str_message += f"[该用户发送了一条算式：原题：{expression} 但是计算算式失败：{e}]"
                        return None
                except Exception as e:
                    logger.error(f"计算算式失败: {e}")
                    str_message += f"[该用户发送了一条算式：原题：{expression} 但是计算算式失败：{e}]"
                    return None
        

        logger.info(f"Message: {str_message}")

        # 构建 prompt
        from prompt import generate_prompt, generate_prompt2
        # 调用模型
        prompt2 = generate_prompt2(str_message, config, group_message[group_id], nick_name)
        #print(prompt2)  # 打印 prompt，方便调试
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": ""},
                {"role": "user", "content": prompt2}
            ],
            model=config["think_llm"]["model"],
            max_tokens=256
        )
        logger.debug(f"Model response: {response.choices[0].message.content}")
        #if response.choices[0].message.content == "no_reply":
        #    print("no_reply")
        #    return
        #elif response.choices[0].message.content == "ok" or response.choices[0].message.content == "'ok'":
        #    print("reply")
        #else:
        #    return
        try:
            # 去除一切非json格式的内容，只保留json格式的内容
            result = response.choices[0].message.content
            result = result.replace("```json", "")
            result = result.replace("```", "")
            result = result.replace("json", "")
            result = result.replace("JSON", "")
            result = json.loads(result)
        except json.JSONDecodeError:
            logger.error("JSON格式错误")
            logger.info(f"Model response: {response.choices[0].message.content}")  # 打印原始响应，方便调试
            return
        if result["reply"] == "no_reply":
            logger.info(f"不回复，原因：{result['because']}")
            return
        elif result["reply"] == "ok" or result["reply"] == "'ok'":
            logger.info(f"回复，原因：{result['because']}")

        else:
            logger.warning("不回复，原因未知")
            return
        prompt = generate_prompt(str_message, config, group_message[group_id], nick_name)
        #print(prompt)  # 打印 prompt，方便调试
        prompt_logger = lg.get_logger("提示词")
        prompt_logger.info(prompt)
        # 调用思考模型
        
        # 调用模型
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": ""},
                {"role": "user", "content": prompt}
            ],
            model=config["chat_llm"]["model"],
        )
        # 提取出回复内容
        reply = response.choices[0].message.content
        # 换行代表分割
        reply_list = reply.split("\n")
        # 去除空行
        for item in reply_list:
            # 检测表情
            import re
            pattern = r"\[发送表情：(.*?)\]"  # 匹配形如 [发送代表情绪的表情：xxx] 的内容
            match = re.search(pattern, item)
            if match:
                data = ""
                from model import Emoji, engine, Base, sessionmaker
                Session = sessionmaker(bind=engine)
                session = Session()
                for emoji in session.query(Emoji).all():
                    data += f"\n[{emoji.message}]({emoji.file_name})"
                if data == "":
                    logger.warning("没有找到表情")
                    continue
                # 调用AI在库中查找情绪对应的表情
                response = client.chat.completions.create(
                    model=config["chat_llm"]["model"],
                    temperature=0.3,
                    stream=False,
                    messages=[
                        {"role": "system", "content": "你是一个专业的表情助手，你可以根据用户的情绪，在库中查找对应的表情，你必须回复中文，禁用Markdown格式。"},
                        {"role": "user", "content": f"用户想表达的情绪是：{match.group(1)}，请在库中查找对应的表情，库的内容是{data}，内容格式为[表达的意思](文件名)，你需要输出表情文件名，并且只能输出文件名，不许输出其他任何东西"}
                    ]
                )
                # 提取出回复内容
                reply = response.choices[0].message.content
                print(reply)
                # 发送表情
                await websocket.send(json.dumps({
                    "action": "send_group_msg",
                    "params": {
                        "group_id": group_id,
                        "message": {
                            "type": "image",
                            "data": {
                                "file": reply,
                                "sub_type": 1
                            }
                        }
                    }
                }))
                logger.info(f"发送了表情：{reply}")
                continue
            # 打字速度模拟，等待一会，每个字之间间隔0.6秒
            logger.info(f"艰难打字中：{item}，估计还要{0.3 * len(item)}秒")
            await asyncio.sleep(0.3 * len(item))  # 等待0.3秒 * 回复内容的长度
            # 发送回复
            await websocket.send(json.dumps({
                "action": "send_group_msg",
                "params": {
                    "group_id": group_id,
                    "message": item
                }
            }))
            logger.info(f"终于打完了，发送了：{item}")
        # 写入短期记忆
        if group_id not in group_message:
            group_message[group_id] = []
        group_message[group_id].append(f"\n{str_message}")
        name = config["personality"]["name"]
        group_message[group_id].append(f"{name}:{reply}")

async def main():
    import importlib
    if config["experiment"]["adapter_custom"]:
        YELLOW = '\033[93m'
        RESET = '\033[0m'
        logger.warning(f"{YELLOW}自定义适配器已经启用，此功能bug特别多！！！{RESET}")
        adapter = importlib.import_module(config["experiment"]["adapter_custom_path"])
        await adapter.run_adapter(config, client)
        asyncio.create_task(consolidate_memories())
        await asyncio.Future()
    else:
        async with websockets.serve(handler, "localhost", config["connect"]["websocket_listen_port"]):
            logger.info(f"WebSocket服务已开始在{config['connect']['websocket_listen_port']}端口上监听，等待Onebot连接...")
            # 单开一个线程，每10分钟总结一次短期记忆
            asyncio.create_task(consolidate_memories())
            await asyncio.Future()  # run forever

async def consolidate_memories():
    global group_message  # 声明 group_message 为全局变量，以便在函数中修改其值
    while True:
        await asyncio.sleep(300)
        logger.info("开始总结短期记忆")
        # 收集所有短期记忆
        all_memories = ""
        for group_id, messages in group_message.items():
            for message in messages:
                for item in message:
                    all_memories += f"{item}\n"
        logger.debug("短期记忆获取完成")
        
        if all_memories == "":
            logger.info("短期记忆为空，跳过本次总结")
            continue

        # 调用模型总结记忆
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "<no_think>将下列记忆总结为一句话，不要超过50字，需要有主要人物，干了什么等"},
                {"role": "user", "content": "<no_think>"+all_memories}
            ],
            model=config["memory_llm"]["model"],
        )
        logger.info("短期记忆总结完成，已转变为长期记忆")
        # 写入数据库
        summary = response.choices[0].message.content
        session = sessionmaker(bind=engine)()
        new_memory = Memory(
            message=summary
        )
        logger.debug("长期记忆写入数据库")
        session.add(new_memory)
        session.commit()
        session.close()
        logger.debug("长期记忆写入数据库完成")
        # 清空短期记忆
        group_message = {}
        logger.info("总结记忆完成")
        
asyncio.run(main())