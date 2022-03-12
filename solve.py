
from construct import AutoProblem
import configparser


class Person:
    def __init__(self, name):
        self.name = name
        self.meeting_sequence = []
        self.already_met = set()

    def show(self):
        print(self.name)
        for p2 in self.meeting_sequence:
            print(" meets ", p2.name)

NOBODY = Person("nobody")

class PersonProblem(AutoProblem):
    def __init__(self, people_by_name):
        AutoProblem.__init__(self, len(people_by_name))
        self.people_by_number = []
        for name in sorted(people_by_name):
            self.people_by_number.append(people_by_name[name])

    def auto_allocate_full(self):
        AutoProblem.auto_allocate_full(self)

        for p in self.people_by_number:
            p.meeting_sequence = []

        for line in self.solution:
            for pair in line.split():
                assert 1 <= len(pair) <= 2
                a = self.people_by_number[ord(pair[0]) - ord('A')]
                if len(pair) > 1:
                    b = self.people_by_number[ord(pair[1]) - ord('A')]
                    a.meeting_sequence.append(b)
                    b.meeting_sequence.append(a)
                else:
                    a.meeting_sequence.append(NOBODY)
            
    def show(self):
        for p in self.people_by_number:
            p.show()
        

def solve(file_name) -> None:
    parser = configparser.ConfigParser(allow_no_value=True)
    parser.read(file_name)

    people = dict()
    for name1 in parser.sections():
        people[name1.lower()] = Person(name1)
        
    for name1 in parser.sections():
        for name2 in parser.options(name1):
            people[name1.lower()].already_met.add(people[name2.lower()])
            people[name2.lower()].already_met.add(people[name1.lower()])

    pp = PersonProblem(people) 
    pp.auto_allocate_full()
    pp.show()


if __name__ == "__main__":
    solve("input.txt")
