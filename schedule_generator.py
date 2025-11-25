# variables = courses
# domain = teachers, timings, day,
# constraints = courses=teachers, courses.timing =/= courses.timing, courses=day, 
# where teachers are the ones choosen by students and days are also the one chosen by students.

# courses is a list of all the courses choosen
# time_slot indicate when the class starts
# day is the day of the week
# teacher choosen for that course
# lab is boolean checking whether the said class is a lab or not

import constraint_cl as csp
from datetime import datetime, time
import copy
import sample_data as sample
import schedule_parser as parser

def model(course_name):
    course_name: str
    teacher: str
    days: tuple[str,str]
    time_start: str
    time_end: str
    code: int
    hasLab: bool
    

    course_details=[]
    for i in range(100):
        course_details.append(((course_name, teacher, days, time_start, time_end, code),hasLab))

    return course_details

def complete_list():
    # file_path = "Spring Schedule 2025.xlsx"

    # courses = parser.parse_schedule(file_path)
    # print(courses)
    course_details = sample.sample_data()
    domain=[]

    for classes, hasLab in course_details:
        course_name=classes[0]
        teacher=classes[1]
        days=classes[2]
        time_start= classes[3]
        time_end= classes[4]
        code=classes[5]

        class_details = (course_name, teacher, days, time_start, time_end, code)
        domain.append([class_details, hasLab])

    return domain

def gui_filters(pref_list, preferred_day_start, preferred_day_end, preferred_days):
    
    teacher_preference={}

    for teachers in pref_list:
        course = teachers[0]
        teacher_preference[course]=[]
        teacher_preference[course]=teachers[1:]

    return (teacher_preference, preferred_day_start, preferred_day_end, preferred_days)


