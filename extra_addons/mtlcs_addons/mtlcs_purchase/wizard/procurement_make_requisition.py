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
from datetime import datetime, timedelta
from openerp.osv import fields, osv
from openerp.exceptions import Warning
from openerp.tools.translate import _


class procurement_make_requisition(osv.osv_memory):
    _name = 'procurement.make.requisition'
    _columns = {
        'name': fields.char(u'Name', size=16),
    }

    def apply(self, cr, uid, ids, context=None):
        req_id = self.make_purchase_requisition(cr, uid, ids, context=context)
        return {
            'type': 'ir.actions.act_window',
            'name': u'比价单',
            'view_type': 'form',
            "view_mode": 'form',
            'res_model': 'purchase.requisition',
            'res_id': req_id,
            #"domain": [('id', 'in', info_ids)],
        }

    def _pre_pare_requisitio(self, cr, uid, procurements, context=None):
        company_id = procurements[0].company_id
        warehouse_id = procurements[0].warehouse_id
        rule_id = procurements[0].rule_id
        date_max = procurements[0].date_planned

        line_datas = []
        for p in procurements:
            if p.requisition_id:
                raise Warning(u"需求已经存在比价单中")
            if p.company_id != company_id:
                raise Warning(u"需求公司不一致")
            if p.warehouse_id != warehouse_id:
                raise Warning(u"需求仓库不一致")
            if p.rule_id.action != 'buy':
                raise Warning(u"需求规则必须是 购买")
            if p.state != 'confirmed':
                raise Warning(u"需求状态不是已确认")
            if p.rule_id != rule_id:
                raise Warning('需求规则必须一致，需要质检的物料和不需要质检的物料请分开采购。或者先手动将需求规则修改一致')

            if p.date_planned > date_max:
                date_max = p.date_planned
            line_datas.append((0, 0, {
                'product_id': p.product_id.id,
                'product_uom_id': p.product_uom.id,
                'product_qty': p.product_qty,
                'procurement_id': p.id,
                'schedule_date': p.date_planned,
            }))

        return {
            'company_id': company_id.id,
            'warehouse_id': warehouse_id.id,
            "rule_id": rule_id.id,
            'picking_type_id': rule_id.picking_type_id.id,
            'schedule_date': date_max,
            'origin': '',
            'line_ids': line_datas,
        }

    def make_purchase_requisition(self, cr, uid, ids, context=None):
        procurement_ids = context.get('active_ids')
        procurement_obj = self.pool.get('procurement.order')
        requisition_obj = self.pool.get('purchase.requisition')

        procurements = procurement_obj.browse(cr, uid, procurement_ids, context=context)
        requisition_data = self._pre_pare_requisitio(cr, uid, procurements, context=context)
        requisition_id = requisition_obj.create(cr, uid, requisition_data, context=context)
        procurement_obj.write(cr, uid, procurement_ids, {'requisition_id': requisition_id, 'state': 'running'})
        requisition_obj.signal_workflow(cr, uid, [requisition_id, ], 'sent_suppliers', context=context)

        return requisition_id
