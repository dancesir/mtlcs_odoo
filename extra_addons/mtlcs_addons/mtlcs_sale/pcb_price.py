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

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp.exceptions import Warning
from pcb_fee_arg import PCB_Fee_Arg_Type, Base_Price_Type

Fee_Digits = [5, 5]
Price_State = [('draft', u'草稿'), ('w_director', u'待主管'), ('w_manager', u'待经理'), ('w_general_manager', u'待总经办',),
               ('done', u'完成'), ('cancel', u'作废'), ('tochange', u'待更改')]


class pcb_price(osv.osv):
    _name = 'pcb.price'
    _inherits = {'receive.order': 'receive_id'}

    def _compute_qty_unit(self, cr, uid, ids, fields, arg=None, context=None):
            res = {}
            for pprice in self.browse(cr,uid,ids,context=context):
                res[pprice.id] = pprice.qty  * pprice.info_id.panel_count
            return res

    def _compute_price_unit(self, cr, uid, ids, fields, arg=None, context=None):
            res = {}
            for pprice in self.browse(cr,uid,ids,context=context):
                res[pprice.id] = pprice.price_pcs / pprice.info_id.panel_count
            return res

    def _compute_area(self, cr, uid, ids, fields, arg=None, context=None):
        res = {}
        for me in self.browse(cr, uid, ids, context=None):
            res[me.id] = {}
            l = me.info_id and me.info_id.length or 0.0
            w = me.info_id and me.info_id.width or 0.0
            qty = me.qty or 0.0
            res[me.id]['area'] = l * w * qty
            res[me.id]['m2_area'] = l * w * qty / 10000.0
        return res

    def _compute_btype(self, cr, uid, ids, fields, arg=None, context=None):
        def get_btype(pprice):
            info = pprice.info_id
            for s in info.special_tech_ids:
                if s.code == 'hdi': return 'hdi'
                if s.code == 'rigid_flexible': return 'flex'
            # judage by material
            for m in info.board_format_ids:
                if 'ptfe' in m.code.lower(): return 'ptfe'
                if 'rogers' in m.code.lower(): return 'rogers'
                if 'al' in m.code.lower(): return 'al_base'
                if 'cu' in m.code.lower(): return 'cu_base'
            # if not any btype, return normal
            return 'normal'

        res = {}
        for pprice in self.browse(cr, uid, ids, context=None):
            res[pprice.id] = get_btype(pprice)
        return res

    _columns = {
        'name': fields.char(u'报价单号', size=32),
        'state': fields.selection(Price_State, u'状态'),
        'receive_id': fields.many2one('receive.order', u'接单', required=True, ondelete="restrict"),
        # product_id = receive_id.pcb_info_id.product_id
        'product_id': fields.related('info_id', 'product_id', type="many2one", relation="product.product",
                                     string=u"档案号"),
        'sol_id': fields.many2one('sale.order.line', u'订单明细'),
        'sol_ids': fields.one2many('sale.order.line', 'price_id', u'订单明细'),
        'so_id': fields.related('sol_id', 'order_id', type="many2one", relation="sale.order", string=u"订单",
                                readonly=True),

        # 'qty': fields.integer(u'数量'),#ref from receive_id
        'area': fields.function(_compute_area, type="float", string=u'面积:CM2', multi='_compute_area'),
        'm2_area': fields.function(_compute_area, type="float", digits=(2, 4), string=u'面积:M2', multi='_compute_area'),

        'delivery_date': fields.datetime(u'交货日期'),
        'standard_period': fields.integer(u'标准交货周期'),
        'min_period': fields.integer(u'最短交货周期'),

        'create_uid': fields.many2one('res.users', u'创建人'),
        'create_date': fields.datetime(u'创建日期'),
        'detection_pass': fields.boolean(u'非常规无/通过'),
        'detection_id': fields.many2one('tech.standard.detection', u'非常规评审'),
        'company_id': fields.many2one('res.company', u'投产工厂'),
        'material_price': fields.float(u'材料价格'),
        'jig_price': fields.float(u'模具成本'),
        'suite_qty': fields.float(u'工程套版数量'),
        'btype': fields.function(_compute_btype, type="selection", selection=Base_Price_Type, string=u'基价类型'),
        # logs
        'log_ids': fields.one2many('price.log', 'price_id', u'计算信息记录'),

        # 标准费用
        'fee1_base': fields.float(u'基板费', digits=Fee_Digits, readonly=False),
        'fee1_board_thick': fields.float(u'板厚', digits=Fee_Digits, readonly=False),
        'fee1_cu_thick': fields.float(u'铜厚', digits=Fee_Digits, readonly=False),
        'fee1_special_tech': fields.float(u'特殊流程', digits=Fee_Digits, readonly=False),
        'fee1_blind': fields.float(u'盲孔费', digits=Fee_Digits, readonly=False),
        'fee1_surface': fields.float(u'表面处理', digits=Fee_Digits, readonly=False),
        'fee1_min_hole': fields.float(u'最小孔径', digits=Fee_Digits, readonly=False),
        'fee1_hole_density': fields.float(u'孔密度费', digits=Fee_Digits, readonly=False),
        'fee1_line_space': fields.float(u'线间距费', digits=Fee_Digits, readonly=False),
        'fee1_hole_line': fields.float(u'孔到线费', digits=Fee_Digits, readonly=False),
        'fee1_routing': fields.float(u'锣程费', digits=Fee_Digits, readonly=False),
        'fee1_usage_rate': fields.float(u'材料利用率费', digits=Fee_Digits, readonly=False),
        'fee1_core': fields.float(u'光板费', digits=Fee_Digits, readonly=False),
        'fee1_pp': fields.float(u'PP费', digits=Fee_Digits, readonly=False),
        'fee1_test': fields.float(u'测试费', digits=Fee_Digits, readonly=False),
        'fee1_finger': fields.float(u'金手指费', digits=Fee_Digits, readonly=False),
        'fee1_finger2': fields.float(u'超常规金手指费', digits=Fee_Digits, readonly=False),
        'fee1_eng': fields.float(u'工程费', digits=Fee_Digits, readonly=False),
        'fee1_plot': fields.float(u'菲林费', digits=Fee_Digits, readonly=False),
        'fee1_special_test': fields.float(u'专测费', digits=Fee_Digits, readonly=False),
        'fee1_common_test': fields.float(u'通用费', digits=Fee_Digits, readonly=False),
        'fee1_eng_pack': fields.float(u'工程打包费', digits=Fee_Digits, readonly=False),
        'fee1_jig': fields.float(u'模具', digits=Fee_Digits, readonly=False),
        'fee1_urgent': fields.float(u'加急费', digits=Fee_Digits, readonly=False),
        'fee1_change': fields.float(u'变更费', digits=Fee_Digits, readonly=False),
        'fee1_other': fields.float(u'其他费', digits=Fee_Digits, readonly=False),
        'fee1_sqcm': fields.float(u'平方厘米价', digits=(12, 5), readonly=False),
        'fee1_pcs': fields.float(u'pcs单价', igits_compute=dp.get_precision('Account'), readonly=False),
        'fee1_all': fields.float(u'费用汇总', digits=Fee_Digits, readonly=False),
        # 客户专用价格
        'fee2_base': fields.float(u'基板费', digits=Fee_Digits, readonly=False),
        'fee2_board_thick': fields.float(u'板厚', digits=Fee_Digits, readonly=False),
        'fee2_cu_thick': fields.float(u'铜厚', digits=Fee_Digits, readonly=False),
        'fee2_special_tech': fields.float(u'特殊流程', digits=Fee_Digits, readonly=False),
        'fee2_surface': fields.float(u'表面处理', digits=Fee_Digits, readonly=False),
        'fee2_blind': fields.float(u'盲孔费', digits=Fee_Digits, readonly=False),
        'fee2_min_hole': fields.float(u'最小孔径', digits=Fee_Digits, readonly=False),
        'fee2_hole_density': fields.float(u'孔密度费', digits=Fee_Digits, readonly=False),
        'fee2_line_space': fields.float(u'线间距费', digits=Fee_Digits, readonly=False),
        'fee2_hole_line': fields.float(u'孔到线费', digits=Fee_Digits, readonly=False),
        'fee2_routing': fields.float(u'锣程费', digits=Fee_Digits, readonly=False),
        'fee2_usage_rate': fields.float(u'材料利用率费', digits=Fee_Digits, readonly=False),
        'fee2_core': fields.float(u'光板费', digits=Fee_Digits, readonly=False),
        'fee2_pp': fields.float(u'PP费', digits=Fee_Digits, readonly=False),
        'fee2_test': fields.float(u'测试费', digits=Fee_Digits, readonly=False),
        'fee2_finger': fields.float(u'金手指费', digits=Fee_Digits, readonly=False),
        'fee2_finger2': fields.float(u'超常规金手指费', digits=Fee_Digits, readonly=False),
        'fee2_eng': fields.float(u'工程费', digits=Fee_Digits, readonly=False),
        'fee2_plot': fields.float(u'菲林费', digits=Fee_Digits, readonly=False),
        'fee2_special_test': fields.float(u'专测费', digits=Fee_Digits, readonly=False),
        'fee2_common_test': fields.float(u'通用费', digits=Fee_Digits, readonly=False),
        'fee2_eng_pack': fields.float(u'工程打包费', digits=Fee_Digits, readonly=False),
        'fee2_jig': fields.float(u'模具', digits=Fee_Digits, readonly=False),
        'fee2_urgent': fields.float(u'加急费', digits=Fee_Digits, readonly=False),
        'fee2_change': fields.float(u'变更费', digits=Fee_Digits, readonly=False),
        'fee2_other': fields.float(u'其他费', digits=Fee_Digits, readonly=False),
        'fee2_sqcm': fields.float(u'平方厘米价', digits=(12, 5), readonly=False),
        'fee2_pcs': fields.float(u'pcs单价', igits_compute=dp.get_precision('Account'), readonly=False),
        'fee2_all': fields.float(u'费用汇总', digits=Fee_Digits, readonly=False),
        # 实际价格
        'fee_base': fields.float(u'基板费', digits=Fee_Digits, readonly=False),
        'fee_board_thick': fields.float(u'板厚', digits=Fee_Digits, readonly=False),
        'fee_cu_thick': fields.float(u'铜厚', digits=Fee_Digits, readonly=False),
        'fee_special_tech': fields.float(u'特殊流程', digits=Fee_Digits, readonly=False),
        'fee_surface': fields.float(u'表面处理', digits=Fee_Digits, readonly=False),
        'fee_blind': fields.float(u'盲孔费', digits=Fee_Digits, readonly=False),
        'fee_min_hole': fields.float(u'最小孔径', digits=Fee_Digits, readonly=False),
        'fee_hole_density': fields.float(u'孔密度费', digits=Fee_Digits, readonly=False),
        'fee_line_space': fields.float(u'线间距费', digits=Fee_Digits, readonly=False),
        'fee_hole_line': fields.float(u'孔到线费', digits=Fee_Digits, readonly=False),
        'fee_routing': fields.float(u'锣程费', digits=Fee_Digits, readonly=False),
        'fee_usage_rate': fields.float(u'材料利用率费', digits=Fee_Digits, readonly=False),
        'fee_core': fields.float(u'光板费', digits=Fee_Digits, readonly=False),
        'fee_pp': fields.float(u'PP费', digits=Fee_Digits, readonly=False),
        'fee_test': fields.float(u'测试费', digits=Fee_Digits, readonly=False),
        'fee_finger': fields.float(u'金手指费', digits=Fee_Digits, readonly=False),
        'fee_finger2': fields.float(u'超常规金手指费', digits=Fee_Digits, readonly=False),
        'fee_eng': fields.float(u'工程费', digits=Fee_Digits, readonly=False),
        'fee_plot': fields.float(u'菲林费', digits=Fee_Digits, readonly=False),
        'fee_special_test': fields.float(u'专测费', digits=Fee_Digits, readonly=False),
        'fee_common_test': fields.float(u'通用费', digits=Fee_Digits, readonly=False),
        'fee_eng_pack': fields.float(u'工程打包费', digits=Fee_Digits, readonly=False),
        'fee_jig': fields.float(u'模具', digits=Fee_Digits, readonly=False),
        'fee_urgent': fields.float(u'加急费', digits=Fee_Digits, readonly=False),
        'fee_change': fields.float(u'变更费', digits=Fee_Digits, readonly=False),
        'fee_other': fields.float(u'其他费', digits=Fee_Digits, readonly=False),
        'fee_sqcm': fields.float(u'平方厘米价', digits=(12, 5), readonly=False),
        'fee_pcs': fields.float(u'pcs单价', igits_compute=dp.get_precision('Account'), readonly=False),
        'fee_all': fields.float(u'费用汇总', digits=Fee_Digits, readonly=False),
        #########
        'once_fee': fields.float(u'一次性费用', digits=Fee_Digits, readonly=False),
        ########

        'price_unit': fields.function(_compute_price_unit,type="float", digits=Fee_Digits, string=u'Unit单价'),
        'qty_unit': fields.function(_compute_qty_unit, type="integer", string=u'Unit数量'),
        'price_pcs': fields.float(u'PCS单价', digits=Fee_Digits, readonly=False),
        'amount_plot_': fields.float(u'菲林费', digits=Fee_Digits, readonly=False),
        'amount_test': fields.float(u'测试费', digits=Fee_Digits, readonly=False),
        'amount_eng': fields.float(u'工程费', digits=Fee_Digits, readonly=False),
        'amount_other': fields.float(u'其他费用', digits=Fee_Digits, readonly=False),
        'amount': fields.float(u'标准总额', digits=Fee_Digits, readonly=False),
        'amount_urgent': fields.float(u'加急费', digits=Fee_Digits, readonly=False),
        'discount': fields.float(u'一次性费用折扣', digits=Fee_Digits),
        'surchage': fields.float(u'一次性费用优惠', digits=Fee_Digits),
        'amount_once_fee': fields.float(u'最终合同一次性费用', digits=Fee_Digits),
        'final_amount': fields.float(u'最终合同总额', digits=Fee_Digits, readonly=False),

        # ('ready',  u'准备费',),
        # ('film',  u'菲林费'),
        # ('test',  u'测试费'),
        # ('material',  u'材料费'),
        # ('jig',  u'磨具费'),
        # ('change',  u'更改费'),
        # ('urgent',  u'加急费'),
        # ('finger',  u'金手指费'),
        # ('sqcm',  u'平方厘米价'),
        # ('other',  u'其他费'),

    }

    _defaults = {
        'name': lambda self, cr, uid, ctx: self._default_name(cr, uid, context=ctx),
        'state': 'draft',
    }

    def _default_name(self, cr, uid, context=None):
        return self.pool.get('ir.sequence').get(cr, uid, 'pcb.price')

    # wkf
    def confirm(self, cr, uid, ids, context=None):
        pprice = self.browse(cr, uid, ids[0], context=context)
        if not pprice.detection_pass:
            raise Warning(u'必须先做非常规检测')
        data = {
            'state': 'w_director',
            'btype': self.get_btype(cr, uid, pprice),
        }
        self.write(cr, uid, pprice.id, data, context=context)
        return True

    def get_btype(self, cr, uid, pprice, context=None):
        info = pprice.info_id
        # judage by special tech
        for s in info.special_tech_ids:
            if s.code == 'hdi': return 'hdi'
            if s.code == 'rigid_flexible': return 'flex'
        # judage by material
        for m in info.board_format_ids:
            if 'ptfe' in m.code.lower(): return 'ptfe'
            if 'rogers' in m.code.lower(): return 'rogers'
            if 'al' in m.code.lower(): return 'al_base'
            if 'cu' in m.code.lower(): return 'cu_base'
        # if not any btype, return normal
        return 'normal'

    def director_approve(self, cr, uid, ids, context=None):
        for p in self.browse(cr, uid, ids, context=context):
            self.write(cr, uid, p.id, {'state': 'w_manager'}, context=context)
        return True

    def manager_approve(self, cr, uid, ids, context=None):
        for p in self.browse(cr, uid, ids, context=context):
            self.write(cr, uid, p.id, {'state': 'w_general_manager'}, context=context)
        return True

    def general_manager_approve(self, cr, uid, ids, context=None):
        p = self.browse(cr, uid, ids[0], context=context)
        self.write(cr, uid, ids, {'state': 'done'}, context=context)
        return True

    def to_tochang(self, cr, uid, ids, context=None):
        for p in self.browse(cr, uid, ids, context=context):
            self.write(cr, uid, p.id, {'state': 'draft'}, context=context)
        return True

    def to_cancel(self, cr, uid, ids, context=None):
        for p in self.browse(cr, uid, ids, context=context):
            self.write(cr, uid, p.id, {'state': 'cancel'}, context=context)
        return True

    def reset_draft(self, cr, uid, ids, context=None):
        for p in self.browse(cr, uid, ids, context=context):
            self.write(cr, uid, p.id, {'state': 'draft'}, context=context)
        return True

    ##wkf end
    def _make_sale_order_line(self, cr, uid, pprices, so_id, context=None):
        sol_obj = self.pool.get('sale.order.line')

        once_fee_pdt_id = self.pool['ir.model.data'].get_object_reference(cr, uid, 'mtlcs_sale', 'pcb_fee_once')[1]
        once_fee_pdt = self.pool['product.product'].browse(cr, uid, once_fee_pdt_id, context=context)

        line_ids = []
        for pprice in pprices:
            sol_id = sol_obj.create(cr, uid, {
                'order_id': so_id,
                'price_id': pprice.id,
                'product_id': pprice.product_id.id,
                'product_uom_qty': pprice.qty_unit,
                'price_unit': pprice.price_unit,
                'product_uom': pprice.product_id.uom_id.id,
            })
            self.write(cr, uid, pprice.id, {'sol_id': sol_id}, context=context)
            line_ids.append(sol_id)

            # add once_fee_line
            if pprice.once_fee:
                fee_sol_id = sol_obj.create(cr, uid, {
                    'order_id': so_id,
                    'price_id': pprice.id,
                    'name': u'一次性费用 %s' % pprice.name,
                    'product_id': once_fee_pdt_id,
                    'product_uom_qty': 1,
                    'product_uom': once_fee_pdt.uom_id.id,
                    'price_unit': pprice.amount_once_fee,
                })
                line_ids.append(fee_sol_id)
        return line_ids

    def _prepare_sale_order(self, cr, uid, prices, context=None):
        return {
            'partner_id': prices[0].partner_id.id,
        }

    def create_sale_order(self, cr, uid, ids, context=None, sale_id=None):
        so_obj = self.pool.get('sale.order')

        def _check(cr, uid, pprices, context=None, sale_id=None):
            partner = so_obj.browse(cr, uid, sale_id).partner_id or pprices[0].partner_id
            for pprice in pprices:
                if pprice.state != 'done':
                    raise Warning(u'报价单为完成状态才能制作合同')
                if pprice.sol_id:
                    raise Warning(u'订单已经存在')
                if pprice.partner_id != partner:
                    raise Warning(u'必须是相同客户')
                if not pprice.product_id:
                    raise Warning(u'没有档案号')
            return True

        pprices = self.browse(cr, uid, ids, context=None)
        _check(cr, uid, pprices)

        for pprice in pprices:
            if not sale_id:
                so_data = self._prepare_sale_order(cr, uid, pprice, context=context)
                sale_id = so_obj.create(cr, uid, so_data, context=context)
            self._make_sale_order_line(cr, uid, pprice, sale_id, context=context)

        return sale_id

    def make_sale_order(self, cr, uid, ids, context=None, sale_id=None):
        sale_id = self.create_sale_order(cr, uid, ids, context=context, sale_id=sale_id)
        return {
            'type': 'ir.actions.act_window',
            'name': u'订单',
            'view_type': 'form',
            "view_mode": 'form',
            'res_model': 'sale.order',
            'res_id': sale_id,
        }

    def check_unconventional(self, cr, uid, ids, context=None):
        detection_obj = self.pool.get('tech.standard.detection')
        pprice = self.browse(cr, uid, ids[0], context=context)
        info = pprice.info_id
        if not pprice.company_id:
            raise Warning(u'非常规检测必须选择一个投产工厂')

        if pprice.detection_id:
            raise Warning(u'非常规已创建')

        detection_data = self.prepare_detection_data(cr, uid, pprice, context=context)
        if detection_data:
            detection_id = detection_obj.create(cr, uid, detection_data)
            self.write(cr, uid, pprice.id, {'detection_id': detection_id})
        else:
            self.write(cr, uid, pprice.id, {'detection_pass': True})
        return True

    def prepare_detection_data(self, cr, uid, pprice, context=None):
        lines_tech = self._prepare_unconventional_tech(cr, uid, pprice, context=context)
        lines_delivery = self._prepare_unconventional_delivery_period(cr, uid, pprice, context=context)
        lines = lines_tech + lines_delivery
        res = False
        if lines:
            res = {
                'pprice_id': pprice.id,
                'info_id': pprice.info_id.id,
                'line_ids': [(0, 0, {'name': n}) for n in lines],
                'company_id': pprice.company_id.id,
                'is_tech': bool(lines_tech),
                'is_delivery_time': bool(lines_delivery),
            }
        return res

    def _prepare_unconventional_tech(self, cr, uid, pprice, context=None):
        us_obj = self.pool['unconventional.standard']
        return us_obj.check_unconventional(cr, uid, pprice, context=context)

    def _prepare_unconventional_delivery_period(self, cr, uid, pprice, context=None):
        dts_obj = self.pool['delivery.time.standard']
        days = dts_obj.check_unconventional(cr, uid, pprice, context=context)
        self.write(cr, uid, pprice.id, {'standard_period': days[0], 'min_period': days[1]})
        res = []
        if pprice.delivery_period < days[1]:
            res.append(u'交货周期%s 小于 最小生产周期%s' % (pprice.delivery_period, days[1]))
        return res

    # fee compute
    def compute_fee(self, cr, uid, ids, context=None):
        pprice = self.browse(cr, uid, ids[0], context=context)
        self.write(cr, uid, pprice.id, {'log_ids': [(5, 0)]})
        fee_dic = self.pool.get('pcb.fee.arg').compute_fee(cr, uid, pprice, context=context)
        self.write(cr, uid, pprice.id, fee_dic, context=context)

    def compute_standard_period(self, cr, uid, ids, context=None):
        pprice = self.browse(cr, uid, ids[0], context=context)
        standard_period, min_period = self.pool.get('delivery.time.standard').compute_standard_period(cr, uid, pprice,
                                                                                                      context=context)
        self.write(cr, uid, pprice.id, {
            'standard_period': standard_period,
            'min_period': min_period
        })
        return True

    def compute_surchage(self, cr, uid, ids, context=None):
        pprice = self.browse(cr, uid, ids[0], context=context)
        discount = pprice.discount or 1
        amount_once_fee = pprice.once_fee * discount - pprice.surchage
        self.write(cr, uid, pprice.id, {
            'amount_once_fee': amount_once_fee,
            'final_amount': pprice.price_pcs * pprice.qty + amount_once_fee,
        })
        return True


class price_log(osv.osv):
    _name = 'price.log'
    _order = 'id'
    _columns = {
        'name': fields.text(u'说明'),
        'price_id': fields.many2one('pcb.price', u'报价单'),
        'arg_id': fields.many2one('pcb.fee.arg', u'计价参数'),
        'type': fields.selection(PCB_Fee_Arg_Type, string=u'类型', readonly=True, size=32),
    }

###############################################################################################
