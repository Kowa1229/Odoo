{
    'name': 'Human Resource Management',
    'summary': "HR System",
    'description': """This is a testing description""",
    'author': 'Kowa Jia Liang',
    # 'license': "AGPL-3",
    # 'website': "http://www.kowa.com",
    # 'category': 'Uncategorized',
    'version': '1.0',
    'depends': ['base', 'hr'],
    'application': True,
    'data': [
        'views/hr_views.xml',
        'views/hr_insurance.xml',
        'report/insurance_report.xml',
    ],
    # 'demo': ['demo.xml'],
}
