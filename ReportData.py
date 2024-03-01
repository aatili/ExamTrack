
import ExamConfig
import StudentData


class ReportData:
    def __init__(self):
        self.exam = None
        self.students = None
        self.exam_number = None
        self.term = None
        self.date = None
        self.duration = None
        self.added_time = None
        self.waiver_available = None
        self.enlisted_count = None
        self.attendance_count = None
        self.auto_confirm_count = None
        self.manual_confirm_count = None
        self.manual_confirm_hist = None
        self.waiver_count = None
        self.notes_count = None
        self.breaks_count = None
        self.avg_break_time = None
        self.notes_hist = None
        self.breaks_reasons_hist = None
        self.breaks_time_hist = None

    def create_new_report(self):

        self.exam = ExamConfig.cur_exam
        self.students = StudentData.students

        # Exam Related Attributes
        self.exam_number = self.exam.get_exam_number()
        self.term = self.exam.get_exam_term()
        self.date = self.exam.get_exam_date()
        self.duration = self.exam.get_exam_duration()
        self.added_time = self.exam.get_exam_added_time()
        self.waiver_available = self.exam.is_waiver_available()

        # Students Related Attributes
        self.enlisted_count = self.students.get_students_count()
        self.attendance_count = self.students.get_students_attendance_count()
        self.auto_confirm_count = self.students.get_auto_confirm_count()
        self.manual_confirm_count = self.students.get_manual_confirm_count()
        self.manual_confirm_hist = self.students.get_manual_confirm_hist()
        self.waiver_count = self.students.get_waiver_count()
        self.notes_count = self.students.get_notes_count()
        self.breaks_count = self.students.get_breaks_count()
        self.avg_break_time = self.students.get_avg_break_time()
        self.notes_hist = self.students.get_notes_hist()
        self.breaks_reasons_hist = self.students.get_breaks_reasons_hist()
        self.breaks_time_hist = self.students.get_breaks_time_hist()

    # Getter methods

    def get_exam_number(self):
        return self.exam_number

    def get_term(self):
        return self.term

    def get_date(self):
        return self.date

    def get_duration(self):
        return self.duration

    def get_added_time(self):
        return self.added_time

    def is_waiver_available(self):
        return self.waiver_available

    def get_enlisted_count(self):
        return self.enlisted_count

    def get_attendance_count(self):
        return self.attendance_count

    def get_auto_confirm_count(self):
        return self.auto_confirm_count

    def get_manual_confirm_count(self):
        return self.manual_confirm_count

    def get_manual_confirm_hist(self):
        return self.manual_confirm_hist

    def get_waiver_count(self):
        return self.waiver_count

    def get_notes_count(self):
        return self.notes_count

    def get_breaks_count(self):
        return self.breaks_count

    def get_avg_break_time(self):
        return self.avg_break_time

    def get_notes_hist(self):
        return self.notes_hist

    def get_breaks_reasons_hist(self):
        return self.breaks_reasons_hist

    def get_breaks_time_hist(self):
        return self.breaks_time_hist


cur_report = ReportData()
