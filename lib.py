import datetime
from typing import List, Callable, Dict
import os
import sqlite3
import os
import ujson as json
from hoshino.typing import *
from hoshino import Service
from .text import *

cmds: Dict[str, Callable] = {}
HADES_DB_PATH = os.path.expanduser("~/.hoshino/had.db")
sv = Service('hades2', bundle='pcr娱乐')


@sv.on_prefix(['!', '！'])  # 指令执行
async def exec_cmd(bot: HoshinoBot, ev: CQEvent):
    # if ev['message_type'] != 'group':
    #     await bot.send(ev, '请在QQ群中使用本插件')
    #     return
    plain_cmd = ev.message.extract_plain_text()
    cmd, *args = plain_cmd.split(' ')  # 分割指令与参数
    if cmd in cmds:
        func = cmds[cmd]
        for each in args:
            if each.isnumeric():
                args[args.index(each)] = int(each)
        await func(bot, ev, args)
    elif cmd != '':
        sv.logger.info('指令列表' + str(cmds))
        await bot.send(ev, '未知指令\n输入!help查看说明')


def reg_cmd(names) -> Callable:
    if type(names) == str:
        names = [names, ]
    elif not type(names) == list:
        err_str = '指令名必须是字符串(str)或列表(list), 但却是' + str(type(names))
        raise ValueError(err_str)

    def reg(func) -> Callable:
        for name in names:
            if name in cmds:
                sv.logger.warning('命名冲突')
            else:
                cmds[name] = func
                sv.logger.info(f'[Hades神器交易]指令{name}已注册')
        return func

    return reg


class RecordDAO:
    def __init__(self, db_path):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._create_table()

    def connect(self):
        return sqlite3.connect(self.db_path)

    def _create_table(self):
        with self.connect() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS trade"
                "(id INT NOT NULL ,data json NOT NULL , PRIMARY KEY (id))"
            )
            conn.execute(
                "CREATE TABLE IF NOT EXISTS user"
                "(uid INT NOT NULL ,data json NOT NULL , PRIMARY KEY (uid))"
            )
            conn.execute(
                'INSERT OR REPLACE INTO trade (id,data) VALUES (?,?)', (0, '''{
    "seller": 0,
    "buyer": 1725036102,
    "status": 3,
    "code": 6,
    "order_time": 1616307547.545731,
    "accept_time": null,
    "complete_time": null,
    "from": 7,
    "to": 10,
    "from_num": 112,
    "to_num": 21,
    "per": 7,
    "comment": ""
}''')
            )

    def add_order(self, di):
        js = json.dumps(di, indent=4)
        with self.connect() as conn:
            i = conn.execute(
                'SELECT MAX(id) FROM trade',
            ).fetchone()[0] + 1
            conn.execute(
                'INSERT OR REPLACE INTO trade (id,data) VALUES (?,?)', (i, js)
            )
        return i

    def read_order(self, i):
        with self.connect() as conn:
            i = conn.execute(
                'SELECT data FROM trade WHERE id=?', (i,)
            ).fetchone()[0]
        return json.loads(i)

    def update_order(self, data, i):
        data = json.dumps(data)
        with self.connect() as conn:
            i = conn.execute(
                'UPDATE trade SET data=? WHERE id=?', (data, i,)
            )

    def get_all_order(self, fr):
        with self.connect() as conn:
            i = conn.execute(
                'select * from trade',
            ).fetchall()
        return i

    def new_user(self, uid, data):
        js = json.dumps(data, indent=4)
        with self.connect() as conn:
            conn.execute(
                'INSERT OR REPLACE INTO user (uid,data) VALUES (?,?)', (uid, js)
            )

    def read_user(self, uid):
        try:
            with self.connect() as conn:
                i = conn.execute(
                    'SELECT data FROM user WHERE uid=?', (uid,)
                ).fetchone()[0]
            return json.loads(i)
        except:
            return None

    def update_user(self, data, uid):
        data = json.dumps(data)
        with self.connect() as conn:
            i = conn.execute(
                'UPDATE user SET data=? WHERE uid=?', (data, uid,)
            )

    def get_name(self, uid):
        data = self.read_user(uid)
        try:
            return f'[{data["corp"]}] {data["name"]}'
        except:
            return uid

    def get_all_user(self):
        with self.connect() as conn:
            i = conn.execute(
                'SELECT * FROM user',
            ).fetchall()
        return i
