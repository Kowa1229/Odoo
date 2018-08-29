{
    'name': 'Leave - Excluded weekends and public holidays',
    'category': 'Human Resources',
    'summary': 'Gives the possibility to exclude weekends and public holidays from leave days',
    'website': 'http://www.facebook.com',
    'version': '11.0.0.1',
    'description': '''Descriptions''',
    'author': 'Jubilant Global Group',
    'depends': [
        'base', 'hr_holidays',
    ],
    'data': [
        'views/public_holidays_view.xml',
        # 'views/hr_holidays.xml',
        'report/public_holiday_report.xml',
    ],
}