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


class parser_purchase_requisition(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(parser_purchase_requisition, self).__init__(cr, uid, name, context=context)

        # ==========1124
        # requisition_ids = context.get('active_ids')
        # requisition_obj = self.pool['purchase.requisition']
        #
        # for p in requisition_obj.browse(cr, uid, requisition_ids, context):
        #     if p.state != 'done':
        #         raise Warning(u'只能打印状态为【完成】的记录')


        self.localcontext.update({
            'make_pol_data': self.make_pol_data,
        })

    def make_pol_data(self, req):
        cr = self.cr
        uid =self.uid
        context={}
        pol_obj = self.pool.get('purchase.order.line')

        info = {}
        supplier_names = []
        pdt_ids = []

        for po in req.purchase_ids:
            partner = po.partner_id
            if partner.name not in supplier_names:
                supplier_names.append(partner.name)
            for line in po.order_line:
                pdt =  line.product_id
                if pdt.id not in pdt_ids:
                    pdt_ids.append(pdt.id)

                p_id = pdt.id
                p_name = '[%s]%s' % (pdt.default_code, pdt.name)
                k = '%s%s%s' % (pdt.default_code, line.product_uom.id, line.product_qty)
                tax = line.taxes_id and line.taxes_id[0].amount*100 or 0
                if k not in info:
                    info.update({k:[p_name, pdt.variants, line.product_qty, line.product_uom.name, {partner.name: [line.price_unit, tax] }, p_id]})
                else:
                    info[k][4].update({partner.name: [line.price_unit, tax]})

        # add the last price
        last_ids = pol_obj.get_last_ids(cr, uid, pdt_ids, context=context)
        last_pols = pol_obj.browse(cr, uid, last_ids, context=context)

        last_pol_dic = {}
        for pol in last_pols:
            last_tax = pol.taxes_id and pol.taxes_id[0].amount*100 or 0
            last_pol_dic[pol.product_id.id] = [pol.price_unit, last_tax]

        #fill three supplier_name
        new_supplier_names = [None] * 3
        for i in range(len(supplier_names)):
            new_supplier_names[i] = supplier_names[i]


        return [info, new_supplier_names, last_pol_dic]

class report_purchase_requisition(osv.AbstractModel):
    _name = 'report.mtlcs_purchase.report_purchase_requisition'
    _inherit = 'report.abstract_report'
    _template = 'mtlcs_purchase.report_purchase_requisition'
    _wrapped_report_class = parser_purchase_requisition




###############################################################################
