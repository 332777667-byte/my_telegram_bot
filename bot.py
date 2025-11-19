import logging
import os
import random
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 设置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 从环境变量获取Token
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
if not TOKEN:
    logging.error("未设置TELEGRAM_BOT_TOKEN环境变量")
    exit(1)

# 本地图片文件名 - 确保这些图片文件放在与bot.py相同的文件夹中
LOCAL_IMAGE_PATH = "welcome.jpg"  # 欢迎图片
RECHARGE_IMAGE_PATH = "recharge_guide.jpg"  # 余额充值说明图片
RECHARGE_DETAIL_IMAGE_PATH = "recharge_detail.jpg"  # 充值详情图片
RECHARGE_QR_IMAGE_PATH = "recharge_qr.jpg"  # 充值二维码图片
BUY_CARD_IMAGE_PATH = "buy_card.jpg"  # 购买卡密图片
INSUFFICIENT_BALANCE_IMAGE_PATH = "insufficient_balance.jpg"  # 余额不足图片
EXTRACT_CARD_IMAGE_PATH = "extract_card.jpg"  # 提取卡密图片
TUTORIAL_CENTER_IMAGE_PATH = "tutorial_center.jpg"  # 教程中心图片
PERSONAL_CENTER_IMAGE_PATH = "personal_center.jpg"  # 个人中心图片
CONTACT_SERVICE_IMAGE_PATH = "contact_service.jpg"  # 联系客服图片

# 群组链接
GROUP_LINK = "https://t.me/+clVPu6NqumQ2ZjU0"

# USDT地址
USDT_ADDRESS = "TC1VcL6xZXLma7bbpKnmdaATLCFMSYxkdk"

# 汇率
EXCHANGE_RATE = 7.10  # 1 USDT = 7.10 元

# 充值金额和赠送比例配置
RECHARGE_OPTIONS = {
    "50": {"bonus_percent": 0, "bonus_amount": 0, "agent_level": 0},
    "100": {"bonus_percent": 0, "bonus_amount": 0, "agent_level": 0},
    "300": {"bonus_percent": 0, "bonus_amount": 0, "agent_level": 0},
    "500": {"bonus_percent": 0, "bonus_amount": 0, "agent_level": 0},
    "800": {"bonus_percent": 2, "bonus_amount": 16, "agent_level": 0},
    "1000": {"bonus_percent": 5, "bonus_amount": 50, "agent_level": 0},
    "2000": {"bonus_percent": 10, "bonus_amount": 200, "agent_level": 0},
    "3000": {"bonus_percent": 12, "bonus_amount": 360, "agent_level": 0},
    "5000": {"bonus_percent": 15, "bonus_amount": 750, "agent_level": 1},
    "10000": {"bonus_percent": 20, "bonus_amount": 2000, "agent_level": 2},
    "20000": {"bonus_percent": 21, "bonus_amount": 4200, "agent_level": 3},
    "30000": {"bonus_percent": 22, "bonus_amount": 6600, "agent_level": 4},
    "50000": {"bonus_percent": 25, "bonus_amount": 12500, "agent_level": 5}
}

# 卡密面值配置
CARD_DENOMINATIONS = {
    "50": {"price": 40, "discount": "8折"},
    "200": {"price": 160, "discount": "8折"},
    "500": {"price": 400, "discount": "8折"},
    "800": {"price": 640, "discount": "8折"},
    "1000": {"price": 750, "discount": "7.5折"},
    "2000": {"price": 1400, "discount": "7折"},
    "3000": {"price": 2040, "discount": "6.8折"},
    "5000": {"price": 3250, "discount": "6.5折"}
}

# 代理等级描述
AGENT_LEVEL_DESCRIPTION = {
    1: "额外赠送1级代理，购卡享受1%优惠！",
    2: "额外赠送2级代理，购卡享受2%优惠！",
    3: "额外赠送3级代理，购卡享受3%优惠！",
    4: "额外赠送4级代理，购卡享受4%优惠！",
    5: "额外赠送5级代理，购卡享受5%优惠！"
}

# 生成订单编号
def generate_order_id():
    timestamp = int(time.time())
    random_num = random.randint(100000, 999999)
    return f"D{timestamp}{random_num}"

# 创建回复键盘（功能键盘）- 已删除升级代理、担保公群、邀请赚钱按钮
def get_reply_keyboard():
    keyboard = [
        ["余额充值", "购买卡密", "提取卡密"],
        ["教程中心", "联系客服", "个人中心"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, input_field_placeholder="请选择功能...")

# 创建内联键盘按钮
def get_main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("进入公群", url=GROUP_LINK)],
        [InlineKeyboardButton("联系客服", url="https://t.me/JDEKa2288_vip")],
        [InlineKeyboardButton("查看教程", callback_data="tutorial_center")]
    ]
    return InlineKeyboardMarkup(keyboard)

