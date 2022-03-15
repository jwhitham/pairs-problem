
from problem import Problem, Person, NOBODY
from solve import solve

def test_simple() -> None:
    for num_people in range(13):
        problem = Problem()
        for i in range(num_people):
            problem.people.append(Person(chr(ord('A') + i), True))
        assert len(problem.people) == num_people

        assert len(NOBODY.schedule) == 0
        solve(problem)
        assert len(NOBODY.schedule) == 0

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

