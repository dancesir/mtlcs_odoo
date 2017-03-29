# -*- encoding: utf-8 -*-
##############################################################################
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

{
    "name": "Lot Produciton Date",
    "version": "1.0",

    "author": "Jon<alangwansui@gmail.com>",
    "website": "http://www.odoo.com",
    "description": """
      Lot Produciton Date
    """,
    "depends": ["stock", "product_expiry",],
    "category": 'Warehouse Management',
    "data": [
       #view
        "stock_production_lot.xml",

    ],
    "installable": True,
    "application": True,
}
