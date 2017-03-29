# -*- coding: utf-8 -*-
{
    "name": "Quality Acceptance_Standard",
    'version': '1.0',
    'category': 'Quality control',
    'sequence': 14,
    'description': """
Quality Acceptance_Standard
    """,
    'author': 'Jon<alangwansui@gmail.com>',
    'website': '',
    'images': [
    ],
    'depends': [ 'base', 'quality_control' ],
    'data': [
        ##data
        'data/acceptance.standard.csv',
        ##view
        'acceptance_standard.xml',
        #'security'
        'security/ir.model.access.csv',

    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
