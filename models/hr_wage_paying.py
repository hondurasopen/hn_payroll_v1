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
    gross_wage = fields.Floot("Salario bruto")
    loan_fee = fields.Float("Cuota de préstamo")
    saving_fee = fields.Float("Aporte Cooperativa")
    amount_isr = fields.Float("ISR")
    amount_ipv = fields.Float("Impuesto Vecinal")
    another_deduction = fields.Float("Otra deducción")
    another_incomes = fields.Float("Otros ingresos")
    amount_deduction = fields.Float("Total de deducciones")
    amount_net = fields.Float("Neto a pagar")
