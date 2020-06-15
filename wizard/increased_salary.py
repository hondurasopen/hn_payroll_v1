# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime
from datetime import *
from odoo.exceptions import Warning


class IncreasedSalary(models.TransientModel):
	_name="payroll.hn.increased.salary.wizard"
	_rec_name = "department_id"		
 

	department_id = fields.Many2one("hr.department", "Departamento", required=True)
	increased_salary = fields.Float("Incremento (%)")
	confirmation = fields.Char("Mensaje")
	employee_ids = fields.One2many("payroll.hn.increased.salary.wizard.line", "wizard_id", "Empleados")

	@api.multi
	def set_increased_salary(self):
		if self.employee_ids:
			for l in self.employee_ids:
				new_salary = l.contract_id.wage * (1 + self.increased_salary / 100)
				l.contract_id.wage = new_salary 
				l.new_wage = new_salary
			self.confirmation = "Se ha aplicado el incremento"
					

	@api.multi
	def get_employees(self):
		for employee in self.department_id.member_ids:
			wizard_obj = self.env["payroll.hn.increased.salary.wizard.line"]
			for contract in employee.contract_ids:
				if contract.state == 'open':
					vals = {
						'employee_id': contract.employee_id.id,
						'wage': contract.wage,
						'contract_id': contract.id,
						'wizard_id': self.id,
					}
					obj_id = wizard_obj.create(vals)



class IncreasedSalary(models.TransientModel):
	_name="payroll.hn.increased.salary.wizard.line"			

	employee_id = fields.Many2one("hr.employee", "Empleado")
	contract_id = fields.Many2one("hr.contract", "contract")
	wage = fields.Float("Salario")
	new_wage = fields.Float("Nuevo salario")
	wizard_id = fields.Many2one("payroll.hn.increased.salary.wizard", "Wizard")
 