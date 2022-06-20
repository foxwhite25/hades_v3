from .lib import *

helps = {('o', 'order'): help_o, ('a', 'accept'): help_a,
         ('c', 'complete'): help_c, ( 'ca', 'cancel'): help_ca,
         ('rej', 'reject'): help_rej, ('l', 'list'): help_l,
         ('s', 'stat'): help_s, ('r', 'rate'): help_r}
helps2 = {}
ally = {}
for tu, text in helps.items():
    for each in tu:
        helps2[each] = text
        ally[each] = tu


@reg_cmd(['help', '帮助'])
async def cmd_complete(bot: HoshinoBot, ev: CQEvent, args):
    if not args:
        await bot.send(ev, overall_help)
        return
    if args[0] in helps2:
        msg = '指令别称:' + ','.join(ally[args[0]]) + '\n' + helps2[args[0]]
        await bot.send(ev, msg)
        return
    else:
        await bot.send(ev, '未知指令')
        return
