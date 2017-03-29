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
from openerp.osv import osv, fields
from openerp import models, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.addons.account_voucher.account_voucher import account_voucher as Voucher

# from openerp.addons.approve_log.approve_log import Approve_Model_Info

Voucher_State = Voucher._columns['state'].selection

add_state = [
    ('w_purchase_manager', u'待采购经理'),
    ('w_account', u'待财务审核'),
    ('w_account_manager', u'待财务经理'),
    ('w_account_chief_inspector', u'待财务总监'),
    ('w_general_manager', u'待总经理'),

    ('w_pay', u'待付款')
]

Voucher_State = Voucher_State[:1] + add_state + Voucher_State[1:]

Statement_Status = [
    ('draft', u'草稿'),
    ('w_purchase_manager', u'待采购经理'),
    ('w_quality_manager', u'待品质经理'),
    ('w_account_user', u'待财务会计'),
    ('w_account_manager', u'财务经理'),
    ('w_account_chief_inspector', u'财务总监'),
    ('w_fapiao_input', u'待收发票'),
    ('w_fapiao_approve', u'待审核发票'),
    ('done', u'完成'),
    ('cancel', u'取消'),
]

Sale_Statement_Status = [
    ('draft', u'草稿'),
    ('w_purchase_manager', u'待采购经理'),
    ('w_quality_manager', u'待品质经理'),
    ('w_account_user', u'待财务会计'),
    ('w_account_manager', u'财务经理'),
    ('w_account_chief_inspector', u'财务总监'),
    ('w_fapiao_input', u'待收发票'),
    ('w_fapiao_approve', u'待审核发票'),
    ('done', u'完成'),
    ('cancel', u'取消'),
]

Invoice_Stat = [
    ('draft', 'Draft'),
    ('proforma', 'Pro-forma'),
    ('proforma2', 'Pro-forma'),
    ('confirmed', u'待对账'),
    ('w_account', u'待财务'),
    ('open', u'生效'),
    ('paid', 'Paid'),
    ('cancel', 'Cancelled'),
]


