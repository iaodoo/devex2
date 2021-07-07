# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Accounting Module Customization',

    'version': '1.1',
    
    'category': 'Accounting',
    
    'summary': 'Accounting Module Customization',
    
    'description': """
This module contains all the features customized for Mining Company.
    """,
    
    'depends': ['account','analytic'],
    
    'data': [
        'views/analytic_group.xml',
        'views/invoice_view.xml',
        'views/analytic_view.xml',
        'views/product_view.xml',
       'views/activity_view.xml',
       'views/tags_view.xml',
        'wizard/chart_account_view.xml',
        'views/account_view.xml',       
        'security/ir.model.access.csv',
        'views/company_view.xml',
        'data/data.xml'
    ],
    
    'demo': [],
    
    'installable': True,
    
    'auto_install': False
}
