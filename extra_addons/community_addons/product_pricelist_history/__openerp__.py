# -*- coding: utf-8 -*-


{
    'name': 'product_pricelist_history',
    'version': '1.0',
    'category': 'Product',
    'sequence': 14,
    'summary': '',
    'description': """
    Record The Supplier Pricelist History
    """,
    'author': 'alangwansui@gmail.com',
    'website': 'www.ingadhoc.com',
    'images': [],
    'depends': ['purchase', 'product', 'product_supplier_pricelist','approve_log'],
    'data': [
        'security/ir.model.access.csv',
        'pricelist_history.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
