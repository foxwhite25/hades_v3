from .lib import *
from aiocqhttp.message import escape

db = RecordDAO(HADES_DB_PATH)
__BASE = os.path.split(os.path.realpath(__file__))


@reg_cmd(['初始化', 'new', 'n'])
async def cmd_new_user(bot: HoshinoBot, ev: CQEvent, args):
    if len(args) < 1:
        await bot.send(ev, '正确指令格式为!初始化 [角色名称]')
    name = ' '.join(args)
    if name.endswith(']') or name.endswith('初始化') or name.startswith('['):
        await bot.send(ev,'''你输个jb[]\n[]只是告诉你这一部分要修改为你的账号''')
        return
    uid, gid = ev['user_id'], ev['group_id']
    data = {'corp': ' ', 'name': ' '.join(args), 'buy': 0, 'sell': 0, 'perm': []}
    db.new_user(uid, data)
    await bot.send(ev, escape(f'成功初始化，{db.get_name(uid)}，如有固定集团，建议使用!修改集团 [集团名称] 来修改你的集团。\n请阅读群文件的卖家/买家指南，以及普遍的交易规则。'))


@reg_cmd(['修改集团'])
async def cmd_edit_corp(bot: HoshinoBot, ev: CQEvent, args):
    if len(args) < 1:
        await bot.send(ev, '正确指令格式为!修改集团 [集团名称]')
        return
    uid, gid = ev['user_id'], ev['group_id']
    if db.get_name(uid) == uid:
        await bot.send(ev, '你还未初始化，请使用!初始化 [游戏内名字] 初始化')
        return
    data = db.read_user(uid)
    data['corp'] = ' '.join(args)
    db.update_user(data, uid)
    await bot.send(ev, escape(f'成功修改集团{db.get_name(uid)}'))


@reg_cmd(['修改名字'])
async def cmd_edit_name(bot: HoshinoBot, ev: CQEvent, args):
    if len(args) < 1:
        await bot.send(ev, '正确指令格式为!修改名字 [玩家名称]')
        return
    uid, gid = ev['user_id'], ev['group_id']
    if db.get_name(uid) == uid:
        await bot.send(ev, '你还未初始化，请使用!初始化 [游戏内名字] 初始化')
        return
    data = db.read_user(uid)
    data['name'] = ' '.join(args)
    db.update_user(data, uid)
    await bot.send(ev, escape(f'成功修改集团{db.get_name(uid)}'))


@reg_cmd(['申请卖家'])
async def cmd_apply_seller(bot: HoshinoBot, ev: CQEvent, args):
    if len(args) < 1:
        await bot.send(ev, '正确指令格式为!申请卖家 [红星等级]')
        return
    if 10 < args[0] < 6:
        await bot.send(ev, '神器等级支持范围为6到10')
        return
    uid, gid = ev['user_id'], ev['group_id']
    if db.get_name(uid) == uid:
        await bot.send(ev, '你还未初始化，请使用!初始化 [游戏内名字] 初始化')
        return
    data = db.read_user(uid)
    if f'R{args[0]}卖家' in data['perm']:
        await bot.send(ev, '你已经拥有这个权限了')
        return
    data['perm'].append(f'R{args[0]}卖家')
    db.update_user(data, uid)
    await bot.send(ev, escape(f'你将会收到未来R{args[0]}的订单通知，可以使用!取消卖家 [红星等级] 来取消通知'))


@reg_cmd(['取消卖家'])
async def cmd_cancel_seller(bot: HoshinoBot, ev: CQEvent, args):
    if len(args) < 1:
        await bot.send(ev, '正确指令格式为!取消卖家 [红星等级]')
        return
    if 10 < args[0] < 6:
        await bot.send(ev, '神器等级支持范围为6到10')
        return
    uid, gid = ev['user_id'], ev['group_id']
    if db.get_name(uid) == uid:
        await bot.send(ev, '你还未初始化，请使用!初始化 [游戏内名字] 初始化')
        return
    data = db.read_user(uid)
    if f'R{args[0]}卖家' not in data['perm']:
        await bot.send(ev, '你目前没有这个权限')
        return
    data['perm'].remove(f'R{args[0]}卖家')
    db.update_user(data, uid)
    await bot.send(ev, escape(f'你将不会收到未来R{args[0]}的订单通知'))
