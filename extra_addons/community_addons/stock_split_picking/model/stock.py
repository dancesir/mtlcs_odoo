# -*- coding: utf-8 -*-
#
#
#    Author: Nicolas Bessi, Guewen Baconnier, Yannick Vaucher
#    Copyright 2013-2015 Camptocamp SA
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
#
"""Adds a split button on stock picking out to enable partial picking without
   passing backorder state to done"""

import datetime
from openerp import fields, osv
from openerp import models, api, _


class stock_transfer_details(models.TransientModel):
    _inherit = 'stock.transfer_details'
    @api.one
    def do_detailed_split(self):
        processed_ids = []
        # Create new and update existing pack operations
        for lstits in [self.item_ids, self.packop_ids]:
            for prod in lstits:
                pack_datas = {
                    'product_id': prod.product_id.id,
                    'product_uom_id': prod.product_uom_id.id,
                    'product_qty': prod.quantity,
                    'package_id': prod.package_id.id,
                    'lot_id': prod.lot_id.id,
                    'location_id': prod.sourceloc_id.id,
                    'location_dest_id': prod.destinationloc_id.id,
                    'result_package_id': prod.result_package_id.id,
                    'date': prod.date if prod.date else fields.datetime.now(),
                    'owner_id': prod.owner_id.id,
                }
                if prod.packop_id:
                    prod.packop_id.with_context(no_recompute=True).write(pack_datas)
                    processed_ids.append(prod.packop_id.id)
                else:
                    pack_datas['picking_id'] = self.picking_id.id
                    packop_id = self.env['stock.pack.operation'].create(pack_datas)
                    processed_ids.append(packop_id.id)
        # Delete the others
        packops = self.env['stock.pack.operation'].search(['&', ('picking_id', '=', self.picking_id.id), '!', ('id', 'in', processed_ids)])
        packops.unlink()
        # 此处返回picking 的 方法
        self.picking_id.do_split()
        return True

    def default_get(self, cr, uid, fields, context=None):
        '''
        When splitting a unassigned state picking,  fill the wizard lines
        '''
        res = super(stock_transfer_details, self).default_get(cr, uid, fields, context=context)
        if not res['item_ids'] and context.get('display_split_button'):
            picking = self.pool.get('stock.picking').browse(cr, uid, context.get('active_id',), context=context)
            for move in picking.move_lines:
                res['item_ids'].append({
                    #'packop_id': move.id,
                    'product_id': move.product_id.id,
                    'product_uom_id': move.product_uom.id,
                    'quantity': 0,
                    #'package_id': op.package_id.id,
                    #'lot_id': move.lot_id.id,
                    'sourceloc_id': move.location_id.id,
                    'destinationloc_id': move.location_dest_id.id,
                    #'result_package_id': op.result_package_id.id,
                    'date': move.date,
                    #'owner_id': op.owner_id.id,
                })
        return res


class stock_picking(models.Model):
    """Adds picking split without done state."""

    _inherit = "stock.picking"

    @api.multi
    def split_process(self):
        """Use to trigger the wizard from button with
           correct context"""
        ctx = {
            'active_model': self._name,
            'active_ids': self.ids,
            'active_id': len(self.ids) and self.ids[0] or False,
            'do_only_split': True,
        }

        wiz = self.env['stock.transfer_details'].with_context(**ctx).create(
            {'picking_id': len(self.ids) and self.ids[0] or False,
             })
        view_dict = wiz.wizard_view()
        view_dict['name'] = _(u'请输入拆分数量')
        return view_dict

#######################################


# class StockMove(models.Model):
#
#     _inherit = 'stock.move'
#     @api.model
#     def split__________(self, move, qty,
#               restrict_lot_id=False, restrict_partner_id=False):
#         new_move_id = super(StockMove, self).split(
#             move, qty,
#             restrict_lot_id=restrict_lot_id,
#             restrict_partner_id=restrict_partner_id,
#         )
#         new_move = self.browse(new_move_id)
#         move_assigned = move.state == 'assigned'
#         moves = move + new_move
#         if move.reserved_availability > move.product_qty:
#             moves.do_unreserve()
#         if move.picking_id:
#             move.picking_id.pack_operation_ids.unlink()
#         if move_assigned:
#             moves.action_assign()
#         else:
#             moves.action_confirm()
#         if move.procurement_id:
#             defaults = {'product_qty': qty,
#                         'state': 'running'}
#             new_procurement = move.procurement_id.copy(default=defaults)
#             new_move.procurement_id = new_procurement
#             move.procurement_id.product_qty = move.product_qty
#         return new_move.id
