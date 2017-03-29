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
from openerp.exceptions import Warning
from openerp.osv import fields, osv, expression
from openerp import api, tools, SUPERUSER_ID
from openerp.tools.translate import _
import re
import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from dateutil.relativedelta import relativedelta


class product_tag(osv.osv):
    _name = 'product.tag'
    _columns = {
        'name': fields.char('Name', size=32),
        'code': fields.char('Code', size=23),
    }

    _sql_constraints = [
        ('uniq_code', 'unique(code)', u'编码必须唯一'),
    ]


class product_attribute_value(osv.osv):
    _inherit = 'product.attribute.value'
    _columns = {
        'is_unconventional': fields.boolean(u'非常规'),
        'is_htg': fields.boolean(u'高tg'),
        'product_tags': fields.many2many('product.tag', 'value_tag_ref', 'tag_id', 'value_id', 'Tages'),
    }


class relation_product_group(osv.osv):
    _name = 'relation.product.group'
    _columns = {
        'name': fields.char(u'名称', required=True),
        'product_ids': fields.one2many('product.product', 'relation_gid', u'相关的物料', ),
    }

    def get_relation_product(self, cr, uid, product_ids, context=None):
        products = self.pool['product.product'].browse(cr, uid, product_ids, context=context)
        relation_ids = []
        realtion_tmpl_ids = []
        for p in products:
            if p.relation_gid:
                for rel_p in p.relation_gid.product_ids:
                    if rel_p.id not in relation_ids:
                        relation_ids.append(rel_p.id)
                    if rel_p.product_tmpl_id.id not in realtion_tmpl_ids:
                        realtion_tmpl_ids.append(rel_p.product_tmpl_id.id)

        return {'relation_product': relation_ids, 'relation_tmpl': realtion_tmpl_ids}


class product_category(osv.osv):
    _inherit = 'product.category'
    _order = 'complete_code'

    def _compute_level(self, cr, uid, ids, field_name, arg=None, context=None):
        res = {}
        for category in self.browse(cr, uid, ids, context=context):
            level = 0
            if category.parent_id:
                level = category.parent_id.level + 1
            res[category.id] = level
        return res

    def _compute_complete_code(self, cr, uid, ids, field_name, arg=None, context=None):
        res = {}
        for category in self.browse(cr, uid, ids, context=context):
            code = category.code or None
            parent_complete_code = category.parent_id and category.parent_id.complete_code
            if parent_complete_code:
                code = '%s%s' % (parent_complete_code, code)
            res[category.id] = code
        return res

    _columns = {
        'level': fields.function(_compute_level, string=u'分类深度', store=True, type='integer'),
        'code': fields.char(u'编码', size=8),
        'complete_code': fields.function(_compute_complete_code, string=u'完整编码', type='char', size=40, store=True,
                                         readonly=True),
    }

    _sql_constraints = [
        ('uniq_complete_code', 'unique(complete_code)', u'分类的完全编码必须唯一'),
    ]

    def recalculate_level(self, cr, uid, context=None):
        if context is None:
            context = {}
        ids = self.search(cr, uid, [], order='id', context=context)
        for categ_id in ids:
            category = self.browse(cr, uid, categ_id, context=context)
            level = 0
            if category.parent_id:
                level = category.parent_id.level + 1
            self.write(cr, uid, categ_id, {'level': level}, context=context)
        return True


class product_template(osv.osv):
    _inherit = 'product.template'
    _columns = {
        'variants': fields.char(u'规格参数', size=32),
        'type': fields.selection([('product', 'Stockable Product'), ('consu', 'Consumable'), ('service', 'Service')],
                                 'Product Type', required=True,
                                 help="Consumable: Will not imply stock management for this product. \nStockable product: Will imply stock management for this product."),
    }

    _defaults = {
        'type': 'product',
    }

    def name_get(self, cr, user, ids, context=None):
        result = []
        for pt in self.browse(cr, SUPERUSER_ID, ids, context=context):
            name = pt.name
            if pt.default_code:
                name = '[%s]' % pt.default_code + name
            if pt.variants:
                name += pt.variants
            result.append((pt.id, name))
        return result


