# PART II

# Reading the csv file

from csv import reader as csv_reader

# Headers in the given csv file are Name of Subjects
headers = True


# Taking the marks input as Array of Dictionaries

# Declaring outer array
marks = []

try:
    with open("Student_marks_list (1).csv", 'r') as file:
        fileReader = csv_reader(file)
        if headers:
            columns = next(fileReader)
        for row in fileReader:

            # Declaring inner dictionaries
            row_data = {}

            for i in range(len(row)):
                if headers:
                    row_key = columns[i].lower()
                else:
                    row_key = i
                row_data[row_key] = row[i]
            marks.append(row_data)
except Exception as e:
    print(repr(e))

# Object Oriented Programming Approach


class Students:
    def _init_(self, details):
        self.student_details = details

    # Finding topper in each subject

    def topperEachSubject(self, subjectName, student_details):

        # Below code also handle students with same marks
        # time -> O(n) | space -> O(1)best case ,O(n)worst case

        largest = [0]
        for i in range(1, len(student_details)):

            if(int(student_details[largest[0]][subjectName]) < int(student_details[i][subjectName])):
                largest = [i]

            elif(int(student_details[largest[0]][subjectName]) == int(student_details[i][subjectName])):
                largest.append(i)

        # Shows the topper in each subject

        print("Topper in {} is".format(subjectName), end=" ") if len(
            largest) == 1 else print("Toppers in {} are".format(subjectName), end=" ")

        for Marks in largest:
            print("{}".format(student_details[Marks]['name']), end="  ")
        print()

    def getValue(self, index, subjectName, student_details):
        return int(student_details[index][subjectName])

    # Calculating total marks of each student

    def calculateTotal(self, student_details):
        # time->O(n) | space O(1) bestcase
        for index in range(0, len(student_details)):
            student_details[index]["total"] = self.getValue(index, 'maths', student_details)+self.getValue(index, 'biology', student_details)+self.getValue(
                index, 'english', student_details)+self.getValue(index, 'physics', student_details)+self.getValue(index, 'chemistry', student_details)+self.getValue(index, 'hindi', student_details)

   # Finding best three students in the class

    def topThreeStudents(self, student_details):
        # time->O(3n) | space O(1) bestcase
        self.calculateTotal(student_details)
        largest = 0
        for i in range(1, len(student_details)):
            if(int(student_details[largest]["total"]) < int(student_details[i]["total"])):
                largest = i
        student_details[largest]["total"] = -1

        secondlarge = 0
        for i in range(1, len(student_details)):
            if(int(student_details[i]["total"]) != -1 and int(student_details[secondlarge]["total"]) < int(student_details[i]["total"])):
                secondlarge = i

        student_details[secondlarge]["total"] = -1

        thirdlarge = 0
        for i in range(1, len(student_details)):
            if(int(student_details[i]["total"]) != -1 and int(student_details[thirdlarge]["total"]) < int(student_details[i]["total"])):
                thirdlarge = i

        # Shows the best three students in the class

        print("Best students in the class are ({}, {} and {}).".format(
            student_details[largest]['name'], student_details[secondlarge]['name'], student_details[thirdlarge]['name']))
        print()


# Declaring Object for Students class

obj = Students()
obj.topperEachSubject("maths", marks)
obj.topperEachSubject("biology", marks)
obj.topperEachSubject("english", marks)
obj.topperEachSubject("physics", marks)
obj.topperEachSubject("chemistry", marks)
obj.topperEachSubject("hindi", marks)
obj.topThreeStudents(marks)
