# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

import time
from openerp.osv import osv, fields
from openerp import models



class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    _columns = {
        'inspection_id': fields.many2one('quality.inspection.order', u'质检单', readonly=True, copy=False),
    }

    def action_done(self, cr, uid, ids, context=None):
        #TODO: ? picking.state is a function filed, the hook to create inspection should put where?
        return super(stock_picking, self).action_done(cr, uid, ids, context=context)
        pick = self.browse(cr, uid, ids[0], context=context)
        if pick.picking_type_id.ref == 'supplier2stock' and not pick.inspection_id:
            self.create_inspection_order(cr, uid, pick.id, context=context)
        return res


    def create_inspection_order(self, cr, uid, ids, context=None):
        '''
        maybe inspection should reference to purchase order
        '''
        inspection_obj = self.pool['quality.inspection.order']
        pick = self.browse(cr, uid, ids[0], context=context)
        if pick.inspection_id:
            return True

        line_date = []
        for move in pick.move_lines:
            line_date.append((0,0,{
                'product_id': move.product_id.id,
                'uom_id': move.product_uom.id,
                'qty': move.product_uom_qty,
                'move_id': move.id,
            }))
        data = {
            'partner_id': pick.partner_id and pick.partner_id.id or False,
            'origin': pick.name,
            'line_ids': line_date,
            'type': 'iqc',
            'res_id': '%s,%s' % (stock_picking._inherit, pick.id),
        }
        inspection_id = inspection_obj.create(cr, uid, data, context=context)
        self.write(cr, uid, pick.id, {'inspection_id': inspection_id}, context=None)
        return True

class stock_transfer_details(osv.osv_memory):
    _inherit = 'stock.transfer_details'

    def do_detailed_transfer(self, cr, uid, ids, context=None):

        # ==========1110
        need_iqc = False
        for p in self.browse(cr, uid, ids).item_ids:
            if p.product_id.need_iqc:
                need_iqc = True

        res = super(stock_transfer_details, self).do_detailed_transfer(cr, uid, ids, context=context)
        pick_obj = self.pool.get('stock.picking')
        pick_id = context.get('active_id')
        pick = pick_obj.browse(cr, uid, pick_id)
        if need_iqc and  pick.state == 'done' and pick.picking_type_id.ref == 'supplier2stock' and not pick.inspection_id:
        # if pick.state == 'done' and pick.picking_type_id.ref == 'supplier2stock' and not pick.inspection_id:
            pick_obj.create_inspection_order(cr, uid, [pick.id], context=context)
        return res

#############################################################################

