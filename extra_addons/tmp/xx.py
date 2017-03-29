#     def get_lowest_price_ids(self, cr, uid, pdt_ids=None, context=None, limit=80):
#         if not pdt_ids:
#             return False
#         context = context and context or {}
#
#         sql = """
#             select id
#             from (
#                 select id, product_id, price_unit, row_number() over(partition by product_id order by price_unit) as row_n
#                 from purchase_order_line where product_id = ANY (%s) and state in ('confirmed', 'done')
#             ) pol
#             where row_n = 1;
#
#         """
#         cr.execute(sql,  (pdt_ids,))
#         return [x[0] for x in cr.fetchall()]
#
#     def get_last_ids(self, cr, uid, pdt_ids=None, context=None, limit=80):
#         if not pdt_ids:
#             return False
#         context = context and context or {}
#
#         sql = """
# select id
# from (
#     select id, product_id, create_date, row_number() over(partition by product_id order by create_date desc) as row_n
#     from purchase_order_line where product_id = ANY (%s) and state in ('confirmed', 'done')
# ) pol
# where row_n = 1;
#
#         """
#         cr.execute(sql,  (pdt_ids,))
#         return [x[0] for x in cr.fetchall()]
#
#     def open_lowest_price(self, cr, uid, ids, context=None):
#         pol_obj = self.pool.get('purchase.order.line')
#         po = self.browse(cr, uid, ids[0], context=context)
#         pdt_ids =[x.product_id.id for x in po.order_line]
#         pol_ids = pol_obj.get_lowest_price_ids(cr, uid, pdt_ids, context=context)
#         return {
#             'domain': [('id', 'in', pol_ids)],
#             'name': _(u'�鿴��ͼ۸�'),
#             'view_type': 'form',
#             'view_mode': 'tree,form',
#             'res_model': 'purchase.order.line',
#             'type': 'ir.actions.act_window',
#             'target': 'new',
#         }
#
#     ##stock.picking
#     def view_receipt(self, cr, uid, ids, context=None):
#         receipt_id = self.create_purchase_receipt(cr, uid, ids, context=context)
#         return {
#             # 'domain': [('id', 'in', ready_id)],
#             'name': _(u'�ջ���'),
#             # 'view_type': 'form',
#             'view_mode': 'form',
#             'res_model': 'purchase.receipt',
#             'res_id': receipt_id,
#             'type': 'ir.actions.act_window',
#             # 'target': 'new',
#         }
#     def create_done(self, cr, uid, values=None, context=None):
#         pick_id = self.create(cr, uid, values, context=context)
#         self.do_transfer(cr, uid, [pick_id], context=context)
#         return pick_id
#
#     def create_assign(self, cr, uid, values=None, context=None):
#         pick_id = self.create(cr, uid, values, context=context)
#         self.action_assign(cr, uid, [pick_id,], context=context)
#         return pick_id
#     def create_purchase_receipt(self, cr, uid, ids, context=None):
#         receipt_obj = self.pool.get('purchase.receipt')
#         pick = self.browse(cr, uid, ids[0], context=context)
#         po_id = pick.move_lines[0].purchase_line_id.order_id.id
#         data = {
#             'picking_id': pick.id,
#             'po_id': po_id,
#             'line_ids': [],
#         }
#         line_data = []
#         for move in pick.move_lines:
#             data['line_ids'].append((0, 0, {
#                 'product_id': move.product_id.id,
#                 'uom_id': move.product_uom.id,
#                 'receipt_qty': move.product_uom_qty,
#                 'move_qty': move.product_uom_qty,
#                 'pol_id': move.purchase_line_id.id,
#             }))
#         receipt_id = receipt_obj.create(cr, uid, data, context=context)
#         if pick.state == 'draft':
#             self.action_confirm(cr, uid, ids, context=context)
#         return receipt_id
#
# class move_intend(osv.osv):
#     _name = 'move.intend'
#     _columns = {
#         'name': fields.char(u'��ע', size=32),
#         'product_id': fields.many2one('product.product', u'����', required=True),
#         # 'uom_id': fields.related('product_id','uom_id', type='many2one', relation='product.uom', string=u'��λ', readonly=True, ),
#         'uom_id': fields.many2one('product.uom', u'��λ', required=True),
#         'move_qty': fields.float(u'����', digits_compute=dp.get_precision('Product Unit of Measure'), ),
#     }
#
#
# Material_Acquire_State = [('draft', u'�ݸ�'), ('w_material_control',u'�����'), ('w_warehouse', '���ֿ�'), ('done', u'���'), ('cancel', u'ȡ��')]
#
#
# class material_acquire_line(osv.osv):
#     _inherits = {'move.intend': 'intend_id'}
#     _name = "material.acquire.line"
#     _columns = {
#         'intend_id': fields.many2one('move.intend', 'Move Intend', required=True, ondelete="cascade"),
#         'acquire_id': fields.many2one('material.acquire', u'�ջ���', ondelete="cascade", ),
#         'state': fields.related('acquire_id', 'state', type="selection", selection=Material_Acquire_State, string=u"״̬", readonly=True),
#         'qty': fields.float(u'��������', digits_compute=dp.get_precision('Product Unit of Measure'), readonly=False, states={'draft': [('readonly', False), ]}),
#         #'offcut': fields.boolean(u'ʹ��'),
#     }
#
#     def have_offcut(self, cr, uid, ids, product_id, context=None):
#         me = self.browse(cr, uid, ids[0], context=context)
#         self.write(cr, uid, me.id, {'move_qty': int(me.qty)}, context=context)
#         return True
#
#     def no_offcut(self, cr, uid, ids, product_id, context=None):
#         me = self.browse(cr, uid, ids[0], context=context)
#         qty = me.qty
#         if not qty.is_integer():
#             qty = int(qty) + 1
#         self.write(cr, uid, me.id, {'move_qty': qty}, context=context)
#         return True
#
#     def onchange_product_id(self, cr, uid, ids, product_id, context=None):
#         pdt_obj = self.pool['product.product']
#         value = {}
#         if not product_id:
#             return True
#         pdt = pdt_obj.browse(cr, uid, product_id, context=context)
#         return {'value': {'uom_id': pdt.uom_id.id, 'qty': 1, 'move_qty': 1,}}
#
#     def onchange_qty(self, cr, uid, ids, qty, context=None):
#         return {'value': {'move_qty': qty,}}
#
#
#
#
# class material_acquire(osv.osv):
#     _name = 'material.acquire'
#     _order = 'id desc'
#
#     def _default_pick_type(self, cr, uid, context=None):
#         return self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mtlcs_stock', 'picking_type_material_production')[1]
#
#     def _defaults_department(self, cr, uid, context=None):
#         res = self.pool.get('res.users').read(cr, uid, uid, ['default_department_id'], context=context, load="_classic_write")
#         return res['default_department_id']
#
#     _columns = {
#         'name': fields.char(u'����', size=32, readonly=True),
#         'department_id': fields.many2one('hr.department', u'����', required=True, readonly=True, states={'draft': [('readonly', False)]},),
#         'user_id': fields.many2one('res.users', u'������', required=False, readonly=True, states={'draft': [('readonly', False)]},),
#         'line_ids': fields.one2many('material.acquire.line', 'acquire_id', 'Lines', readonly=True, states={'draft': [('readonly', False)]}, copy=True),
#         'state': fields.selection(Material_Acquire_State, u'״̬', ),
#         'picking_id': fields.many2one('stock.picking', u'���ϳ��ⵥ', readonly=True, copy=False),
#         'create_uid': fields.many2one('res.users', u'������', readonly=True),
#         'create_date': fields.datetime(u'����ʱ��', readonly=True),
#         'pick_type_id': fields.many2one("stock.picking.type", string=u"�ƿ�����", readonly=True),
#         'note': fields.text(u'��ע'),
#     }
#
#     _defaults = {
#         'state': 'draft',
#         'name': lambda self, cr, uid, ctx: self.pool.get('ir.sequence').get(cr, uid, self._name),
#         'create_uid': lambda self, cr, uid, ctx: uid,
#         'user_id': lambda self, cr, uid, ctx: uid,
#         'create_date': lambda self, cr, uid, ctx: fields.datetime.now(),
#         'pick_type_id': lambda self, cr, uid, ctx: self._default_pick_type(cr, uid, ctx),
#         'department_id': lambda self, cr, uid, ctx: self._defaults_department(cr, uid, ctx),
#     }
#
#
#     def unlink(self, cr, uid, ids, context=None):
#         for data in self.read(cr, uid, ids, ['state']):
#             if data['state'] not in ['draft', 'cancel']:
#                 raise Warning(u"�ǲݸ塢ȡ��״̬����ɾ��")
#         return super(material_acquire, self).unlink(cr, uid, ids, context=context)
#
#     def confirm(self, cr, uid, ids, context=None):
#         line_obj = self.pool.get('material.acquire.line')
#         acquire = self.browse(cr, uid, ids[0], context=context)
#         for line in acquire.line_ids:
#             line_obj.write(cr, uid, line.id, {'move_qty': line.qty})
#         self.write(cr, uid, ids, {'state': 'w_material_control'}, context=context)
#         return True
#
#     def material_control_approve(self, cr, uid, ids, context=None):
#         self.write(cr, uid, ids, {'state': 'w_warehouse'}, context=context)
#         return True
#
#     def warehouse_approve(self, cr, uid, ids, context=None):
#         self.make_picking(cr, uid, ids, context=context)
#         self.write(cr, uid, ids, {'state': 'done'}, context=context)
#         return True
#
#     def to_cancel(self, cr, uid, ids, context=None):
#         self.write(cr, uid, ids, {'state': 'cancel'}, context=context)
#         return True
#
#     def reset_draft(self, cr, uid, ids, context=None):
#         self.write(cr, uid, ids, {'state': 'draft'}, context=context)
#         return True
#
#     def make_picking(self, cr, uid, ids, context=None):
#         pick_obj = self.pool.get('stock.picking')
#         o = self.browse(cr, uid, ids[0], context=context)
#         if not o.picking_id:
#             picking_vals = self._prepare_picking(cr, uid, o, context=context)
#             picking_id = pick_obj.create_assign(cr, uid, picking_vals, context=context)
#             self.write(cr, uid, o.id, {'picking_id': picking_id}, context=context)
#             pick_state = pick_obj.read(cr, uid, picking_id, ['state'], context=context)['state']
#             if pick_state == "assigned":
#                 pick_obj.do_transfer(cr, uid, [picking_id], context=context)
#             else:
#                 pass
#                 raise Warning(u'��治��')
#         return True
#
#
#     def _prepare_picking(self, cr, uid, o, context=None):
#         picking_type_id = o.pick_type_id.id
#         location_id = o.pick_type_id.default_location_src_id.id
#         location_dest_id = o.pick_type_id.default_location_dest_id.id
#         move_data = []
#         for line in o.line_ids:
#             data = {
#                 'name': line.product_id.name,
#                 'product_id': line.product_id.id,
#                 'product_uom': line.uom_id.id,
#                 'product_uom_qty': line.move_qty,
#                 # 'date': lin.date_order,
#                 'location_id': location_id,
#                 'location_dest_id': location_dest_id,
#                 # 'partner_id': order.dest_address_id.id,
#                 # 'move_dest_id': False,
#                 'state': 'draft',
#                 # 'purchase_line_id': order_line.id,
#                 # 'company_id': order.company_id.id,
#                 # 'price_unit': price_unit,
#                 'picking_type_id': picking_type_id,
#                 # 'group_id': group_id,
#                 # 'procurement_id': False,
#                 'origin': line.name,
#                 # 'route_ids': order.picking_type_id.warehouse_id and [(6, 0, [x.id for x in order.picking_type_id.warehouse_id.route_ids])] or [],
#                 # 'warehouse_id':order.picking_type_id.warehouse_id.id,
#                 'invoice_state': 'none',
#             }
#             move_data.append((0, 0, data))
#         picking_vals = {
#             'picking_type_id': picking_type_id,
#             'department_id': o.department_id.id,
#             # 'date': o.date_order,
#             'origin': o.name,
#             'move_lines': move_data,
#         }
#         return picking_vals
#
#
#     def view_product_qty(self, cr, uid, ids, context=None):
#         pick = self.browse(cr, uid, ids[0], context=context)
#         pdt_ids = [line.product_id.id for line in pick.line_ids]
#         return {
#             'domain': [('id', 'in', pdt_ids)],
#             'name': _(u'�鿴��Ʒ����'),
#             'view_type': 'form',
#             'view_mode': 'tree,form',
#             'res_model': 'product.product',
#             'type': 'ir.actions.act_window',
#             'target': 'new',
#         }
#
#     def view_this_month_record(self, cr, uid, ids, context=None):
#         acq = self.browse(cr, uid, ids[0], context=context)
#         ptd_ids = [line.product_id.id for line in acq.line_ids]
#         this_ids = [line.id for line in acq.line_ids]
#         history_ids = self.pool.get('material.acquire.line').search(cr, uid, [('acquire_id.department_id.id','=',acq.department_id.id),('product_id', 'in', ptd_ids), ('id', 'not in', this_ids)])
#         return {
#             'domain': [('id', 'in', history_ids)],
#             'name': _(u'������ʷ���ϼ�¼'),
#             # 'view_type': 'form',
#             'view_mode': 'tree,form',
#             'res_model': 'material.acquire.line',
#             'type': 'ir.actions.act_window',
#             'target': 'new',
#         }
#
#     def batch_select_product(self, cr, uid, ids, context=None):
#         view_id = self.pool['ir.model.data'].get_object_reference(cr, uid, 'mtlcs_product', 'product_tree_view_for_preparation_order')[1]
#         return {
#             'name': _(u'�����ϸ����'),
#             'view_type': 'form',
#             'view_mode': 'tree',
#             'res_model': 'product.product',
#             'type': 'ir.actions.act_window',
#             'view_id': view_id,
#             'domain': [('purchase_ok', '=', True)],
#             'no_destroy': True,
#             'flags': {'selectable': False,'search_view': True,  'pager':True,},
#             'context': {'add_to_material_acquire': 1},
#             #'target': 'new',
#         }
#
#
#
# Receipt_State = [('draft', u'�ݸ�'), ('w_qc', u'���ʼ�'), ('w_warehouse', u'���ֿ�'),('w_warehouse_manager', u'���ֿ�����'),
#                  ('input_finish',u'�����'), ('cancel', u'ȡ��'), ('done', u'���')]
#
# #TODO finish all return status
# Receipt_Return_State = [('draft', u'�ݸ�'), ('w_purchase', u'���ɹ�'), ('w_account', u'������'), ('w_warehouse', u'���ֿ�'),('done',u'�˻����')]
#
#
#
# class purchase_receipt_line(osv.osv):
#     _inherits = {'move.intend': 'intend_id'}
#     _name = "purchase.receipt.line"
#
#     def _track_incoming(self, cr, uid, ids, fields_name, arg=None, context=None):
#         res = {}
#         for line in self.browse(cr, uid, ids, context=context):
#             res[line.id] = line.product_id.track_all or line.product_id.track_incoming
#         return res
#
#     _columns = {
#         'intend_id': fields.many2one('move.intend', 'Move Intend', required=True, ondelete="cascade"),
#         'receipt_id': fields.many2one('purchase.receipt', u'�ջ���', ondelete="cascade", ),
#         'state': fields.related('receipt_id', 'state', type="selection", selection=Receipt_State, string=u"״̬", readonly=True),
#         'receipt_qty': fields.float(u'�ջ�����', digits_compute=dp.get_precision('Product Unit of Measure'), readonly=True,
#                                     states={'draft': [('readonly', False), ]}),
#         'unqualified_qty': fields.float(u'���ϸ�����', digits_compute=dp.get_precision('Product Unit of Measure'),),
#         'pol_id': fields.many2one('purchase.order.line', u'�ɹ���ϸ'),
#         'lot_id': fields.many2one('stock.production.lot', '���κ�', domain="[('product_id','=?',product_id)]"),
#         'track_incoming': fields.function(_track_incoming, type="boolean", string=u"��������", readonly=True),
#     }
#
#     def onchange_qty(self, cr, uid, ids, receipt_qty, move_qty, unqualified_qty, field_name=None, context=None):
#         if not field_name:
#             raise Warning('Pls input field_name')
#         value = {}
#         if field_name == 'receipt_qty':
#             value = {'move_qty': receipt_qty, 'unqualified_qty':0}
#         elif field_name == 'move_qty':
#             value = {'unqualified_qty': receipt_qty - move_qty }
#         elif field_name == 'unqualified_qty':
#             value = {'move_qty': receipt_qty - unqualified_qty }
#
#         return {'value':value}
#
#     def onchange_unqualified_qty(self, cr, uid, ids, unqualified_qty, receipt_qty,   context=None):
#         return {'value':{'move_qty': receipt_qty - unqualified_qty}}
#
#     def create_lot(self, cr, uid, ids, context=None):
#         me = self.browse(cr, uid, ids[0], context=context)
#         product = me.product_id
#
#         if (product.track_all or product.track_incoming) and (me.state in ['draft',]) and (not me.lot_id) :
#             return {
#                 'name': _(u'���κ�'),
#                 'view_type': 'form',
#                 'view_mode': 'form',
#                 'res_model': 'stock.production.lot',
#                 'type': 'ir.actions.act_window',
#                 'target': 'new',
#                 'context': {'default_product_id': me.product_id.id, 'res_field': 'lot_id'},
#                 'flags': {'form': {'action_buttons': True}},
#             }
#         else:
#             raise Warning(u'����Ҫ׷������')
#         return True
#
#
# class purchase_receipt(osv.osv):
#     _name = 'purchase.receipt'
#     _order = 'id desc'
#     _inherit = ['mail.thread']
#     _track = {
#         'state': {
#             'mtlcs_stock.purchase_receipt_w_qc': lambda self, cr, uid, obj, ctx=None: obj.state == 'w_qc',
#             'mtlcs_stock.purchase_receipt_w_warehouse': lambda self, cr, uid, obj, ctx=None: obj.state == 'w_warehouse',
#             'mtlcs_stock.purchase_receipt_w_warehouse_manager': lambda self, cr, uid, obj, ctx=None: obj.state == 'w_warehouse_manager',
#             'mtlcs_stock.purchase_receipt_done': lambda self, cr, uid, obj, ctx=None: obj.state == 'done',
#         },
#     }
#
#     _columns = {
#         'name': fields.char(u'����', size=32, readonly=True),
#         'line_ids': fields.one2many('purchase.receipt.line', 'receipt_id', 'Lines'),
#         'state': fields.selection(Receipt_State, u'״̬', ),
#         'return_state': fields.selection(Receipt_Return_State, u'�˻�״̬'),
#         'have_unqualified': fields.boolean(u'�в���Ʒ', readonly=True),
#         'picking_id': fields.many2one('stock.picking', u'Picking'),
#         'partner_id': fields.related('picking_id', 'partner_id', type="many2one", relation="res.partner", readonly=True, string=u"��Ӧ��"),
#         'po_id': fields.many2one('purchase.order', u'�ɹ���'),
#         'create_uid': fields.many2one('res.users', u'������', readonly=True),
#         'create_date': fields.datetime(u'����ʱ��', readonly=True),
#         'note': fields.text(u'��ע'),
#         'pick_type_id': fields.related('picking_id', 'picking_type_id', type="many2one", relation="stock.picking.type", readonly=True,
#                                        string=u"�ƿ�����"),
#         'partner_ref': fields.char(u'��Ӧ���ͻ���', readonly=True, states={'draft': [('readonly', False),]}, ),
#     }
#
#     _defaults = {
#         'state': 'draft',
#         'name': lambda self, cr, uid, ctx: self.pool.get('ir.sequence').get(cr, uid, self._name),
#         'create_uid': lambda self, cr, uid, ctx: uid,
#         'create_date': lambda self, cr, uid, ctx: fields.datetime.now(),
#     }
#
#     ##�ջ��˻�
#     def return_confirm(self, cr, uid, ids, context=None):
#         self.write(cr, uid, ids, {'return_state': 'w_purchase'})
#         return True
#
#     def return_purchase_approve(self, cr, uid, ids, context=None):
#         self.write(cr, uid, ids, {'return_state': 'w_account'})
#         return True
#
#     def return_account_approve(self, cr, uid, ids, context=None):
#         self.write(cr, uid, ids, {'return_state': 'w_warehouse'})
#         return True
#
#     def return_warehouse_approve(self, cr, uid, ids, context=None):
#         self.write(cr, uid, ids, {'return_state': 'done'})
#         return True
#
#     ##
#     def unlink(self, cr, uid, ids, context=None):
#         for data in self.read(cr, uid, ids, ['state']):
#             if data['state'] not in ['draft', 'cancel']:
#                 raise Warning(u"�ǲݸ塢ȡ��״̬����ɾ��")
#         return super(purchase_receipt, self).unlink(cr, uid, ids, context=context)
#
#     def to_cancel(self, cr, uid, ids, context=None):
#         self.write(cr, uid, ids, {'state': 'cancel'}, context=context)
#         return True
#
#     def reset_draft(self, cr, uid, ids, context=None):
#         self.write(cr, uid, ids, {'state': 'draft'}, context=context)
#         return True
#
#     def need_check_quality(self, cr, uid, receipt, context=None):
#         #TODO -- need check quantity
#         for line in receipt.line_ids:
#             if line.product_id.need_iqc:
#                 return True
#         return False
#
#     def confirm(self, cr, uid, ids, context=None):
#         receipt = self.browse(cr, uid, ids[0], context=context)
#         for line in receipt.line_ids:
#             if (line.product_id.track_all or line.product_id.track_incoming) and (not line.lot_id):
#                 raise Warning(u'�ջ���ϸ������Ҫ׷�����κŵĲ�Ʒ���������ö�Ӧ�����κ�')
#
#         next_state = 'w_warehouse_manager'
#         if self.need_check_quality(cr, uid, receipt, context=context):
#             next_state = 'w_qc'
#         self.write(cr, uid, ids, {'state': next_state}, context=context)
#         return True
#
#     def qc_approve(self, cr, uid, ids, context=None):
#         receipt = self.browse(cr, uid, ids[0], context=context)
#         have_unqualified = False
#         for line in receipt.line_ids:
#             if line.move_qty > line.receipt_qty:
#                 raise Warning('�ϸ������ܴ����ջ�����')
#             if line.unqualified_qty:
#                 have_unqualified = True
#         self.write(cr, uid, ids, {'state': 'w_warehouse','have_unqualified': have_unqualified, 'return_state': 'draft'}, context=context)
#         return True
#
#     def warehouse_approve(self, cr, uid, ids, context=None):
#         self.write(cr, uid, ids, {'state': 'w_warehouse_manager'}, context=context)
#         return True
#
#     def warehouse_manager_approve(self, cr, uid, ids, context=None):
#         return self.action_done(cr, uid, ids, context=context)
#
#     def action_done(self, cr, uid, ids, context=None):
#         assert len(ids) == 1
#         receipt = self.browse(cr, uid, ids[0], context=context)
#         if receipt.picking_id.state != 'done':
#             self.picking_transfer(cr, uid, ids, context=context)
#         self.write(cr, uid, ids, {'state': 'done'}, context=context)
#         return True
#
#     def picking_transfer(self, cr, uid, ids, context=None):
#         wizard_id = self.create_transfer(cr, uid, ids, context=context)
#         self.pool.get('stock.transfer_details').do_detailed_transfer(cr, uid, wizard_id, context=context)
#         return True
#
#     def create_transfer(self, cr, uid, ids, context=None):
#         if not context:
#             context = {}
#         transfer_obj = self.pool.get('stock.transfer_details')
#         ready = self.browse(cr, uid, ids[0], context=context)
#         pick = ready.picking_id
#         if pick.state != 'assigned':
#             raise Warning(u'��ⵥ״̬������')
#
#         item_data = {} #data from to create transfer_details
#         for line in ready.line_ids:
#             item_data.update({line.product_id.id: {'product_uom_id': line.uom_id.id, 'quantity': line.move_qty, 'lot_id': line.lot_id.id }})
#
#         context.update({
#             'active_model': 'stock.picking',
#             'active_ids': [pick.id],
#             'active_id': pick.id,
#             'change_item': item_data,
#         })
#         wizard_id = self.pool['stock.transfer_details'].create(cr, uid, {'picking_id': pick.id}, context=context)
#         return wizard_id
#
#     def open_transfer(self, cr, uid, ids, context=None):
#         wizard_id = self.create_transfer(cr, uid, ids, context=context)
#         return {
#             # 'domain': [('id', 'in', [wizard_id,])],
#             'name': _(u'�ջ�ȷ�����'),
#             'view_type': 'form',
#             'view_mode': 'form',
#             'res_model': 'stock.transfer_details',
#             'res_id': wizard_id,
#             'type': 'ir.actions.act_window',
#             'target': 'new',
#         }
#
#
#
#
# class stock_move(osv.osv):
#     _inherit = 'stock.move'
#     _columns = {
#         'department_id': fields.related('picking_id', 'department_id', type="many2one", relation="hr.department", readonly=True, string=u"����"),
#     }
#
#     # def onchange_product_id(self, cr, uid, ids, prod_id=False, loc_id=False, loc_dest_id=False, partner_id=False, picking_type_id=False,
#     #                         context=None):
#     #     res = super(stock_move, self).onchange_product_id(cr, uid, ids, prod_id=prod_id, loc_id=loc_id, loc_dest_id=loc_dest_id,
#     #                                                       partner_id=partner_id)
#     #     pdt_obj = self.pool.get('product.product')
#     #     if context.get('use_po_unit') and prod_id:
#     #         pdt = pdt_obj.browse(cr, uid, prod_id, context=context)
#     #         uom_po_id = pdt.uom_po_id.id
#     #         if uom_po_id != res['value']['product_uom']:
#     #             uos_id = pdt.uos_id and pdt.uos_id.id or False
#     #             product_uos_qty = self.pool.get('stock.move').onchange_quantity(cr, uid, ids, prod_id, 1.00, uom_po_id, uos_id)['value'][
#     #                 'product_uos_qty']
#     #             res['value'].update({'product_uom': uom_po_id, 'product_uos_qty': product_uos_qty})
#     #     return res
#
#
#
#
# class material_department(osv.osv):
#     _name = "material.department"
#
#     def _compute_name(self, cr, uid, ids, field_name, arg=None, context=None):
#         res = {}
#         for d in self.browse(cr, uid, ids, context=context):
#             res[d.id] = '%s:%s' % (d.product_id.name, d.department_id.name)
#         return res
#
#     _columns = {
#         'name': fields.function(_compute_name, type='char', size=32, string=u'����Ȩ��'),
#         'product_id': fields.many2one('product.product', u'����', required=True),
#         'department_id': fields.many2one('hr.department', u'����', required=True),
#         'create_uid': fields.many2one('res.users', u'������'),
#     }
#
#     _defaults = {
#     }
#
#     _sql_constraints = [
#         ('name_uniq', 'unique(product_id,department_id)', u'���ϺͲ��Ų����ظ�'),
#     ]