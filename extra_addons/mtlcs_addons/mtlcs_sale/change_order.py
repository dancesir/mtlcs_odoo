# -*- encoding: utf-8 -*-
##############################################################################
#
#    Daniel Campos (danielcampos@avanzosc.es) Date: 08/09/2014
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################
import time
from openerp.osv import osv, fields
from datetime import datetime as DT
from receive_order import Receive_Type

Change_Order_State = [
    ('draft', u'草稿'),
    ('w_eng', u'待工程'),
    ('w_dpt', u'待部门'),
    ('w_gm', u'待总经办'),
    ('w_oc', u'待确认结果'),
    ('w_send', u'待发通知'),
    ('done', u'完成',),
    ('cancel', u'取消',),
]


class change_order(osv.osv):
    _name = 'change.order'
    _inherits = {'receive.order': 'receive_id'}

    _State_Transfer = {
        'draft': 'w_eng',
        'w_eng': 'w_dpt',
        'w_dpt': 'w_gm',
        'w_gm': 'w_oc',
        'w_oc': 'w_send',
        'w_send': 'done',
    }

    _columns = {
        'name': fields.char(u'更改单', size=32),
        'state': fields.selection(Change_Order_State, u'状态'),
        'receive_id': fields.many2one('receive.order', u'接单', required=True, ondelete="restrict"),
        'production_ids': fields.many2many('mrp.production', 'change_order_production_ref', 'order_id', 'production_id', u'生产批次'),
        'finish_qty': fields.float(u'成品库存数'),
        'sol_id': fields.many2one('sale.order.line', u'合同明细'),
        'so_id': fields.related('sol_id', 'order_id', type='many2one', relation='sale.order', string=u'合同', readonly=True),

        'prescription': fields.selection([(1, u'永久'), (2, u'临时')], u'时效'),
        'description': fields.text(u'更改内容'),
        'company_id': fields.many2one('res.company', u'公司'),

        'change_so': fields.boolean(u'需要修改合同'),
        'change_info': fields.boolean(u'需要修改用户单'),
        ###
        'comment_lines': fields.one2many('dpt.comment.line', 'change_id', u'部门评审'),
        'gm_comment': fields.text(u'总经办评审'),
        'gm_ok': fields.boolean(u'同意'),
        'order_center_ok': fields.boolean(u'同意'),
        'loss_total': fields.float('损失金额计总'),
        'customer_accept_amount': fields.float('客户接受金额'),
        # 'change_notice_id':
    }

    _sql_constraints = [
        ('name_uniq', 'unique(name)', u'非常规单号不允许重复'),
    ]

    def default_get(self, cr, uid, fields, context=None):
        return {
            'name': time.strftime('%Y%m%d%H%M%S'),
            'state': 'draft',
            'prescription': 1,
        }

    def action_next(self, cr, uid, ids, context=None):
        me = self.browse(cr, uid, ids[0], context=context)
        now_state = me.state
        to_state = self._State_Transfer.get(now_state)
        if to_state == 'w_eng':
            self.pool['pcb.info'].write(cr, uid, me.info_id.id, {'state': 'w_change'})

        self.write(cr, uid, me.id, {'state': to_state}, context=context)
        return True

    def send_change_notice(self, cr, uid, ids, context=None):
        return True

    def action_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'cancel'}, context=context)

    def rest_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)

    def reset_pcb_info_done(self, cr, uid, ids, context=None):
        co = self.browse(cr, uid, ids[0], context=context)
        self.pool.get('pcb.info').write(cr, uid, co.info_id.id, {'state': 'done'}, context=context)
        return True

class dpt_comment_line(osv.osv):
    _name = 'dpt.comment.line'
    _columns = {
        'change_id': fields.many2one('change.order', u'更改单',  ),
        'detection_id': fields.many2one('tech.standard.detection', u'非常规'),

        'department_id': fields.many2one('hr.department', u'部门' , required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'ok': fields.boolean(u'评审通过', readonly=True, states={'draft': [('readonly', False)]}),
        'name': fields.text(u'评审内容', readonly=True, states={'draft': [('readonly', False)]}),
        'loss_amount': fields.float('损失金额', readonly=True, states={'draft': [('readonly', False)]}),
        'user_id': fields.many2one('res.users', u'评审人', readonly=True, states={'draft': [('readonly', False)]}),
        'state': fields.selection([('draft',u'草稿'),('done',u'完成')], u'状态', readonly=True,),

        'done_time': fields.datetime(u'完成时间'),
    }

    _defaults = {
        'state': 'draft',
    }

    def action_done(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'user_id': uid,  'state': 'done', 'done_time': DT.utcnow()})
        return True

    def action_draft(self, cr, uid, ids, ):
        self.write(cr, uid, ids, {'user_id': uid,  'state': 'draft'})
        return True

    #################
