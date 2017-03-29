# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
##############################################################################

from openerp.osv import fields, osv
from openerp import tools, _
from openerp.exceptions import Warning

class pcb_remind(osv.osv):
    _name = 'pcb.remind'
    _columns = {
        'name': fields.char(u'提醒内容'),
        'state': fields.selection([('draft', u'草稿'),('confirmed',u'确认')],u'状态'),
        'partner_id': fields.many2one('res.partners', u'客户'),
        'info_id': fields.many2one('pcb.info', u'用户单'),
        'line_ids': fields.one2many('pcb.remind.line','remind_id', u'消息明细'),
    }

    def acton_confirm(self, cr, uid, ids, context=None):
        remind = self.browse(cr, uid, ids[0], context=context)
        self.write(cr, uid, remind.id, {'state': 'confirmed'}, context=context)
        #self.pool['pcb.remind.line'].write(cr, uid, [x.id for x in remind.line_ids], '')
        return True

class pcb_remind_line(osv.osv):
    _name = 'pcb.remind.line'
    _columns = {
        'name': fields.char(u'提醒内容'),
        'remind_id': fields.many2one('pcb.remind',  u'提醒'),
        'info_id': fields.many2one('pcb.info', u'用户单'),
        'processed': fields.boolean(u'已处理', help='设置无效后，次消息不再提醒'),
    }

    _defaults = {
        'processed': False,
    }

    def action_processed(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'active': False}, context=context)


##############################################################################