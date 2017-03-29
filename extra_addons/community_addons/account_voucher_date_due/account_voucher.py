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


class account_voucher(osv.osv):
    _inherit = 'account.voucher'
    _columns = {
    }
    _defaults = {
    }
    def onchange_partner_id(self, cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context=None, date_due=None):
        ctx = context.copy()
        if date_due:
            ctx.update({'extra_domain': [('date_maturity','<=', date_due)]})
        return super(account_voucher, self).onchange_partner_id( cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context=ctx)
