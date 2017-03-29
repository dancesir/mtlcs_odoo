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
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _

class mrp_production_workcenter_line(osv.osv):
    _inherit = 'mrp.production.workcenter.line'
    _columns = {

    }
    def scrap(self, cr, uid, ids, context=None):
        line = self.browse(cr, uid, ids, context=context)
        move_id = line.production_id.move_created_ids[0].id
        ctx = context.copy()
        ctx.update({
            'active_id': move_id,
            'active_ids': [move_id, ],
            'active_model': 'stock.move',
            'ticket_id': line.id,
        })

        return {
            'name': _(u'工序报废'),
            'view_type': 'form',
            'view_mode': 'form',
            #"view_id": 635,
            'res_model': 'stock.move.scrap',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': ctx,
        }

class stock_move(osv.osv):
    _inherit = 'stock.move'
    _columns = {
        'ticket_id': fields.many2one('mrp.production.workcenter.line', u'工票'),
        'workcenter_id': fields.related('ticket_id', 'workcenter_id', type='many2one',
                                        relation='mrp.workcenter', readonly=True, string=u'工作中心'),
    }

    def action_scrap(self, cr, uid, ids, quantity, location_id, restrict_lot_id=False,
                     restrict_partner_id=False, context=None):
        new_move_ids = super(stock_move, self).action_scrap(cr, uid, ids, quantity, location_id,
                                                   restrict_lot_id=restrict_lot_id,
                                                   restrict_partner_id=restrict_partner_id, context=context)

        ticket_id = context.get('ticket_id')
        if ticket_id:
            self.write(cr, uid, new_move_ids, {'ticket_id': ticket_id}, context=context)
        return new_move_ids
