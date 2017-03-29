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

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.exceptions import except_orm, Warning

class stock_invoice_onshipping(osv.osv_memory):
    _inherit = "stock.invoice.onshipping"
    _columns = {

    }

    def view_init(self, cr, uid, fields_list, context=None):
        '''
        add rule, the picking.account_touched must be True
        '''
        if context is None:
            context = {}
        res = super(stock_invoice_onshipping, self).view_init(cr, uid, fields_list, context=context)

        pick_obj = self.pool.get('stock.picking')
        active_ids = context.get('active_ids',[])

        for pick in pick_obj.read(cr, uid, active_ids, ['account_touched'], context=context, load="_classic_write"):
            if not pick['account_touched']:
                raise Warning(u'根据入库单开票，先请财务签收')
        return res