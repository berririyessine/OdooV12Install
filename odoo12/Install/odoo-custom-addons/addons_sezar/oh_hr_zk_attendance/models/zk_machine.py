# -*- coding: utf-8 -*-
import pytz
import sys
import datetime
import logging
import binascii

from . import zklib
from .zkconst import *
from struct import unpack
from odoo import api, fields, models
from odoo import _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
_logger = logging.getLogger(__name__)


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'
    check_in = fields.Datetime(string="Check In", default=False,compute="compute_check_in_out",required=False)
    check_out = fields.Datetime(string="Check Out",compute="compute_check_in_out",required=False)

    device_id = fields.Char(string='Biometric Device ID', help="Device Id")
    time_in = fields.Char('')
    time_out = fields.Char('')
    date = fields.Date('' , default=date.today())

    def calcul_presence(self):
        employees = self.env['hr.employee'].search([])
        hr_attendance = self.env['hr.attendance'].search([])
        for employe in employees:
            res = []
            attendance_ids = self.env['hr.attendance'].search([('employee_id','=',employe.id)])
            attendances = self.env['hr.attendance'].search([('employee_id','=',employe.id)])
            for presence in attendances:
                date_in=''
                date_out =''
                time_in=''
                time_out=''
                date=False
                date = presence.date
                if presence.check_in:
                    date_in = presence.check_in
                    time_in = presence.time_in
                if presence.check_out:
                    date_out = presence.check_out
                    time_out = presence.time_out
                for find in attendance_ids.search([('id','!=',presence.id),('employee_id','=',employe.id),('date','=',presence.date)]):
                    if find.date == presence.date:
                        presence.write({'check_in':presence.check_in,'check_out':find.check_out,'time_in':presence.time_in,'time_out':find.time_out})
                    if (find.date == presence.date) and (presence.time_in==False or presence.time_out==False) :
                        presence.unlink()
                        pass
                    else:
                        find.unlink()
                        pass



    @api.depends('date','time_in','time_out')
    def compute_check_in_out(self):
        from datetime import datetime
        for rec in self:
            check_in_tim_first=''
            check_in_tim_last=''
            check_out_tim_first =''
            check_out_tim_last =''
            date1 = ''
            date2 = ''
            # try:
            if rec.date:
                print('')
                start= datetime.strptime(str(rec.date), '%Y-%m-%d')
                if len(str(rec.time_in))>=5:
                    check_in_tim_first= str(rec.time_in)[:2]
                    check_in_tim_last= str(rec.time_in)[3:]
                else:
                    check_in_tim_first= str(rec.time_in)[:1]
                    check_in_tim_last= str(rec.time_in)[2:]

                if len(str(rec.time_out))>=5:
                    check_out_tim_first= str(rec.time_out)[:2]
                    check_out_tim_last= str(rec.time_out)[3:]
                else:
                    check_out_tim_first= str(rec.time_out)[:1]
                    check_out_tim_last= str(rec.time_out)[2:]


                if rec.time_in :
                    date1 = start.replace(hour=int(check_in_tim_first)-1,minute=int(check_in_tim_last))
                if rec.time_out:
                    date2 = start.replace(hour=int(check_out_tim_first)-1,minute=int(check_out_tim_last))
                # raise ValidationError(str(check_in_tim_last))
                rec.check_in = date1
                rec.check_out = date2
                # raise ValidationError(str(date2))
                # date1= datetime.strptime(str(date1), '%Y-%m-%d %H:%M:%S')
                # date2= datetime.strptime(str(date2), '%Y-%m-%d %H:%M:%S')
                # date_compare_AM = start.replace(hour=8,minute=0)
                # date_compare_PM = start.replace(hour=17,minute=0)
                # if date1 <= date_compare_AM and date1 < date_compare_PM :

                #     rec.check_out = False
                # else :

                    # rec.check_in = False
            # except Exception as e:
            #     print('')
    @api.multi
    def name_get(self):
        result = []
        for attendance in self:
            if not attendance.check_out:
                result.append((attendance.id, _("%(empl_name)s from %(check_in)s") % {
                    'empl_name': attendance.employee_id.name,
                    'check_in': attendance.check_in or False#fields.Datetime.to_string(fields.Datetime.context_timestamp(attendance, fields.Datetime.from_string(attendance.check_in))) or False,
                }))
            else:
                result.append((attendance.id, _("%(empl_name)s from %(check_in)s to %(check_out)s") % {
                    'empl_name': attendance.employee_id.name,
                    'check_in': attendance.check_in or False,#fields.Datetime.to_string(fields.Datetime.context_timestamp(attendance, fields.Datetime.from_string(attendance.check_in))) or False,
                    'check_out': attendance.check_out or False #fields.Datetime.to_string(fields.Datetime.context_timestamp(attendance, fields.Datetime.from_string(attendance.check_out))) or False,
                }))
        return result
    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        """ Verifies the validity of the attendance record compared to the others from the same employee.
            For the same employee we must have :
                * maximum 1 "open" attendance record (without check_out)
                * no overlapping time slices with previous employee records
        """
        # for attendance in self:
        #     # we take the latest attendance before our check_in time and check it doesn't overlap with ours
        #     last_attendance_before_check_in = self.env['hr.attendance'].search([
        #         ('employee_id', '=', attendance.employee_id.id),
        #         ('check_in', '<=', attendance.check_in),
        #         ('id', '!=', attendance.id),
        #     ], order='check_in desc', limit=1)
        #     if last_attendance_before_check_in and last_attendance_before_check_in.check_out and last_attendance_before_check_in.check_out > attendance.check_in:
        #         raise exceptions.ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee was already checked in on %(datetime)s") % {
        #             'empl_name': attendance.employee_id.name,
        #             'datetime': fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.from_string(attendance.check_in))),
        #         })
        #
        #     if not attendance.check_out:
        #         # if our attendance is "open" (no check_out), we verify there is no other "open" attendance
        #         no_check_out_attendances = self.env['hr.attendance'].search([
        #             ('employee_id', '=', attendance.employee_id.id),
        #             ('check_out', '=', False),
        #             ('id', '!=', attendance.id),
        #         ], order='check_in desc', limit=1)
        #         if no_check_out_attendances:
        #             raise exceptions.ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee hasn't checked out since %(datetime)s") % {
        #                 'empl_name': attendance.employee_id.name,
        #                 'datetime': fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.from_string(no_check_out_attendances.check_in))),
        #             })
        #     else:
        #         # we verify that the latest attendance with check_in time before our check_out time
        #         # is the same as the one before our check_in time computed before, otherwise it overlaps
        #         last_attendance_before_check_out = self.env['hr.attendance'].search([
        #             ('employee_id', '=', attendance.employee_id.id),
        #             ('check_in', '<', attendance.check_out),
        #             ('id', '!=', attendance.id),
        #         ], order='check_in desc', limit=1)
        #         if last_attendance_before_check_out and last_attendance_before_check_in != last_attendance_before_check_out:
        #             raise exceptions.ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee was already checked in on %(datetime)s") % {
        #                 'empl_name': attendance.employee_id.name,
        #                 'datetime': fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.from_string(last_attendance_before_check_out.check_in))),
        #             })

    @api.depends('check_in', 'check_out')
    def _compute_worked_hours(self):
        for attendance in self:
            if attendance.check_out:
                # delta = attendance.check_out - attendance.check_in
                attendance.worked_hours = 0.0
