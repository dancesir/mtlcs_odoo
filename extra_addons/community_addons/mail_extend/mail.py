
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


class mail_compose_message(osv.TransientModel):
    _inherit = 'mail.compose.message'

    def get_mail_values(self, cr, uid, wizard, res_ids, context=None):
        template_obj = self.pool['email.template']
        value = super(mail_compose_message, self).get_mail_values(cr, uid, wizard, res_ids, context=context)
        if context.get('default_template_id'):
            reply_to = template_obj.read(cr, uid, context.get('default_template_id'), ['reply_to'])['reply_to']
            if reply_to:
                for k in value:
                    value[k].update({'reply_to': reply_to})
        return value


class ir_mail_server(osv.osv):
    _inherit = "ir.mail_server"

    def build_email(self, email_from, email_to, subject, body, email_cc=None, email_bcc=None, reply_to=False,
               attachments=None, message_id=None, references=None, object_id=False, subtype='plain', headers=None,
               body_alternative=None, subtype_alternative='plain'):
        res = super(ir_mail_server, self).build_email(email_from, email_to, subject, body, email_cc, email_bcc, reply_to,
               attachments, message_id, references, object_id, subtype, headers,
               body_alternative, subtype_alternative)

        #TODO ? why can not replace Return-Path, maybe to look the type(res)
        #res['Return-Path'] = 'stmp@mtlpcb.com'

        return res


