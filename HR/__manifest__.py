{
    'name': 'Human Resource Management',
    'summary': "HR System",
    'description': """This is a HR module developed by Jubilant Global
                      The contents included are:
                                - Insurance
                                - Medical Claim
                                - Fields inherited for foreign employee""",
    'author': 'Jubilant Global',
    # 'license': "AGPL-3",
    # 'website': "http://www.kowa.com",
    # 'category': 'Uncategorized',
    'version': '1.0',
    'depends': ['base', 'hr', 'hr_contract'],
    'application': True,
    'data': [
        # 'views/hr_views.xml',
        'views/hr_insurance.xml',
        'views/hr_medical_claim.xml',
        'views/hr_insurance_inherit_hr.xml',
        'report/insurance_report.xml',
    ],
    # 'demo': ['demo.xml'],
}
