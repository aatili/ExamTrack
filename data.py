# Table data
import pandas as pd

table_columns =  ["id", "first_name", "last_name", "extra_time", "tuition","major"]
table_data = [    
    ["243731", "Adnan", "Atili", "No" , "Yes","Information Systems"],
    ["777777", "John", "Doe", "Yes", "No","Art"],
    ["002", "Jane", "Smith", "No", "Yes","Biology"],
    ["963852", "Michael", "Johnson", "Yes", "Yes","Computer Science"],
    ["112233", "Haya", "Shalash", "No", "No","Information Systems"],
    ["005", "David", "Brown", "Yes", "Yes","Computer Science"]
]
table_df = pd.DataFrame(table_data, columns=table_columns)

#print(table_df.loc[table_df['ID']=='002', 'First Name'].values[0])

#print(table_df.columns.tolist())

#print(table_df.values.tolist())

def student_get_name(student_id):
    temp_first = "No"
    temp_last = "Name"
    if student_id in table_df['id'].values:
        temp_first = table_df.loc[table_df['id']==student_id, 'first_name'].values[0]
        temp_last = table_df.loc[table_df['id']==student_id, 'last_name'].values[0]
    return temp_first + ' ' + temp_last

def student_get_extra_time(student_id):
    temp_first = "No"
    if student_id in table_df['id'].values:
        temp_first = table_df.loc[table_df['id']==student_id, 'extra_time'].values[0]
    return temp_first

def student_get_tuition(student_id):
    temp_first = "No"
    if student_id in table_df['id'].values:
        temp_first = table_df.loc[table_df['id']==student_id, 'tuition'].values[0]
    return temp_first

def student_get_major(student_id):
    temp_first = "No Major"
    if student_id in table_df['id'].values:
        temp_first = table_df.loc[table_df['id']==student_id, 'major'].values[0]
    return temp_first



# exam attendance
attendance = {}
for i in table_data:
    attendance[i[0]] = 0


def confirm_attendace(id):
    attendance[id] = 1


def check_attendance(id):
    return attendance[id]

