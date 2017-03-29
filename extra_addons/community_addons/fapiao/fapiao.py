# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 - 2013 Daniel Reis
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

class fa_piao(osv.osv):
    _name="fa.piao"
    _order = "id desc"

    def _compute_lines_amount(self, cr, uid, ids, field_name, arg=None, context=None):
        res = {}
        for p in self.browse(cr, uid, ids, context=context):
            res[p.id] = sum([x.price_subtotal_gross for x in p.line_dr_ids]) - sum([x.price_subtotal_gross for x in p.line_cr_ids])
        return res

    _columns = {
        'name': fields.char(u'发票号', size=32, required=True, readonly=True, states={'draft': [('readonly', False), ]},),
        'amount': fields.float(u'金额', required=True,  readonly=True, states={'draft': [('readonly', False), ]}),
        'partner_id': fields.many2one('res.partner', u'合作伙伴', required=True, readonly=True, states={'draft': [('readonly', False), ]}),
        'create_date': fields.datetime(u'创建日期', readonly=True,),
        'date': fields.date(u'发票日期'),
        'create_uid': fields.many2one('res.users', u'创建人', readonly=True),
        'state': fields.selection([('draft',u'草稿'),('confirmed',u'确认'),('done', u'完成')], u'状态'),
        'type': fields.selection([('in', u'应付'), ('out', u'应收')], u'类型', readonly=True,required=True, states={'draft': [('readonly', False), ]}),
        'note':fields.text(u'备注'),
        'line_dr_ids': fields.one2many('account.invoice.line', 'fapiao_id', string=u'对账明细',
                                       domain=[('invoice_id.type', '=', 'in_invoice')], readonly=True),
        'line_cr_ids': fields.one2many('account.invoice.line', 'fapiao_id', string=u'对账明细 红',
                                       domain=[('invoice_id.type', '=', 'in_refund')], readonly=True),
        'amount_lines': fields.function(_compute_lines_amount, type='float', string=u'关联对账明细金额'),

        # ==========multi company
        # 'company_id': fields.many2one('res.company', readonly=True, string=u'公司'),

    }

    _defaults = {
        'state': 'draft',
        # 'company_id': lambda self, cr, uid, ctx: self.pool.get('res.users').browse(cr, uid, uid).company_id.id,
    }

    _sql_constraints = {
        ('name_uniq', 'unique(name, company_id)',(u"同一公司发票号不能重复")),
    }

    def unlink(self, cr, uid, ids, context=None):
        for i in self.browse(cr, uid, ids, context=context):
            if i.state != 'draft':
                Warning(u'不能删除非草稿状态fap')
        return super(fa_piao, self).unlink(cr, uid, ids, context=context)

    def action_confirm(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'confirmed'}, context=context)

    def action_done(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'done'}, context=context)

    def check_to_done(self, cr, uid, ids, context=None):
        to_done_ids = []
        for p in self.browse(cr, uid, ids, context=context):
            if (p.amount == p.amount_lines
                and all([l.invoice_id.state == 'open' for l in p.line_dr_ids])
                and all([l.invoice_id.state == 'open' for l in p.line_cr_ids])
                ):
                to_done_ids.append(p.id)

        if to_done_ids:
            self.action_done(cr, uid, to_done_ids, context=context)
        return True


class account_invoice_line(osv.osv):
    _inherit = 'account.invoice.line'
    _columns = {
        'fapiao_id': fields.many2one("fa.piao", u'发票号'),
    }

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    _columns = {
        'fapiao_id': fields.many2one('fa.piao', u'发票号'),
    }


#######################################################################################