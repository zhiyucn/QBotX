import websocket
import asyncio
import json
import logging
from typing import Dict, List
from logger import get_logger
import websockets
#from app import group_message
logger = get_logger("Onebot适配器")
websocket_ = None
async def run_adapter(config, client):
    # 监听8080端口的Websocket
    async def echo(websocket, path=None):
        global websocket_
        websocket_ = websocket
        async for message in websocket:
            #logger.info(f"收到来自Onebot的消息: {message}")
            import json
            message = json.loads(message)
            if "meta_event_type" in message and message["meta_event_type"] == "lifecycle":
                continue
            if "meta_event_type" in message and message["meta_event_type"] == "heartbeat":
                continue
            import message_handler 
            await message_handler.handler(message)

    server = await websockets.serve(echo, 'localhost', 8080)
    try:
        await server.wait_closed()
    finally:
        server.close()

def decode_array(arrays):
    result = []
    # 遍历数组中的每个元素
    #logger.info(arrays)
    if isinstance(arrays, str):
        logger.info("奇怪，怎么是字符串，转换再说")
        arrays = json.loads(arrays)
    #logger.info(arrays)
    arrays_index = arrays["message"]
    result.append({"type":"info","group_id": arrays["group_id"], "user_id": arrays["sender"]["user_id"],"user_name":arrays["sender"]["nickname"]})
    for array in arrays_index:
        # 如果元素是字符串类型
        #logger.info(array)
        if array["type"] == "text":
            # 提取出文本内容
            text = array["data"]["text"]
            result.append({"type": "text", "text": text})
        # 如果元素是图片类型
        elif array["type"] == "image":
            # 提取出图片的 URL
            url = array["data"]["url"]
            # 检测有没有subType
            if "subType" in array["data"]:
                result.append({"type": "image", "url": url, "subtype": array["data"]["subType"], "file": array["data"]["file"]})
            else:
                result.append({"type": "image", "url": url, "subtype": array["data"]["sub_type"], "file": array["data"]["file"]})
        elif array["type"] == "at":
            # 提取出 at 信息
            user_id = array["data"]["qq"]
            result.append({"type": "at", "user_id": user_id})
        elif array["type"] == "reply":
            # 提取出 reply 信息
            message_id = array["data"]["id"]
            result.append({"type": "reply", "message_id": message_id})
    logger.info("消息处理完成")
    return result
    
async def send_text(group_id, message):
    # 发送文本消息
    websocket = websocket_
    await websocket.send(json.dumps({
        "action": "send_group_msg",
        "params": {
            "group_id": group_id,
            "message": message
        }
    }))

async def send_image(group_id, image_path):
    # 发送图片消息
    websocket = websocket_
    await websocket.send(json.dumps({
    "action": "send_group_msg",
    "params": {
        "group_id": group_id,
        "message": [
            {
                "type": "image",
                "data": {
                    "file": image_path
                }
            }
        ]
    }
}))

async def get_group_member_info(group_id, user_id):
    websocket = websocket_
    await websocket.send(json.dumps({
        "action": "get_group_member_info",
        "params": {
            "group_id": group_id,
            "user_id": user_id,
            "no_cache": False
        }
    }))
    response = await websocket.recv()
    # 处理消息
    response = json.loads(response)
    return response["data"]["nickname"]
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Create a new event loop for this operation
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                result = new_loop.run_until_complete(get_info())
                return result
            finally:
                new_loop.close()
                asyncio.set_event_loop(loop)
        else:
            return await loop.run_until_complete(get_info())
    except Exception as e:
        logger.error(f"获取群成员信息失败: {e}")
        return None
    """
