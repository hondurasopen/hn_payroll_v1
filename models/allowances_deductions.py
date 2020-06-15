# -*- coding: utf-8 -*-
from openerp import models, fields, api 


class PlanificacionMasterDetail(models.Model):
	_name = "hr.contract.deduction.allowance"

	name = fields.Many2one("hr.contract.concepts.deductions", "Concepto", required=True)
	contract_id = fields.Many2one("hr.contract", "Contrato")
	state = fields.Selection([('progress', 'Progreso'), ('done', 'Finalizado')], "Estado", default='progress')
	periodicity = fields.Selection([('finita','Finita'),('infinita','Infinita')], "Periodicidad", required=True)
	concept_type = fields.Selection([('beneficio','Beneficio'),('deduccion','Deduccion')], "Tipo", default='deduccion')

	amount_total = fields.Float("Monto Total")
	amount_fee = fields.Float("Monto cuota")
	number_fee = fields.Integer("Número de pagos")
	number_fee_record = fields.Integer("Acumulado de pagos")

	number_fee_pending = fields.Integer("# pagos restantes")
	start_date = fields.Date("Fecha de inicio")
	end_date = fields.Date("Fecha de finalización")

	@api.onchange("amount_fee", "number_fee")
	def onchangecuota_pago(self):
		self.amount_total = self.amount_fee * self.number_fee
		self.number_fee_pending = self.number_fee


class PlanificacionMasterDetail(models.Model):
	_name = "hr.contract.concepts.deductions"

	name = fields.Char("Nombre de concepto")
	code = fields.Char("Código de concepto")
	active = fields.Boolean("Activo", default=True)
	structure_id = fields.Many2one("hr.special.structure", "Estructura")
	account_id = fields.Many2one("account.account", "Cuenta")
	concept_type = fields.Selection([('beneficio','Beneficio'),('deduccion','Deduccion')], "Tipo", default='deduccion')