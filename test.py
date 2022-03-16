
import json
import random

from problem import Problem, Person, NOBODY
from solve import solve

def test_simple() -> None:
    # The solver must come up with a solution that's
    # valid for 0 to 12 people. Nobody has already met.
    # Note that a solution for less than 2 people is initially
    # valid (since nobody has to meet).
    for num_people in range(13):
        problem = Problem()
        for i in range(num_people):
            problem.people.append(Person(chr(ord('A') + i), True))
        assert len(problem.people) == num_people

        assert len(NOBODY.schedule) == 0
        assert problem.validate_problem()
        assert (num_people < 2) or not problem.validate_solution()
        solve(problem)
        assert len(NOBODY.schedule) == 0
        assert problem.validate_solution()

        all_people = set(problem.people)
        if (num_people % 2) == 1:
            schedule_size = num_people
            all_people.add(NOBODY)
        else:
            schedule_size = num_people - 1

        for person in problem.people:
            assert len(person.schedule) == schedule_size
            assert len(set(person.schedule)) == schedule_size
            assert (set(person.schedule) | set([person])) == all_people 
            for (i, person2) in enumerate(person.schedule):
                assert person2 != person
                if person2 is not NOBODY:
                    assert person2.schedule[i] == person

def test_save_load() -> None:
    # The solver must still work if the solution is passed through JSON.
    # The same answer is expected
    for num_people in range(8, 10):
        for scenario in range(4):
            problem = Problem()
            for i in range(num_people):
                problem.people.append(Person(chr(ord('Z') - i), True))
            assert len(problem.people) == num_people

            unsolved = problem.to_text()
            assert problem.validate_problem()
            assert not problem.validate_solution()

            if scenario & 2:
                tmp = json.dumps(problem.to_dict())
                problem = Problem.from_dict(json.loads(tmp))

            assert unsolved == problem.to_text()
            assert problem.validate_problem()
            assert not problem.validate_solution()

            solve(problem)

            solved = problem.to_text()
            assert problem.validate_solution()

            if scenario & 1:
                tmp = json.dumps(problem.to_dict())
                problem = Problem.from_dict(json.loads(tmp))

            assert solved == problem.to_text()
            assert problem.validate_solution()

            for person in problem.people:
                if num_people == 8:
                    assert len(person.schedule) == 7
                    assert not (NOBODY in person.schedule)
                else:
                    assert len(person.schedule) == 9
                    assert (NOBODY in person.schedule)
                for person2 in problem.people:
                    assert (person2 == person) or (person2 in person.schedule)


def test_all_already_met() -> None:
    # In this situation everyone already met! So there is nothing to do.
    problem = Problem()
    for i in range(8):
        problem.people.append(Person(str(i), True))
    for p1 in problem.people:
        for p2 in problem.people:
            if p2 != p1:
                p1.already_met.append(p2)

    assert problem.validate_solution()
    solved = problem.to_text()

    solve(problem)

    assert problem.validate_solution()
    assert solved == problem.to_text()

    tmp = json.dumps(problem.to_dict())
    problem = Problem.from_dict(json.loads(tmp))

    assert problem.validate_solution()
    assert solved == problem.to_text()

    solve(problem)

    assert problem.validate_solution()
    assert solved == problem.to_text()

def test_some_already_met() -> None:
    # In this situation some people already met
    r = random.Random(1)
    for scenario in range(100):
        problem = Problem()
        for i in range(8):
            problem.people.append(Person(str(i), True))
        for p1 in problem.people:
            for p2 in problem.people:
                if (p2.name > p1.name) and (r.random() >= 0.5):
                    p1.already_met.append(p2)
                    p2.already_met.append(p1)

        solve(problem)

        assert problem.validate_solution()
        for person in problem.people:
            assert len(person.schedule) <= 7

def test_ysj() -> None:
    # (a) 18 people organised themselves into a horseshoe double ring.
    # They rotated - inner ring clockwise, outer ring anti-clockwise.
    # After some iterations, they found that everyone was talking to someone
    # they had already met.
    # (b) They stopped and attempted to assign pairs by hand.
    # It turned out to be very hard to figure out an optimal pairing and
    # some people were left out.
    # (c) Then we wrote this program to try to come up with the best solution.

    # In this situation some people already met
    r = random.Random(1)
    for scenario in range(100):
        problem = Problem()
        for i in range(8):
            problem.people.append(Person(str(i), True))
        for p1 in problem.people:
            for p2 in problem.people:
                if (p2.name > p1.name) and (r.random() >= 0.5):
                    p1.already_met.append(p2)
                    p2.already_met.append(p1)

        solve(problem)

        assert problem.validate_solution()
        for person in problem.people:
            assert len(person.schedule) <= 7

