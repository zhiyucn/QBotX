import logger
logger = logger.get_logger("提示词生成器")
def generate_prompt(question, config, group_message, nick_name):
    # 构建 prompt
    name = config["personality"]["name"]
    personality = config["personality"]["personality_core"]
    language_style = config["personality"]["language_style"]
    # 遍历添加 personality_side 中的每个元素
    personality_side = ""
    for item in config["personality"]["personality_side"]:
        personality_side += f"{item}\n"
    
    # 遍历添加短期记忆中的每个元素
    short_term_memory = ""
    for value in group_message:
        short_term_memory += f"{value}\n"
    
    from model import Memory, engine, Base, sessionmaker
    # 读取长期记忆
    Session = sessionmaker(bind=engine)
    session = Session()
    long_term_memory = session.query(Memory).all()
    # 只读取后 50 条
    long_term_memory = long_term_memory[-50:]
    # 遍历添加长期记忆中的每个元素
    long_term_memory_str = ""
    for item in long_term_memory:
        long_term_memory_str += f"{item.message} 创建时间{item.created_at}\n"
    # 关闭 session
    session.close()
    # 构建 prompt
    prompt = f"""你是{name}，你的人格特征是{personality}，你的侧面特征是{personality_side}，你最近的短期记忆是{short_term_memory}，你最近的长期记忆是{long_term_memory_str}，你的语言风格是{language_style}，
现在，{nick_name}在群中发布了新的消息：{question}，这条消息引起了你的注意，你需要回复他，根据你的人格特征和侧面特征，以及记忆来回复他，"""
    if config["personality"]["world"] == "reality":
        prompt += "你的回复不需要多余的符号，尽量在15字以内。换行代表分割"
    elif config["personality"]["world"] == "dummy":
        prompt += "你正在扮演这个角色，可以使用符号，使用括号括起来的内容表示你的动作或心情，尽量超过25字。"
    # 中文高手
    import random
    # 5%概率
    if random.random() < 0.05:
        prompt += "\n你喜欢使用文言文" 
    elif random.random() < 0.05:
        prompt += "\n你喜欢使用倒装句"
    elif random.random() < 0.10:
        prompt += "\n你喜欢使用成语"
    elif random.random() < 0.10:
        prompt += "\n你喜欢使用俗语"
    elif random.random() < 0.05:
        prompt += "\n你喜欢使用谐音梗"


    # 加载配置文件中的表情包使用概率
    emoji_probability = config["emoji"]["use_emoji_need"]
    # 随机生成一个数字
    random_number = random.random()
    # 如果随机生成的数字小于配置文件中的表情包使用概率
    if random_number < emoji_probability:
        prompt += "\n输出[发送表情：你想表达的情绪]可以发出表情包"
        logger.info("本次回答可以使用表情包")
    return prompt
def generate_prompt2(question, config, group_message, nick_name):
    # 构建 prompt
    name = config["personality"]["name"]
    personality = config["personality"]["personality_core"]
    # 遍历添加 personality_side 中的每个元素
    personality_side = ""
    for item in config["personality"]["personality_side"]:
        personality_side += f"{item}\n"
    # 遍历添加短期记忆中的每个元素
    short_term_memory = ""
    for value in group_message:
        short_term_memory += f"{value}\n"
    # 读取长期记忆
    from model import Memory, engine, Base, sessionmaker
    Session = sessionmaker(bind=engine)
    session = Session()
    long_term_memory = session.query(Memory).all()
    # 只读取后 50 条
    long_term_memory = long_term_memory[-50:]
    # 遍历添加长期记忆中的每个元素
    long_term_memory_str = ""
    for item in long_term_memory:
        long_term_memory_str += f"{item.message}\n"
    # 关闭 session
    session.close()
    # 构建 prompt
    prompt = f"""<no_think>你是{name}，你的人格特征是{personality}，你的侧面特征是{personality_side}，你最近的短期记忆是{short_term_memory}，你最近的长期记忆是{long_term_memory_str}，
现在，{nick_name}在群中发布了新的消息：{question}，你现在必须回复一段json格式的消息，其中reply字段可以为no_reply或ok，'no_reply'代表你不回复这条消息，'ok'代表你需要回复这条消息，还有一个because字段，里面需要填写你为什么这么做，需要纯文本。你必须只回复json格式的消息"""
    return prompt