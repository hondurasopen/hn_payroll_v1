# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime
from datetime import *
import time
from datetime import datetime, timedelta
from odoo.exceptions import Warning


class PlanificacionMasterDetail(models.Model):
	_name = "hr.historial.contract"

	name = fields.Many2one("hr.contract.concepts.deductions", "Concepto", required=True)
	contract_id = fields.Many2one("hr.contract", "Contrato")
	concept_type = fields.Selection([('beneficio','Beneficio'),('deduccion','Deduccion')], string="Tipo")

	amount_fee = fields.Float("Monto")
	number_fee = fields.Integer("Número de pagos")

	payment_date = fields.Date("Fecha")

