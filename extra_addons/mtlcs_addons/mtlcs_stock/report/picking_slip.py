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
from openerp.osv import osv
from openerp.report import report_sxw


class parse_picking_slip(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(parse_picking_slip, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'test_test': self.test_test,
        })

    def test_test(self, n=10):
        return  n*n

class picking_slip(osv.AbstractModel):
    _name = 'report.mtlcs_stock.picking_slip'
    _inherit = 'report.abstract_report'
    _template = 'mtlcs_stock.picking_slip'
    _wrapped_report_class = parse_picking_slip




###############################################################################
