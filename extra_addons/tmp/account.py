#
#     def make_account_voucher(self, cr, uid, ids, context=None):
#         voucher_obj = self.pool['account.voucher']
#         statement = self.browse(cr, uid, ids[0], context=None)
#         data = self._prepare_voucher_value(cr, uid, statement, context=context)
#         voucher_id =voucher_obj.create(cr, uid, data, context=context )
#         return {
#             #'domain': [('id', '=', voucher_id)],
#             'name': u'���',
#             'view_type': 'form',
#             'view_mode': 'tree,form',
#             'res_model': 'account.voucher',
#             'res_id': voucher_id,
#             'type': 'ir.actions.act_window',
#             'target': 'new',
#         }
#
#     def _prepare_voucher_value(self, cr, uid, statement, context=None):
#         voucher_obj = self.pool['account.voucher']
#         partner_id = statement.partner_id.id
#         amount = statement.amount
#         journal_id = 9
#         journal = self.pool['account.journal'].browse(cr, uid, journal_id, context=context)
#         currency_id = journal.company_id.currency_id.id
#
#         ttype = 'payment'
#         date = fields.date.today()
#         invoice_ids = [x.id for x in statement.invoice_ids]
#         rest_domain =[('invoice' ,'in', invoice_ids),('state','=','valid'), ('account_id.type', '=', 'payable'),
#                       ('reconcile_id', '=', False), ('partner_id', '=', statement.partner_id.id)]
#         value = voucher_obj.onchange_partner_id(cr, uid, [], partner_id, journal_id, amount, currency_id, ttype, date, context=context)['value']
#
#         data = value.copy()
#
#         data.update( {
#             'type' : ttype,
#             'partner_id': partner_id,
#             'date': date,
#             'amount':  amount,
#             'journal_id': journal_id,
#             'line_dr_ids': value['line_dr_ids'] and [(0, 0, x) for x in value['line_dr_ids']] or None,
#             'line_cr_ids':  value['line_cr_ids'] and [(0, 0, x) for x in value['line_cr_ids']] or None,
#         })
#
#         return date
#
#
# class account_invoice(osv.osv):
#     _inherit = 'account.invoice'
#     statement_id = FD.Many2one('account.statement.order', u'���˵�'),
#     # colums
#     state = FD.Selection([
#         ('draft', 'Draft'),
#         ('proforma', 'Pro-forma'),
#         ('proforma2', 'Pro-forma'),
#         ('confirmed', u'������'),
#         ('w_account', u'������'),
#         ('open', u'��Ч'),
#         ('paid', 'Paid'),
#         ('cancel', 'Cancelled'),
#     ], string='Status', index=True, readonly=True, default='draft',
#         track_visibility='onchange', copy=False,
#         help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Invoice.\n"
#              " * The 'Pro-forma' when invoice is in Pro-forma status,invoice does not have an invoice number.\n"
#              " * The 'Open' status is used when user create invoice,a invoice number is generated.Its in open status till user does not pay invoice.\n"
#              " * The 'Paid' status is set automatically when the invoice is paid. Its related journal entries may or may not be reconciled.\n"
#              " * The 'Cancelled' status is used when user cancel invoice.")
#     # colums
#
#     @api.multi
#     def _check_confirm(self):
#         for invoice in self:
#             for line in invoice.invoice_line:
#                 if not line.supplier_invoice_number:
#                     raise Warning(_(u'�����빩Ӧ�̷�Ʊ��'))
#                 po = line.po_id
#                 if (po and po.payment_by_shipped) and not po.shipped:
#                     if po.state != 'except_picking':
#                         raise Warning(u'�ɹ���δȫ���ջ�����������ˡ������Ҫ�����ȶԸòɹ������� �ջ��쳣�᰸')
#
#     @api.multi
#     def confirm(self):
#         self._check_confirm()
#         self.write({'state': 'confirmed'})
#
#     @api.multi
#     def account_approve(self):
#         self.signal_workflow('invoice_open')
#
#     @api.cr_uid_ids_context
#     def write_supplier_invoice_number2lines(self, cr, uid, ids, context=None):
#         return {
#             'name': _(u'������ϸʹ��ͬһ����Ʊ����'),
#             'type': 'ir.actions.act_window',
#             'view_type': 'form',
#             'view_mode': 'form',
#             'res_model': 'batch.invoice.line',
#             'target': 'new',
#             'context': context,
#         }