class ZkMachine(models.Model):
    _name = 'zk.machine'

    name = fields.Char(string='Machine IP', required=True, help="Give the machine IP")
    port_no = fields.Integer(string='Port No', required=True, help="Give the Port number")
    address_id = fields.Many2one('res.partner', string='Working Address', help="Working address")
    company_id = fields.Many2one('res.company', string='Company', help="Company",
                                 default=lambda self: self.env.user.company_id.id)

    def device_connect(self, zk):
        command = CMD_CONNECT
        command_string = ''
        chksum = 0
        session_id = 0
        reply_id = -1 + USHRT_MAX
        buf = zk.createHeader(command, chksum, session_id,
                              reply_id, command_string)
        zk.zkclient.sendto(buf, zk.address)
        try:
            zk.data_recv, addr = zk.zkclient.recvfrom(1024)
            zk.session_id = unpack('HHHH', zk.data_recv[:8])[2]
            command = unpack('HHHH', zk.data_recv[:8])[0]
            if command == 2005:
                conn = True
            else:
                conn = False
        except:
            conn = False
        return conn

    def clear_attendance(self):
        for info in self:
            try:
                machine_ip = info.name
                port = info.port_no
                zk = zklib.ZKLib(machine_ip, port)
                conn = self.device_connect(zk)
                if conn:
                    zk.enableDevice()
                    clear_data = zk.getAttendance()
                    if clear_data:
                        zk.clearAttendance()
                        self._cr.execute("""delete from zk_machine_attendance""")
                    else:
                        raise UserError(_('Unable to get the attendance log, please try again later.'))
                else:
                    raise UserError(_('Unable to connect, please check the parameters and network connections.'))
            except:
                raise ValidationError('Warning !!! Machine is not connected')

    def getSizeUser(self, zk):
        """Checks a returned packet to see if it returned CMD_PREPARE_DATA,
        indicating that data packets are to be sent

        Returns the amount of bytes that are going to be sent"""
        command = unpack('HHHH', zk.data_recv[:8])[0]
        if command == CMD_PREPARE_DATA:
            size = unpack('I', zk.data_recv[8:12])[0]
            return size
        else:
            return False

    def zkgetuser(self, zk):
        """Start a connection with the time clock"""
        command = CMD_USERTEMP_RRQ
        command_string = '\x05'
        chksum = 0
        session_id = zk.session_id
        reply_id = unpack('HHHH', zk.data_recv[:8])[3]
        buf = zk.createHeader(command, chksum, session_id, reply_id, command_string)
        zk.zkclient.sendto(buf, zk.address)
        try:
            zk.data_recv, addr = zk.zkclient.recvfrom(1024)

            if self.getSizeUser(zk):
                bytes = self.getSizeUser(zk)

                while bytes > 0:
                    data_recv, addr = zk.zkclient.recvfrom(1032)
                    zk.userdata.append(data_recv)
                    bytes -= 1024

                zk.session_id = unpack('HHHH', zk.data_recv[:8])[2]
                data_recv = zk.zkclient.recvfrom(8)

            users = {}
            if len(zk.userdata) > 0:
                for x in range(len(zk.userdata)):
                    if x > 0:
                        zk.userdata[x] = zk.userdata[x][8:]
                userdata = b''.join(zk.userdata)
                userdata = userdata[11:]
                while len(userdata) > 72:
                    uid, role, password, name, userid = unpack('2s2s8s28sx31s', userdata.ljust(72)[:72])
                    uid = int(binascii.hexlify(uid), 16)
                    # Clean up some messy characters from the user name
                    password = password.split(b'\x00', 1)[0]
                    password = str(password.strip(b'\x00|\x01\x10x|\x000').decode('utf-8'))
                    # uid = uid.split('\x00', 1)[0]
                    userid = str(userid.strip(b'\x00|\x01\x10x|\x000|\x9aC').decode('utf-8'))
                    name = name.split(b'\x00', 1)[0].decode('utf-8')
                    if name.strip() == "":
                        name = uid
                    users[uid] = (userid, name, int(binascii.hexlify(role), 16), password)
                    userdata = userdata[72:]
            return users
        except:
            return False

    @api.model
    def cron_download(self):
        machines = self.env['zk.machine'].search([])
        for machine in machines:
            machine.download_attendance()

    def download_attendance(self):
        _logger.info("++++++++++++Cron Executed++++++++++++++++++++++")
        zk_attendance = self.env['zk.machine.attendance']
        att_obj = self.env['hr.attendance']
        for info in self:
            machine_ip = info.name
            port = info.port_no
            zk = zklib.ZKLib(machine_ip, port)
            conn = self.device_connect(zk)
            raise ValidationError(str(conn))
            if conn:
                zk.enableDevice()
                user = self.zkgetuser(zk)
                command = CMD_ATTLOG_RRQ
                command_string = ''
                chksum = 0
                session_id = zk.session_id
                reply_id = unpack('HHHH', zk.data_recv[:8])[3]
                buf = zk.createHeader(command, chksum, session_id,
                                      reply_id, command_string)
                zk.zkclient.sendto(buf, zk.address)
                try:
                    zk.data_recv, addr = zk.zkclient.recvfrom(1024)
                    command = unpack('HHHH', zk.data_recv[:8])[0]
                    if command == CMD_PREPARE_DATA:
                        size = unpack('I', zk.data_recv[8:12])[0]
                        zk_size = size
                    else:
                        zk_size = False
                    if zk_size:
                        bytes = zk_size
                        while bytes > 0:
                            data_recv, addr = zk.zkclient.recvfrom(1032)
                            zk.attendancedata.append(data_recv)
                            bytes -= 1024
                        zk.session_id = unpack('HHHH', zk.data_recv[:8])[2]
                        data_recv = zk.zkclient.recvfrom(8)
                    attendance = []
                    if len(zk.attendancedata) > 0:
                        # The first 4 bytes don't seem to be related to the user
                        for x in range(len(zk.attendancedata)):
                            if x > 0:
                                zk.attendancedata[x] = zk.attendancedata[x][8:]
                        attendancedata = b''.join(zk.attendancedata)
                        attendancedata = attendancedata[14:]
                        while len(attendancedata) > 0:
                            uid, state, timestamp, space = unpack('24s1s4s11s', attendancedata.ljust(40)[:40])
                            pls = unpack('c', attendancedata[29:30])
                            uid = uid.split(b'\x00', 1)[0].decode('utf-8')
                            tmp = ''
                            for i in reversed(range(int(len(binascii.hexlify(timestamp)) / 2))):
                                tmp += binascii.hexlify(timestamp).decode('utf-8')[i * 2:(i * 2) + 2]
                            attendance.append((uid, int(binascii.hexlify(state), 16),
                                               decode_time(int(tmp, 16)), unpack('HHHH', space[:8])[0]))

                            attendancedata = attendancedata[40:]
                except Exception as e:
                    _logger.info("++++++++++++Exception++++++++++++++++++++++", e)
                    attendance = False
                if attendance:
                    for each in attendance:
                        atten_time = each[2]
                        atten_time = datetime.strptime(
                            atten_time.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
                        local_tz = pytz.timezone(
                            self.env.user.partner_id.tz or 'GMT')
                        local_dt = local_tz.localize(atten_time, is_dst=None)
                        utc_dt = local_dt.astimezone(pytz.utc)
                        utc_dt = utc_dt.strftime("%Y-%m-%d %H:%M:%S")
                        atten_time = datetime.strptime(
                            utc_dt, "%Y-%m-%d %H:%M:%S")
                        atten_time = fields.Datetime.to_string(atten_time)
                        if user:
                            for uid in user:
                                if user[uid][0] == str(each[0]):
                                    get_user_id = self.env['hr.employee'].search(
                                        [('device_id', '=', str(each[0]))])
                                    if get_user_id:
                                        duplicate_atten_ids = zk_attendance.search(
                                            [('device_id', '=', str(each[0])), ('punching_time', '=', atten_time)])
                                        if duplicate_atten_ids:
                                            continue
                                        else:
                                            zk_attendance.create({'employee_id': get_user_id.id,
                                                                  'device_id': each[0],
                                                                  'attendance_type': str(each[1]),
                                                                  'punch_type': str(each[3]),
                                                                  'punching_time': atten_time,
                                                                  'address_id': info.address_id.id})
                                            att_var = att_obj.search([('employee_id', '=', get_user_id.id),
                                                                      ('check_out', '=', False)])
                                            if each[3] == 0:  # check-in
                                                if not att_var:
                                                    att_obj.create({'employee_id': get_user_id.id,
                                                                    'check_in': atten_time})
                                            if each[3] == 1:  # check-out
                                                if len(att_var) == 1:
                                                    att_var.write({'check_out': atten_time})
                                                else:
                                                    att_var1 = att_obj.search([('employee_id', '=', get_user_id.id)])
                                                    if att_var1:
                                                        att_var1[-1].write({'check_out': atten_time})

                                    else:
                                        employee = self.env['hr.employee'].create(
                                            {'device_id': str(each[0]), 'name': user[uid][1]})
                                        zk_attendance.create({'employee_id': employee.id,
                                                              'device_id': each[0],
                                                              'attendance_type': str(each[1]),
                                                              'punch_type': str(each[3]),
                                                              'punching_time': atten_time,
                                                              'address_id': info.address_id.id})
                                        att_obj.create({'employee_id': employee.id,
                                                        'check_in': atten_time})
                                else:
                                    pass
                    zk.enableDevice()
                    zk.disconnect()
                    return True
                else:
                    raise UserError(_('Unable to get the attendance log, please try again later.'))
            else:
                raise UserError(_('Unable to connect, please check the parameters and network connections.'))
