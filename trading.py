import asyncio
import math
from .lib import *
from PIL import Image, ImageFont, ImageDraw
from hoshino import util
from aiocqhttp.message import escape

db = RecordDAO(HADES_DB_PATH)
__BASE = os.path.split(os.path.realpath(__file__))
BUY_STATE = {}
BUY_DATA = {}
temp = {'seller': 114514, 'buyer': 114514, 'code': 6, 'from': 7, 'to': 10, 'from_num': 100, 'to_num': 20, "per": 10}
rate = {6: {4: 2.5, 5: 2}, 7: {4: 4, 5: 3, 6: 2}, 8: {4: 5, 5: 4, 6: 3, 7: 2}, 9: {4: 7, 5: 5, 6: 4, 7: 3, 8: 2},
        10: {6: 7, 7: 5, 8: 4, 9: 3}, 1010: {6: 8, 7: 6, 8: 5, 9: 4}}
color_list = {0: (52, 152, 216), 1: (241, 196, 15), 2: (31, 139, 76), 3: (231, 76, 60)}
code_list = (0, 0, 1), (0, 1, 0), (1, 0, 0), (1, 1, 0), (1, 0, 1), (0, 1, 1), (1, 1, 1)
status_code = {0: '待处理订单', 1: '接受的订单', 2: '完成的订单', 3: '取消的订单'}
n_name = ['紫', '蓝', '黄', '蓝+黄', '黄+紫', '紫+蓝', '黄+蓝+紫']
TIMEOUT_TIME = 120


def stop_buy(guid):
    try:
        del BUY_STATE[guid]
        del BUY_DATA[guid]
    except Exception:
        pass


def all_seller(lv):
    a = db.get_all_user()
    b = {}
    c = []
    for uid, data in a:
        data = json.loads(data)
        if f'R{lv}卖家' in data['perm']:
            b[uid] = data
            c.append(uid)
    return b, c


def for_order(data, i):
    color = color_list[data['status']]
    at_list = [data['buyer']]
    if not data['seller']:
        data['seller'] = f'@R{data["to"]}卖家'
    else:
        at_list.append(data['seller'])
    seller_data, buyer_data = db.read_user(data['seller']), db.read_user(data['buyer'])
    h = 900
    w = 1200
    im = Image.new('RGB', (w, h), 'white')
    draw = ImageDraw.Draw(im)
    draw.rectangle((10, 10, 20, h - 10), fill=color)
    font_path = os.path.join(__BASE[0], 'random.ttf')
    fnt = ImageFont.truetype(font_path, 100)
    h1_fnt = ImageFont.truetype(font_path, 70)
    text_fnt = ImageFont.truetype(font_path, 50)
    footer_fnt = ImageFont.truetype(font_path, 30)
    count = 10 - round(len(str(i)) / 2)
    placeholder = '_' * count
    draw.text((40, 10), f'{placeholder}#{i}{placeholder}', font=fnt, fill="black")
    time_to_str(data['order_time'])
    buyer_num = str(round(buyer_data["buy"], -len(str(buyer_data["buy"])) + 1)) + "+ 买入订单"
    try:
        seller_num = str(round(seller_data["sell"], -len(str(seller_data["sell"])) + 1)) + "+ 卖出订单"
        seller_str = db.get_name(data["seller"]) + f'({seller_num})'
    except:
        seller_str = data['seller']
    buyer_str = db.get_name(data["buyer"]) + f'({buyer_num})'
    msg_dict = {"买家:": buyer_str,
                '卖家:': seller_str,
                '报价:': f'{data["from_num"]}xR{data["from"]} : {data["to_num"]}xR{data["to"]}'}
    a = 110
    for header, text in msg_dict.items():
        draw.text((40, a + 10), header, font=h1_fnt, fill="black")
        draw.text((40, a + 80), text, font=text_fnt, fill="black")
        a += 140
    tet = Image.open(os.path.join(__BASE[0], f'arts/Tetrahedron_{data["to"]}.png')).resize((50, 50))
    orb = Image.open(os.path.join(__BASE[0], f'arts/Orb_{data["to"]}.png')).resize((50, 50))
    crystal = Image.open(os.path.join(__BASE[0], f'arts/Bluecrystal_{data["to"]}.png')).resize((50, 50))
    im.paste(tet, (40, a), tet)
    im.paste(orb, (190, a), orb)
    im.paste(crystal, (340, a), crystal)
    tem = code_list[data['code']]
    b = []  # 黄,蓝,紫
    for each in tem:
        b.append(each * data['per'])
    draw.text((90, a), f':{b[2]}', font=text_fnt, fill="black")
    draw.text((240, a), f':{b[0]}', font=text_fnt, fill="black")
    draw.text((390, a), f':{b[1]}', font=text_fnt, fill="black")
    a += 60
    draw.text((40, a + 10), '留言:', font=h1_fnt, fill="black")
    draw.text((40, a + 80), data['comment'], font=text_fnt, fill="black")
    status_str = status_code[data['status']]
    now = datetime.datetime.now()
    time_str = now.strftime('%y-%m-%d %I:%M:%S %p')
    draw.text((40, h - 40), f'{status_str} · {time_str}', font=footer_fnt, fill=(72, 72, 72))
    msg = str(MessageSegment.image(util.pic2b64(im))) + '\n'
    for each in at_list:
        msg += f'[CQ:at,qq={each}]'
    return msg


