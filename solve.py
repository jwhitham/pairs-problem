
import typing

from problem import Problem, Person, NOBODY

class SolverPerson:
    def __init__(self, person: Person, initial_index: int) -> None:
        self.person = person
        self.initial_index = initial_index
        self.already_met: typing.Set[SolverPerson] = set()
        self.busy = False
   
def social_score(p: SolverPerson) -> typing.Tuple[int, int]:
    # NOBODY is allocated last
    if p.person is NOBODY:
        return (1 << 31, 0)

    # Allocate the person with the fewest meetings first
    # In case of a tie, allocate the person who has been waiting longest
    waiting_time = 0
    for other in reversed(p.person.schedule):
        if other is NOBODY:
            waiting_time += 1
        else:
            break

    return (len(p.already_met), -waiting_time)

class Solver:
    def __init__(self, problem: Problem) -> None:
        self.problem = problem
        self.problem.reset()

        # Filter out people who are not present
        self.my_people: typing.List[SolverPerson] = []
        for person in self.problem.people:
            assert len(person.schedule) == 0
            if person.is_present:
                self.my_people.append(SolverPerson(person, len(self.my_people)))

        # Number of people is padded to an even number with NOBODY
        self.num_people = len(self.my_people)
        if (self.num_people % 2) == 1:
            self.num_people += 1
            self.my_people.append(SolverPerson(NOBODY, len(self.my_people)))

        self.num_pairs = self.num_people // 2

        # Met matrix - true if people have met
        for p1 in self.my_people:
            for person in p1.person.already_met:
                for p2 in self.my_people:
                    if p2.person is person:
                        # p1 has met p2
                        p1.already_met.add(p2)
                        p2.already_met.add(p1)

        # How many meetings haven't happened yet?
        self.num_meetings_todo = 0
        for p1 in self.my_people:
            for p2 in self.my_people:
                if ((p2 not in p1.already_met)
                and (p1.initial_index < p2.initial_index)):
                    self.num_meetings_todo += 1

    def reset(self) -> None:
        # Prepare to solve - order the people so that
        # the people with the fewest meetings are allocated first
        self.my_people.sort(key = social_score)

        self.pairs: typing.List[typing.Tuple[SolverPerson, SolverPerson]] = []
        self.best_pairs: typing.List[typing.Tuple[SolverPerson, SolverPerson]] = []
        for p1 in self.my_people:
            p1.busy = False

    def allocate_next(self, i1: int, i2: int) -> bool:
        # Find first person who can be allocated
        some_p2_exists = False
        while i1 < self.num_people:
            p1 = self.my_people[i1]
            if not p1.busy:
                # p1 can be allocated
                while i2 < self.num_people:
                    p2 = self.my_people[i2]
                    if (not p2.busy) and (p2 not in p1.already_met):
                        # p2 can be allocated
                        some_p2_exists = True
                        self.pairs.append((p1, p2))
                        p1.busy = True
                        p2.busy = True
                        
                        if len(self.pairs) > len(self.best_pairs):
                            self.best_pairs.clear()
                            self.best_pairs.extend(self.pairs)
                            if len(self.pairs) == self.num_pairs:
                                return True

                        if self.allocate_next(i1, i2):
                            return True

                        self.pairs.pop()
                        p1.busy = False
                        p2.busy = False

                    # advance to next p2
                    i2 += 1

            if some_p2_exists:
                # No point in searching further values of p1, they
                # will just be equivalent to the one we already found
                # (symmetry)
                return False

            # advance to next p1
            i1 += 1
            i2 = i1 + 1

        # No complete solution was found
        return False

    def solve(self) -> None:
        for p1 in self.my_people:
            assert len(p1.person.schedule) == 0

        num_rounds = 0
        while self.num_meetings_todo > 0:
            self.reset()
            self.allocate_next(0, 1)
            num_rounds += 1

            assert len(self.best_pairs) != 0

            for (p1, p2) in self.best_pairs:
                p1.already_met.add(p2)
                p2.already_met.add(p1)
                self.num_meetings_todo -= 1
                assert self.num_meetings_todo >= 0
                if p1.person is not NOBODY:
                    p1.person.schedule.append(p2.person)
                if p2.person is not NOBODY:
                    p2.person.schedule.append(p1.person)

            for p1 in self.my_people:
                if p1.person is NOBODY:
                    continue
                assert len(p1.person.schedule) <= num_rounds
                assert (num_rounds - 1) <= len(p1.person.schedule)
                if len(p1.person.schedule) == (num_rounds - 1):
                    p1.person.schedule.append(NOBODY)


def solve(problem: Problem) -> None:
    Solver(problem).solve()
