# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
from openerp.exceptions import Warning
from openerp.osv import fields, osv
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from openerp import SUPERUSER_ID
from openerp.addons.base.res.res_request import referencable_models

#  ojb.fields  want to log
# Approve_Model_Info = {
#     'preparation.order': ['state'],
#     'price.adjust.order': ['state'],
#     'account.statement.order': ['state'],
#     'account.voucher': ['state'],
#     'quality.inspection.order': ['state'],
#     'stock.picking': ['mtl_state'],
#     'purchase.order': ['state'],
# }

class approve_log(osv.osv):
    _name = 'approve.log'
    _order = 'id desc'

    _columns = {
        'name':fields.char(string=u'名称', readonly=True, size=80 ),
        'model': fields.char(string=u'所在模块',  size=32, readonly=True),
        'res_id': fields.integer(u'资源ID',  readonly=True),
        'user_id': fields.many2one('res.users', u'审核人',  readonly=True),
        'state_from': fields.char(u'审核前状态', readonly=True),
        'state_to': fields.char(u'审核后状态', readonly=True),
        'from': fields.char(u'审核前状态', size=32, readonly=True),
        'to': fields.char(u'审核后状态', sieze=32, readonly=True),
        'time': fields.datetime(u'审核时间', readonly=True),
        'note': fields.char(u'备注'),
        'fd_name': fields.char(u'字段名'),
        'record_id': fields.reference(selection=referencable_models, string=u'单据',),
    }
    _sql_constraints = []
    _defaults = {
        # ==========1205
        # 'time': fields.datetime.now,
        'time': lambda *a: datetime.utcnow().strftime(DTF),
    }

    def create(self, cr, uid, values, context=None):

        model = values['model']
        df_name = values['fd_name']
        selection = dict(self.pool.get(model)._fields[df_name].selection)
        values.update({
            'to':  selection.get(values['state_to']),
            'record_id': '%s,%s' % (values['model'],  values['res_id']),
        })
        return super(approve_log, self).create(cr, uid, values, context=context)


class approve_log_thread(osv.AbstractModel):
    _name = 'approve.log.thread'

    def make_approve_log(self, cr, uid, event_ids, state_from=None, state_to=None, fd_name='state', note=None, context=None):

        log_obj = self.pool['approve.log']
        for event_id in event_ids:
            # ==========1121
            selection = dict(self.pool.get(self._name)._fields[fd_name].selection)
            data = {
                # 'name': '%s:%s:%s:%s' % (self._name, event_id, state_from, state_to ),
                # ==========1121
                'name': '%s:%s:%s:%s' % (self._name, event_id, state_from, selection.get(state_to)),
                'model': self._name,
                'res_id': event_id,
                'user_id': uid,
                'state_from': state_from,
                'state_to':state_to,
                'fd_name': fd_name,
            }

            log_obj.create(cr, SUPERUSER_ID, data, context=context)
        return True

    def get_logs(self, cr, uid, event_ids, context=None, arg=None):
        log_obj = self.pool['approve.log']
        arg = arg or  [('model','=',self._name),('res_id','in',event_ids)]
        return log_obj.search(cr, SUPERUSER_ID, arg)

    def show_approve_logs(self, cr, uid, event_ids, context=None, arg=None):
        ids = self.get_logs(cr, uid, event_ids, context=None, arg=arg) or []
        return {
            'name': (u'审批日志'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'approve.log',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', ids)],
            'target': 'new',
        }

    def write(self, cr, uid, event_ids, values, context=None,):

        # ==========1121
        # model= self._name
        # field_names = Approve_Model_Info.get(model)
        field_names = getattr(self, '_approve_log', None)

        todo_names = field_names and ( set(field_names) & set(values))

        if todo_names:
            fn = list(todo_names)[0]
            state_to = values[fn]
            self.make_approve_log(cr, uid, event_ids, state_from=None, state_to=state_to, fd_name=fn)

        return super(approve_log_thread, self).write(cr, uid, event_ids, values, context=context)
















