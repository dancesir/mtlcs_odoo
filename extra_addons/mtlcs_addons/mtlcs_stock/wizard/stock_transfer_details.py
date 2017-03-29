# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP S.A. <http://www.odoo.com>
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
import openerp.addons.decimal_precision as dp
from datetime import datetime

#####################################################

class stock_transfer_details(osv.osv_memory):
    _inherit = 'stock.transfer_details'

    def action_save(self, cr, uid, ids, context=True):
        res = super(stock_transfer_details, self).action_save(cr, uid, ids, context=context)
        pick_obj = self.pool['stock.picking']
        pick_id = context.get('active_id')
        pick = pick_obj.browse(cr, uid, ids, context=context)
        mtl_state = context.get('to_mtl_state')
        if mtl_state:
            pick_obj.write(cr, uid, pick_id, {'mtl_state':mtl_state}, context=context)
        return res

    def default_get(self, cr, uid, fields, context=None):
        res = super(stock_transfer_details, self).default_get(cr, uid, fields, context=context)
        if context.get('default_zero_qty'):
            for item in res['item_ids']:
                item['quantity'] = 0
        return res
