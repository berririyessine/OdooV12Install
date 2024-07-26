# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo import _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, timedelta as td, timedelta

from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
# import datetime
# _logger = logging.getLogger(__name__)
class res_company(models.Model):
    _inherit = 'res.company'
    deduct_sunday_in_leave = fields.Boolean('')
    deduct_saturday_in_leave = fields.Boolean('')


class HrAttendanceEtatInherit(models.Model):
    _name = 'hr.attendance.etat'
    name = fields.Char('')
    check_de = fields.Date(string="Check In",default=lambda self: fields.Date.to_string(date.today().replace(day=1)))
    check_out = fields.Date(string="Check Out", default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()))


    def Etat_Presences(self):
        print('')
        from datetime import datetime
        for rec in self:
            list_employee_added=[]
            list_to_create= dict()

            list=[]
            employees = self.env['hr.employee'].search([])
            for employe in employees:
                list_attendance=[]
                attendances = self.env['hr.attendance'].search([('employee_id','=',employe.id),
                ('date','>=',rec.check_de),('date','<=',rec.check_out)])
                # raise ValidationError(str(attendances))
                for list_append in attendances:
                    list_attendance.append(list_append.id)
                for add_aatendance in attendances:
                    if str(employe.id) not in list_employee_added :
                        list_to_create[add_aatendance.employee_id.id]={
                        'employee_id':add_aatendance.employee_id.id ,
                        'attendance_ids':[ (6, 0, list_attendance)],
                        }
                        list_employee_added.append(str(employe.id))
                    else :
                        list_to_create[employe.id].update({
                        'employee_id':add_aatendance.employee_id.id ,
                        'attendance_ids':[ (6, 0, list_attendance)],
                            })
            # raise ValidationError(str(list_to_create))
            for val in list_to_create:
                list.append(self.env['hr.attendance.etat.line'].create(list_to_create[val]).id)
            precences_ids = self.env['hr.attendance.etat.model'].create({
                "date_from":self.check_de,
                "date_to":self.check_out,
                "precences_ids":[ (6, 0, list)],
            })

            return self.env.ref('oh_hr_zk_attendance.hr_attendance_etat_journal').report_action(precences_ids)

class WizardExcelReport(models.TransientModel):
    _name = "wizard.txt.report"
    name=fields.Char("")
    excel_file = fields.Binary('')
    file_name = fields.Char('', size=64)

class HrAttendanceEtatModel(models.Model):
    _name = 'hr.attendance.etat.model'
    date_from = fields.Date("De" )
    date_to = fields.Date("à" )
    precences_ids = fields.Many2many("hr.attendance.etat.line")

class HrAttendanceEtatModel(models.Model):
    _name = 'hr.attendance.etat.line'
    employee_id=fields.Many2one('hr.employee')
    attendance_ids=fields.Many2many('hr.attendance')





class HrAttendanceInherit(models.Model):
    _inherit = 'hr.attendance'

    sup_hours = fields.Float('Heures Supp',compute="calculate_attendance")
    heures_travil = fields.Float('Heures Travaillés',compute="calculate_attendance")
    heures_absences = fields.Float('Heures Absences',compute="calculate_attendance")
    jour_travil  = fields.Float('Jour Travaillés',compute="calculate_attendance")

    @api.multi
    def calculate_attendance(self):
        import datetime
        for rec in self:
            rec.heures_travil = 0.0
            rec.jour_travil = 0.0
            start_date=datetime.datetime.strptime(str(rec.date), "%Y-%m-%d")
            check_in= start_date.replace(hour=7, minute=0)
            check_out = start_date.replace(hour=14, minute=0)
            # raise ValidationError(str(check_out))
            diff = check_out - check_in
            hours = diff.days * 24 + diff.seconds // 3600
            # raise ValidationError(str(hours))
            rec.heures_travil=hours

            if rec.heures_travil >= 7.0 :
                rec.jour_travil = 1
            else :
                rec.jour_travil = 0

    def inCongDays(self,date):
        d = date
        if d.weekday()==6 and  self.employee_id.company_id.deduct_sunday_in_leave :
            return  True
        if d.weekday()==5 and  self.employee_id.company_id.deduct_saturday_in_leave :
            return  True
        return False


    # @api.multi
    # def calculate_attendance(self):
    #     import datetime
    #     for rec in self:
    #         rec.heures_travil = 0.0
    #         rec.heures_absences = 0.0
    #         rec.sup_hours = 0.0
    #         difference_hours = ''
    #         start_date=datetime.datetime.strptime(str(rec.date), "%Y-%m-%d")
    #         check_in= start_date.replace(hour=7, minute=0)
    #         break_in = start_date.replace(hour=12, minute=0)
    #         break_out = start_date.replace(hour=16, minute=0)
    #         date_start_weekend = datetime.datetime.strptime(str(rec.date), "%Y-%m-%d").date()
    #         end_date= datetime.datetime.strptime(str(rec.date), "%Y-%m-%d")
    #         check_out= end_date.replace(hour=11, minute=0)
    #         if not  rec.inCongDays(date_start_weekend):
    #             if rec.check_in and rec.check_in > check_in :
    #                 rec.heures_absences += 1.0
    #             if rec.check_out and rec.check_out < break_out :
    #                 rec.heures_absences += 1.0
    #             if start_date > check_in and end_date > check_out and end_date<break_in:
    #                 rec.heures_absences += 1.0
    #             if start_date > check_in and end_date < check_out and end_date<break_out:
    #                 rec.heures_absences += 1.0
    #             if end_date < check_out and start_date== check_in or end_date == check_out and start_date> check_in or end_date < check_out and start_date> check_in:
    #                 rec.heures_absences += 1.0
    #             if end_date < break_out and start_date== break_in or end_date == break_out and start_date> break_in or end_date < break_out and start_date> break_in:
    #                 rec.heures_absences += 1.0
    #             if start_date > break_in:
    #                 rec.heures_absences += 1.0
    #             if start_date > break_in and break_out> end_date:
    #                 rec.heures_absences += 1.0
    #             if rec.check_out and  break_out<rec.check_out :
    #                 difference_hours = str(rec.check_out  - break_out)
    #                 if difference_hours:
    #                     rec.sup_hours = difference_hours.split(':')[0]
    #             if rec.check_in and rec.check_out:
    #                 rec.heures_travil = 8.0 - rec.heures_absences
    #             elif rec.check_in == False and rec.check_out==False:
    #                 rec.heures_travil = 0.0
    #             else:
    #                 rec.heures_travil = 4.0 - rec.heures_absences
    #         else:
    #             if rec.inCongDays(date_start_weekend):
    #                 if rec.check_out and rec.check_in:
    #                     difference_hours = str(rec.check_out  - rec.check_in)
    #                     if difference_hours:
    #                         rec.sup_hours = difference_hours.split(':')[0]
