import nonebot
import asyncio
import random
import os

from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageSegment,MessageEvent,Bot
from nonebot.plugin import PluginMetadata
from BingImageCreator import ImageGen
from .config import Config, ConfigError
__zx_plugin_name__ = "bing ai绘图"
__plugin_usage__ = """
usage：
    画图：画图+问题
""".strip()
__plugin_des__ = "bing paint"
__plugin_cmd__ = ["画图"]
__plugin_type__ = ("一些工具",)
__plugin_version__ = 0.3
__plugin_author__ = "xuyufenfei"
__plugin_settings__ = {"level": 5, "admin_level": 2, "default_status": True, "limit_superuser": False, "cmd": __plugin_cmd__}
__plugin_cd_limit__ = {"cd": 10, "limit_type": "group", "rst": "请求过快！"}

plugin_config = Config.parse_obj(nonebot.get_driver().config.dict())
if not plugin_config.bing_cookies:
    raise ConfigError("请设置BingImageCreator的cookies!")
if plugin_config.bing_proxy:
    os.environ["http_proxy"] = plugin_config.bing_proxy
    os.environ["https_proxy"] = plugin_config.bing_proxy

paint = on_command("画图", block=False, priority=1)

__plugin_meta__ = PluginMetadata(
    name="DALL-E 3绘图",
    description="调用NewBing的DALL-E 3进行绘图",
    usage=
    '''
    直接发送: 画图 XXXXXX
    ''',
    config= Config,
    extra={},
    type="application",
    homepage="https://github.com/Alpaca4610/nonebot_plugin_BingImageCreator.git",
    supported_adapters={"~onebot.v11"}
)


@paint.handle()
async def _(bot: Bot,event: MessageEvent, msg: Message = CommandArg()):
    content = msg.extract_plain_text()
    random_cookies = random.choice(plugin_config.bing_cookies)
    image_ = ImageGen(random_cookies,None,None,None)
    await paint.send(str("DALL·E 3正在画图中....."))
    loop =  asyncio.get_event_loop()
    try:
        res = await loop.run_in_executor(None, image_.get_images, content)
    except Exception:
        await paint.finish(MessageSegment.text("画图错误"),at_sender = True)

    msgs = [
                    {
                        "type": "node",
                        "data": {
                            "name": "DALLE 3",
                            "uin": bot.self_id,
                            "content": MessageSegment.image(pic),
                        },
                    }
                    for pic in res               
                ]
    
    await bot.call_api("send_group_forward_msg",group_id=event.group_id,messages=msgs)
