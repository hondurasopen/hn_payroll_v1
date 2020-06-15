# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime
from datetime import *
from odoo.exceptions import Warning


class IncreasedSalary(models.TransientModel):
	_name="payroll.hn.structure.contract.wizard"
	_rec_name = "structure_id"

	structure_id = fields.Many2one("hr.payroll.structure", "Estructura", required=True)
	department_id = fields.Many2one("hr.department", "Departamento", required=True) 		
 

	@api.multi
	def set_structure(self):
	    contract_obj = self.env["hr.contract"].search([('department_id', '=', self.department_id.id), ('state', '=', 'open')])
	    for contract in contract_obj:
	    	contract.struct_id = self.structure_id.id