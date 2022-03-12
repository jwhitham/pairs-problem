

class Problem:
    def __init__(self, num_people):
        self.num_people = num_people
        self.meetings_to_do = set()
        self.meetings_done = set()
        self.solution = []
        self.steps = 0
        for a in range(self.num_people - 1):
            for b in range(a + 1, self.num_people):
                self.meetings_to_do.add((a, b))

    def allocate(self, pairs):
        self.steps += 1
        for pair in pairs:
            assert len(pair) == 2
            a = ord(pair[0]) - ord('A')
            assert 0 <= a < (self.num_people - 1)
            b = ord(pair[1]) - ord('A')
            assert a < b < self.num_people
            assert (a, b) in self.meetings_to_do
            assert not ((a, b) in self.meetings_done)
            self.meetings_to_do.remove((a, b))
            self.meetings_done.add((a, b))
            self.solution.append(pair)
            self.solution.append(" ")
        self.solution.append("\n")

    def check(self):
        assert len(self.meetings_to_do) == 0
        assert self.steps == (self.num_people - 1)
        print("Good solution for {} people".format(self.num_people))
        print("".join(self.solution))

def check_file(filename):
    problem = None
    problems = []
    num_people = 0

    for line in open(filename):
        line = line.strip()
        if line == "":
            pass
        elif line[0].isdigit():
            if problem:
                problem.check()
            num_people = int(line)
            problem = Problem(num_people)
            problems.append(problem)
        else:
            problem.allocate(line.split())

        
    if problem:
        problem.check()

if __name__ == "__main__":
    check_file("by_hand.txt")
