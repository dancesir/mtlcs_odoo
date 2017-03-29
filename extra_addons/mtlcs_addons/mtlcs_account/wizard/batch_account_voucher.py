# -*- coding: utf-8 -*-
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.exceptions import Warning


class batch_account_voucher(osv.osv_memory):
    _name = 'batch.account.voucher'
    _columns = {
        'name': fields.char(u'Name', size=32),
        'month_id': fields.many2one('year.month', u'月份'),
        'start_date': fields.date(u'开始时间'),
        'end_date': fields.date(u'截止时间'),
    }

    def default_get(self, cr, uid, fields, context=None):
        res = {}
        month_obj = self.pool.get('year.month')
        next_month = month_obj.get_last_month(cr, uid,)[0]
        month = month_obj.browse(cr, uid, next_month)
        res = {
            'start_date' : month.start_time[:10],
            'end_date': month.end_time[:10],
        }
        return res

    def make_account_voucher(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids, context=context)
        partner_ids, extra_domain = self._partner_and_extra_domain(cr, uid, wizard, context=context)

        ctx = context.copy()
        ctx.update({'extra_domain': extra_domain, 'type': 'payment'})

        voucher_ids = self._create_vouchers(cr, uid, wizard, partner_ids,  context=ctx)
        if not voucher_ids:
            return True

        window = self.pool.get('ir.actions.act_window').for_xml_id(cr, uid, 'account_voucher', 'action_vendor_payment', context)
        window['domain'] = "[('id', 'in', [%s])])"  % ','.join([str(x) for x in voucher_ids])
        return window

    def _create_vouchers(self, cr, uid, wizard, partner_ids, context=None):
        voucher_obj = self.pool.get('account.voucher')

        #v = self._voucher_default(cr, uid, context=context)
        journal_id =  voucher_obj._get_journal(cr, uid, context=context)
        currency_id = voucher_obj._get_currency(cr, uid, context=context)
        ttype = voucher_obj._get_type(cr, uid, context=context)
        company_id = voucher_obj.pool.get('res.company')._company_default_get(cr, uid, 'account.voucher',context=context)
        date= fields.date.today()
        amount = 0.0

        voucher_ids = []
        for partner_id in partner_ids:

            #voucher_date
            voucher_data = {
                'partner_id': partner_id,
                'date': date,
                'type': ttype,
                'start_date': wizard.start_date,
                'end_date': wizard.end_date,
            }

            v = voucher_obj.onchange_partner_id(cr, uid, [], partner_id, journal_id, amount, currency_id, ttype, date, context=context)['value']

            #if not line_ids, next
            if not v['line_cr_ids'] and not v['line_dr_ids']:
                continue

            voucher_data.update(v)
            amount_dr = v['line_dr_ids'] and sum([x['amount_unreconciled'] for x in v['line_dr_ids']]) or 0.0
            amount_cr = v['line_cr_ids'] and sum([x['amount_unreconciled'] for x in v['line_cr_ids']]) or 0.0
            amount = amount_dr - amount_cr
            value = voucher_obj.onchange_amount(cr, uid, [], amount, v['payment_rate'], partner_id, journal_id, v['currency_id'],
                                                ttype, date, v['payment_rate_currency_id'], company_id,
                                                start_date=wizard.start_date, end_date=wizard.end_date, context=context)['value']

            voucher_data.update(value)
            voucher_data.update({
                'line_cr_ids': value['line_cr_ids'] and [(0, 0, x) for x in value['line_cr_ids']] or False,
                'line_dr_ids': value['line_dr_ids'] and [(0, 0, x) for x in value['line_dr_ids']] or False,
                'amount': amount,
            })
            voucher_id = voucher_obj.create(cr, uid, voucher_data, context=context)
            voucher_ids.append(voucher_id)

        return voucher_ids

    def _partner_and_extra_domain(self, cr, uid, wizard, context=None):
        invoice_obj = self.pool.get('account.invoice')
        from_mod = context.get('active_model')
        partner_ids = None
        extra_domain = None

        def check_invoices(invoices):
            for i in invoices:
                if i.state != 'open':
                    raise Warning(u'创建付款的电子凭证必须是 生效 状态')

        if from_mod == 'res.partner':
            partner_ids = context.get('active_ids')
            extra_domain = [('date_maturity','>=', wizard.start_date), ('date_maturity','<=', wizard.end_date)]

        elif from_mod == 'account.invoice':
            invoices = invoice_obj.browse(cr, uid, context.get('active_ids'), context=context)
            check_invoices(invoices)
            partner_ids = set([x.partner_id.id for x in invoices])
            extra_domain = [('invoice', 'in', [x.id for x in invoices]),
                            ('date_maturity','>=', wizard.start_date),
                            ('date_maturity','<=', wizard.end_date)]

        return (partner_ids, extra_domain)

#################################################################################################################

