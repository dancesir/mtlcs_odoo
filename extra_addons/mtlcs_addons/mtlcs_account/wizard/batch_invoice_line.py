# -*- coding: utf-8 -*-
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.exceptions import Warning


class batch_invoice_line(osv.osv_memory):
    _name = 'batch.invoice.line'
    _columns = {
        'name': fields.char(u'Name', size=32),
        'fapiao_id': fields.many2one('fa.piao', u'发票',),
        'partner_id': fields.many2one('res.partner', u'合作伙伴'),
    }

    def apply(self, cr, uid, ids, context=None):
        src_mode = context.get('active_model')
        src_ids = context.get('active_ids')
        wizard = self.browse(cr, uid, ids[0], context=context)
        if src_mode == 'account.invoice.line':
            self.write_by_invoice_line(cr, uid, wizard, context=context)
        elif src_mode == 'account.invoice':
            self.write_by_invoice(cr, uid, wizard, context=context)
        elif src_mode == 'account.statement.order':
            self.write_by_statement(cr, uid, wizard, context=context)
        return {'type': 'ir.actions.act_window_close'}

    def write_by_invoice(self, cr, uid, wizard, context=None):
        invoice_obj = self.pool.get('account.invoice')
        line_obj = self.pool.get('account.invoice.line')
        invoice_id = context.get('active_id')
        invoice = invoice_obj.browse(cr, uid, invoice_id, context=context)
        if invoice.state != 'draft':
            raise Warning(u'不能录入非草稿状态的发票')

        invoice_obj.write(cr, uid, invoice_id, {'supplier_invoice_number': wizard.supplier_number}, context=context)
        line_obj.write(cr, uid, [x.id for x in invoice.invoice_line], {'fapiao_id': wizard.fapiao_id.id})

    def write_by_invoice_line(self, cr, uid, wizard, context=None):
        line_obj = self.pool.get('account.invoice.line')
        line_ids = context.get('active_ids')
        info = line_obj.read(cr, uid, line_ids, ['partner_id', 'invoice_state'], context=context, load='_classic_write')
        partner_id = None
        for d in info:
            if not partner_id:
                partner_id = d['partner_id']
            if partner_id != d['partner_id']:
                raise Warning(u'不能选择不同供应商的发票明细')
            if d['invoice_state'] != 'draft':
                raise Warning(u'不能录入非草稿状态的发票')
        line_obj.write(cr, uid, line_ids, {'fapiao_id': wizard.fapiao_id.id},  context=context)

    def write_by_statement(self, cr, uid, wizard, context=None):
        line_obj = self.pool.get('account.invoice.line')
        statement_obj = self.pool.get('account.statement.order')
        statement_id = context.get('active_id')
        statement = statement_obj.browse(cr, uid, statement_id, context=None)
        line_ids = [x.id for x in statement.line_ids] + [x.id for x in statement.line_cr_ids]
        line_obj.write(cr, uid, line_ids, {'fapiao_id': wizard.fapiao_id.id}, context=context )
        return True


#################################################################################################################

