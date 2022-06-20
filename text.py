overall_help = '''买家指令:
!o - 创建订单
!ca - 取消订单
!c - 完成订单
卖家指令
!a - 接受订单
!rej - 取消接受订单
!c - 完成订单
综合指令
!r - 显示汇率
!l - 显示目前待处理的订单
!s - 显示你目前的订单
如果要得到更多资讯请打 !help_ [指令]
(参数)代表参数为可选，而[参数]代表必要参数'''

help_o = '''用法: !o (<你有的等级> <你需要的等级> <你拥有的数量> <需要的种类代码>)
栗子: !o 7 9 60 6 就代表要混合的9，你有60个7 或 !o 开始引导发单模式
用户: 任何非封禁用户

种类代码:
0 紫
1 黄
2 蓝
3 黄蓝
4 蓝紫
5 紫黄
6 蓝紫黄
给R10订单的提醒
一些红星等级的紫是比蓝黄贵，这是因为用户需求和供应的偏差'''

help_ca = '''用法: !ca [订单ID]
栗子: !ca 123
用户: [订单ID]的卖家和买家

买方可以由于不可预见的情况或进行修改取消订单[订单ID]。'''

help_c = '''用法：!c [订单ID]
栗子: !c 123
用户: [订单ID]的卖家和买家

买方或卖方标记的订单[订单ID]已成功完成。'''

help_a = '''用法: !a [订单ID]
栗子: !a 123
用户：具有卖方资格的用户

卖方接受订单[订单ID]，并被分配为买方完成订单。'''

help_rej = '''用法: !rej [订单ID]
栗子: !rej 123
用户：[订单ID]的卖方

卖方拒绝订单<订单ID>，并将其恢复为待处理状态，以便其他卖方可以接手。'''

help_s = '''用法:!s (订单ID)
用户:任何用户

查看所有和自己相关的订单，或特定订单#(订单ID)的情况。'''

help_l = '''用法:!l [神器等级]
用户:任何用户

查询目前所有[神器等级]的待处理订单，以便卖家评估。'''

help_r = '''用法:!r
用户:任何用户

查询目前的最新汇率（机器人将会发送图片，请耐心等待）'''