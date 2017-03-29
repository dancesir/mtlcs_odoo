# -*- coding: utf-8 -*-
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.exceptions import Warning


class batch_statement_order(osv.osv_memory):
    _name = 'batch.statement.order'
    _columns = {
        'name': fields.char(u'Name', size=32),
        'month_id': fields.many2one('year.month', u'月份'),
        'start_time': fields.datetime(u'开始时间'),
        'end_time': fields.datetime(u'截止时间'),
    }

    def default_get(self, cr, uid, fields, context=None):
        res = {}
        month_obj = self.pool.get('year.month')
        next_month = month_obj.get_last_month(cr, uid,)[0]
        month = month_obj.browse(cr, uid, next_month)
        res = {
            'start_time' : month.start_time,
            'end_time': month.end_time,
        }
        return res

    def make_statement_order(self, cr, uid, ids, context=None):
        invoice_obj = self.pool.get('account.invoice')
        st_obj = self.pool.get('account.statement.order')

        wizard = self.browse(cr, uid, ids, context=context)
        partner_ids = context.get('active_ids')

        self.check_before_statement(cr, uid, wizard, partner_ids, context=context)

        domain = [('partner_id', 'in', partner_ids), ('state', '=', ['draft', 'confirmed']), ('statement_id', '=', None)]
        invoice_ids = invoice_obj.search(cr, uid, domain, context=context)

        dic = {}
        for invoice in invoice_obj.browse(cr, uid, invoice_ids, context=context):
            if invoice.partner_id.id not in dic:
                dic.update({invoice.partner_id.id:[]})
            dic[invoice.partner_id.id].append(invoice.id)
        st_ids = []
        for partner_id in dic:
            st_id = st_obj.create(cr, uid, {
                'partner_id': partner_id,
                'invoice_ids': [(6, 0, dic[partner_id])],
                'start_time':  wizard.start_time,
                'end_time': wizard.end_time,
            }, context=context)
            st_ids.append(st_id)

        return {
            'name': u'对账单',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.statement.order',
             #'target': 'new',
            'domain': [('id', 'in', st_ids)],
        }

    def check_before_statement(self, cr, uid, wizard, partner_ids, context=None):
        '''
        before create statement, make sure not have picking state is waiting make invoice
        '''
        pick_obj = self.pool.get('stock.picking')
        inspection_obj = self.pool.get('quality.inspection.order')

        pick_ids =  pick_obj.search(cr, uid, [('partner_id', 'in', partner_ids),
                                  ('state','=','done'),
                                  ('invoice_state','=','2binvoiced')])

        if pick_ids:
            raise Warning(u'供应商中，有采购未确认的出入库单据，请处理后再对账')

        inspection_ids = inspection_obj.search(cr, uid, [
            ('partner_id', 'in', partner_ids),
            ('state', '=', 'w_make_return')])

        if inspection_ids:
            raise Warning(u'供应商中，有待退货的质检单据，请处理后再对账')




















#################################################################################################################

