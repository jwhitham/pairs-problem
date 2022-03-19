
import typing

from problem import Problem, Person, NOBODY

class Solver:
    def __init__(self, problem: Problem) -> None:
        self.problem = problem
        self.problem.reset()
        self.nobody_is_present = False

        # Filter out people who are not present
        self.my_people: typing.List[Person] = []
        for p1 in self.problem.people:
            if p1.is_present:
                self.my_people.append(p1)

        # Met the fewest people? Then you are assigned first
        self.my_people.sort(key = lambda p: len(p.already_met))

        # Number of people is padded to an even number with NOBODY
        self.num_people = len(self.my_people)
        if (self.num_people % 2) == 1:
            self.num_people += 1
            self.my_people.append(NOBODY)
            self.nobody_is_present = True

        self.num_pairs = self.num_people // 2

        # Met matrix - true if people have met
        self.met: typing.List[typing.List[bool]] = []
        for a in range(self.num_people):
            self.met.append([False for b in range(self.num_people)])

        # Merge already_met into matrix
        self.already_met: typing.Set[typing.Tuple[int, int]] = set()
        for a in range(self.num_people):
            p1 = self.my_people[a]
            for p2 in p1.already_met:
                try:
                    b = self.my_people.index(p2)
                except ValueError:
                    b = -1
                if (b >= 0) and (p1 is not NOBODY) and (p2 is not NOBODY):
                    self.met[a][b] = True
                    self.met[b][a] = True

        # How many meetings haven't happened yet?
        self.num_meetings_todo = 0
        for a in range(self.num_people):
            for b in range(a + 1, self.num_people):
                if not self.met[a][b]:
                    self.num_meetings_todo += 1


        self.reset()

    def reset(self) -> None:
        # Prepare to solve
        self.pairs: typing.List[typing.Tuple[int, int]] = []
        self.best_pairs: typing.List[typing.Tuple[int, int]] = []
        self.busy: typing.List[bool] = [
                False for i in range(self.num_people)]
        self.best_score = 0
        self.score = 0

        # Priority is given to anyone who hasn't had a meeting recently
        self.priority = [0 for i in range(self.num_people)]
        for a in range(self.num_people):
            for b in range(self.num_people):
                if not self.met[a][b]:
                    self.priority[a] += 1

        if self.nobody_is_present:
            self.priority[-1] = -self.num_people

    def allocate_next(self, a: int, b: int) -> bool:
        while a < self.num_people:
            if not self.busy[a]:
                # a can be allocated
                while b < self.num_people:
                    if ((not self.busy[b]) and not self.met[a][b]):
                        # b can be allocated
                        assert a < b
                        self.pairs.append((a, b))
                        self.busy[a] = True
                        self.busy[b] = True
                        
                        delta_score = self.priority[a] + self.priority[b]
                        self.score += delta_score
                        if ((len(self.pairs) > len(self.best_pairs))
                        or (len(self.pairs) == len(self.best_pairs)
                                    and self.best_score < self.score)):
                            self.best_pairs.clear()
                            self.best_pairs.extend(self.pairs)
                            self.best_score = self.score
                            if len(self.pairs) == self.num_pairs:
                                return True

                        if self.allocate_next(a, b):
                            return True

                        self.score -= delta_score
                        self.pairs.pop()
                        self.busy[a] = False
                        self.busy[b] = False

                    # advance to next b
                    b += 1

            # advance to next a
            a += 1
            b = a + 1

        # No complete solution was found
        return False

    def solve(self) -> None:
        for p1 in self.my_people:
            assert len(p1.schedule) == 0
        num_rounds = 0
        while self.num_meetings_todo > 0:
            self.reset()
            self.allocate_next(0, 1)
            num_rounds += 1

            assert len(self.best_pairs) != 0

            for (a, b) in self.best_pairs:
                assert a < b
                assert not self.met[a][b]
                assert not self.met[b][a]
                self.met[a][b] = True
                self.met[b][a] = True
                self.num_meetings_todo -= 1
                assert self.num_meetings_todo >= 0
                p1 = self.my_people[a]
                p2 = self.my_people[b]
                if p1 is not NOBODY:
                    p1.schedule.append(p2)
                if p2 is not NOBODY:
                    p2.schedule.append(p1)

            for p1 in self.my_people:
                if p1 is NOBODY:
                    continue
                assert len(p1.schedule) <= num_rounds
                assert (num_rounds - 1) <= len(p1.schedule)
                if len(p1.schedule) == (num_rounds - 1):
                    p1.schedule.append(NOBODY)


def solve(problem: Problem) -> None:
    Solver(problem).solve()
