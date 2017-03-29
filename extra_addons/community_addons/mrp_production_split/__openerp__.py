# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2009 Albert Cervera i Areny - NaN  (http://www.nan-tic.com) All Rights Reserved.
#    Copyright (c) 2010-Today Elico Corp. All Rights Reserved.
#    Author: Andy Lu <andy.lu@elico-corp.com>
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
{
	"name" : "MRP Production Split",
	"version" : "0.1",
	"description" : """
""",
	"author" : "alangwansui@qq.com",
	"website" : "",
	"depends" : [ 
		'mrp', 'stock', 'procurement'
	],
	"category" : "Manufacturing",
	"init_xml" : [],
	"demo_xml" : [],
	"update_xml" : [
		'mrp_view.xml',
		'wizard/mrp_production_split.xml',
	],
	"active": False,
	"installable": True
}
