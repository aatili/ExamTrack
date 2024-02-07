# Table data
import pandas as pd

table_columns =  ["ID", "First Name", "Last_Name", "ExtraTime", "Tuition", "Confirmed"]
table_data = [    
    ["243731", "Adnan", "Atili", "No" , "Yes", "No"],
    ["777777", "John", "Doe", "Yes", "No", "Yes"],
    ["002", "Jane", "Smith", "No", "Yes", "No"],
    ["963852", "Michael", "Johnson", "Yes", "Yes", "Yes"],
    ["112233", "Emily", "Williams", "No", "No", "Yes"],
    ["005", "David", "Brown", "Yes", "Yes", "No"]
]
table_df = pd.DataFrame(table_data, columns=table_columns)

#print(table_df.loc[table_df['ID']=='002', 'First Name'].values[0])

#print(table_df.columns.tolist())

#print(table_df.values.tolist())

attendance = {}
for i in table_data:
    attendance[i[0]] = 0


def confirm_attendace(id):
    attendance[id] = 1


def check_attendance(id):
    return attendance[id]

