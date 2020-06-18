# -*- coding: utf-8 -*-
from openerp import models, fields, api 


class HnWaheHistorical(models.Model):
	_name = "hr.historical.wage"

	contract_id = fields.Many2one("hr.contract", "Contrato")
	gross_salary = fields.Float("Salario Bruto")
	payment_date = fields.Date("Fecha")
	payroll_id = fields.Many2one("hr.wage.paying", "Nómina")
	month = fields.Char("Mes")

