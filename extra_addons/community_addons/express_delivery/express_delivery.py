# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 - 2013 Daniel Reis
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import time
from openerp.osv import osv, fields

Express_State = [
    ('0', u'未定义'),
    ('1', u'快件揽收'),
    ('2', u'揽件扫描'),
    ('3', u'快件分拨'),
    ('4', u'装车扫描'),
    ('5', u'快件扫描'),
    ('6', u'快件分拨'),
    ('7', u'安排投递'),
    ('8', u'正在投递'),
    ('9', u'快件签收'),
    ('10', u'异常'),
]

Express_State_Help = u'''
1.快件揽收。指发货人通过电话/传真/邮件等形式，通知快件公司上门取件。
2.揽件扫描。指快递人员将快件送达快递公司的分拨中心，相关人员对快件信息进行录入和检查。
3.快件分拨。指快递公司按照快件的地址信息或者其他要求进行分拣。
4.装车扫描。指快递已完成分拣，并开始发往目的地，此环节会包含在途运输的时间。
5.快件扫描。指快件已到达目的地所在城市的分拨中心。
6.快件分拨。指快件按照区域所在地进行分拣。
7.安排投递。指分拨中心已将快件分拣完毕，等待投递员进行投递。
8.正在投递。指快递人员已经开始根据快件上的信息进行快件的寄送。
9.快件签收。指收货人确认收到快递，并签收
'''


class express_delivery(osv.osv):
    _name = 'express.delivery'
    _columns = {
        'name': fields.char(u'快递单号', size=36),
        'carrier_id': fields.many2one('delivery.carrier', u'承运方'),
        'state': fields.selection(Express_State, u'状态', help=Express_State_Help),
        'create_uid': fields.many2one('res.users', 'Create User', readonly=True),
        'create_date': fields.datetime('Create Date', readonly=True),
        'fee': fields.float(u'费用'),
    }

    _defaults = {
        'state': '1',
    }


#####################################