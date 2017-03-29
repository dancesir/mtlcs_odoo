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
from lxml import etree
from openerp.tools.translate import _
from openerp.osv import fields, osv
from openerp.addons.decimal_precision import decimal_precision as dp
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from datetime import datetime

Pick_MTL_State = [
    ('draft', u'草稿'),
    ('w_check_number', u'待点数'),
    ('w_iqc', u'来料待检查'),
    ('w_purchase', u'待采购'),
    ('w_account', u'待采财务'),
    ('w_technical', u'待工艺'),
    ('w_general_manager', u'待总经办'),
    ('w_quality', u'待品质'),
    ('w_quality_manager', u'待品质经理'),
    ('w_material_control', u'待物控'),
    ('grant', u'允许转移'),

]

MTL_PICKING_TYPE = [
    ('slip_board', u'领板料'),
]


class stock_warehouse(osv.osv):
    _inherit = 'stock.warehouse'

    # ==========multi company
    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True, select=True),
    }

    # ==========0208
    def create(self, cr, uid, values, context=None):
        return super(stock_warehouse, self).create(cr, uid, values, context=context)

class stock_warehouse_orderpoint(osv.osv):
    _inherit = 'stock.warehouse.orderpoint'
    _columns = {
        # 'qty_available': fields.char(u'在手数量', size=12),
        'qty_available': fields.related('product_id', 'qty_available', type='float', readonly=True, string=u"在手数量"),
        'company_id': fields.many2one('res.company', 'Company', readonly=True, required=True),
    }

    # ==========multi company
    # _defaults = {
    #     'company_id': lambda self, cr, uid, ctx: self.pool.get('res.users').browse(cr, uid, uid).company_id.id,
    # }


