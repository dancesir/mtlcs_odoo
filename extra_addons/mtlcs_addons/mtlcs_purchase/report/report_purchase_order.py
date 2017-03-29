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


class parser_purchase_order(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(parser_purchase_order, self).__init__(cr, uid, name, context=context)

        # ==========1124
        # purchase_ids = context.get('active_ids')
        # purchase_obj = self.pool['purchase.order']
        #
        # for p in purchase_obj.browse(cr, uid, purchase_ids, context):
        #     if p.state != 'done':
        #         raise Warning(u'只能打印状态为【完成】的记录')

        self.localcontext.update({
            'get_tax': self._get_tax,
            'po_origin':self.get_origin
        })


    def _get_tax(self, order_line):
        res = ''
        for tax in order_line.taxes_id:
            res += tax.name

        return res

    def get_origin(self, o):

        if o.requisition_id.id:
            pr_id = self.pool.get('purchase.requisition').browse(self.cr, self.uid, o.requisition_id.id)[0]
            po_id = self.pool.get('procurement.order').search(self.cr, self.uid, [('requisition_id', '=', pr_id.id)])
            po_obj =  self.pool.get('procurement.order').browse(self.cr, self.uid, po_id[0])[0]

            return po_obj.preparation_id.name

class report_purchase_order(osv.AbstractModel):
    _name = 'report.mtlcs_purchase.report_purchase_order'
    _inherit = 'report.abstract_report'
    _template = 'mtlcs_purchase.report_purchase_order'
    _wrapped_report_class = parser_purchase_order




###############################################################################
