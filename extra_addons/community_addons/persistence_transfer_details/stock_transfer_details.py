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
from openerp.osv import osv, fields
from openerp.exceptions import Warning

Max_Hours = 24 * 5

class stock_transfer_details_items(osv.osv_memory):
    _inherit = 'stock.transfer_details_items'
    _transient_max_hours = Max_Hours

class stock_transfer_details(osv.osv_memory):
    _inherit = 'stock.transfer_details'
    _transient_max_hours = Max_Hours
    _columns= {
    }

    def action_save(self, cr, uid, ids, context=True):
        return {}

    def do_check(self, cr, uid, wizard, context=None):
        for item in wizard.item_ids:
            if item.quantity <= 0.0:
                raise Warning(u'转移数量不能小于等于0')

    def do_detailed_transfer(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids[0], context=context)
        self.do_check(cr, uid, wizard, context=context)
        return super(stock_transfer_details, self).do_detailed_transfer(cr, uid, ids, context=context)


#####################################################
