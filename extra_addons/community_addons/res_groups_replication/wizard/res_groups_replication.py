
# -*- encoding: utf-8 -*-
##############################################################################
#
#    Daniel Campos (danielcampos@avanzosc.es) Date: 08/09/2014
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp.osv import osv, fields


class res_groups_replication_line(osv.osv_memory):
    _name = 'res.groups.replication.line'
    _columns = {
        'name':fields.char('Name', size=16),
        'user_id': fields.many2one('res.users', u'用户'),
        'wizard_id': fields.many2one('res.groups.replication', 'Wizard'),
    }


class res_groups_replication(osv.osv_memory):
    _name = 'res.groups.replication'

    _columns = {
        'name':fields.char('Name', size=16),
        'from_uid': fields.many2one('res.users', u'从',),
        'lines': fields.one2many('res.groups.replication.line', 'wizard_id',  u'复制到'),
    }

    def default_get(self, cr, uid, fields, context=None):
        res = {}
        lines = [{'user_id': x} for x in context.get('active_ids') if x != 1]
        res.update({'lines': lines})
        return res

    def apply(self, cr, uid, ids, context):
        user_obj = self.pool.get('res.users')
        wizard = self.browse(cr, uid, ids[0], context=context)

        group_ids = [g.id for g in wizard.from_uid.groups_id]
        to_ids = [x.user_id.id for x in wizard.lines]

        user_obj.write(cr, uid, to_ids, {'groups_id': [(6, 0, group_ids),]}, context=context)
        return True



#################