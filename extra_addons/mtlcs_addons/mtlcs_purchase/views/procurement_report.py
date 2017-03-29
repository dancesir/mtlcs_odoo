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

from openerp import tools
from openerp.osv import fields, osv
from openerp.addons.decimal_precision import decimal_precision as dp

"""
申请日期	物料名称	物料规格	是否常规	单位	数量	购料周期	要求到货时间	采购接单时间	采购回复到料时间	实际到厂时间	是否准时	备注
relation table:
procurement_order
mail_message: time of approve
purchase_order_line
product_product
stock_move
"""

class procurement_report(osv.osv):
    _name = "procurement.report"
    _auto = False
    _columns = {
        'id': fields.integer('ID'),
		'preparation_id': fields.many2one('preparation.order', u'申购单', readonly=True),
        'product_id': fields.many2one('product.product', u'物料名称', readonly=True),
        'uom_id': fields.many2one('product.uom', u'单位', readonly=True),
        'product_qty': fields.float(u'数量', digits_compute=dp.get_precision('Product Unit of Measure'), ),
		'purchase_qty': fields.float(u'采购数', digits_compute=dp.get_precision('Product Unit of Measure'),),
		'input_qty': fields.float(u'入库数', digits_compute=dp.get_precision('Product Unit of Measure'),),
        'purchase_period': fields.integer(u'采购周期：天', readonly=True),
        'date_planned': fields.datetime(u'要求到货时间', readonly=True),
        'purchase_approve_date': fields.datetime(u'采购接单时间', readonly=True),
        'input_date': fields.datetime(u'实际到厂时间', readonly=True),
        'is_overtime': fields.boolean(u'是否迟交', readonly=True),
    }

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'procurement_report')

        cr.execute("""
            create or replace view procurement_report as (


WITH mess as (
        select
                mess.id,
                mess.res_id,
                mess.date as purchase_approve_date
        from
                mail_message as mess
                left join mail_message_subtype as mess_type on(mess.subtype_id = mess_type.id)
        where
                mess.model = 'preparation.order'  and  mess_type.name = 'preparation_order_done'
),
proc AS(
	select
		proc.id as id,
		pre.id as preparation_id,
		pre.state as state,
		pre.department_id,
		pdt.id as product_id,
		proc.product_qty as product_qty,
		proc.product_uom as proc_uom,
		proc.date_planned,
		pdt.purchase_period,
		pol.id as pol_id,
		pol.product_qty as purchase_qty,
		pol.product_uom as pol_uom
	from procurement_order as proc
		left join preparation_order as pre on(proc.preparation_id = pre.id)
		left join product_product as pdt on(proc.product_id = pdt.id)
		left join purchase_order_line as pol on(proc.purchase_line_id = pol.id)
	order by proc.id
)
select
	proc.id as id,
	proc.preparation_id,
	proc.state,
	proc.department_id,
	proc.product_id,
	proc.product_qty,
	proc.proc_uom as uom_id,
	proc.date_planned,
	mess.purchase_approve_date,
	proc.purchase_period,
	proc.pol_id,
	proc.purchase_qty,
	count(move.id) as move_count,
	sum(move.product_uom_qty) as input_qty,
	min(move.date) as input_date,
	min(move.date) > proc.date_planned as is_overtime
from proc
	left join mess on(mess.res_id = proc.preparation_id)
	left join stock_move as move on(proc.pol_id = move.purchase_line_id and move.state='done')
group by
	proc.id,
	proc.preparation_id,
	proc.state,
	proc.department_id,
	proc.product_id,
	proc.product_qty,
	proc.proc_uom,
	proc.date_planned,
	proc.pol_id,
	proc.purchase_qty,
	proc.purchase_period,
	mess.purchase_approve_date


            )
        """)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