# 创建充值金额选择键盘
def get_recharge_amount_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("50元", callback_data="recharge_50"),
            InlineKeyboardButton("100元", callback_data="recharge_100")
        ],
        [
            InlineKeyboardButton("300元", callback_data="recharge_300"),
            InlineKeyboardButton("500元", callback_data="recharge_500")
        ],
        [
            InlineKeyboardButton("800元|送2%", callback_data="recharge_800"),
            InlineKeyboardButton("1000元|送5%", callback_data="recharge_1000")
        ],
        [
            InlineKeyboardButton("2000元|送10%", callback_data="recharge_2000"),
            InlineKeyboardButton("3000元|送12%", callback_data="recharge_3000")
        ],
        [
            InlineKeyboardButton("5000元|送15%", callback_data="recharge_5000"),
            InlineKeyboardButton("10000元|送20%", callback_data="recharge_10000")
        ],
        [
            InlineKeyboardButton("20000元|送21%", callback_data="recharge_20000"),
            InlineKeyboardButton("30000元|送22%", callback_data="recharge_30000")
        ],
        [
            InlineKeyboardButton("50000元|送25%", callback_data="recharge_50000"),
            InlineKeyboardButton("关闭", callback_data="close_recharge")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# 创建充值确认键盘
def get_recharge_confirm_keyboard(amount):
    keyboard = [
        [InlineKeyboardButton("确认充值", callback_data=f"confirm_recharge_{amount}")],
        [InlineKeyboardButton("关闭", callback_data="close_recharge")]
    ]
    return InlineKeyboardMarkup(keyboard)

# 创建充值完成键盘
def get_recharge_complete_keyboard():
    keyboard = [
        [InlineKeyboardButton("USDT购买/提升教程", callback_data="usdt_tutorial")],
        [InlineKeyboardButton("联系客服", url="https://t.me/JDEKa2288_vip")],
        [InlineKeyboardButton("关闭", callback_data="close_recharge")]
    ]
    return InlineKeyboardMarkup(keyboard)

# 创建购买卡密面值选择键盘
def get_buy_card_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("面值50元 | 40元", callback_data="buy_card_50"),
            InlineKeyboardButton("面值200元 | 160元", callback_data="buy_card_200")
        ],
        [
            InlineKeyboardButton("面值500元 | 400元", callback_data="buy_card_500"),
            InlineKeyboardButton("面值800元 | 640元", callback_data="buy_card_800")
        ],
        [
            InlineKeyboardButton("面值1000元 | 750元", callback_data="buy_card_1000"),
            InlineKeyboardButton("面值2000元 | 1400元", callback_data="buy_card_2000")
        ],
        [
            InlineKeyboardButton("面值3000元 | 2040元", callback_data="buy_card_3000"),
            InlineKeyboardButton("面值5000元 | 3250元", callback_data="buy_card_5000")
        ],
        [
            InlineKeyboardButton("关闭", callback_data="close_buy_card")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# 创建余额不足提示键盘（已删除"立即充值"按钮）
def get_insufficient_balance_keyboard():
    keyboard = [
        [InlineKeyboardButton("关闭", callback_data="close_buy_card")]
    ]
    return InlineKeyboardMarkup(keyboard)

# 创建提取卡密键盘
def get_extract_card_keyboard():
    keyboard = [
        [InlineKeyboardButton("关闭", callback_data="close_extract_card")]
    ]
    return InlineKeyboardMarkup(keyboard)

# 创建教程中心键盘按钮 - 按照图片内容制作，点击后跳转到指定链接
def get_tutorial_center_keyboard():
    keyboard = [
        [InlineKeyboardButton("礼品卡项目搬砖简介", url="https://t.me/jdekbzpd/3")],
        [InlineKeyboardButton("火币交易所购买USDT教程", url="https://t.me/jdekbzpd/6")],
        [InlineKeyboardButton("微信核销卡密变现教程", url="https://t.me/jdekbzpd/7")],
        [InlineKeyboardButton("返回主菜单", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

# 创建个人中心键盘按钮 - 只有一个返回菜单按钮
def get_personal_center_keyboard():
    keyboard = [
        [InlineKeyboardButton("返回主菜单", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

# 创建联系客服键盘按钮 - 只有一个在线客服按钮
def get_contact_service_keyboard():
    keyboard = [
        [InlineKeyboardButton("在线客服", url="https://t.me/JDEKa2288_vip")]
    ]
    return InlineKeyboardMarkup(keyboard)

# /start 命令的处理函数 - 发送带本地图片和按钮的消息
def start_command(update: Update, context: CallbackContext):
    # 更新后的消息文本，与图片内容一致
    caption = """项目操作流程
- ①火币交易所注册
- ②火币交易所购买USDT
- ③余额充值
- ④购买卡密
- ⑤提取卡密
- ⑥微信核销卡密
- ⑦微信打款给您

唯一客服 @JDEKa2288_vip谨防假冒

新用户请看下教程"""

    try:
        # 检查图片文件是否存在
        if not os.path.exists(LOCAL_IMAGE_PATH):
            # 如果图片不存在，只发送文字和按钮
            update.message.reply_text(
                text=caption,
                reply_markup=get_main_menu_keyboard()
            )
            # 同时发送提示信息
            update.message.reply_text("⚠️ 欢迎图片未找到，请确保welcome.jpg文件存在于机器人目录中")
        else:
            # 发送本地图片消息，附带文字和按钮
            with open(LOCAL_IMAGE_PATH, 'rb') as photo:
                context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=photo,
                    caption=caption,
                    reply_markup=get_main_menu_keyboard()
                )
        
        # 发送功能键盘提示消息
        update.message.reply_text(
            "菜单 - 下方是功能键盘！",
            reply_markup=get_reply_keyboard()
        )
        
    except Exception as e:
        # 如果发送图片失败，发送错误信息
        logging.error(f"发送图片时出错: {e}")
        update.message.reply_text(
            text="发送欢迎图片时出错，但机器人功能正常。\n\n" + caption,
            reply_markup=get_main_menu_keyboard()
        )
        update.message.reply_text(
            "菜单 - 下方是功能键盘！",
            reply_markup=get_reply_keyboard()
        )

# 处理回复键盘按钮点击
def handle_reply_buttons(update: Update, context: CallbackContext):
    text = update.message.text
    user = update.message.from_user
    
    if text == "余额充值":
        # 余额充值说明文字
        recharge_text = """
  单笔充值如下金额赠送代理等级1  
  单笔充值 5000 元赠送代理等级1 级  
  单笔充值 10000 元赠送代理等级 2 级  
  单笔充值 20000 元赠送代理等级 3 级  
  单笔充值 30000 元赠送代理等级 4 级  
  单笔充值 50000 元赠送代理等级 5 级  

例：您当前代理等级是0级，充值5000元送1级，则您的代理等级为0+1=1级

请选择充值金额："""
        
        try:
            # 检查余额充值图片是否存在
            if not os.path.exists(RECHARGE_IMAGE_PATH):
                # 如果图片不存在，只发送文字和按钮
                update.message.reply_text(
                    text=recharge_text,
                    reply_markup=get_recharge_amount_keyboard()
                )
                # 同时发送提示信息
                update.message.reply_text("⚠️ 余额充值说明图片未找到，请确保recharge_guide.jpg文件存在于机器人目录中")
            else:
                # 发送本地图片消息，附带文字和按钮
                with open(RECHARGE_IMAGE_PATH, 'rb') as photo:
                    context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=photo,
                        caption=recharge_text,
                        reply_markup=get_recharge_amount_keyboard()
                    )
                
        except Exception as e:
            # 如果发送图片失败，发送错误信息
            logging.error(f"发送余额充值图片时出错: {e}")
            update.message.reply_text(
                text="发送余额充值说明图片时出错。\n\n" + recharge_text,
                reply_markup=get_recharge_amount_keyboard()
            )
    
    elif text == "购买卡密":
        # 获取用户昵称，如果没有昵称则使用用户名，如果都没有则使用"未知用户"
        user_nickname = user.first_name or user.username or "未知用户"
        
        # 购买卡密页面文字
        buy_card_text = f"""▫️用户昵称： {user_nickname}
▫️用户余额： 0.01 元
▫️代理等级： 0级代理 
▫️代理积分： 0 分
▫️请选择 京东E卡 面值"""
        
        try:
            # 检查购买卡密图片是否存在
            if not os.path.exists(BUY_CARD_IMAGE_PATH):
                # 如果图片不存在，只发送文字和按钮
                update.message.reply_text(
                    text=buy_card_text,
                    reply_markup=get_buy_card_keyboard()
                )
                # 同时发送提示信息
                update.message.reply_text("⚠️ 购买卡密图片未找到，请确保buy_card.jpg文件存在于机器人目录中")
            else:
                # 发送本地图片消息，附带文字和按钮
                with open(BUY_CARD_IMAGE_PATH, 'rb') as photo:
                    context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=photo,
                        caption=buy_card_text,
                        reply_markup=get_buy_card_keyboard()
                    )
                
        except Exception as e:
            # 如果发送图片失败，发送错误信息
            logging.error(f"发送购买卡密图片时出错: {e}")
            update.message.reply_text(
                text="发送购买卡密图片时出错。\n\n" + buy_card_text,
                reply_markup=get_buy_card_keyboard()
            )
    
    elif text == "提取卡密":
        # 提取卡密页面文字
        extract_card_text = "▫️您没有购卡订单"
        
        try:
            # 检查提取卡密图片是否存在
            if not os.path.exists(EXTRACT_CARD_IMAGE_PATH):
                # 如果图片不存在，只发送文字和按钮
                update.message.reply_text(
                    text=extract_card_text,
                    reply_markup=get_extract_card_keyboard()
                )
                # 同时发送提示信息
                update.message.reply_text("⚠️ 提取卡密图片未找到，请确保extract_card.jpg文件存在于机器人目录中")
            else:
                # 发送本地图片消息，附带文字和按钮
                with open(EXTRACT_CARD_IMAGE_PATH, 'rb') as photo:
                    context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=photo,
                        caption=extract_card_text,
                        reply_markup=get_extract_card_keyboard()
                    )
                
        except Exception as e:
            # 如果发送图片失败，发送错误信息
            logging.error(f"发送提取卡密图片时出错: {e}")
            update.message.reply_text(
                text="发送提取卡密图片时出错。\n\n" + extract_card_text,
                reply_markup=get_extract_card_keyboard()
            )
    
    elif text == "教程中心":
        # 教程中心文字
        tutorial_text = """请选择您需要查看的教程："""
        
        try:
            # 检查教程中心图片是否存在
            if not os.path.exists(TUTORIAL_CENTER_IMAGE_PATH):
                # 如果图片不存在，只发送文字和按钮
                update.message.reply_text(
                    text=tutorial_text,
                    reply_markup=get_tutorial_center_keyboard()
                )
                # 同时发送提示信息
                update.message.reply_text("⚠️ 教程中心图片未找到，请确保tutorial_center.jpg文件存在于机器人目录中")
            else:
                # 发送本地图片消息，附带文字和按钮
                with open(TUTORIAL_CENTER_IMAGE_PATH, 'rb') as photo:
                    context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=photo,
                        caption=tutorial_text,
                        reply_markup=get_tutorial_center_keyboard()
                    )
                
        except Exception as e:
            # 如果发送图片失败，发送错误信息
            logging.error(f"发送教程中心图片时出错: {e}")
            update.message.reply_text(
                text="发送教程中心图片时出错。\n\n" + tutorial_text,
                reply_markup=get_tutorial_center_keyboard()
            )
    
    elif text == "联系客服":
        # 联系客服文字 - 使用纯文本格式避免解析错误
        contact_service_text = """📞 联系客服

如有任何问题，请直接联系我们的客服：
@JDEKa2288_vip

工作时间：全天24小时"""
        
        try:
            # 检查联系客服图片是否存在
            if not os.path.exists(CONTACT_SERVICE_IMAGE_PATH):
                # 如果图片不存在，只发送文字和按钮
                update.message.reply_text(
                    text=contact_service_text,
                    reply_markup=get_contact_service_keyboard()
                )
                # 同时发送提示信息
                update.message.reply_text("⚠️ 联系客服图片未找到，请确保contact_service.jpg文件存在于机器人目录中")
            else:
                # 发送本地图片消息，附带文字和按钮
                with open(CONTACT_SERVICE_IMAGE_PATH, 'rb') as photo:
                    context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=photo,
                        caption=contact_service_text,
                        reply_markup=get_contact_service_keyboard()
                    )
                
        except Exception as e:
            # 如果发送图片失败，发送错误信息
            logging.error(f"发送联系客服图片时出错: {e}")
            update.message.reply_text(
                text="发送联系客服图片时出错。\n\n" + contact_service_text,
                reply_markup=get_contact_service_keyboard()
            )
    
    elif text == "个人中心":
        # 获取用户昵称，如果没有昵称则使用用户名，如果都没有则使用"未知用户"
        user_nickname = user.first_name or user.username or "未知用户"
        
        # 个人中心文字 - 使用指定的格式
        personal_center_text = f"""▫️用户编号：7775227112
▫️用户昵称：{user_nickname}
▫️用户余额： 0.01 元
▫️代理等级： 0 级
▫️代理积分： 0 分"""
        
        try:
            # 检查个人中心图片是否存在
            if not os.path.exists(PERSONAL_CENTER_IMAGE_PATH):
                # 如果图片不存在，只发送文字和按钮
                update.message.reply_text(
                    text=personal_center_text,
                    reply_markup=get_personal_center_keyboard()
                )
                # 同时发送提示信息
                update.message.reply_text("⚠️ 个人中心图片未找到，请确保personal_center.jpg文件存在于机器人目录中")
            else:
                # 发送本地图片消息，附带文字和按钮
                with open(PERSONAL_CENTER_IMAGE_PATH, 'rb') as photo:
                    context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=photo,
                        caption=personal_center_text,
                        reply_markup=get_personal_center_keyboard()
                    )
                
        except Exception as e:
            # 如果发送图片失败，发送错误信息
            logging.error(f"发送个人中心图片时出错: {e}")
            update.message.reply_text(
                text="发送个人中心图片时出错。\n\n" + personal_center_text,
                reply_markup=get_personal_center_keyboard()
            )
    
    elif text == "返回主菜单":
        update.message.reply_text(
            "返回主菜单",
            reply_markup=get_reply_keyboard()
        )
    
    else:
        update.message.reply_text(
            f"您点击了: {text}\n如需返回主菜单，请点击'返回主菜单'",
            reply_markup=get_reply_keyboard()
        )

