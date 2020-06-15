# -*- coding: utf-8 -*-
from openerp import models, fields, api 

class HrPrePayroll(models.Model):
    _name = 'hr.wage.paying'

    start_date = fields.Date("Fecha inicial")
    end_date = fields.Date("Fecha final")
    employee_detail_ids = fields.One2many("hr.wage.paying.line", "parent_id", "Detalle de empleados")



class HrPrePayroll(models.Model):
    _name = 'hr.wage.paying.line'

    parent_id = fields.Many2one("hr.wage.paying", "Pago")
    employee_id = fields.Many2one("hr.employee", "empleado")
    wage = fields.Float("Salario")

