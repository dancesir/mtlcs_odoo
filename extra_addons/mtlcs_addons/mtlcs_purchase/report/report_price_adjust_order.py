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
import time
from openerp.osv import osv
from openerp.report import report_sxw
from openerp.tools.translate import _
from openerp.exceptions import  Warning


class parser_price_adjust_order(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(parser_price_adjust_order, self).__init__(cr, uid, name, context=context)

        # ==========1124
        # adjustorder_ids = context.get('active_ids')
        # adjustorder_obj = self.pool['price.adjust.order']
        #
        # for p in adjustorder_obj.browse(cr, uid, adjustorder_ids, context):
        #     if p.state != 'done':
        #         raise Warning(u'只能打印状态为【完成】的记录')

        self.localcontext.update({
            'get_tax': self._get_tax,
        })


    def _get_tax(self, o):
        res = []
        i = 0
        for tax in o.line_ids:
            temp = ''
            for temp in tax.product_id.supplier_taxes_id:
                temp += temp.name
            res[i] = temp
            i += 1
        return res and res[0] or ''


class report_purchase_order(osv.AbstractModel):
    _name = 'report.mtlcs_purchase.report_price_adjust_order'
    _inherit = 'report.abstract_report'
    _template = 'mtlcs_purchase.report_price_adjust_order'
    _wrapped_report_class = parser_price_adjust_order




###############################################################################
