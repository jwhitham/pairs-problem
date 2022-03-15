
import json

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
        assert (num_people < 2) or not problem.validate()
        solve(problem)
        assert len(NOBODY.schedule) == 0
        assert problem.validate()

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
            assert not problem.validate()

            if scenario & 2:
                tmp = json.dumps(problem.to_dict())
                problem = Problem.from_dict(json.loads(tmp))

            assert unsolved == problem.to_text()
            assert not problem.validate()

            solve(problem)

            solved = problem.to_text()
            assert problem.validate()

            if scenario & 1:
                tmp = json.dumps(problem.to_dict())
                problem = Problem.from_dict(json.loads(tmp))

            assert solved == problem.to_text()
            assert problem.validate()

            for person in problem.people:
                if num_people == 8:
                    assert len(person.schedule) == 7
                    assert not (NOBODY in person.schedule)
                else:
                    assert len(person.schedule) == 9
                    assert (NOBODY in person.schedule)
                for person2 in problem.people:
                    assert (person2 == person) or (person2 in person.schedule)