class ScheduleSolver:
    def __init__(self, courses_needed, teacher_preference, preferred_day_start, preferred_day_end, preferred_days):
        self.courses=courses_needed   # variable
        classes=[]                      # extracts the list of all the classes of theory & lab of a course
        classes=complete_list()             # extracting all classes of a course
        # print(classes)
        all_cls = {}
        all_theories = {}
        all_labs = {}
        # print("classes: ", classes)
        self.all_classes={}          # domain -> all_classes=  { "information security": [((theory_class), (lab_class))] }
        
        for course in self.courses:
             for cl in classes:
                if course not in all_cls:
                    all_cls[course]=[]
                if course in cl[0][0]:
                     all_cls[course].append(cl)


        # for course in self.courses:
        #     print(course)
        #     for cl in all_cls[course]:
        #          print(cl[0])

        for course in self.courses:
             for cl in all_cls[course]:

                if course not in all_labs:
                    all_labs[course]=[]

                if cl[1]:
                    all_labs[course].append(cl)

                if course not in all_theories:
                    all_theories[course]=[]
                
                if not cl[1]:
                     all_theories[course].append(cl)  
        # for course in self.courses:
        #     print(course)
        #     for cl, _ in all_labs[course]:
        #         print(cl)
                
        # for key in all_theories.keys():
        #     if key in all_labs and len(all_labs[key]) != 0:
        #         print(key)
        #         for cl in all_theories[key]:
        #             cl[1] = True

        # for course in self.courses:
        #     print(course)
        #     for lab in all_labs[course]:
        #         print(lab[0])
        #     for theory in all_theories[course]:
        #          print(theory[0])

        for course in self.courses:     # assigning domain to each variable
            for theory_class in all_theories[course]:
                if course not in self.all_classes:
                    self.all_classes[course] = []       # initializing the list of class_details of a course
                
                if theory_class[1]:                  # if course has lab
                        
                    # Pair each theory class with each lab option
                        for lab in all_labs[course]:
                            if theory_class[0][5]==lab[0][5]:  # checking the class code to ensure the right lab is given to right theory class
                                    self.all_classes[course].append((theory_class[0], lab[0]))   # forming domain as dictionary of a list of tuple thoery_class and lab, where theory & lab is a tuple of class_details
                    
                else:                       # if course doesn't have lab
                    self.all_classes[course].append((theory_class[0], None))  # form a tuple of theory class with none, and then putting it in a list of all possible classes of that course
        # print()
        # for course in self.courses:
        #     print(course, ":")
        #     print()
        #     for cls in self.all_classes[course]:
        #      print(cls[0])
        #      print(cls[1])
             

        
        # print("initial domain")
        # print(self.all_classes)
        # print("final domain")

        self.CSP = csp.CSP(self.courses, self.all_classes)

        self.pr_teachers={}
        self.teacher_priority = {}           # marks teacher preference
        preference_details=gui_filters(teacher_preference, preferred_day_start, preferred_day_end, preferred_days)

        for course in self.courses:
            if course not in self.teacher_priority:
                self.teacher_priority[course]=[]
            for teachers in preference_details[0][course]:  # dictionary of teacher preferences with string->string
                self.teacher_priority[course].append(teachers)

        self.copy_all_classes = copy.deepcopy(self.all_classes)

        
        self.pr_day_begin=preference_details[1]         # datetime variable
        self.pr_day_end=preference_details[2]           # datetime variable
        self.pr_days=preference_details[3]              # string

    def teacher_preference(self, course):                         # strong soft constraint of teacher preference   
        
        if not self.teacher_priority[course]:
            return self.copy_all_classes[course]
        
        filtered = []
        for teacher in self.teacher_priority[course]:

            for cl in self.copy_all_classes[course]:
                theory_teacher=cl[0][1]
                if theory_teacher == teacher:
                    filtered.append(cl)


        if filtered:
            self.all_classes[course] = copy.deepcopy(filtered)   
            return True
        # else:
        #     return self.teacher_preference(course) if self.teacher_priority[course] else False

        return False
        
    

    def reordering(self): 
        for course in self.courses:                              # weak soft constraints of time and day preference
            self.all_classes[course].sort(key=lambda x: (self.lambda_func(x)))
    

    def lambda_func(self, x):
        theory_time_pr = 0 if self.pr_day_begin <= x[0][3] and x[0][4] <= self.pr_day_end else 1    # if theory class is in preferred time
        theory_day = 0 if x[0][2][0] in self.pr_days or x[0][2][1] in self.pr_days else 1           # if theory class in preferred day
        
        if x[1] != None:                                                                            # if lab
            lab_time_pr = 0 if self.pr_day_begin <= x[1][3] and x[1][4] <= self.pr_day_end else 1   # if lab in preferred time
            lab_day_pr = 0 if x[1][2][0] in self.pr_days or x[1][2][1] in self.pr_days else 1       # if lab in preferred day
        else:
            lab_time_pr = 1
            lab_day_pr = 1

        return (theory_time_pr, theory_day, lab_time_pr, lab_day_pr)    # priority given to theory time, then theory days, then lab time, then lab days

    def avoid_clashes(self, value1, value2):

        course1 = ""
        course2 = ""

        for course in self.courses:
            if course in value1[0][0]:
                course1 = course
            if course in value2[0][0]:
                course2 = course

        theory_1_day = value1[0][2]            
        theory_2_day = value2[0][2]

        theory_1_start = value1[0][3]
        theory_1_end = value1[0][4]

        theory_2_start = value2[0][3]
        theory_2_end = value2[0][4]

        if theory_1_day[0] in theory_2_day or theory_1_day[1] in theory_2_day:      # if clashes in day of theory classes
            if theory_1_start < theory_2_end and theory_2_start < theory_1_end:     # if clashes in time " " "
                # self.all_classes[course2].remove(value2)
                return False
                
        if value1[1] != None and value2[1] == None:       # if course 1 has lab and course 2 does not
            lab_1_day = value1[1][2]
            lab_1_start = value1[1][3]
            lab_1_end = value1[1][4]
            if lab_1_day[0] in theory_2_day or lab_1_day[1] in theory_2_day:    # if clashes in lab and thoery days
                if lab_1_start < theory_2_end and theory_2_start < lab_1_end:   # if lab1 starts before theory2 ends and theory2 starts before lab1 ends
                    # self.all_classes[course2].remove(value2)
                    return False

        if value1[1] == None and value2[1] != None:       # if course 1 does not have lab and course 2 does
            lab_2_day = value2[1][2]
            lab_2_start = value2[1][3]
            lab_2_end = value2[1][4]
            if lab_2_day[0] in theory_1_day or lab_2_day[1] in theory_1_day:    # if clashes in lab and theory days
                if lab_2_start < theory_1_end and theory_1_start < lab_2_end:   # if clashes in lab and theory timing
                    # self.all_classes[course2].remove(value2)
                    return False

        if value1[1] != None and value2[1] != None:       # if course 1 and course 2 have labs
            lab_1_day = value1[1][2]
            lab_1_start = value1[1][3]
            lab_1_end = value1[1][4]
            lab_2_day = value2[1][2]
            lab_2_start = value2[1][3]
            lab_2_end = value2[1][4]
            if lab_1_day[0] in theory_2_day or lab_1_day[1] in theory_2_day:        # if clash in theory and lab days
                if lab_1_start < theory_2_end and theory_2_start < lab_1_end:       # if clash in theory and lab time
                    # self.all_classes[course2].remove(value2)
                    return False
            if lab_2_day[0] in theory_1_day or lab_2_day[1] in theory_1_day:        # if clash in theory and lab days
                if lab_2_start < theory_1_end and theory_1_start < lab_2_end:       # if clash in theory and lab time
                    # self.all_classes[course2].remove(value2)
                    return False
            if lab_1_day[0] in lab_2_day or lab_1_day[1] in lab_2_day:              # if clash in lab1 and lab2 days
                if lab_2_start < lab_1_end and lab_1_start < lab_2_end:             # if clash in lab1 and lab2 time 
                    # self.all_classes[course2].remove(value2)
                    return False                 

        return True

    def table_generator(self):

        for course_1 in self.courses:
            self.teacher_preference(course_1)
            for course_2 in self.courses:
                if course_1 != course_2:
                    self.CSP.add_constraint(course_1,course_2, self.avoid_clashes)

        # for course in self.courses:
        #     print(course)
        #     for cls in self.all_classes[course]:
        #         print(cls[0])
        #         print(cls[1])
        
        self.reordering()
        # if self.CSP.backtrack() == None:
        #     for course in self.courses:
        #         if self.teacher_priority[course]:
        #             self.teacher_preference(course)
        return self.CSP.backtrack()

         

    

def main():
    courses_needed = ["Pakistan History", "Computer Communication and Networking", "Introduction to Artificial Intelligence", 
                      "Computer Architecture and Assembly Language", "Theory of Automata"]
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    day_start = time(8,30)
    day_end = time(15,45)
    teacher_preference= [("Computer Communication and Networking", "Ms. Tasbiha Fatima"), 
                         ("Pakistan History", "Ms. Parmal Ahmed"),
                         ("Introduction to Artificial Intelligence", "Ms. Sumaira Saeed", "Dr. Tahir Syed"), 
                         ("Computer Architecture and Assembly Language", "Salman Zafar"), 
                         ("Theory of Automata", "Dr. Shahid Hussain", "Dr. Imran Rauf")]
    timetable = ScheduleSolver(courses_needed, teacher_preference, day_start, day_end, days)
    table, clash = timetable.table_generator()
    print()
    # if table != None:
    #     for course in courses_needed:
    #         print(course)
    #         for cls in table[course]:
    #             print(cls)
    # else:
    if table == None:
        for course in courses_needed:
            print(course)
            print(clash[course])
    
if __name__ == "__main__":
     main()


