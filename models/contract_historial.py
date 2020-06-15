# -*- coding: utf-8 -*-
from openerp import models, fields, api 


class PlanificacionMasterDetail(models.Model):
	_name = "hr.historial.contract"

	name = fields.Many2one("hr.contract.concepts.deductions", "Concepto", required=True)
	contract_id = fields.Many2one("hr.contract", "Contrato")
	concept_type = fields.Selection([('beneficio','Beneficio'),('deduccion','Deduccion')], string="Tipo")

	amount_fee = fields.Float("Monto")
	number_fee = fields.Integer("Número de pagos")

	payment_date = fields.Date("Fecha")