def time_to_str(time):
    now = datetime.datetime.timestamp(datetime.datetime.now())
    seconds = math.floor(now - time)
    if seconds >= 43200:
        seconds = 43200
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    time_str = ("%d小时%02d分%02d秒" % (h, m, s))
    return time_str


def list_to_forward(li):
    if isinstance(li, str):
        li = [li]
    a = []
    for each in li:
        data = {
            "type": "node",
            "data": {
                "name": '小冰',
                "uin": '2854196306',
                "content": each
            }
        }
        a.append(data)
    return a


def time_to_hour(time):
    now = datetime.datetime.timestamp(datetime.datetime.now())
    seconds = math.floor(now - time)
    if seconds >= 43200:
        seconds = 43200
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    time_str = ("%d小时" % h)
    return time_str


def order(data):
    base = 1
    rat = rate[data['to']][data['fr']]
    if 5 >= data['code'] >= 3:
        base = 2
    if data['code'] == 6:
        base = 3
    rat = rat * base
    if data['code'] == 6 and data['to'] == 10:
        rat = rate[data['to']][data['fr']] * 2 + rate[data['to'] + 1000][data['fr']]
    if data['code'] == 0 and data['to'] == 10:
        rat = rate[data['to'] + 1000][data['fr']]
    if (data['code'] == 4 or data['code'] == 5) and data['to'] == 10:
        rat = rate[data['to']][data['fr']] + rate[data['to'] + 1000][data['fr']]
    iteration = math.floor(data['num'] / rat)
    total = iteration * rat
    if data['to'] == 6 and data['fr'] == 4:
        rat = rate[data['to']][data['fr']] * 2
        iteration = math.floor(iteration / 2)
        total = iteration * rat
    return total, base * iteration, iteration


@reg_cmd(['o', 'order', '来份外卖', '发单'])
async def cmd_test(bot: HoshinoBot, ev: CQEvent, args):
    global BUY_STATE
    global BUY_DATA
    uid, gid = ev['user_id'], ev['group_id']
    if db.get_name(uid) == uid:
        await bot.send(ev, '你还未初始化，请使用!初始化 [游戏内名字]初始化')
        return
    a = await bot.get_group_member_list(group_id=ev['group_id'])
    b = {}
    for each in a:
        b[each['user_id']] = each['nickname']
    guid = (gid, uid)
    BUY_DATA[guid] = {}
    if len(args) >= 4:
        try:
            args = list(map(int, args[:4]))
        except Exception:
            await bot.send(ev, f'请输入数字')
            stop_buy(guid)
            return
        comment = args[4:]
        comment = ' '.join(comment)
        args = args[:4]
        if not 4 <= args[0] <= 9:
            await bot.send(ev, f'你有的神器支持范围为4到9')
            stop_buy(guid)
            return
        if not 6 <= args[1] <= 10:
            await bot.send(ev, f'你需要购买的神器等级支持范围为6到10')
            stop_buy(guid)
            return
        try:
            rate[args[1]][args[0]]
        except Exception:
            await bot.send(ev, f'不支持使用{args[0]}购买{args[1]}')
            stop_buy(guid)
            return
        if args[2] <= 0:
            await bot.send(ev, f'请输入实数正整数')
            stop_buy(guid)
            return
        if not 0 <= args[3] <= 6:
            await bot.send(ev, f'种类代码支持范围为0到6')
            stop_buy(guid)
            return
        stop_buy(guid)
        BUY_DATA = {guid: {"fr": args[0], "to": args[1], "num": args[2], "code": args[3], "comment": comment}}
        data = order(BUY_DATA[guid])
        data = {'seller': 0, 'buyer': uid, 'status': 0, 'code': BUY_DATA[guid]['code'],
                'order_time': datetime.datetime.timestamp(datetime.datetime.now()), 'accept_time': None,
                'complete_time': None, 'from': BUY_DATA[guid]['fr'], 'to': BUY_DATA[guid]['to'], 'from_num': data[0],
                'to_num': data[1], "per": data[2], 'comment': BUY_DATA[guid]['comment']}
        i = db.add_order(data)
        msg = for_order(data, i)
        await bot.send(ev, f'{msg}')
        msg2 = f'R{data["to"]}卖家:'
        user_dict, at_list = all_seller(data['to'])
        for each in at_list:
            msg2 += f'[CQ:at,qq={each}]'
        if not len(at_list):
            msg2 += '暂无'
        await bot.send(ev, msg2)
        ev['group_id'] = 853218742
        await bot.send(ev, msg)
        return
    BUY_STATE[guid] = 1
    await bot.send(ev, f'请在{TIMEOUT_TIME}s内完成，请输入你的神器等级[4-9]')
    await asyncio.sleep(TIMEOUT_TIME)
    try:
        if BUY_STATE[guid] == 5:
            stop_buy(guid)
            return
        stop_buy(guid)
        await bot.send(ev, f'超过了{TIMEOUT_TIME}s，指令超时请重新开始')
    except KeyError:
        return


