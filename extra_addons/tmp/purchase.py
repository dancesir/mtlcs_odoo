# #     def open_lowest_price(self, cr, uid, ids, context=None):
# #         pol_obj = self.pool.get('purchase.order.line')
# #         req = self.browse(cr, uid, ids[0], context=context)
# #         pdt_ids =[x.product_id.id for x in req.line_ids]
# #
# #         #TODO  sql limit create time min_data
# #         sql = """
# # select id
# # from (
# #     select id, product_id, price_unit, row_number() over(partition by product_id order by price_unit) as row_n
# #     from purchase_order_line where product_id = ANY (%s) and state in ('done', 'confirmed')
# # ) pol
# # where row_n = 1;
# #
# #         """
# #         cr.execute(sql,  (pdt_ids,))
# #         pol_ids = [x[0] for x in cr.fetchall()]
# #         return {
# #             'domain': [('id', 'in', pol_ids)],
# #             'name': _(u'�鿴��ͼ۸�'),
# #             'view_type': 'form',
# #             'view_mode': 'tree,form',
# #             'res_model': 'purchase.order.line',
# #             'type': 'ir.actions.act_window',
# #             'target': 'new',
# #         }
#
#     def unlink_no_supplierinfo_pol____(self, cr, uid, ids, context=None):
#         '''
#         del the pol that the product not have supplierinfo related to PO.supplier
#         '''
#         pol_pbj = self.pool.get('purchase.order.line')
#         pr = self.browse(cr, uid, ids[0], context=context)
#         for po in pr.purchase_ids:
#             partner_id = po.partner_id.id
#             if po.state in ['draft', 'sent']:
#                 for pol in po.order_line:
#                     if partner_id not in [info.name.id for info in pol.product_id.seller_ids]:
#                         pol_pbj.unlink(cr, uid, [pol.id], context=context)
#         return  True
#
#
#
#     # def _prepare_order_line_move(self, cr, uid, order, order_line, picking_id, group_id, context=None):
#     #     '''
#     #     create invoice by picking_type  input->stock, not purchase->input.
#     #     '''
#     #     res =  super(purchase_order, self)._prepare_order_line_move(cr, uid, order, order_line, picking_id, group_id, context=context)
#     #     if order.picking_type_id.ref == 'supplier2input':
#     #         for line in res:
#     #             line['invoice_state'] = 'none'
#     #     return res
#
#
#
# # ###picking.return
# #         ctx = context.copy()
# #         ctx.update({
# #             'active_model':'stock.picking',
# #             'active_id': inspection.res_id.id,
# #             'active_ids': [inspection.res_id.id,],
# #             'inspection_id': inspection.id,
# #             'default_invoice_state': '2binvoiced',
# #         })
# #         product_return_moves = []
# #         for l in inspection.line_ids:
# #             if l.qty_ng > 0:
# #                 product_return_moves.append({'product_id':l.product_id.id, 'quantity':l.qty_return, 'move_id': l.move_id.id })
# #
# #         if not product_return_moves:
# #             raise Warning('û�в��ϸ�����������Ҫ�˻�')
# #         ctx.update({'replace_product_return_moves': product_return_moves })
# #         return_obj.create(cr, uid, {}, context=ctx)
# #         return {
# #             'name': u'�����˻�',
# #             'view_type': 'form',
# #             'view_mode': 'form',
# #             'res_model': 'stock.return.picking',
# #             'type': 'ir.actions.act_window',
# #             'target': 'new',
# #             'context':ctx,
# #         }