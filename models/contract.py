# -*- coding: utf-8 -*-
from odoo import api, models, fields
from datetime import *

class DoffHistorialSalarios(models.Model):
    _inherit = 'hr.contract'

    #DEDUCCIONES
    allowences_ids = fields.One2many("hr.contract.deduction.allowance", "contract_id", "Otros Beneficios y deducciones")
    historical_ids = fields.One2many("hr.historial.contract", "contract_id", "Historial")



