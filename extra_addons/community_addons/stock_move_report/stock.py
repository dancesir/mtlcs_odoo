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
from openerp.osv import osv, fields

class sotck_move(osv.osv):
    _inherit = 'stock.move'

    def _compute_amount(self, cr, uid, ids, field_name, arg=None, context=None):
        res = {}
        for move in self.read(cr, uid, ids, ['product_uom_qty', 'price_unit'], load='_classic_write'):
            res[move['id']] = move['product_uom_qty'] * move['price_unit']
        return res

    _columns = {
        'amount': fields.function(_compute_amount, type='float', string=u"金额"),
    }