@reg_cmd(['接单', '接收', 'a', 'accept'])
async def cmd_accept(bot: HoshinoBot, ev: CQEvent, args):
    uid, gid = ev['user_id'], ev['group_id']
    if db.get_name(uid) == uid:
        await bot.send(ev, '你还未初始化，请使用!初始化 [游戏内名字]初始化')
        return
    if not len(args) == 1:
        await bot.send(ev, '请输入一个订单ID')
        return
    data = db.read_order(args[0])
    data2 = db.read_user(uid)
    if f'R{data["to"]}卖家' not in data2['perm']:
        await bot.send(ev, '你目前没有这个权限，使用!申请卖家 [红星等级]获得权限')
        return
    if data['buyer'] == uid and uid != 1725036102:
        await bot.send(ev, '不能接收自己的订单')
        return
    if data['status'] != 0:
        await bot.send(ev, f'此订单状态为{data["status"]}，不是处于能够接受的状态')
        return
    # TODO:在这加卖家判定
    data['status'] = 1
    data['seller'] = uid
    data['accept_time'] = datetime.datetime.timestamp(datetime.datetime.now())
    msg = for_order(data, args[0])
    db.update_order(data, args[0])
    await bot.send(ev, msg)
    ev['group_id'] = 853218742
    await bot.send(ev, msg)


@reg_cmd(['完成', '结算', 'c', 'complete'])
async def cmd_complete(bot: HoshinoBot, ev: CQEvent, args):
    uid, gid = ev['user_id'], ev['group_id']
    if db.get_name(uid) == uid:
        await bot.send(ev, '你还未初始化，请使用!初始化 [游戏内名字]初始化')
        return
    if not len(args) == 1:
        await bot.send(ev, '请输入一个订单ID')
        return
    data = db.read_order(args[0])
    if data['buyer'] != uid and data['seller'] != uid:
        await bot.send(ev, '不是此订单的卖家或买家无法完成订单')
        return
    if data['status'] != 1:
        await bot.send(ev, f'此订单状态为{data["status"]}，不是处于能够完成的状态')
        return
    data['status'] = 2
    data['complete_time'] = datetime.datetime.timestamp(datetime.datetime.now())
    db.update_order(data, args[0])
    seller_data, buyer_data = db.read_user(data['seller']), db.read_user(data['buyer'])
    seller_data['sell'] += 1
    buyer_data['buy'] += 1
    db.update_user(seller_data, data['seller'])
    db.update_user(buyer_data, data['buyer'])
    msg = for_order(data, args[0])
    await bot.send(ev, msg)
    ev['group_id'] = 853218742
    await bot.send(ev, msg)