class stock_picking(osv.osv):
    # ==========1121
    _inherit = ['stock.picking', 'mail.thread', 'approve.log.thread']
    # _inherit = 'stock.picking'
    _name = 'stock.picking'
    _approve_log = ['mtl_state']

    def _defaults_department(self, cr, uid, context=None):

        default_department_id = False
        if context.get('need_department'):
            default_department_id = \
                self.pool.get('res.users').read(cr, uid, uid, ['default_department_id'], context=context,
                                                load="_classic_write")[
                    'default_department_id']
            return default_department_id

    # multi company
    # def _defaults_picking_type_id(self, cr, uid, context=None):
    #     print '=======',context.get('default_picking_type_id')
    #     if context.get('default_picking_type_id'):
    #         ptype_obj = self.pool.get('stock.picking.type')
    #         for p in ptype_obj.browse(cr, uid, context.get('default_picking_type_id')):
    #             company_id = self.pool.get('res.users').browse(cr, uid, uid).company_id.id
    #             if company_id == p.warehouse_id.company_id.id:
    #                 return p.id

    _columns = {
        'department_id': fields.many2one('hr.department', u'部门', readonly=True,
                                         states={'draft': [('readonly', False)]}, ),
        'account_touched': fields.boolean(u'财务已签收', readonly=True, ),
        'mtl_type': fields.selection(MTL_PICKING_TYPE, u'扩展类型', readonly=True,
                                     states={'draft': [('readonly', False)]}, ),
        'mtl_state': fields.selection(Pick_MTL_State, u'状态', readonly=True),
    }
    _defaults = {
        'department_id': lambda self, cr, uid, ctx=None: self._defaults_department(cr, uid, context=ctx),
        # ==========1205
        'date': lambda *a: datetime.utcnow().strftime(DTF),
        # multi company
        # 'picking_type_id': _defaults_picking_type_id,
    }

    def onchange_mtl_type(self, cr, uid, ids, mtl_type, domain=None, context=None):
        value = {}
        if mtl_type == 'slip_board':
            value.update({'move_type': 'direct'})
        else:
            value.update({'move_type': 'one'})
        return {'value': value}

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}

        default.update({'mtl_state': False, 'account_touched': False})
        return super(stock_picking, self).copy(cr, uid, id, default, context=context)

    def create_return_picking(self, cr, uid, ids, context=None):
        '''
        TODO:avoid repeat return
        '''
        return {
            'name': _(u'创建退货'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.return.picking',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def get_to_state(self, cr, uid, pick, context=None):
        type_ref = pick.picking_type_id and pick.picking_type_id.ref

        now_state = pick.mtl_state
        to_state = 'grant'

        # #one company
        # if not now_state or now_state == 'draft':
        #     to_state = 'grant'
        #     if type_ref == 'stock2production':
        #         if self.is_poison(cr, uid, pick, context=context):
        #             to_state = 'w_technical'
        #         if self.is_precious(cr, uid, pick, context=context):
        #             to_state = 'w_general_manager'
        #     if type_ref == 'stock2ng':
        #         to_state = 'w_quality_manager'
        #     if type_ref == 'ng2supplier':
        #         to_state = 'w_account'
        #     if type_ref == 'production2ng':
        #         to_state = 'w_quality_manager'
        #     if type_ref == 'finish2production':
        #         to_state = 'w_quality_manager'
        #     if type_ref == 'pending2production':
        #         to_state = 'w_quality_manager'
        #     if type_ref == 'finish2ng':
        #         to_state = 'w_material_control'
        #     if type_ref == 'pending2ng':
        #         to_state = 'w_material_control'
        #
        # elif now_state == 'w_quality_manager':
        #     if type_ref == 'stock2ng':
        #         to_state = 'w_purchase'
        #     if type_ref == 'production2ng':
        #         to_state = 'w_purchase'
        #     if type_ref == 'finish2production':
        #         to_state = 'grant'
        #     if type_ref == 'pending2production':
        #         to_state = 'grant'
        #     if type_ref == 'finish2ng':
        #         to_state = 'w_account'
        #     if type_ref == 'pending2ng':
        #         to_state = 'w_account'
        #
        # elif now_state == 'w_purchase':
        #     if type_ref == 'stock2ng':
        #         to_state = 'w_material_control'
        #     if type_ref == 'production2ng':
        #         to_state = 'w_material_control'
        #
        # elif now_state == 'w_material_control':
        #     if type_ref == 'stock2ng':
        #         to_state = 'grant'
        #     if type_ref == 'production2ng':
        #         to_state = 'grant'
        #     if type_ref == 'finish2ng':
        #         to_state = 'w_quality_manager'
        #     if type_ref == 'pending2ng':
        #         to_state = 'w_quality_manager'
        #
        # elif now_state == 'w_account':
        #     if type_ref == 'ng2supplier':
        #         to_state = 'grant'
        #     if type_ref == 'finish2ng':
        #         to_state = 'w_general_manager'
        #     if type_ref == 'pending2ng':
        #         to_state = 'w_general_manager'
        #
        # elif now_state == 'w_general_manager':
        #     if type_ref == 'finish2ng':
        #         to_state = 'grant'
        #     if type_ref == 'pending2ng':
        #         to_state = 'grant'

        # multi company
        if not now_state or now_state == 'draft':
            to_state = 'grant'
            if 'stock2production' in type_ref:
                if self.is_poison(cr, uid, pick, context=context):
                    to_state = 'w_technical'
                if self.is_precious(cr, uid, pick, context=context):
                    to_state = 'w_general_manager'
            if 'stock2ng' in type_ref:
                to_state = 'w_quality_manager'
            if 'ng2supplier' in type_ref:
                to_state = 'w_account'
            if 'production2ng' in type_ref:
                to_state = 'w_quality_manager'
            if 'finish2production'in type_ref:
                to_state = 'w_quality_manager'
            if 'pending2production' in type_ref:
                to_state = 'w_quality_manager'
            if 'finish2ng' in type_ref:
                to_state = 'w_material_control'
            if 'pending2ng' in type_ref:
                to_state = 'w_material_control'

        elif now_state == 'w_quality_manager':
            if 'stock2ng' in type_ref:
                to_state = 'w_purchase'
            if 'production2ng' in type_ref:
                to_state = 'w_purchase'
            if 'finish2production' in type_ref:
                to_state = 'grant'
            if 'pending2production' in type_ref:
                to_state = 'grant'
            if 'finish2ng' in type_ref:
                to_state = 'w_account'
            if 'pending2ng' in type_ref:
                to_state = 'w_account'

        elif now_state == 'w_purchase':
            if 'stock2ng' in type_ref:
                to_state = 'w_material_control'
            if 'production2ng' in type_ref:
                to_state = 'w_material_control'

        elif now_state == 'w_material_control':
            if 'stock2ng' in type_ref:
                to_state = 'grant'
            if 'production2ng' in type_ref:
                to_state = 'grant'
            if 'finish2ng' in type_ref:
                to_state = 'w_quality_manager'
            if 'pending2ng' in type_ref:
                to_state = 'w_quality_manager'

        elif now_state == 'w_account':
            if 'ng2supplier' in type_ref:
                to_state = 'grant'
            if 'finish2ng' in type_ref:
                to_state = 'w_general_manager'
            if 'pending2ng' in type_ref:
                to_state = 'w_general_manager'

        elif now_state == 'w_general_manager':
            if 'finish2ng' in type_ref:
                to_state = 'grant'
            if 'pending2ng' in type_ref:
                to_state = 'grant'

        if to_state == now_state:
            to_state = False
        return to_state

    # ==========0909

    def action_confirm(self, cr, uid, ids, context=None):
        assert len(ids) == 1
        res = super(stock_picking, self).action_confirm(cr, uid, ids, context=context)
        pick = self.browse(cr, uid, ids[0], context=context)

        # ==========1118
        if not pick.move_lines:
            raise Warning(u'请至少选择一个物料')

        to_state = self.get_to_state(cr, uid, pick, context=context)
        self.write(cr, uid, pick.id, {'mtl_state': to_state}, context=context)
        return res

    # ==========1203
    def action_assign(self, cr, uid, ids, context=None):

        res = super(stock_picking, self).action_assign(cr, uid, ids, context=context)
        pick = self.browse(cr, uid, ids[0], context=context)

        # multi company
        # if pick.picking_type_id.ref == 'stock2production':
        if 'stock2production' in pick.picking_type_id.ref:
            info = ''
            for p in pick.move_lines:
                if p.product_uom_qty > p.product_id.qty_available:
                    info += '%s%s%s' % (p.product_id.name, p.product_id.variants, '\n')
            if info:
                raise Warning(u'以下物料库存不足:\n%s' % info)

        return res

    def common_approve(self, cr, uid, pick, context=None):
        to_state = to_state = self.get_to_state(cr, uid, pick, context=context)
        if to_state:
            self.write(cr, uid, pick.id, {'mtl_state': to_state}, context=context)
        if to_state == 'grant':
            self.action_assign(cr, uid, [pick.id, ], context=context)
        return True

    def quality_manager_approve(self, cr, uid, ids, context=None):
        pick = self.browse(cr, uid, ids, context=context)
        self.common_approve(cr, uid, pick, context=context)

    def purchase_approve(self, cr, uid, ids, context=None):
        pick = self.browse(cr, uid, ids, context=context)
        self.common_approve(cr, uid, pick, context=context)

    def material_control_approve(self, cr, uid, ids, context=None):
        pick = self.browse(cr, uid, ids, context=context)
        self.common_approve(cr, uid, pick, context=context)

    def account_approve(self, cr, uid, ids, context=None):
        pick = self.browse(cr, uid, ids, context=context)
        self.common_approve(cr, uid, pick, context=context)

    def general_manager_approve(self, cr, uid, ids, context=None):
        pick = self.browse(cr, uid, ids, context=context)
        self.common_approve(cr, uid, pick, context=context)

    def technical_approve(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'mtl_state': 'grant'}, context=context)

    def action_confirm_return(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'mtl_state': 'w_purchase'}, context=context)
        return self.action_confirm(cr, uid, ids, context=context)

    def check_strict_department(self, cr, uid, pick, context=None):
        '''
        check production_application_slip rule
        '''
        for move in pick.move_lines:
            p = move.product_id
            if p.strict_department and not (pick.department_id in p.material_department_ids):
                raise Warning(u'%s没有%s领料权限，请联系物控' % (pick.department_id.name, p.default_code))
        return True

    def is_precious(self, cr, uid, pick, context=None):
        for move in pick.move_lines:
            if move.product_id.is_precious:
                return True
        return False

    def is_poison(self, cr, uid, pick, context=None):
        for move in pick.move_lines:
            if move.product_id.is_poison:
                return True
        return False

    # receive wkf
    def open_enter_transfer_details(self, cr, uid, ids, context=None):
        trans_obj = self.pool['stock.transfer_details']
        pick_id = ids[0]
        transfer_ids = trans_obj.search(cr, uid, [('picking_id', '=', pick_id)], context=context, limit=1,
                                        order="id desc")
        if transfer_ids:
            res = trans_obj.wizard_view(cr, uid, transfer_ids[0], context)
            # TODO: how to set wizard form view:no_edit
            return res
        else:
            raise Warning(u'请先点数')

    def check_number(self, cr, uid, ids, context=None):
        '''
        create or write transfer_details date to save the check product_qty,
        '''
        trans_obj = self.pool['stock.transfer_details']
        pick_id = ids[0]
        transfer_ids = trans_obj.search(cr, uid, [('picking_id', '=', pick_id)], context=context, limit=1,
                                        order="id desc")
        if transfer_ids:
            return trans_obj.wizard_view(cr, uid, transfer_ids[0], context)
        else:
            return self.do_enter_transfer_details(cr, uid, ids, context=context)

    def _create_extra_moves(self, cr, uid, picking, context=None):
        raise Warning(u'转移数不能大于计划数')
        # res = super(stock_picking, self)._create_extra_moves(cr, uid, picking, context=None)
        # return res

    def account_touch(self, cr, uid, ids, context=None):
        pick = self.browse(cr, uid, ids[0], context=context)
        if pick.inspection_id and pick.inspection_id.state != 'done':
            raise Warning(u'入库的质检单未完成，财务不签收')
        self.write(cr, uid, ids[0], {'account_touched': True}, context=context)
        return True

    def batch_select_product(self, cr, uid, ids, context=None):
        view_id = self.pool['ir.model.data'].get_object_reference(cr, uid, 'mtlcs_product',
                                                                  'product_tree_view_for_preparation_order')[1]
        return {
            'name': _(u'选择多个物料'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'product.product',
            'type': 'ir.actions.act_window',
            'view_id': view_id,
            'domain': [('purchase_ok', '=', True)],
            'flags': {'selectable': False, },
            'context': {'add_to_stock_picking': 1},
            # 'target': 'new',
        }

    def product_quick_view(self, cr, uid, ids, context=None):
        view_id = self.pool['ir.model.data'].get_object_reference(cr, uid, 'mtlcs_product',
                                                                  'material_product_tree_view')[1]
        pi_list = []
        ml_obj = self.browse(cr, uid, ids)
        for ml in ml_obj.move_lines:
            pi_list.append(ml.product_id.id)

        return {
            'name': _(u'物料信息查看'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'product.product',
            'type': 'ir.actions.act_window',
            'view_id': view_id,
            'domain': [('id', 'in', pi_list)],
            'flags': {'selectable': False, },
            # 'context': {},
            'target': 'new',
        }

    def print_by_usage(self, cr, uid, ids, context=None):
        assert len(ids) == 1
        report_names = {
            'slip': 'mtlcs_stock.picking_slip',
            'receive': 'mtlcs_stock.picking_purchase_receive',
            'default': 'stock.report_picking',
        }
        usage = context.get('usage', 'default')
        if usage not in report_names:
            raise Warning(u'没有找到匹配的报表，请联系管理员')
        return self.pool['report'].get_action(cr, uid, ids, report_names[usage], context=context)

    def make_next_picking(self, cr, uid, ids, context=None):
        pick = self.browse(cr, uid, ids[0], context=context)

        next_ref = None
        invoice_state = 'none'

        # multi company
        # if pick.picking_type_id.ref == 'stock2ng':
        if 'stock2ng' in pick.picking_type_id.ref:
            next_ref = 'ng2supplier'
            invoice_state = '2binvoiced'

        if not next_ref:
            raise Warning(u'无法确认下一步的调拨，请联系管理员')

        next_type = self.pool['stock.picking.type'].browse_by_ref(cr, uid, next_ref, context=context)
        moves = []
        for m in pick.move_lines:
            moves.append((0, 0, {
                'name': m.product_id.name,
                'product_id': m.product_id.id,
                'product_uom_qty': m.product_uom_qty,
                'product_uom': m.product_uom.id,
                'location_id': next_type.default_location_src_id.id,
                'location_dest_id': next_type.default_location_dest_id.id,
                'price_unit': m.price_unit,
            }))
        data = {
            'partner_id': pick.partner_id.id,
            'origin': pick.name,
            'picking_type_id': next_type.id,
            'move_lines': moves,
            'invoice_state': invoice_state,
        }
        new_id = self.create(cr, uid, data)

        return True


class stock_move(osv.osv):
    _inherit = 'stock.move'

    def _compute_department(self, cr, uid, ids, field_name, arg=None, context=None):
        res = {}
        for move in self.browse(cr, uid, ids, context=context):
            res[move.id] = move.picking_id.department_id and move.picking_id.department_id.id or False
        return res

    def _switch_move_from_picking(self, cr, uid, picking_ids, context=None):
        return self.pool['stock.move'].search(cr, uid, [('picking_id', 'in', picking_ids)], context=context)

    def _compute_display_offcut(self, cr, uid, ids, field_name, arg=None, context=None):
        res = {}
        for i in ids:
            res[i] = False
        return res

    def _compute_sub_total(self, cr, uid, ids, fields_name, arg=None, context=None):
        res = {}
        for move in self.browse(cr, uid, ids, context=context):
            res[move.id] = move.product_uom_qty * move.price_unit
        return res

    # ==========1212
    def _compute_no_move_qty(self, cr, uid, ids, fields_name, arg=None, context=None):
        res = {}
        move_obj = self.browse(cr, uid, ids, context=context)
        for m in move_obj:
            dm = [('id', '!=', m.id), ('product_id', '=', m.product_id.id), ('state', 'in', ['assigned', ]),
                  ('location_id', '=', m.location_id.id), ('location_dest_id', '=', m.location_dest_id.id)]
            no_move_ids = self.pool['stock.move'].search(cr, uid, dm, context=context)
            no_move_obj = self.browse(cr, uid, no_move_ids, context=context)
            res[m.id] = 0.0
            for nm in no_move_obj:
                res[m.id] += nm.product_uom_qty

        return res

    _columns = {
        # 'department_id': fields.related('picking_id', 'department_id', type="many2one", relation="hr.department", readonly=True, string=u"部门"),
        'department_id': fields.function(_compute_department, type="many2one", relation="hr.department", readonly=True,
                                         string=u"部门",
                                         store={'stock.picking': (_switch_move_from_picking, ['department_id'], 10), }
                                         ),
        'plan_qty': fields.float(digits_compute=dp.get_precision('Product Unit of Measure'), string=u'计划数量'),
        'mtl_type': fields.related('picking_id', 'mtl_type', type="selection", selection=MTL_PICKING_TYPE,
                                   string="MTL Type", ),
        'sub_total': fields.function(_compute_sub_total, type='float', string=u'小计'),

        # ==========1212
        'qty_available': fields.related('product_id', 'qty_available', type='float', string=u'在库', readonly=True),
        'incoming_qty': fields.related('product_id', 'incoming_qty', type='float', string=u'在途', readonly=True),
        'no_move_qty': fields.function(_compute_no_move_qty, type='float', string=u'未领取'),

    }

    # ==========1205
    _defaults = {
        'date_expected': lambda *a: datetime.utcnow().strftime(DTF),
    }

    def have_offcut(self, cr, uid, ids, context=None):
        move = self.browse(cr, uid, ids[0], context=context)
        if move.plan_qty:
            self.write(cr, uid, move.id, {'product_uom_qty': int(move.plan_qty)}, context=context)
        else:
            self.write(cr, uid, move.id,
                       {'product_uom_qty': int(move.product_uom_qty), 'plan_qty': move.product_uom_qty},
                       context=context)
        return True

    def no_offcut(self, cr, uid, ids, context=None):
        move = self.browse(cr, uid, ids[0], context=context)
        if move.plan_qty:
            if not move.plan_qty.is_integer():
                self.write(cr, uid, move.id, {'product_uom_qty': int(move.plan_qty) + 1}, context=context)
        else:
            if not move.plan_qty.is_integer():
                self.write(cr, uid, move.id,
                           {'product_uom_qty': int(move.product_uom_qty) + 1, 'plan_qty': move.product_uom_qty},
                           context=context)
        return True

    def regain_plan_qty(self, cr, uid, ids, context=None):
        move = self.browse(cr, uid, ids[0], context=context)
        if move.plan_qty:
            self.write(cr, uid, move.id, {'product_uom_qty': move.plan_qty}, context=context)
        return True


# class stock_production_lot(osv.osv):
#     _inherit = 'stock.production.lot'
#     _description = 'Lot/Serial'
#     _columns = {
#         # ==========multi company
#         'company_id': fields.many2one('res.company', readonly=True, string=u'公司'),
#     }
#     _defaults = {
#         # ==========multi company
#         'company_id': lambda self, cr, uid, ctx: self.pool.get('res.users').browse(cr, uid, uid).company_id.id,
#     }

#############################################################################