class account_statement_order(osv.osv):

    _inherit = [ 'mail.thread', 'approve.log.thread']
    _name = 'account.statement.order'
    _approve_log = ['state']

    def _compute_amount(self, cr, uid, ids, fields_name, arg=None, context=None):
        res = {}
        for x in self.browse(cr, uid, ids, context=None):
            res[x.id] = sum(i.amount_total for i in x.invoice_ids) - sum(i.amount_total for i in x.invoice_cr_ids)
        return res
    def _compute_partner_id(self, cr, uid, ids, fields_name, arg=None, context=None):
        res = {}
        for x in self.browse(cr, uid, ids, context=None):
            res[x.id] = x.type=='purchase' and x.supplier_id.id or x.customer_id.id
        return res

    _columns = {
        'name': fields.char(u'对账单号', size=16, required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'create_uid': fields.many2one('res.users', u'创建人', readonly=True, ),
        'create_date': fields.datetime(u'创建日期', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'start_time': fields.datetime(u'开始时间', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'end_time': fields.datetime(u'截止时间', required=True, readonly=True, states={'draft': [('readonly', False)]}),

        'supplier_id': fields.many2one('res.partner', u'供应商', domain=[('supplier','=',True)], readonly=True,  states={'draft': [('readonly', False)]}),
        'customer_id': fields.many2one('res.partner', u'客户',  domain=[('customer','=',True)],readonly=True,  states={'draft': [('readonly', False)]}),

        'partner_id': fields.function(_compute_partner_id, type='many2one', relation='res.partner', string=u'合作伙伴',  readonly=True,),

        'state': fields.selection(Statement_Status, u'状态', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'state2': fields.selection(Sale_Statement_Status, u'状态', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'invoice_ids': fields.one2many('account.invoice', 'statement_id', 'Invoice', domain=[('type', 'in', ['in_invoice','out_invoice'])], readonly=True,
                                       states={'draft': [('readonly', False)]}),
        'line_ids': fields.one2many('account.invoice.line', 'statement_id', u'对账明细', domain=[('invoice_id.type', 'in', ['in_invoice','out_invoice'])]),
        'invoice_cr_ids': fields.one2many('account.invoice', 'statement_id', 'Invoice', domain=[('type', 'in', ['in_refund','out_refund'])], readonly=True,
                                          states={'draft': [('readonly', False)]}),
        'line_cr_ids': fields.one2many('account.invoice.line', 'statement_id', u'对账明细 红冲', domain=[('invoice_id.type', 'in', ['in_refund', 'out_refund'])]),
        'amount': fields.function(_compute_amount, type="float", string="对账金额", readonly=True, ),
        'voucher_id': fields.many2one('account.voucher', u'付款单', readonly=True),
        # ==========1201
        'type': fields.selection([('purchase',u'采购'),('sale',u'销售')],  u'类型', readonly=True, states={'draft': [('readonly', False)]}),

        # ==========multi company
        # 'company_id': fields.many2one('res.company', readonly=True, string=u'公司'),

    }

    def default_get(self, cr, uid, fields_name, context=None):
        res = {}
        month_obj = self.pool.get('year.month')
        next_month = month_obj.get_last_month(cr, uid,)[0]
        month = month_obj.browse(cr, uid, next_month)
        res = {
            'name': self.pool['ir.sequence'].get(cr, uid, 'account.statement.order'),
            'state': 'draft',
            'start_time': month.start_time,
            'end_time': month.end_time,
            'create_date': fields.datetime.now(),
            'type': context.get('default_type') or 'purchase',

            # ==========multi company
            # 'company_id': self.pool.get('res.users').browse(cr, uid, uid).company_id.id,
        }
        return res

    def unlink(self, cr, uid, ids, context=None):
        for data in self.read(cr, uid, ids, ['state']):
            if data['state'] not in ['draft', 'cancel']:
                raise osv.except_osv(_('Error'), _(u"非草稿、取消状态不可删除"))
        return super(account_statement_order, self).unlink(cr, uid, ids, context=context)

    def confirm(self, cr, uid, ids, context=None):
        s = self.browse(cr, uid, ids[0], context=context)

        if not s.invoice_ids and not s.line_cr_ids:
            raise Warning(u'没有任何对账内容')

        # ==========1117
        picking_obj = self.pool.get('stock.picking')
        domain = [('invoice_state', '=', '2binvoiced'),('partner_id', '=', s.supplier_id.id)]
        picking_ids = picking_obj.search(cr, uid, domain)
        if picking_ids:
            raise Warning(u'该供应商有还有未开票的入库单/退货单，请先开票')

        self.write(cr, uid, ids, {'state': 'w_purchase_manager'}, context=context)


    def purchase_manager_approve(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'w_quality_manager'}, context=context)

    def quality_manager_approve(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'w_account_user'}, context=context)

    def account_user_approve(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'w_account_manager'}, context=context)

    def account_manager_approve(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'w_account_chief_inspector'}, context=context)

    def account_chief_inspector_approve(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'w_fapiao_input'}, context=context)

    def fapiao_input(self, cr, uid, ids, context=None):
        fapiao_obj = self.pool['fa.piao']
        s = self.browse(cr, uid, ids[0], context=None)###
        checked = []
        for line in s.line_ids + s.line_cr_ids:
            p = line.fapiao_id
            if not p:
                raise Warning(u'对账明细没有关联发票')
            if p.id not in checked:
                if p.amount < p.amount_lines:
                    raise Warning(u'发票%s 金额%s 大于关联的对账金额%s' % (p.name, p.amount, p.amount_lines))
                if  p.amount == p.amount_lines:
                    fapiao_obj.action_done(cr, uid, [p.id], context=context)

                checked.append(line.fapiao_id.id)

        self.write(cr, uid, ids, {'state': 'w_fapiao_approve'}, context=context)

    def fapiao_approve(self, cr, uid, ids, context=None):
        self.action_done(cr, uid, ids, context=context)

    def action_done(self, cr, uid, ids, context=None):
        invoice_obj = self.pool.get('account.invoice')
        st = self.browse(cr, uid, ids[0], context=None)
        all_ids = [x.id for x in st.invoice_ids] + [x.id for x in st.invoice_cr_ids]
        invoice_obj.signal_workflow(cr, uid, all_ids, 'invoice_open')

        self.check_fapiao_done(cr, uid, ids, context=None)

        return self.write(cr, uid, ids, {'state': 'done'}, context=context)

    def reset_draft(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'draft'}, context=context)

    def check_fapiao_done(self, cr, uid, ids, context=None):
        fapiao_obj = self.pool.get('fa.piao')
        statements = self.browse(cr, uid, ids, context=context)
        fp_ids = []
        for s in statements:
            for line in s.line_ids + s.line_cr_ids:
                if line.fapiao_id.id not in fp_ids:
                    fp_ids.append(line.fapiao_id.id)
        fapiao_obj.check_to_done(cr, uid, fp_ids, context=context)
        return True

    def relation_lines(self, cr, uid, ids, context=None):
        statement = self.browse(cr, uid, ids[0], context=context)
        invoice_ojb = self.pool.get('account.invoice')
        ttype = statement.type

        domain = [('state', '=', 'draft'), ('partner_id', '=', statement.partner_id.id), ('statement_id', '=', None)]

        invoice_ids = invoice_ojb.search(cr, uid, domain)


        self.write(cr, uid, ids, {'invoice_ids': [(6, 0, invoice_ids)]}, context=context)
        return True

    def remove_lines(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'invoice_ids': [(5,)], 'invoice_cr_ids': [(5,)]  }, context=context)
        return True

    def input_fapiao(self, cr, uid, ids, context=None):
        s = self.browse(cr, uid, ids[0], context=context)
        ctx = context.copy()
        ctx.update({'default_partner_id': s.partner_id.id})
        return {
            'name': u'录入发票',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'batch.invoice.line',
            'target': 'new',
            # 'domain': [('partner_id','=',s.partner_id.id)],
            'context': ctx,
        }

    def make_account_voucher(self, cr, uid, ids, context=None):
        voucher_obj = self.pool['account.voucher']
        statement = self.browse(cr, uid, ids[0], context=None)
        data = self._prepare_voucher_value(cr, uid, statement, context=context)
        voucher_id = voucher_obj.create(cr, uid, data, context=context)
        self.write(cr, uid, statement.id, {'voucher_id': voucher_id}, context=context)
        return {
            # 'domain': [('id', '=', voucher_id)],
            'name': u'付款单',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.voucher',
            'res_id': voucher_id,
            'type': 'ir.actions.act_window',
            'view_id': self.pool['ir.model.data'].get_object_reference(cr, uid, 'account_voucher', 'view_vendor_payment_form')[1]
            # 'target': 'new'
        }

    def _prepare_voucher_value(self, cr, uid, statement, context=None):
        voucher_obj = self.pool['account.voucher']
        partner_id = statement.partner_id.id
        amount = statement.amount
        journal_id = 9
        journal = self.pool['account.journal'].browse(cr, uid, journal_id, context=context)
        currency_id = journal.company_id.currency_id.id
        ttype = 'payment'
        date = fields.date.today()
        invoice_ids = [x.id for x in statement.invoice_ids] + [x.id for x in statement.invoice_cr_ids]
        ##
        rest_domain = [('invoice', 'in', invoice_ids), ('state', '=', 'valid'), ('account_id.type', '=', 'payable'),
                       ('reconcile_id', '=', False), ('partner_id', '=', statement.partner_id.id)]
        ctx = context.copy()
        ctx.update({'rest_domain': rest_domain})

        value = voucher_obj.onchange_partner_id(cr, uid, [], partner_id, journal_id, amount, currency_id, ttype, date, context=ctx)['value']
        data = value.copy()
        data.update({
            'type': ttype,
            'partner_id': partner_id,
            'date': date,
            'amount': amount,
            'journal_id': journal_id,
            'line_dr_ids': value['line_dr_ids'] and [(0, 0, x) for x in value['line_dr_ids']] or None,
            'line_cr_ids': value['line_cr_ids'] and [(0, 0, x) for x in value['line_cr_ids']] or None,
        })
        return data


