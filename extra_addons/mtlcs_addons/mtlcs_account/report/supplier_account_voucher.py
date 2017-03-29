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
from openerp.exceptions import Warning
from openerp.addons.mtlcs_base.tools.tool import number2china, cncurrency


class parser_supplier_account_voucher(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(parser_supplier_account_voucher, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_info': self._get_info,
            'get_order': self._get_order,
            'get_voucher_ids': self._get_voucher_ids,

        })

    def _get_info(self, o):
        partner = o.partner_id
        bank = partner.bank_ids and partner[0] or None
        if partner.bank_ids:
            bank = partner.bank_ids[0]
            bank_name = bank.bank_name
            acc_number = bank.acc_number

        date = u'%s年%s月%s日' % (o.date[0:4], o.date[5:7], o.date[8:10])
        # cn_number = u'%s佰%s拾%s万%s仟%s佰%s拾%s元%s角%s分' %  number2china(o.amount)
        cn_number = cncurrency(o.amount)
        return {
            'bank_name': bank and bank.bank_name or '',
            'acc_number': bank and acc_number,
            'date': date,
            'cn_number': cn_number,
        }

    def _get_order(self, o):
        cr = self.cr
        uid = self.uid

        aso_obj = self.pool.get('account.statement.order')
        aso_id = aso_obj.search(cr, uid, [('voucher_id', '=', o.id), ])
        order = aso_obj.browse(cr, uid, aso_id)

        return {
            'order': order,
        }

    def _get_voucher_ids(self, o):
        voucher_obj = self.pool.get('account.voucher')
        cr = self.cr
        uid = self.uid

        args = [('state', 'in', ('posted',)), ('id', '!=', o.id), ('partner_id', '=', o.partner_id.id)]
        order = 'create_date desc'
        voucher_ids = voucher_obj.search(cr, uid, args, limit=6, order=order)
        voucher = voucher_obj.browse(cr, uid, voucher_ids)

        return {
            'voucher': voucher,
        }


class report_supplier_account_voucher(osv.AbstractModel):
    _name = 'report.mtlcs_account.report_supplier_account_voucher'
    _inherit = 'report.abstract_report'
    _template = 'mtlcs_account.report_supplier_account_voucher'
    _wrapped_report_class = parser_supplier_account_voucher

###############################################################################