Product_ABC = [('a', 'A'), ('b', 'B'), ('c', 'C')]
Product_Approve_State = [('draft', u'草稿'), ('w_technical', u'待工艺'), ('w_materia_control', u'待物控'),
                         ('w_quality', u'待品质'), ('w_general_manager', '待总经理'), ('done', u'完成')]


class product_product(osv.osv):
    _inherit = "product.product"

    def _get_procurement_qty(self, cr, uid, ids, field_name, arg=None, context=None):
        '''
        Get the total qty where procuremnt not pol.
        '''
        prc_obj = self.pool.get('procurement.order')
        uom_obj = self.pool.get('product.uom')

        res = {}
        for pid in ids:
            prc_ids = prc_obj.search(cr, uid, [('product_id', '=', pid), ('purchase_line_id', '=', False),
                                               ('state', '!=', 'draft')], context=context)
            sum = 0
            for prc in prc_obj.browse(cr, uid, prc_ids, context=context):
                base_uom_id = prc.product_id.uom_id.id
                if prc.product_uom.id != base_uom_id:
                    qty = uom_obj._compute_qty(cr, uid, prc.product_uom.id, prc.product_qty, base_uom_id, round=True,
                                               rounding_method='UP')
                else:
                    qty = prc.product_qty
                sum += qty
            res[pid] = sum
        return res

    def _strict_department(self, cr, uid, ids, field_name, arg=None, context=None):
        res = {}
        for p in self.browse(cr, uid, ids, context=context):
            res[p.id] = p.material_department_ids and True or False
        return res

    def _compute_area_sqm(self, cr, uid, ids, field_name, arg=None, context=None):
        res = {}
        uom_obj = self.pool['product.uom']
        meters_uom_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'product', 'product_uom_meter')[1]
        for p in self.browse(cr, uid, ids, context=context):
            res[p.id] = p.size_uom and (
                uom_obj._compute_qty(cr, uid, p.size_uom.id, p.length, meters_uom_id, round=True, rounding_method='UP')
                * uom_obj._compute_qty(cr, uid, p.size_uom.id, p.width, meters_uom_id, round=True, rounding_method='UP')
            ) or 0.0
        return res

    # ==========1216
    def _compute_purchase_info(self, cr, uid, ids, fieldname, arg, context=None):
        res = {}
        prl_obj = self.pool.get('purchase.order.line')

        for pid in ids:
            res[pid] = {
                'highest_price': False,
                'highest_date': False,
                'highest_qty': False,
                'highest_parnter': False,

                'bottom_price': False,
                'bottom_date': False,
                'bottom_qty': False,
                'bottom_parnter': False,

                'last_price': False,
                'last_date': False,
                'last_qty': False,
                'last_parnter': False,
            }

            order_0 = 'price_unit DESC'
            order_1 = 'price_unit ASC'
            order_2 = 'create_date DESC'
            args = [('product_id', '=', pid), ('state', 'in', ('confirmed', 'done'))]

            if prl_obj.search(cr, uid, args, offset=0, limit=1, order=order_0, context=context):
                highest_obj = prl_obj.browse(cr, uid, prl_obj.search(cr, uid, args, offset=0, limit=1, order=order_0, context=context))
                res[pid].update({
                    'highest_price': highest_obj.price_unit,
                    'highest_date': highest_obj.create_date,
                    'highest_qty': highest_obj.product_qty,
                    'highest_parnter': highest_obj.partner_id.name,
                })

            if prl_obj.search(cr, uid, args, offset=0, limit=1, order=order_1, context=context):
                bottom_obj = prl_obj.browse(cr, uid, prl_obj.search(cr, uid, args, offset=0, limit=1, order=order_1, context=context))
                res[pid].update({
                    'bottom_price': bottom_obj.price_unit,
                    'bottom_date': bottom_obj.create_date,
                    'bottom_qty': bottom_obj.product_qty,
                    'bottom_parnter': bottom_obj.partner_id.name,
                })

            if prl_obj.search(cr, uid, args, offset=0, limit=1, order=order_2, context=context):
                last_obj = prl_obj.browse(cr, uid, prl_obj.search(cr, uid, args, offset=0, limit=1, order=order_2, context=context))
                res[pid].update({
                    'last_price': last_obj.price_unit,
                    'last_date': last_obj.create_date,
                    'last_qty': last_obj.product_qty,
                    'last_parnter': last_obj.partner_id.name,
                })

        return res

    def _computer_purchase_average(self, cr, uid, ids, fieldname, arg, context=None):
        res = {}
        prl_obj = self.pool.get('purchase.order.line')

        this_month1st = datetime.datetime.now().strftime('%Y-%m-01 00:00:00')
        last_year = (datetime.datetime.today() + relativedelta(years=-1)).strftime('%Y-%m-01 00:00:00')
        last_3months = (datetime.datetime.today() + relativedelta(months=-3)).strftime('%Y-%m-01 00:00:00')
        last_month = (datetime.datetime.today() + relativedelta(months=-1)).strftime('%Y-%m-01 00:00:00')

        for pid in ids:
            res[pid] = {
                'last12months_average': False,
                'last3months_average': False,
                'lastmonth_average': False,
            }

            dm = [('product_id', '=', pid), ('state', 'in', ('confirmed', 'done'))]
            dm_year = dm + [('create_date', '>=', last_year),('create_date', '<', this_month1st),]
            dm_3months = dm + [('create_date', '>=', last_3months),('create_date', '<', this_month1st),]
            dm_1month = dm + [('create_date', '>=', last_month),('create_date', '<', this_month1st),]

            lastyesr_sum = 0.0
            prl_ids = prl_obj.search(cr, uid, dm_year, context=context)
            for prl in prl_obj.browse(cr, uid, prl_ids):
                lastyesr_sum += prl.product_qty

            last3months_sum = 0.0
            prl_ids = prl_obj.search(cr, uid, dm_3months, context=context)
            for prl in prl_obj.browse(cr, uid, prl_ids):
                last3months_sum += prl.product_qty

            lastmonth_sum = 0.0
            prl_ids = prl_obj.search(cr, uid, dm_1month, context=context)
            for prl in prl_obj.browse(cr, uid, prl_ids):
                lastmonth_sum += prl.product_qty

            res[pid].update({
                'last12months_average': lastyesr_sum / 12,
                'last3months_average': last3months_sum / 3,
                'lastmonth_average': lastmonth_sum,
            })

        return res

    def _supplier_amount(self, cr, uid, ids, fieldname, args, context=None):
        res = {}
        for p in self.browse(cr, uid, ids, context=context):
            res[p.id] = len(p.seller_ids)
        return res

    _columns = {
        'material_state': fields.selection(Product_Approve_State, 'State', ),
        'relation_gid': fields.many2one('relation.product.group', u'产品关联组'),
        'location_id': fields.many2one('stock.location', string=u'库位', ),
        'attribute_value_ids': fields.many2many('product.attribute.value', id1='prod_id', id2='att_id',
                                                string='Attributes', readonly=False, ondelete='restrict'),
        'dongshuo_id': fields.integer(u'东烁ID'),
        'dongshuo_code': fields.char(u'东烁编码', size=32),
        'default_code': fields.char(u'产品编码', select=True, required=False),
        'purchase_period': fields.integer(u'采购周期：天'),
        # 'variants': fields.char(u'规格参数', size=32),
        'length': fields.float(u'长', digits=(2, 4)),
        'width': fields.float(u'宽'),
        'height': fields.float(u'高/厚度'),

        'size_uom': fields.many2one('product.uom', u'尺寸单位', domain=[('category_id', '=', 4)]),
        'area_sqm': fields.function(_compute_area_sqm, type='float', string=u'平方米', help=u"单位产品的面积平米",
                                    store={'product.product': (
                                        lambda s, c, u, i, x: i, ['length', 'width', 'size_uom'], 10)}),
        # 'unit_name': fields.char(u'库存单位', size=12),
        # 'thickness':fields.float(u'厚度'),
        'material_department_ids': fields.many2many('hr.department', 'material_department', 'product_id',
                                                    'department_id', u'授权部门'),
        'abc': fields.selection(Product_ABC, 'ABC'),
        'strict_department': fields.function(_strict_department, type="boolean", string=u'需授权使用', readonly=True,
                                             store=True, ),
        'unconventional': fields.boolean(u'非常规'),
        'dangerous': fields.boolean(u'危险品'),
        'strict_supplier': fields.boolean(u'需评审供应商'),
        'need_iqc': fields.boolean(u'来料是否需要质检'),
        "need_trial": fields.boolean(u'需要试用'),
        # product category attributes
        # 板料就是TG值、板料、铜厚、尺寸钻头就是直径
        # 'board_thick': fields.char(u'板厚mm',size=32), use field height
        'cu_thick': fields.char(u'铜厚'),
        # 'cu_thick_a': fields.float(u'A面铜厚oz'),
        # 'cu_thick_b': fields.float(u'B面铜厚oz'),
        'tg_value': fields.integer(u'TG值'),
        # 'halogen_free': fields.boolean(u'无卤素'), use  product_tag replace
        # 钻头类
        'diameter': fields.float(u'直径'),
        # 油墨类
        'colour': fields.char(u'颜色', size=24),
        # 已经申购，未采购数量
        'procurement_qty': fields.function(_get_procurement_qty, type="float", string=u"需求数量"),
        'active': fields.boolean('Active'),
        'category_code_id': fields.many2one('product.category.code', u'物料编码规则', ),
        'is_precious': fields.boolean(u'贵重'),
        'is_poison': fields.boolean(u'剧毒'),

        # ==========1216
        'highest_price': fields.function(_compute_purchase_info, string=u'历史最高价', type='float', multi='_purchase_info',
                                         readonly=True),
        'highest_date': fields.function(_compute_purchase_info, string=u'采购日期', type='date', multi='_purchase_info',
                                        readonly=True),
        'highest_qty': fields.function(_compute_purchase_info, string=u'采购数量', type='float', multi='_purchase_info',
                                       readonly=True),
        'highest_parnter': fields.function(_compute_purchase_info, string=u'供应商', type='char', multi='_purchase_info',
                                           readonly=True),
        'bottom_price': fields.function(_compute_purchase_info, string=u'历史最低价', type='float', multi='_purchase_info',
                                        readonly=True),
        'bottom_date': fields.function(_compute_purchase_info, string=u'采购日期', type='date', multi='_purchase_info',
                                       readonly=True),
        'bottom_qty': fields.function(_compute_purchase_info, string=u'采购数量', type='float', multi='_purchase_info',
                                      readonly=True),
        'bottom_parnter': fields.function(_compute_purchase_info, string=u'供应商', type='char', multi='_purchase_info',
                                          readonly=True),
        'last_price': fields.function(_compute_purchase_info, string=u'上次采购价', type='float', multi='_purchase_info',
                                      readonly=True),
        'last_date': fields.function(_compute_purchase_info, string=u'采购日期', type='date', multi='_purchase_info',
                                     readonly=True),
        'last_qty': fields.function(_compute_purchase_info, string=u'采购数量', type='float', multi='_purchase_info',
                                    readonly=True),
        'last_parnter': fields.function(_compute_purchase_info, string=u'供应商', type='char', multi='_purchase_info',
                                        readonly=True),
        'last12months_average': fields.function(_computer_purchase_average, string=u'过去12个月平均数量', type='float',
                                                multi='_computer_purchase_average',readonly=True),
        'last3months_average': fields.function(_computer_purchase_average, string=u'过去3个月平均数量', type='float',
                                               multi='_computer_purchase_average', readonly=True),
        'lastmonth_average': fields.function(_computer_purchase_average, string=u'上月采购数量', type='float',
                                             multi='_computer_purchase_average', readonly=True),

        'supplier_amount': fields.function(_supplier_amount, string=u'供应商数', type='integer', readonly=True),

    }

    _sql_constraints = [
        ('uniq_default_code', 'unique(default_code)', u'物料编码不能重复'),
    ]

    _defaults = {
        'size_uom': lambda self, cr, uid, ctx: self._default_size_uom(cr, uid, context=ctx),
        'active': False,
        'material_state': 'draft',
    }

    def copy(self, cr, uid, id, defaults, context=None):
        raise Warning(u'不允许使用复制')
        return False

    def confirm(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'material_state': 'w_technical'}, context=context)

    def technical_approve(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'material_state': 'w_materia_control'}, context=context)

    def materia_control_approve(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'material_state': 'w_quality'}, context=context)

    def quality_approve(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'material_state': 'w_general_manager'}, context=context)

    def general_manager(self, cr, uid, ids, context=None):
        self.make_default_code(cr, uid, ids, context=context)
        return self.write(cr, uid, ids, {'material_state': 'done', 'active': True}, context=context)

    def _default_size_uom(self, cr, uid, context=None):
        return self.pool.get('ir.model.data').get_object_reference(cr, uid, 'product', 'product_uom_meter')[1]

    def make_default_code(self, cr, uid, ids, context=None):
        product = self.browse(cr, uid, ids[0], context=context)
        if not product.default_code:
            default_code = product.category_code_id.complete_code
            if not default_code:
                raise Warning(u'没有编码，请确认分类是否正确')
            self.write(cr, uid, product.id, {'default_code': default_code})
            return True

    def name_get(self, cr, user, ids, context=None):
        """
        product name get, add variants
        """
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        if not len(ids):
            return []

        def _name_get(d):
            name = d.get('name', '')
            code = context.get('display_default_code', True) and d.get('default_code', False) or False
            variants = d.get('variants', '')
            if code:
                name = '[%s] %s' % (code, name)
            if variants:
                name = '%s(%s)' % (name, variants)
            return (d['id'], name)

        partner_id = context.get('partner_id', False)
        if partner_id:
            partner_ids = [partner_id, self.pool['res.partner'].browse(cr, user, partner_id,
                                                                       context=context).commercial_partner_id.id]
        else:
            partner_ids = []

        # all user don't have access to seller and partner
        # check access and use superuser
        self.check_access_rights(cr, user, "read")
        self.check_access_rule(cr, user, ids, "read", context=context)

        result = []
        for product in self.browse(cr, SUPERUSER_ID, ids, context=context):
            variant = ", ".join([v.name for v in product.attribute_value_ids])
            name = variant and "%s (%s)" % (product.name, variant) or product.name
            sellers = []
            if partner_ids:
                sellers = filter(lambda x: x.name.id in partner_ids, product.seller_ids)
            if sellers:
                for s in sellers:
                    seller_variant = s.product_name and (
                        variant and "%s (%s)" % (s.product_name, variant) or s.product_name
                    ) or False
                    mydict = {
                        'id': product.id,
                        'name': seller_variant or name,
                        'default_code': s.product_code or product.default_code,
                        'variants': product.variants,
                    }
                    result.append(_name_get(mydict))
            else:
                mydict = {
                    'id': product.id,
                    'name': name,
                    'default_code': product.default_code,
                    'variants': product.variants,
                }
                result.append(_name_get(mydict))
        return result

    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        """
        product can be search by variants
        """
        if not args:
            args = []
        if name:
            positive_operators = ['=', 'ilike', '=ilike', 'like', '=like']
            ids = []
            if operator in positive_operators:
                ids = self.search(cr, user, [('default_code', '=', name)] + args, limit=limit, context=context)
                if not ids:
                    ids = self.search(cr, user, [('ean13', '=', name)] + args, limit=limit, context=context)
            if not ids and operator not in expression.NEGATIVE_TERM_OPERATORS:
                # Do not merge the 2 next lines into one single search, SQL search performance would be abysmal
                # on a database with thousands of matching products, due to the huge merge+unique needed for the
                # OR operator (and given the fact that the 'name' lookup results come from the ir.translation table
                # Performing a quick memory merge of ids in Python will give much better performance
                ids = self.search(cr, user,
                                  args + ['|', ('default_code', operator, name), ('variants', operator, name)],
                                  limit=limit,
                                  context=context)
                if not limit or len(ids) < limit:
                    # we may underrun the limit because of dupes in the results, that's fine
                    limit2 = (limit - len(ids)) if limit else False
                    ids += self.search(cr, user, args + [('name', operator, name), ('id', 'not in', ids)], limit=limit2,
                                       context=context)
            elif not ids and operator in expression.NEGATIVE_TERM_OPERATORS:
                ids = self.search(cr, user, args + ['&', ('default_code', operator, name), ('name', operator, name)],
                                  limit=limit,
                                  context=context)
            if not ids and operator in positive_operators:
                ptrn = re.compile('(\[(.*?)\])')
                res = ptrn.search(name)
                if res:
                    ids = self.search(cr, user, [('default_code', '=', res.group(2))] + args, limit=limit,
                                      context=context)
        else:
            ids = self.search(cr, user, args, limit=limit, context=context)
        result = self.name_get(cr, user, ids, context=context)
        return result

    def add_to_preparation_order(self, cr, uid, ids, context=None):

        procument_obj = self.pool['procurement.order']
        preparation_id = context.get('active_id')
        product_id = ids[0]

        pp_obj = self.browse(cr, uid, ids[0])
        date_planned = (datetime.datetime.now() + datetime.timedelta(days=pp_obj.purchase_period)).strftime(DTF)

        if context.get('active_model') == 'preparation.order' and preparation_id:
            value = procument_obj.onchange_qty(cr, uid, ids, product_id, 0, 0, date_planned, fname='product_id',
                                               context=context)
            # value = procument_obj.onchange_qty(cr, uid, ids, product_id, 0, 0, fname='product_id', context=context)
            data = value['value']
            data.update({'product_id': product_id, 'preparation_id': preparation_id})
            procument_obj.create(cr, uid, data, context=context)

        return True

    def add_to_stock_picking(self, cr, uid, ids, context=None):
        model_name = 'stock.picking'
        picking_obj = self.pool.get(model_name)
        active_id = context.get('active_id')
        move_obj = self.pool.get('stock.move')
        pdt_id = ids[0]
        if context.get('active_model') == model_name and active_id:
            pick = picking_obj.browse(cr, uid, active_id, context=context)
            type_id = pick.picking_type_id.id
            loc_id = pick.picking_type_id.default_location_src_id.id
            loc_dest_id = pick.picking_type_id.default_location_dest_id.id
            ctx = context.copy()
            ctx.update({'use_po_unit': 1})
            res = move_obj.onchange_product_id(cr, uid, [], prod_id=pdt_id, loc_id=loc_id, loc_dest_id=loc_dest_id,
                                               partner_id=False)
            line_data = res['value']
            line_data.update({'product_id': pdt_id})
            picking_obj.write(cr, uid, [pick.id, ], {
                'move_lines': [(0, 0, line_data)],
            }, context=context)
        return True

##### vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