@reg_cmd(['取消', '收单', 'ca', 'cancel'])
async def cmd_cancel(bot: HoshinoBot, ev: CQEvent, args):
    uid, gid = ev['user_id'], ev['group_id']
    if db.get_name(uid) == uid:
        await bot.send(ev, '你还未初始化，请使用!初始化 [游戏内名字]初始化')
        return
    if not len(args) == 1:
        await bot.send(ev, '请输入一个订单ID')
        return
    data = db.read_order(args[0])
    if data['buyer'] != uid:
        if uid != 1725036102:
            await bot.send(ev, '不是此订单的买家无法取消订单')
            return
    if data['status'] != 1 and data['status'] != 0:
        await bot.send(ev, f'此订单状态为{data["status"]}，不是处于能够完成的状态')
        return
    data['status'] = 3
    data['complete_time'] = datetime.datetime.timestamp(datetime.datetime.now())
    msg = for_order(data, args[0])
    db.update_order(data, args[0])
    await bot.send(ev, msg)
    ev['group_id'] = 853218742
    await bot.send(ev, msg)


@reg_cmd(['拒绝', '拒绝订单', 'rej', 'reject'])
async def cmd_cancel(bot: HoshinoBot, ev: CQEvent, args):
    uid, gid = ev['user_id'], ev['group_id']
    if db.get_name(uid) == uid:
        await bot.send(ev, '你还未初始化，请使用!初始化 [游戏内名字]初始化')
        return
    if not len(args) == 1:
        await bot.send(ev, '请输入一个订单ID')
        return
    data = db.read_order(args[0])
    if data['seller'] != uid:
        await bot.send(ev, '不是此订单的卖无法取消订单')
        return
    if data['status'] != 1:
        await bot.send(ev, f'此订单状态为{data["status"]}，不是处于能够拒绝的状态')
        return
    data['status'] = 0
    data['seller'] = 0
    msg = for_order(data, args[0])
    db.update_order(data, args[0])
    msg2 = f'R{data["to"]}卖家:'
    user_dict, at_list = all_seller(data['to'])
    for each in at_list:
        msg2 += f'[CQ:at,qq={each}]'
    if not len(at_list):
        msg2 += '暂无'
    await bot.send(ev, msg2)
    await bot.send(ev, msg)
    ev['group_id'] = 853218742
    await bot.send(ev, msg)


@reg_cmd(['l', 'list', '列表'])
async def cmd_cancel(bot: HoshinoBot, ev: CQEvent, args):
    uid, gid = ev['user_id'], ev['group_id']
    all_order = db.get_all_order(args[0])
    status = 5
    if not args:
        await bot.send(ev, '请输入一个红星等级')
        return
    if len(args) == 1:
        status = 0
    if uid == 1725036102 and status:
        status = args[1]
    orders = {}
    for i, data in all_order:
        data = json.loads(data)
        if data['to'] == args[0] and data['status'] == status:
            orders[i] = data
    if not len(orders):
        await bot.send(ev, f'没有R{args[0]}待处理订单，' + str(MessageSegment.at(uid)) + '。')
        return
    msg = f'_____R{args[0]}待处理订单清单_____'
    msg += f'\n一共找到{len(orders)}个订单'
    for i, each in orders.items():
        msg += f'\n#{i}来自{db.get_name(each["buyer"])}({time_to_hour(each["order_time"])}之前)'
        msg += f'\n{each["from_num"]}xR{each["from"]} : {each["to_num"]}xR{each["to"]}({n_name[each["code"]]})'
    await bot.send(ev, str(msg))


@reg_cmd(['s', 'stat', '查看订单', '查看'])
async def cmd_cancel(bot: HoshinoBot, ev: CQEvent, args):
    uid, gid = ev['user_id'], ev['group_id']
    if db.get_name(uid) == uid:
        await bot.send(ev, '你还未初始化，请使用!初始化 [游戏内名字]初始化')
        return
    if len(args):
        o = db.read_order(args[0])
        await bot.send(ev, for_order(o, args[0]))
        return
    all_order = db.get_all_order(0)
    orders = {}
    for i, data in all_order:
        data = json.loads(data)
        if (data['buyer'] == uid or data['seller'] == uid) and data['status'] <= 1:
            orders[i] = data
    if not orders:
        await bot.send(ev, '你当前并没有相关订单。')
    a = []
    for i, data in orders.items():
        a.append(for_order(data, i))
    data = list_to_forward(a)
    await bot.send_group_forward_msg(group_id=gid, messages=data)


@reg_cmd(['汇率', '比率', 'r', 'rate'])
async def cmd_rate(bot: HoshinoBot, ev: CQEvent, args):
    im = Image.open(os.path.join(__BASE[0], f'rate.png'))
    await bot.send(ev, MessageSegment.image(util.pic2b64(im)))


