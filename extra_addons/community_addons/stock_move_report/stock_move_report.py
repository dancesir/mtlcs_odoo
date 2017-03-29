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
from openerp.osv import osv, fields
from openerp import tools
from openerp.addons.decimal_precision import decimal_precision as dp
from openerp.addons.stock.stock import stock_move as SM
from openerp.addons.stock_account.stock import stock_move as ACCOUNT_SM

Move_State = SM._columns['state'].selection
Invoice_State = ACCOUNT_SM._columns['invoice_state'].selection

class stock_move_report(osv.osv):
    _name = 'stock.move.report'
    _order = 'id desc'
    _auto = False
    _columns = {
        'id': fields.integer('ID', readonly=True),
        'name': fields.char('Name', size=32, readonly=True),
        'origin': fields.char(u'源单据', size=32, readonly=True),
        'product_id': fields.many2one('product.product', u'产品', readonly=True),
        'product_uom_qty': fields.float(u'数量', digits_compute=dp.get_precision('Product Unit of Measure'), readonly=True),
        'product_uom': fields.many2one('product.uom', u'单位', readonly=True),
        'create_date': fields.datetime(u'创建日期', readonly=True),
        'date': fields.datetime(u'完成日期', readonly=True),
        'date_expected': fields.datetime(u'计划日期', readonly=True),

        'picking_id': fields.many2one('stock.picking', u'调拨单',  readonly=True),
        'location_id': fields.many2one('stock.location', u'源库位', readonly=True),
        'location_dest_id':  fields.many2one('stock.location', u'目的库位', readonly=True),

        'state': fields.selection(Move_State, u'状态', readonly=True),
        'partner_id': fields.many2one('res.partner', u'合作伙伴', readonly=True),
        'company_id': fields.many2one('res.company', u'公司', readonly=True),
        'picking_type_id': fields.many2one('stock.picking.type', u'类型', readonly=True),
        'price_unit':fields.float(u'价格', digits_compute=dp.get_precision('Product Unit of Measure'), readonly=True),
        'amount':fields.float(u'金额', digits_compute=dp.get_precision('Product Unit of Measure'), readonly=True),
        'invoice_state': fields.selection(Invoice_State,u'开票状态', readonly=True),
        'reception_to_invoice': fields.boolean(u'是否开票', readonly=True),
        'code': fields.char(u'方向'),
        'create_uid': fields.many2one('res.users', u'创建人', readonly=True),
    }


    def init(self, cr):
        tools.drop_view_if_exists(cr, 'stock_move_report')
        cr.execute("""
            create or replace view stock_move_report as (


select
        mv.id as id,
        mv.create_uid,
        pk.partner_id,
        pk.origin,
        mv.product_id,
        mv.product_uom,
        mv.product_uom_qty,
        mv.price_unit,
        mv.product_uom_qty * mv.price_unit as amount,
        mv.location_id,
        mv.location_dest_id,
        mv.state,
        mv.picking_id,
        mv.picking_type_id,
        mv.invoice_state,
        pk.reception_to_invoice,
        mv.date_expected,
        mv.date,
        mv.create_date,
        mv.company_id,
        pt.code
 from
        stock_move as mv
        left join stock_picking as pk on(mv.picking_id =pk.id)
        left join stock_picking_type as pt on(pk.picking_type_id = pt.id)

            )
        """)


