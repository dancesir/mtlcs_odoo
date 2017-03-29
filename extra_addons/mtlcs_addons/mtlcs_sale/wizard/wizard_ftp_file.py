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



class wizard_ftp_file(osv.osv_memory):
    _name = 'wizard.ftp.file'
    _columns = {
        'so_id': fields.many2one('sale.order', u'报价合同', domain=[('state','=','draft')], ),
    }

    def apply(self, cr, uid, ids, context=None):
        price_ids = context.get('active_ids')
        price_obj = self.pool['pcb.price']

        return price_obj.make_sale_order(cr, uid, price_ids, context=context)











