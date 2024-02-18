class ExamConfig:

    def __init__(self, number=None, duration=None, term=None, supervisors=[], camera_no=None):
        self.exam_number = number
        self.exam_duration = duration
        self.exam_term = term
        self.exam_supervisors = list(supervisors)
        self.exam_camera = camera_no

        self.added_time = 0
        self.waiver_available = False

    def get_exam_number(self):
        return self.exam_number

    def get_exam_duration(self):
        return self.exam_duration

    def get_exam_term(self):
        return self.exam_term

    def get_exam_supervisors(self):
        return self.exam_supervisors

    def get_exam_camera(self):
        return self.exam_camera

    def is_waiver_available(self):
        return self.waiver_available

    def add_time(self, duration):
        self.added_time += duration

    def set_all(self, number, duration, term, supervisors, camera_no):
        self.exam_number = number
        self.exam_duration = duration
        self.exam_term = term
        self.exam_supervisors = list(supervisors)
        self.exam_camera = camera_no

        self.waiver_available = False
        if term.lower() == 'moedb' or term.lower() == 'special':
            self.waiver_available = True


cur_exam = ExamConfig()
