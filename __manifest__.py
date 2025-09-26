{
    'name': "CRM pour Étudiants",
    'summary': """
        Gère les étudiants en tant que opportunités CRM.
    """,
    'description': """
        Ce module étend le module CRM d'Odoo pour y ajouter des fonctionnalités
        spécifiques à la gestion des étudiants et de leur cursus.
    """,
    'author': "Basilio, Luca, Manantsoa IGF-IA/PRO42",
    'category': 'Sales/CRM',
    'version': '18.0.1.0.0',
    'depends': ['base', 'crm', 'mail', 'web', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/etudiant_views.xml',
        'views/etudiant_menu.xml',
        'views/crm_views.xml',
        'views/stage_views.xml',
        'views/crm_lead_kanban_views.xml',
        'views/crm_data.xml',
        'views/etudiant_search_views.xml',
        'views/stage_kanban_views.xml',
        'views/crm_list_views.xml',
        'reports/report_etudiant_template.xml',
        'reports/etudiant_report.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'icon': '/etudiants_crm/static/images/icon.png',
}