class account_invoice(osv.osv):
    # _inherit = 'account.invoice'
    _inherit = ['account.invoice', 'mail.thread', 'approve.log.thread']
    _name = 'account.invoice'

    _approve_log = ['state']

    _columns = {
        'statement_id': fields.many2one('account.statement.order', u'对账单'),
        'state': fields.selection(Invoice_Stat, u'状态'),
        #'fapiao_id': fields.many2one('fa.piao', u'发票号'),
    }

    _defaults = {
        'state': 'draft',
    }

    def confirm(self, cr, uid, ids, context=None):
        # self._check_confirm()
        self.write(cr, uid, ids, {'state': 'confirmed'})

    def account_approve(self, cr, uid, ids, context=None):
        self.signal_workflow(cr, uid, ids, 'invoice_open')

    def onchange_payment_term_date_invoice(self, cr, uid, ids, payment_term_id, date_invoice):
        res = super(account_invoice, self,).onchange_payment_term_date_invoice(cr, uid, ids, payment_term_id, date_invoice)
        return res


class account_invoice_line(osv.osv):
    _inherit = 'account.invoice.line'

    def _compute_statement_id(self, cr, uid, ids, fields_name, arg=None, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = line.invoice_id.statement_id.id
        return res

    def _get_line_from_invoice(self, cr, uid, invoice_ids, context=None):
        return self.pool.get('account.invoice.line').search(cr, uid, [('invoice_id', 'in', invoice_ids)], context=context)

    _columns = {
        #'fapiao_id': fields.many2one("fa.piao", u'发票号'),
        'supplier_invoice_number': fields.char(u'发票号', size=32,),
        'move_id': fields.many2one('stock.move', u'移库明细'),
        'statement_id': fields.function(_compute_statement_id,
                                        store={'account.invoice': (_get_line_from_invoice, ['statement_id'], 10), },
                                        type='many2one', relation='account.statement.order', string=u'对账单'),
        'po_id': fields.related('purchase_line_id', 'order_id', type='many2one', relation='purchase.order', readonly=True, string=u'采购单'),
        'date_due': fields.related('invoice_id', 'date_due', type='date', string=u'应付日期'),
        'picking_id': fields.related('move_id', 'picking_id', type='many2one', relation='stock.picking', string=u'出入库', readonly=True),
        'move_origin': fields.related('move_id', 'origin', type='char',  string=u'来源', readonly=True),
        'pick_date': fields.related('picking_id', 'date_done', type='datetime', string=u'出入库时间', readonly=True),
    }


class stock_picking(osv.osv):
    _inherit = 'stock.picking'

    def _get_invoice_vals(self, cr, uid, key, inv_type, journal_id, move, context=None):
        res = super(stock_picking, self)._get_invoice_vals(cr, uid, key, inv_type, journal_id, move, context=context)
        invoice_obj = self.pool['account.invoice']
        date_invoice = res.get('date_invoice') or fields.date.today()
        payment_term = res.get('payment_term')
        value = invoice_obj.onchange_payment_term_date_invoice(cr, uid, [], payment_term, date_invoice)
        res.update({'date_due': value['value'].get('date_due') })
        return res


class stock_move(osv.osv):
    _inherit = 'stock.move'

    def _get_invoice_line_vals(self, cr, uid, move, partner, inv_type, context=None):
        res = super(stock_move, self)._get_invoice_line_vals(cr, uid, move, partner, inv_type, context=context)
        res.update({'move_id': move.id})
        return res


class account_voucher(osv.osv):
    # _inherit = 'account.voucher'
    _inherit = ['account.voucher', 'mail.thread', 'approve.log.thread']
    _name = 'account.voucher'

    _approve_log = ['state']

    _columns = {
        'state': fields.selection(Voucher_State, 'state'),
        #'month_id': fields.many2one('year.month', u'月付款'),
        'start_date': fields.date(u'开始日期'),
        'end_date': fields.date(u'截止日期'),
        'payment_term': fields.related('partner_id', 'property_supplier_payment_term', type='many2one',
                                       relation='payment.term', string=u'付款条款')
    }
    _defaults = {
    }

    def copy(self, cr, uid, id, defaults, context=None):
        raise Warning(u'禁止复制')
        return False

    def confirm(self, cr, uid, ids, context=None):
        voucher = self.browse(cr, uid, ids[0], context=context)
        if (voucher.line_dr_ids or voucher.line_cr_ids) and voucher.writeoff_amount != 0:
            raise Warning('差异金额不为0，请核对付款总额，和明细总额之和')
        if voucher.date_due:
            for line in voucher.line_dr_ids:
                if line.date_due >= voucher.date_due:
                    raise Warning(u'%s到期日期大于最小到期日期' % line.move_line_id.ref)
        self.write(cr, uid, ids[0], {'state': 'w_purchase_manager'}, context=context)
        return True

    def purchase_manager_approve(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids[0], {'state': 'w_account'}, context=context)
        return True

    def account_approve(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids[0], {'state': 'w_account_manager'}, context=context)
        return True

    def account_manager_approve(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids[0], {'state': 'w_account_chief_inspector'}, context=context)
        return True

    def account_chief_inspector_approve(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids[0], {'state': 'w_general_manager'}, context=context)
        return True

    def general_manager_approve(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids[0], {'state': 'w_pay'}, context=context)
        return True

    def reconcile_all(self, cr, uid, ids, context=None):
        voucher = self.browse(cr, uid, ids, context=None)
        avl_obj = self.pool.get('account.voucher.line')
        for line in voucher.line_dr_ids:
            avl_obj.write(cr, uid, line.id, {'amount': line.amount_unreconciled, 'reconcile': True}, context=context)
        return True

    def undo_reconcile_all(self, cr, uid, ids, context=None):
        voucher = self.browse(cr, uid, ids, context=None)
        line_obj = self.pool.get('account.voucher.line')
        for line in voucher.line_dr_ids:
            line_obj.write(cr, uid, line.id, {'amount': 0, 'reconcile': False}, context=context)
        return True

    def onchange_amount(self, cr, uid, ids, amount, rate, partner_id, journal_id, currency_id,
                        ttype, date, payment_rate_currency_id, company_id, start_date=None, end_date=None, context=None):

        extra_domain = []
        if start_date:
            extra_domain.append( ('date_maturity','>=', start_date) )
        if end_date:
            extra_domain.append( ('date_maturity','<=', end_date) )
        ctx = context.copy()
        if extra_domain:
            ctx.update({'extra_domain': extra_domain})
        return super(account_voucher, self).onchange_amount(cr, uid, ids, amount, rate, partner_id, journal_id, currency_id, ttype, date, payment_rate_currency_id, company_id, context=ctx)

class account_payment_term(osv.osv):
    _inherit = 'account.payment.term'
    _columns = {
        'auto_voucher_monthly': fields.boolean(u'自动生成月付款计划'),
    }


##############################################################################

#TODO if want to show account.invoice at account.voucher.line
# add the invoice_id to function account.invoice. action_move_create
#

# class account_move(osv.osv):
#     _inherit = 'account.move'
#     _columns = {
#         'invoice_id': fields.many2one('account.invoice', readonly=True),
#     }
#
# class account_move_line(osv.osv):
#     _inherit = 'account.move.line'
#     _columns = {
#         'invoice_id': fields.related('move_id', 'invoice_id', type='many2one', relation='account.invoice', readonly=True),
#     }