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

# class sale_order(osv.osv):
#     _inherit = 'sale.order'
#
#     def action_ship_create(self, cr, uid, ids, context=None):
#         if context is None:
#             context = {}
#         ctx = context.copy()
#         ctx.update({'procurement_run_now':True})
#         return super(sale_order, self).action_ship_create(cr, uid, ids, context=ctx)
#
# class stock_move(osv.osv):
#     _inherit = 'stock.move'
#
#     def _create_procurements(self, cr, uid, moves, context=None):
#         procurement_ids = super(stock_move,self)._create_procurements(cr, uid, moves, context=None)
#         if context.get('procurement_run_now',True):
#             self.pool['procurement.order'].run(cr, uid, procurement_ids, context=context)
#         return procurement_ids


####################################################################################