import pandas as pd
from datetime import datetime
import io
from enum import Enum

# Constants

STUDENT_NOT_FOUND = -1
STUDENT_CONFIRMED = -2
STUDENT_ALREADY_CONFIRMED = -3
STUDENT_ALREADY_ON_BREAK = -4

FUNC_SUCCESS = 0


class ManualConfirmReason(Enum):
    FACEREC = 'Face not recognized'
    PIC = "No picture in system"
    TIME = "Time Circumstances"
    OTHER = "Other"


class StudentManager:
    def __init__(self):
        # Attendance and Confirmation

        self.students_attendance = {}  # tracks current state of exam attendance
        self.students_manual_confirm = {}  # students manually confirmed - will contain the reason
        self.students_auto_confirm = {}  # students auto confirmed

        self.manual_confirm_hist = {attr.value: 0 for attr in ManualConfirmReason}

        # Waiver

        self.students_waiver = []

        # Notes

        self.student_notes = {}
        self.notes_count = 0

        # Breaks

        self.students_breaks = {}  # contains: [number of breaks, list of time(seconds) and list of reasons for each break]
        self.current_break = {}  # contains : [timestamp of current break]

        self.dtype_dict = {
            "id": str,  # Specify 'id' column as string to preserve leading zeros
            "first_name": str,
            "last_name": str,
            "extra_time": str,
            "tuition": str,
            "major": str
        }

        self.table_df = pd.DataFrame(columns=list(self.dtype_dict.keys()))

        # print(table_df.loc[table_df['ID']=='002', 'First Name'].values[0])

        '''def get_csv():
            table_df.to_csv('output.csv', index=False)'''

    # initiate attendance
    def student_data_initiate(self):
        list_id = self.table_df['id'].tolist()
        for i in list_id:
            self.students_attendance[i] = False

    # CHECKING CSV FILE STRUCTURE

    def check_csv_struct(self):
        # Get the columns from the DataFrame
        df_columns = self.table_df.columns
        # Get the keys from the dtype dictionary
        dtype_keys = self.dtype_dict.keys()
        # Check if the columns match the keys in the dtype dictionary
        if set(df_columns) == set(dtype_keys):
            return True
        else:
            return False

    # READING CSV FILE

    def read_students_blob(self, csv_data):
        try:
            self.table_df = pd.read_csv(io.BytesIO(csv_data), dtype=self.dtype_dict)
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return False
        return True

    def read_students_csv(self, filepath):
        try:
            self.table_df = pd.read_csv(filepath, dtype=self.dtype_dict)
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return False
        return True

    # DATAFRAME GET

    def get_student_df_ref(self):
        return self.table_df

    def student_table_values(self):
        return self.table_df.values.tolist()

    def student_table_columns(self):
        return self.table_df.columns.tolist()

    def student_table_ids(self):
        return self.table_df['id'].tolist()

    # Student GET Functions
    def student_get_name(self, student_id):
        temp_first = "No"
        temp_last = "Name"
        if student_id in self.table_df['id'].values:
            temp_first = self.table_df.loc[self.table_df['id'] == student_id, 'first_name'].values[0]
            temp_last = self.table_df.loc[self.table_df['id'] == student_id, 'last_name'].values[0]
        return temp_first + ' ' + temp_last

    def student_get_extra_time(self, student_id):
        temp_first = "No"
        if student_id in self.table_df['id'].values:
            temp_first = self.table_df.loc[self.table_df['id'] == student_id, 'extra_time'].values[0]
        return temp_first

    def student_get_tuition(self, student_id):
        temp_first = "No"
        if student_id in self.table_df['id'].values:
            temp_first = self.table_df.loc[self.table_df['id'] == student_id, 'tuition'].values[0]
        return temp_first

    def student_get_major(self, student_id):
        temp_first = "No Major"
        if student_id in self.table_df['id'].values:
            temp_first = self.table_df.loc[self.table_df['id'] == student_id, 'major'].values[0]
        return temp_first

    # Attendance Functions: Confirm or Check
    def student_confirm_attendance(self, student_id):
        if student_id in self.students_attendance.keys():
            if self.students_attendance[student_id]:
                return STUDENT_ALREADY_CONFIRMED
            else:
                self.students_attendance[student_id] = True
                return STUDENT_CONFIRMED
        else:
            return STUDENT_NOT_FOUND

    def student_auto_confirm_attendance(self, student_id):
        res = self.student_confirm_attendance(student_id)
        if res != STUDENT_CONFIRMED:
            return res
        else:
            self.students_auto_confirm[student_id] = True
            return res

    def student_manual_confirm_attendance(self, student_id, reason):
        res = self.student_confirm_attendance(student_id)
        if res != STUDENT_CONFIRMED:
            return res
        else:
            self.students_manual_confirm[student_id] = reason
            # Check if reason matches any enum value
            if reason in [member.value for member in ManualConfirmReason]:
                self.manual_confirm_hist[reason] += 1
            else:
                self.manual_confirm_hist[ManualConfirmReason.OTHER.value] += 1
        return res

    def get_manual_confirm_hist(self):
        return self.manual_confirm_hist

    def student_cancel_attendance(self, student_id):
        if student_id in self.students_attendance.keys():
            self.students_attendance[student_id] = False
            return FUNC_SUCCESS
        return STUDENT_NOT_FOUND

    def student_check_attendance(self, student_id):
        if student_id in self.students_attendance.keys():
            return self.students_attendance[student_id]
        return False

    def student_check_manual_attendance(self, student_id):
        if student_id in self.students_manual_confirm.keys():
            return True
        return False

    def student_check_manual_reason(self, student_id):
        if self.student_check_manual_attendance(student_id):
            return self.students_manual_confirm[student_id]
        else:
            return None

    # Break functions

    def student_in_break(self, student_id):  # Student currently on a break
        if not self.student_check_attendance(student_id):
            return False
        if student_id in self.current_break.keys():
            return True
        return False

    def student_had_break(self, student_id):  # Student had a break before
        if student_id in self.students_breaks.keys():
            return True
        return False

    def student_report_break(self, student_id, reason):
        if not self.student_check_attendance(student_id):
            return STUDENT_NOT_FOUND
        elif self.student_in_break(student_id):
            return STUDENT_ALREADY_ON_BREAK
        if student_id in self.students_breaks:
            self.students_breaks[student_id][0] += 1
            self.students_breaks[student_id][2].append(reason)
        else:
            self.students_breaks[student_id] = [1, [], []]
            self.students_breaks[student_id][2].append(reason)
        self.current_break[student_id] = datetime.now()
        return FUNC_SUCCESS

    def student_back_break(self, student_id):  # Student back from break
        if not self.student_check_attendance(student_id):
            return STUDENT_NOT_FOUND
        elif not self.student_in_break(student_id):
            return STUDENT_NOT_FOUND
        cur_time = datetime.now()
        dif = cur_time - self.current_break[student_id]
        self.students_breaks[student_id][1].append(int(dif.total_seconds()))
        total_time = divmod(dif.total_seconds(), 60)
        total_time_string = 'Total Break time: ' + str(int(total_time[0])) + ' minutes ' + str(int(total_time[1])) + ' seconds'
        del self.current_break[student_id]
        return total_time_string

    def student_total_break_time(self, student_id):
        if not self.student_had_break(student_id):
            return STUDENT_NOT_FOUND
        return sum(self.students_breaks[student_id][1])

    def student_total_breaks(self, student_id):
        if not self.student_had_break(student_id):
            return STUDENT_NOT_FOUND
        return self.students_breaks[student_id][0]

    # Notes functions

    def student_report_note(self, student_id):
        if student_id in self.student_notes:
            # If the student exists, increment notes value by 1
            self.student_notes[student_id] += 1
        else:
            # otherwise, initiate
            self.student_notes[student_id] = 1
        self.notes_count += 1

    def get_notes_count(self):
        return self.notes_count

    # Waiver functions

    def student_report_waiver(self, student_id):
        if not self.student_check_attendance(student_id):
            return STUDENT_NOT_FOUND
        self.student_cancel_attendance(student_id)
        self.students_waiver.append(student_id)
        return FUNC_SUCCESS

    def student_undo_waiver(self, student_id):
        if self.student_check_attendance(student_id):
            return STUDENT_ALREADY_CONFIRMED
        if self.student_confirm_attendance(student_id) != STUDENT_CONFIRMED:
            return STUDENT_NOT_FOUND
        self.students_waiver.remove(student_id)
        return FUNC_SUCCESS

    def student_check_waiver(self, student_id):
        if student_id in self.students_waiver:
            return True
        return False


students = StudentManager()


