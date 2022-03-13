

class Problem:
    def __init__(self, num_people):
        self.num_people = num_people
        self.meetings_to_do = set()
        self.meetings_done = set()
        self.solution = []
        self.steps = 0
        self.even_number = True

        if (self.num_people % 2) == 1:
            self.even_number = False
            self.num_people += 1

        for a in range(self.num_people - 1):
            for b in range(a + 1, self.num_people):
                self.meetings_to_do.add((a, b))

    def allocate(self, pairs):
        self.steps += 1
        odd_pair = False
        nobody = chr(self.num_people - 1 + ord('A'))
        for pair in pairs:
            if self.even_number:
                assert len(pair) == 2
            elif len(pair) == 1:
                assert not odd_pair
                odd_pair = True
                pair += nobody
            else:
                assert len(pair) == 2

            a = ord(pair[0]) - ord('A')
            assert 0 <= a < (self.num_people - 1)
            b = ord(pair[1]) - ord('A')
            assert a < b < self.num_people
            assert (a, b) in self.meetings_to_do, (self.steps, pair)
            assert not ((a, b) in self.meetings_done)
            self.meetings_to_do.remove((a, b))
            self.meetings_done.add((a, b))

            if (not self.even_number) and (pair[-1] == nobody):
                self.solution.append(pair[0])
            else:
                self.solution.append(pair)
            self.solution.append(" ")
        self.solution.append("\n")

    def check(self):
        assert len(self.meetings_to_do) == 0
        assert self.steps == (self.num_people - 1)

    def show(self):
        if self.even_number:
            print(self.num_people)
        else:
            print(self.num_people - 1)
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
                problem.show()
            num_people = int(line)
            problem = Problem(num_people)
            problems.append(problem)
        else:
            problem.allocate(line.split())

        
    if problem:
        problem.check()
        problem.show()

if __name__ == "__main__":
    check_file("by_hand.txt")
