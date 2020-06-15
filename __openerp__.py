# -*- coding: utf-8 -*-
{
    'name': "Honduras Payroll",
    "author": "César Alejandro Rodriguez",
    'summary': 'Payroll Honduras', 
    'description': """
        Honduras Payroll  Version Especial
    """,          
    'version': '1.0',
    'depends': ['base', 'hr', "hr_payroll", "hr_contract"],
    'data': [
        "wizard/set_structure_contract.xml",
    	#"views/hr_payslip_inh.xml",
        "views/concet_deduction_allowances.xml",
        "wizard/increased_salary_view.xml",
        "views/doff_add_contract.xml",
        "views/allowance_deduction_view.xml",
        "views/hr_wage_paying.xml",
    ],
    'update_xml': [
    ],
    'application': True,
}