# 处理内联按钮回调
def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    
    # 处理教程图片按钮
    if query.data == "tutorial_image":
        # 教程中心文字
        tutorial_text = """请选择您需要查看的教程："""
        
        try:
            # 检查教程中心图片是否存在
            if not os.path.exists(TUTORIAL_CENTER_IMAGE_PATH):
                # 如果图片不存在，只发送文字和按钮
                query.edit_message_caption(
                    caption=tutorial_text,
                    reply_markup=get_tutorial_center_keyboard()
                )
            else:
                # 发送本地图片消息，附带文字和按钮
                with open(TUTORIAL_CENTER_IMAGE_PATH, 'rb') as photo:
                    context.bot.send_photo(
                        chat_id=query.message.chat_id,
                        photo=photo,
                        caption=tutorial_text,
                        reply_markup=get_tutorial_center_keyboard()
                    )
                # 删除原来的消息
                query.message.delete()
                
        except Exception as e:
            # 如果发送图片失败，发送错误信息
            logging.error(f"发送教程中心图片时出错: {e}")
            query.edit_message_text(
                text="发送教程中心图片时出错。\n\n" + tutorial_text,
                reply_markup=get_tutorial_center_keyboard()
            )
    
    # 处理充值金额选择
    elif query.data.startswith("recharge_"):
        amount = query.data.replace("recharge_", "")
        
        # 获取充值配置
        recharge_config = RECHARGE_OPTIONS.get(amount)
        if recharge_config:
            bonus_percent = recharge_config["bonus_percent"]
            bonus_amount = recharge_config["bonus_amount"]
            agent_level = recharge_config["agent_level"]
            total_amount = int(amount) + bonus_amount
            
            # 生成额外福利描述
            extra_benefit = "无"
            if agent_level > 0:
                extra_benefit = AGENT_LEVEL_DESCRIPTION[agent_level]
            
            # 生成充值详情文本 - 使用你要求的格式
            detail_text = f"""温馨提示

如果您的电报 不是 在 https://telegram.org 下载，则有可能被 窃取 和 篡改 数据！

▫️充值金额：{amount} 元
▫️首充赠送：{bonus_amount} 元（{bonus_percent}%）
▫️金额首充：是
▫️总计到账：{total_amount} 元
▫️额外福利：{extra_benefit}"""
            
            try:
                # 检查充值详情图片是否存在
                if not os.path.exists(RECHARGE_DETAIL_IMAGE_PATH):
                    # 如果图片不存在，只发送文字
                    query.edit_message_caption(
                        caption=detail_text,
                        reply_markup=get_recharge_confirm_keyboard(amount)
                    )
                else:
                    # 发送充值详情图片消息，附带文字
                    with open(RECHARGE_DETAIL_IMAGE_PATH, 'rb') as photo:
                        context.bot.send_photo(
                            chat_id=query.message.chat_id,
                            photo=photo,
                            caption=detail_text,
                            reply_markup=get_recharge_confirm_keyboard(amount)
                        )
                    # 删除原来的消息
                    query.message.delete()
                    
            except Exception as e:
                # 如果发送图片失败，发送错误信息
                logging.error(f"发送充值详情图片时出错: {e}")
                query.edit_message_text(
                    text="发送充值详情图片时出错。\n\n" + detail_text,
                    reply_markup=get_recharge_confirm_keyboard(amount)
                )
    
    # 处理充值确认
    elif query.data.startswith("confirm_recharge_"):
        amount = query.data.replace("confirm_recharge_", "")
        
        # 获取充值配置
        recharge_config = RECHARGE_OPTIONS.get(amount)
        if recharge_config:
            bonus_amount = recharge_config["bonus_amount"]
            total_amount = int(amount) + bonus_amount
            
            # 计算USDT数量
            usdt_amount = round(total_amount / EXCHANGE_RATE, 4)
            
            # 生成订单编号
            order_id = generate_order_id()
            
            # 生成充值页面文本 - 使用你要求的新格式
            recharge_page_text = f"""▫️订单编号：{order_id}
▫️当前汇率：1 USDT = {EXCHANGE_RATE} 元
▫️订单金额：{amount} 元（{usdt_amount} USDT）
▫️赠送金额：{bonus_amount} 元
▫️总计到账：{total_amount} 元
----------------------
🔸提币网络：TRC20
🔸提币数量：{usdt_amount} USDT
🔸提币地址：
{USDT_ADDRESS}
----------------------
‼️提币地址前后  {USDT_ADDRESS[:5]}  ...  {USDT_ADDRESS[-5:]}  请仔细核对！
🚫如果 提币地址 与 二维码地址 不相同请勿支付！
👩‍💻唯一客服 @JDEKa2288_vip"""
            
            try:
                # 检查充值二维码图片是否存在
                if not os.path.exists(RECHARGE_QR_IMAGE_PATH):
                    # 如果图片不存在，只发送文字
                    query.edit_message_text(
                        text=recharge_page_text,
                        reply_markup=get_recharge_complete_keyboard()
                    )
                else:
                    # 发送充值二维码图片消息，附带文字
                    with open(RECHARGE_QR_IMAGE_PATH, 'rb') as photo:
                        context.bot.send_photo(
                            chat_id=query.message.chat_id,
                            photo=photo,
                            caption=recharge_page_text,
                            reply_markup=get_recharge_complete_keyboard()
                        )
                    # 删除原来的消息
                    query.message.delete()
                    
            except Exception as e:
                # 如果发送图片失败，发送错误信息
                logging.error(f"发送充值二维码图片时出错: {e}")
                query.edit_message_text(
                    text="发送充值二维码图片时出错。\n\n" + recharge_page_text,
                    reply_markup=get_recharge_complete_keyboard()
                )
    
    # 处理购买卡密面值选择 - 显示余额不足提示
    elif query.data.startswith("buy_card_"):
        denomination = query.data.replace("buy_card_", "")
        
        # 获取卡密配置
        card_config = CARD_DENOMINATIONS.get(denomination)
        if card_config:
            price = card_config["price"]
            
            # 生成余额不足提示文本 - 按照您提供的格式
            insufficient_balance_text = f"""▫️现价： {price} 元
▫️应付： {price} 元
▫️余额： 0.01 元

🔔余额不足，请充值！

请点击👉[ /chongzhi ] 充值余额。"""
            
            try:
                # 检查余额不足图片是否存在
                if not os.path.exists(INSUFFICIENT_BALANCE_IMAGE_PATH):
                    # 如果图片不存在，只发送文字
                    query.edit_message_caption(
                        caption=insufficient_balance_text,
                        reply_markup=get_insufficient_balance_keyboard()
                    )
                else:
                    # 发送余额不足图片消息，附带文字
                    with open(INSUFFICIENT_BALANCE_IMAGE_PATH, 'rb') as photo:
                        context.bot.send_photo(
                            chat_id=query.message.chat_id,
                            photo=photo,
                            caption=insufficient_balance_text,
                            reply_markup=get_insufficient_balance_keyboard()
                        )
                    # 删除原来的消息
                    query.message.delete()
                    
            except Exception as e:
                # 如果发送图片失败，发送错误信息
                logging.error(f"发送余额不足图片时出错: {e}")
                query.edit_message_text(
                    text="发送余额不足图片时出错。\n\n" + insufficient_balance_text,
                    reply_markup=get_insufficient_balance_keyboard()
                )
    
    # 处理从卡密购买页面跳转到充值（此功能已删除，但保留回调处理以防万一）
    elif query.data == "recharge_from_card":
        # 余额充值说明文字
        recharge_text = """# 六部无值

- A 单笔充值如下金额赠送代理等级1  
  单笔充值 5000 元赠送代理等级1 级  
  单笔充值 10000 元赠送代理等级 2 级  
  单笔充值 20000 元赠送代理等级 3 级  
  单笔充值 30000 元赠送代理等级 4 级  
  单笔充值 50000 元赠送代理等级 5 级  

例：您当前代理等级是0级，充值5000元送1级，则您的代理等级为0+1=1级

请选择充值金额："""
        
        try:
            # 检查余额充值图片是否存在
            if not os.path.exists(RECHARGE_IMAGE_PATH):
                # 如果图片不存在，只发送文字和按钮
                query.edit_message_caption(
                    caption=recharge_text,
                    reply_markup=get_recharge_amount_keyboard()
                )
            else:
                # 发送本地图片消息，附带文字和按钮
                with open(RECHARGE_IMAGE_PATH, 'rb') as photo:
                    context.bot.send_photo(
                        chat_id=query.message.chat_id,
                        photo=photo,
                        caption=recharge_text,
                        reply_markup=get_recharge_amount_keyboard()
                    )
                # 删除原来的消息
                query.message.delete()
                
        except Exception as e:
            # 如果发送图片失败，发送错误信息
            logging.error(f"发送余额充值图片时出错: {e}")
            query.edit_message_text(
                text="发送余额充值说明图片时出错。\n\n" + recharge_text,
                reply_markup=get_recharge_amount_keyboard()
            )
    
    # 处理关闭充值
    elif query.data == "close_recharge":
        query.message.delete()
    
    # 处理关闭购买卡密
    elif query.data == "close_buy_card":
        query.message.delete()
    
    # 处理关闭提取卡密
    elif query.data == "close_extract_card":
        query.message.delete()
    
    # 处理USDT教程
    elif query.data == "usdt_tutorial":
        usdt_tutorial_text = """💰 USDT购买/提升教程

步骤1：购买USDT
- 登录火币、币安等交易所
- 进入"买币"或"快捷买卖"页面
- 选择购买金额和支付方式
- 完成购买获取USDT

步骤2：转账到指定地址
- 复制我们提供的USDT地址
- 在交易所选择"提现"或"转账"
- 选择TRC20网络
- 输入提示数量和地址
- 确认转账

步骤3：等待到账
- 转账完成后
- 系统会自动处理充值
- 通常在10-30分钟内到账
- 如有问题请联系客服"""
        
        query.edit_message_caption(
            caption=usdt_tutorial_text,
            reply_markup=get_tutorial_center_keyboard()
        )
    
    elif query.data == "tutorial_center":
        # 教程中心文字
        tutorial_text = """请选择您需要查看的教程："""
        
        try:
            # 检查教程中心图片是否存在
            if not os.path.exists(TUTORIAL_CENTER_IMAGE_PATH):
                # 如果图片不存在，只发送文字和按钮
                query.edit_message_caption(
                    caption=tutorial_text,
                    reply_markup=get_tutorial_center_keyboard()
                )
            else:
                # 发送本地图片消息，附带文字和按钮
                with open(TUTORIAL_CENTER_IMAGE_PATH, 'rb') as photo:
                    context.bot.send_photo(
                        chat_id=query.message.chat_id,
                        photo=photo,
                        caption=tutorial_text,
                        reply_markup=get_tutorial_center_keyboard()
                    )
                # 删除原来的消息
                query.message.delete()
                
        except Exception as e:
            # 如果发送图片失败，发送错误信息
            logging.error(f"发送教程中心图片时出错: {e}")
            query.edit_message_text(
                text="发送教程中心图片时出错。\n\n" + tutorial_text,
                reply_markup=get_tutorial_center_keyboard()
            )
    
    elif query.data == "personal_center":
        # 获取用户昵称，如果没有昵称则使用用户名，如果都没有则使用"未知用户"
        user = query.from_user
        user_nickname = user.first_name or user.username or "未知用户"
        
        # 个人中心文字 - 使用指定的格式
        personal_center_text = f"""▫️用户编号：7775227112
▫️用户昵称：{user_nickname}
▫️用户余额： 0.01 元
▫️代理等级： 0 级
▫️代理积分： 0 分"""
        
        try:
            # 检查个人中心图片是否存在
            if not os.path.exists(PERSONAL_CENTER_IMAGE_PATH):
                # 如果图片不存在，只发送文字和按钮
                query.edit_message_caption(
                    caption=personal_center_text,
                    reply_markup=get_personal_center_keyboard()
                )
            else:
                # 发送本地图片消息，附带文字和按钮
                with open(PERSONAL_CENTER_IMAGE_PATH, 'rb') as photo:
                    context.bot.send_photo(
                        chat_id=query.message.chat_id,
                        photo=photo,
                        caption=personal_center_text,
                        reply_markup=get_personal_center_keyboard()
                    )
                # 删除原来的消息
                query.message.delete()
                
        except Exception as e:
            # 如果发送图片失败，发送错误信息
            logging.error(f"发送个人中心图片时出错: {e}")
            query.edit_message_text(
                text="发送个人中心图片时出错。\n\n" + personal_center_text,
                reply_markup=get_personal_center_keyboard()
            )
    
    elif query.data == "my_balance":
        # 获取用户昵称，如果没有昵称则使用用户名，如果都没有则使用"未知用户"
        user = query.from_user
        user_nickname = user.first_name or user.username or "未知用户"
        
        # 个人中心文字 - 使用指定的格式
        personal_center_text = f"""▫️用户编号：7775227112
▫️用户昵称：{user_nickname}
▫️用户余额： 0.01 元
▫️代理等级： 0 级
▫️代理积分： 0 分"""
        
        try:
            # 检查个人中心图片是否存在
            if not os.path.exists(PERSONAL_CENTER_IMAGE_PATH):
                # 如果图片不存在，只发送文字和按钮
                query.edit_message_caption(
                    caption=personal_center_text,
                    reply_markup=get_personal_center_keyboard()
                )
            else:
                # 发送本地图片消息，附带文字和按钮
                with open(PERSONAL_CENTER_IMAGE_PATH, 'rb') as photo:
                    context.bot.send_photo(
                        chat_id=query.message.chat_id,
                        photo=photo,
                        caption=personal_center_text,
                        reply_markup=get_personal_center_keyboard()
                    )
                # 删除原来的消息
                query.message.delete()
                
        except Exception as e:
            # 如果发送图片失败，发送错误信息
            logging.error(f"发送个人中心图片时出错: {e}")
            query.edit_message_text(
                text="发送个人中心图片时出错。\n\n" + personal_center_text,
                reply_markup=get_personal_center_keyboard()
            )
    
    elif query.data == "my_orders":
        # 获取用户昵称，如果没有昵称则使用用户名，如果都没有则使用"未知用户"
        user = query.from_user
        user_nickname = user.first_name or user.username or "未知用户"
        
        # 个人中心文字 - 使用指定的格式
        personal_center_text = f"""▫️用户编号：7775227112
▫️用户昵称：{user_nickname}
▫️用户余额： 0.01 元
▫️代理等级： 0 级
▫️代理积分： 0 分"""
        
        try:
            # 检查个人中心图片是否存在
            if not os.path.exists(PERSONAL_CENTER_IMAGE_PATH):
                # 如果图片不存在，只发送文字和按钮
                query.edit_message_caption(
                    caption=personal_center_text,
                    reply_markup=get_personal_center_keyboard()
                )
            else:
                # 发送本地图片消息，附带文字和按钮
                with open(PERSONAL_CENTER_IMAGE_PATH, 'rb') as photo:
                    context.bot.send_photo(
                        chat_id=query.message.chat_id,
                        photo=photo,
                        caption=personal_center_text,
                        reply_markup=get_personal_center_keyboard()
                    )
                # 删除原来的消息
                query.message.delete()
                
        except Exception as e:
            # 如果发送图片失败，发送错误信息
            logging.error(f"发送个人中心图片时出错: {e}")
            query.edit_message_text(
                text="发送个人中心图片时出错。\n\n" + personal_center_text,
                reply_markup=get_personal_center_keyboard()
            )
    
    elif query.data == "invite_records":
        # 获取用户昵称，如果没有昵称则使用用户名，如果都没有则使用"未知用户"
        user = query.from_user
        user_nickname = user.first_name or user.username or "未知用户"
        
        # 个人中心文字 - 使用指定的格式
        personal_center_text = f"""▫️用户编号：7775227112
▫️用户昵称：{user_nickname}
▫️用户余额： 0.01 元
▫️代理等级： 0 级
▫️代理积分： 0 分"""
        
        try:
            # 检查个人中心图片是否存在
            if not os.path.exists(PERSONAL_CENTER_IMAGE_PATH):
                # 如果图片不存在，只发送文字和按钮
                query.edit_message_caption(
                    caption=personal_center_text,
                    reply_markup=get_personal_center_keyboard()
                )
            else:
                # 发送本地图片消息，附带文字和按钮
                with open(PERSONAL_CENTER_IMAGE_PATH, 'rb') as photo:
                    context.bot.send_photo(
                        chat_id=query.message.chat_id,
                        photo=photo,
                        caption=personal_center_text,
                        reply_markup=get_personal_center_keyboard()
                    )
                # 删除原来的消息
                query.message.delete()
                
        except Exception as e:
            # 如果发送图片失败，发送错误信息
            logging.error(f"发送个人中心图片时出错: {e}")
            query.edit_message_text(
                text="发送个人中心图片时出错。\n\n" + personal_center_text,
                reply_markup=get_personal_center_keyboard()
            )
    
    elif query.data == "huobi_tutorial":
        huobi_text = "🏦 火币交易所教程\n\n步骤1：注册火币账户\n- 访问火币官网\n- 点击注册，填写基本信息\n- 完成身份验证\n\n步骤2：购买USDT\n- 登录账户，进入'买币'页面\n- 选择支付方式，输入购买金额\n- 确认交易，获取USDT\n\n步骤3：提现到项目\n- 进入'资产'页面\n- 选择USDT，点击提现\n- 输入项目提供的地址和金额"
        query.edit_message_caption(
            caption=huobi_text,
            reply_markup=get_tutorial_center_keyboard()
        )
    
    elif query.data == "wechat_tutorial":
        wechat_text = "💬 微信核销教程\n\n步骤1：获取卡密\n- 在项目中购买成功后\n- 在'我的订单'中查看卡密\n- 复制卡密信息\n\n步骤2：微信核销\n- 打开微信，扫描核销二维码\n- 粘贴卡密信息\n- 确认核销\n\n步骤3：等待打款\n- 核销成功后\n- 系统会自动处理打款\n- 通常在1-2小时内到账"
        query.edit_message_caption(
            caption=wechat_text,
            reply_markup=get_tutorial_center_keyboard()
        )
    
    elif query.data == "language_pack":
        language_text = "🌐 中文语言包使用教程\n\n1. 下载中文语言包\n   - 点击下方链接下载语言包文件\n   - 解压到指定目录\n\n2. 安装语言包\n   - 打开软件设置\n   - 选择语言选项\n   - 导入中文语言包\n\n3. 重启软件\n   - 关闭并重新打开软件\n   - 界面将显示为中文\n\n如有问题，请联系客服获取最新语言包下载链接。"
        query.edit_message_caption(
            caption=language_text,
            reply_markup=get_tutorial_center_keyboard()
        )
    
    elif query.data == "back_to_main":
        # 重新发送主菜单
        caption = """项目操作流程
- ①火币交易所注册
- ②火币交易所购买USDT
- ③余额充值
- ④购买卡密
- ⑤提取卡密
- ⑥微信核销卡密
- ⑦微信打款给您

担保交易公开
请点击"进入公群"进入公群

唯一客服：@JDEKa2288_vip谨防假冒

新用户请看下教程 | 中文语言包"""
        
        # 检查图片是否存在
        if os.path.exists(LOCAL_IMAGE_PATH):
            with open(LOCAL_IMAGE_PATH, 'rb') as photo:
                query.message.reply_photo(
                    photo=photo,
                    caption=caption,
                    reply_markup=get_main_menu_keyboard()
                )
                # 删除原来的消息
                query.message.delete()
        else:
            # 如果图片不存在，只发送文字
            query.edit_message_caption(
                caption=caption,
                reply_markup=get_main_menu_keyboard()
            )

