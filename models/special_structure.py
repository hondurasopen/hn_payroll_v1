# -*- coding: utf-8 -*-
from openerp import models, fields, api 


class HrSpecialStructure(models.Model):
	_name = "hr.special.structure"

	name = fields.Char("Nombre")
	active = fields.Boolean("Activo", default=True)
	concept_ids = fields.One2many("hr.contract.concepts.deductions", "structure_id", "Detalle de conceptos") 