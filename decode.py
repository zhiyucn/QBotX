import re
def decode_array(arrays):
    print(arrays)
    result = []
    # 遍历数组中的每个元素
    #logger.info(arrays)
    for array in arrays:
        # 如果元素是字符串类型
        if array["type"] == "text":
            # 提取出文本内容
            text = array["data"]["text"]
            result.append({"type": "text", "text": text})
        # 如果元素是图片类型
        elif array["type"] == "image":
            # 提取出图片的 URL
            url = array["data"]["url"]
            # 检测有没有subType
            if "subType" in array["data"] and "sub_type" in array["data"]:
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
    return result
    