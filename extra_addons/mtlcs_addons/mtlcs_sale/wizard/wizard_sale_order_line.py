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
import base64
from openerp.osv import fields, osv
from openerp.exceptions import Warning


class wizard_sale_order_line(osv.osv_memory):
    _name = 'wizard.sale.order.line'
    _inherit = 'sale.order.line.batch'

    _columns = {
        'wizard_id': fields.many2one('wizard.sale.order', u'Wizard'),
    }


class wizard_sale_order(osv.osv_memory):
    _name = 'wizard.sale.order'

    _columns = {
        'qty': fields.float(u'数量'),
        'line_ids': fields.one2many('wizard.sale.order.line', 'wizard_id', u'Lines'),
    }

    def apply(self, cr, uid, ids, context=None):
        sol_obj = self.pool.get('sale.order.line')
        wizard = self.browse(cr, uid, ids[0], context=context)

        sol_id = context.get('active_id')
        sol_obj.write(cr, uid, sol_id, {'batch_ids': [(0, 0, {
            'qty': wizard.qty,

        })]})
