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


class stock_picking(osv.osv):
    _inherit = 'stock.picking'

    def do_enter_transfer_all_once(self, cr, uid, ids, context=None):
        ctx = context.copy()
        ctx.update({'all_once':True})
        return self.do_enter_transfer_details(cr, uid, ids, context=ctx)

    def _create_backorder(self, cr, uid, picking, backorder_moves=[], context=None):
        backorder_id = super(stock_picking, self)._create_backorder(cr, uid, picking, backorder_moves=backorder_moves, context=context)
        if backorder_id and context.get('all_once'):
            raise Warning(u'此调拨需一次性完成所有，不允许拆分，请核对转移数量')
        return backorder_id