# /chongzhi 命令处理函数
def chongzhi_command(update: Update, context: CallbackContext):
    # 余额充值说明文字
    recharge_text = """# 六部无值

- A 单笔充值如下金额赠送代理等级1  
  单笔充值 5000 元赠送代理等级1 级  
  单笔充值 10000 元赠送代理等级 2 级  
  单笔充值 20000 元赠送代理等级 3 级  
  单笔充值 30000 元赠送代理等级 4 级  
  单笔充值 50000 元赠送代理等级 5 级  

例：您当前代理等级是0级，充值5000元送1级，则您的代理等级为0+1=1级

请选择充值金额："""
    
    try:
        # 检查余额充值图片是否存在
        if not os.path.exists(RECHARGE_IMAGE_PATH):
            # 如果图片不存在，只发送文字和按钮
            update.message.reply_text(
                text=recharge_text,
                reply_markup=get_recharge_amount_keyboard()
            )
            # 同时发送提示信息
            update.message.reply_text("⚠️ 余额充值说明图片未找到，请确保recharge_guide.jpg文件存在于机器人目录中")
        else:
            # 发送本地图片消息，附带文字和按钮
            with open(RECHARGE_IMAGE_PATH, 'rb') as photo:
                context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=photo,
                    caption=recharge_text,
                    reply_markup=get_recharge_amount_keyboard()
                )
            
    except Exception as e:
        # 如果发送图片失败，发送错误信息
        logging.error(f"发送余额充值图片时出错: {e}")
        update.message.reply_text(
            text="发送余额充值说明图片时出错。\n\n" + recharge_text,
            reply_markup=get_recharge_amount_keyboard()
        )

