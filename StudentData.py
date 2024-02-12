# Table data
import pandas as pd
from datetime import datetime

# Constants

STUDENT_NOT_FOUND = -1
STUDENT_CONFIRMED = 0
STUDENT_ALREADY_CONFIRMED = -3

FUNC_SUCCESS = 1

# Attendance and Confirmation

students_attendance = {}  # exam attendance
students_manual_confirm = {}  # students manually confirmed - will contain the reason
students_auto_confirm = {}  # students auto confirmed

# Notes

# Breaks

students_breaks = {}  # contains: [number of breaks, list of time and list of reasons for each break]
current_break = {}  # contains : [timestamp of current break]

# Sample data

table_columns = ["id", "first_name", "last_name", "extra_time", "tuition", "major"]
table_data = [
    ["243731", "Adnan", "Atili", "No", "Yes", "Information Systems"],
    ["777777", "John", "Doe", "Yes", "No", "Art"],
    ["002", "Jane", "Smith", "No", "Yes", "Biology"],
    ["963852", "Michael", "Johnson", "Yes", "Yes", "Computer Science"],
    ["112233", "Haya", "Shalash", "No", "No", "Information Systems"],
    ["005", "David", "Brown", "Yes", "Yes", "Computer Science"]
]
table_df = pd.DataFrame(table_data, columns=table_columns)

# print(table_df.loc[table_df['ID']=='002', 'First Name'].values[0])

# print(table_df.columns.tolist())

# print(table_df.values.tolist())

# initiate attendance
for i in table_data:
    students_attendance[i[0]] = False


def student_get_name(student_id):
    temp_first = "No"
    temp_last = "Name"
    if student_id in table_df['id'].values:
        temp_first = table_df.loc[table_df['id'] == student_id, 'first_name'].values[0]
        temp_last = table_df.loc[table_df['id'] == student_id, 'last_name'].values[0]
    return temp_first + ' ' + temp_last


# GET Functions

def student_get_extra_time(student_id):
    temp_first = "No"
    if student_id in table_df['id'].values:
        temp_first = table_df.loc[table_df['id'] == student_id, 'extra_time'].values[0]
    return temp_first


def student_get_tuition(student_id):
    temp_first = "No"
    if student_id in table_df['id'].values:
        temp_first = table_df.loc[table_df['id'] == student_id, 'tuition'].values[0]
    return temp_first


def student_get_major(student_id):
    temp_first = "No Major"
    if student_id in table_df['id'].values:
        temp_first = table_df.loc[table_df['id'] == student_id, 'major'].values[0]
    return temp_first


# Attendance Functions: Confirm or Check

def student_confirm_attendance(student_id):
    if student_id in students_attendance.keys():
        if students_attendance[student_id]:
            return STUDENT_ALREADY_CONFIRMED
        else:
            students_attendance[student_id] = True
            return STUDENT_CONFIRMED
    else:
        return STUDENT_NOT_FOUND


def student_auto_confirm_attendance(student_id):
    res = student_confirm_attendance(student_id)
    if res != STUDENT_CONFIRMED:
        return res
    else:
        students_auto_confirm[student_id] = True
        return res


def student_manual_confirm_attendance(student_id, reason):
    res = student_confirm_attendance(student_id)
    if res != STUDENT_CONFIRMED:
        return res
    else:
        students_manual_confirm[student_id] = reason
        return res


def student_check_attendance(student_id):
    if student_id in students_attendance.keys():
        return students_attendance[student_id]
    return False


def student_check_manual_attendance(student_id):
    if student_id in students_manual_confirm.keys():
        return True
    return False


def student_check_manual_reason(student_id):
    if student_check_manual_attendance(student_id):
        return students_manual_confirm[student_id]
    else:
        return None

# Break functions

def student_in_break(student_id):  # Student currently on a break
    if not student_check_attendance(student_id):
        return False
    if student_id in current_break.keys():
        return True
    return False


def student_had_break(student_id):  # Student had a break before
    if not student_check_attendance(student_id):
        return False
    if student_id in students_breaks.keys():
        return True
    return False


def student_report_break(student_id, reason):
    if not student_check_attendance(student_id):
        return STUDENT_NOT_FOUND
    elif student_in_break(student_id):
        return STUDENT_ALREADY_CONFIRMED
    if student_id in students_breaks:
        students_breaks[student_id][0] += 1
        students_breaks[student_id][2].append(reason)
    else:
        students_breaks[student_id] = [1, [], []]
        students_breaks[student_id][2].append(reason)
    current_break[student_id] = datetime.now()
    return FUNC_SUCCESS


def student_back_break(student_id):  # Student back from break
    if not student_check_attendance(student_id):
        return STUDENT_NOT_FOUND
    elif not student_in_break(student_id):
        return STUDENT_ALREADY_CONFIRMED
    cur_time = datetime.now()
    dif = cur_time - current_break[student_id]
    students_breaks[student_id][1].append(round(dif.total_seconds() / 60,2))
    del current_break[student_id]
    return FUNC_SUCCESS
