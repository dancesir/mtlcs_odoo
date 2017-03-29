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
from openerp.exceptions import except_orm, Warning, RedirectWarning


class account_move_line(osv.osv):
    _inherit = 'account.move.line'
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        context = context or {}
        extra_domain = context.get('extra_domain')
        rest_domain = context.get('rest_domain')
        if extra_domain:
            args+=extra_domain
        if rest_domain:
            args = rest_domain
        return super(account_move_line, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)