# 其他命令
def help_command(update: Update, context: CallbackContext):
    update.message.reply_text('发送 /start 查看主菜单', reply_markup=get_reply_keyboard())

def custom_command(update: Update, context: CallbackContext):
    update.message.reply_text('这是一个自定义命令！', reply_markup=get_reply_keyboard())

# 处理普通文本消息
def handle_message(update: Update, context: CallbackContext):
    # 如果消息不是回复键盘按钮点击，则使用默认处理
    text = update.message.text
    if text not in ["余额充值", "购买卡密", "提取卡密", "教程中心", "联系客服", "个人中心", "返回主菜单"]:
        user = update.message.from_user
        logging.info(f"用户 {user.first_name} (ID: {user.id}) 发送了: {text}")
        response = f'你说了: "{text}"\n发送 /start 查看主菜单'
        update.message.reply_text(response, reply_markup=get_reply_keyboard())

# 错误处理
def error(update: Update, context: CallbackContext):
    logging.warning(f'更新 {update} 导致了错误: {context.error}')

# 主函数
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # 添加处理器
    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("custom", custom_command))
    dp.add_handler(CommandHandler("chongzhi", chongzhi_command))
    dp.add_handler(CallbackQueryHandler(button_callback))
    
    # 添加回复键盘按钮处理器
    dp.add_handler(MessageHandler(
        Filters.text & ~Filters.command, 
        handle_reply_buttons
    ))
    
    dp.add_error_handler(error)

    print("机器人正在启动...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
