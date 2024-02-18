import pandas as pd
from datetime import datetime
import io

# Constants

STUDENT_NOT_FOUND = -1
STUDENT_CONFIRMED = -2
STUDENT_ALREADY_CONFIRMED = -3
STUDENT_ALREADY_ON_BREAK = -4

FUNC_SUCCESS = 0


# Attendance and Confirmation

students_attendance = {}  # tracks current state of exam attendance
students_manual_confirm = {}  # students manually confirmed - will contain the reason
students_auto_confirm = {}  # students auto confirmed

# Waiver

students_waiver = []

# Notes

# Breaks

students_breaks = {}  # contains: [number of breaks, list of time(seconds) and list of reasons for each break]
current_break = {}  # contains : [timestamp of current break]


df_list = []

# print(table_df.loc[table_df['ID']=='002', 'First Name'].values[0])



'''def get_csv():
    table_df.to_csv('output.csv', index=False)'''


# initiate attendance
def student_data_initiate():
    list_id = df_list[0]['id'].tolist()
    for i in list_id:
        students_attendance[i] = False


dtype_dict = {
    "id": str,  # Specify 'id' column as string to preserve leading zeros
    "first_name": str,
    "last_name": str,
    "extra_time": str,
    "tuition": str,
    "major": str
}


def student_table_values():
    if len(df_list) == 0:
        return None
    return df_list[0].values.tolist()


def student_table_columns():
    if len(df_list) == 0:
        return None
    return df_list[0].columns.tolist()


def read_students_blob(csv_data):
    try:
        df_list.insert(0, pd.read_csv(io.BytesIO(csv_data), dtype=dtype_dict))
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return False
    return True


def read_students_csv(filepath):
    try:
        df_list.insert(0, pd.read_csv(filepath, dtype=dtype_dict))
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return False
    return True


def get_student_df_ref():
    if len(df_list) == 0:
        return None
    return df_list[0]


# GET Functions
def student_get_name(student_id):
    table_df = df_list[0]
    temp_first = "No"
    temp_last = "Name"
    if student_id in table_df['id'].values:
        temp_first = table_df.loc[table_df['id'] == student_id, 'first_name'].values[0]
        temp_last = table_df.loc[table_df['id'] == student_id, 'last_name'].values[0]
    return temp_first + ' ' + temp_last


def student_get_extra_time(student_id):
    table_df = df_list[0]
    temp_first = "No"
    if student_id in table_df['id'].values:
        temp_first = table_df.loc[table_df['id'] == student_id, 'extra_time'].values[0]
    return temp_first


def student_get_tuition(student_id):
    table_df = df_list[0]
    temp_first = "No"
    if student_id in table_df['id'].values:
        temp_first = table_df.loc[table_df['id'] == student_id, 'tuition'].values[0]
    return temp_first


def student_get_major(student_id):
    table_df = df_list[0]
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


def student_cancel_attendance(student_id):
    if student_id in students_attendance.keys():
        students_attendance[student_id] = False
        return FUNC_SUCCESS
    return STUDENT_NOT_FOUND


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
    if student_id in students_breaks.keys():
        return True
    return False


def student_report_break(student_id, reason):
    if not student_check_attendance(student_id):
        return STUDENT_NOT_FOUND
    elif student_in_break(student_id):
        return STUDENT_ALREADY_ON_BREAK
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
        return STUDENT_NOT_FOUND
    cur_time = datetime.now()
    dif = cur_time - current_break[student_id]
    students_breaks[student_id][1].append(int(dif.total_seconds()))
    total_time = divmod(dif.total_seconds(), 60)
    total_time_string = 'Total Break time: ' + str(int(total_time[0])) + ' minutes ' + str(int(total_time[1])) + ' seconds'
    del current_break[student_id]
    return total_time_string


def student_total_break_time(student_id):
    if not student_had_break(student_id):
        return STUDENT_NOT_FOUND
    return sum(students_breaks[student_id][1])


def student_total_breaks(student_id):
    if not student_had_break(student_id):
        return STUDENT_NOT_FOUND
    return students_breaks[student_id][0]


# Waiver functions

def student_report_waiver(student_id):
    if not student_check_attendance(student_id):
        return STUDENT_NOT_FOUND
    student_cancel_attendance(student_id)
    students_waiver.append(student_id)


def student_check_waiver(student_id):
    if student_id in students_waiver:
        return True
    return False