@sv.on_message()
async def on_input_new(bot, ev: CQEvent):
    global BUY_STATE
    global BUY_DATA
    uid, gid = ev['user_id'], ev['group_id']
    guid = (gid, uid)
    arg = ev.message.extract_plain_text()
    try:
        if BUY_STATE[guid] != 5:
            try:
                arg = int(arg)
            except Exception:
                await bot.send(ev, f'请输入一个数字')
                return
        if BUY_STATE[guid] == 1:
            if not 4 <= arg <= 9:
                await bot.send(ev, f'你有的神器支持范围为4到9')
                stop_buy(guid)
                return
            BUY_STATE[guid] += 1
            BUY_DATA[guid]['fr'] = arg
            await bot.send(ev, f'输入你需要购买的神器等级[6-10]')
            return
        if BUY_STATE[guid] == 2:
            if not 6 <= arg <= 10:
                await bot.send(ev, f'你需要购买的神器等级支持范围为6到10')
                stop_buy(guid)
                return
            try:
                rate[arg][BUY_DATA[guid]['fr']]
            except Exception:
                await bot.send(ev, f'不支持使用{BUY_DATA[guid]["fr"]}购买{arg}')
                stop_buy(guid)
                return
            BUY_STATE[guid] += 1
            BUY_DATA[guid]['to'] = arg
            await bot.send(ev, f'输入你拥有的神器数量[>0]')
            return
        if BUY_STATE[guid] == 3:
            if arg <= 0:
                await bot.send(ev, f'请输入实数正整数')
                stop_buy(guid)
                return
            BUY_STATE[guid] += 1
            BUY_DATA[guid]['num'] = arg
            msg = ''
            for n in range(0, 7):
                BUY_DATA[guid]['code'] = n
                data = order(BUY_DATA[guid])
                msg += f'{n}:使用{data[0]}xR{BUY_DATA[guid]["fr"]}购买{data[1]}xR{BUY_DATA[guid]["to"]}({data[2]}个{n_name[n]})\n'
            await bot.send(ev, f'''输入种类代码[0-6]\n{str(msg)}''')
            return
        if BUY_STATE[guid] == 4:
            if not 0 <= arg <= 6:
                await bot.send(ev, f'种类代码支持范围为0到6')
                return
            BUY_DATA[guid]['code'] = arg
            BUY_STATE[guid] += 1
            await bot.send(ev, f'''输入额外需求/对于卖家的提示:''')
            return
        if BUY_STATE[guid] == 5:
            BUY_DATA[guid]['comment'] = escape(str(arg))
            data = order(BUY_DATA[guid])
            data = {'seller': 0, 'buyer': uid, 'status': 0, 'code': BUY_DATA[guid]['code'],
                    'order_time': datetime.datetime.timestamp(datetime.datetime.now()), 'accept_time': None,
                    'complete_time': None, 'from': BUY_DATA[guid]['fr'], 'to': BUY_DATA[guid]['to'],
                    'from_num': data[0],
                    'to_num': data[1], "per": data[2], 'comment': BUY_DATA[guid]['comment']}
            i = db.add_order(data)
            msg = for_order(data, i)
            await bot.send(ev, f'{msg}')
            msg2 = ''
            user_dict, at_list = all_seller(data['to'])
            for each in at_list:
                msg2 += f'[CQ:at,qq={each}]'
            if not len(at_list):
                msg2 += '暂无'
            await bot.send(ev, msg2)
            await bot.send(ev,
                           f'下次可以使用此指令一键发送相同订单\n !o {BUY_DATA[guid]["fr"]} {BUY_DATA[guid]["to"]} {BUY_DATA[guid]["num"]} {BUY_DATA[guid]["code"]}')
            ev['group_id'] = 853218742
            await bot.send(ev, msg)
            stop_buy(guid)
            return
    except Exception:
        pass


sv = Service('hades2_reminder', enable_on_default=False)


@sv.scheduled_job('cron', hour='*')
async def hour_reminder():
    now = datetime.datetime.timestamp(datetime.datetime.now())
    all_order = db.get_all_order(0)
    for i, data in all_order:
        data = json.loads(data)
        if data['seller'] and data['status'] == 1:
            seconds = math.floor(now - data['accept_time'])
            m, s = divmod(seconds, 60)
            h, m = divmod(m, 60)
            at_list = [data['buyer'], data['seller']]
            if h % 2 == 0 and h != 0:
                msg = f'此订单已经距离接单经过了{h}小时了，'
                for each in at_list:
                    msg += f'[CQ:at,qq={each}]'
                msg += '如果完成了订单请使用 !c 指令完成订单'
                await sv.broadcast(msg, 'hades2_reminder')
