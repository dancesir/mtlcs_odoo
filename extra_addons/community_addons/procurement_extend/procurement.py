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
from openerp.tools.translate import _
from openerp.osv import fields, osv
from openerp.exceptions import Warning

from openerp.addons.procurement.procurement import procurement_order as Procurement_Order

Procurement_Order_State = Procurement_Order._columns['state'].selection
Procurement_Order_State = [('draft', u'草稿')] + Procurement_Order_State
for FIELD in Procurement_Order._columns.values():
    field_states = getattr(FIELD, 'states')
    if field_states and 'confirmed' in field_states:
        field_states.update({'draft': [('readonly', False)]})


class procurement_order(osv.osv):
    _inherit = 'procurement.order'
    _columns = {
        'state': fields.selection(selection=Procurement_Order_State, string=u'状态'),
    }

    def run(self, cr, uid, ids, autocommit=False, context=None):
        for p in self.read(cr, uid, ids, ['state'], context=context):
            if p['state'] == 'draft':
                raise Warning(u'不能运行草稿状态的需求单')
        return super(procurement_order, self).run( cr, uid, ids, autocommit=autocommit, context=context)

    def action_confirm(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'confirmed'}, context=context)
        return True

    def reset_to_draft(self, cr, uid, ids, context=None):
        for proc in self.browse(cr, uid, ids, context=context):
            if proc.state != 'cancel':
                raise Warning('非取消状态，不可重置草稿')
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)
        return True

