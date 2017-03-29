{
    'name': 'Web Search view extend',
    'version': '1.0',
    'category': 'web',
    'author':'Emipro Technologies Pvt. Ltd.',
    'sequence': 9,
    'summary': 'Get search drawer unfolded by default in search view',
    'description': """ 
By default when any view loads in Odoo, search drawer will be folded except Graph view. 
After installation of this module, search drawer will visible unfolded by default. This will work on all views except form view. 
    
Contact us at info@emiprotechnologies.com for more queries related to Odoo Customisation.
""",
    'website': 'www.emiprotechnologies.com',
    'depends': ['web'],
    'data': ['views/webclient_templates.xml'],
    'images': ['static/description/main_screen.png'],
    'installable': True,
    'auto_install': False,
    'application': True,
}
