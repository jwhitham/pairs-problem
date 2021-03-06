
import json
import random
import typing

from problem import Problem, Person, NOBODY, Cell
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
    # The solver must still work if the problem and
    # solution are passed through JSON or the spreadsheet encoder.
    # The same answer is expected
    for num_people in range(8, 10):
        for scenario in range(16):
            problem = Problem()
            for i in range(num_people):
                problem.people.append(Person(chr(ord('Z') - i), True))
            assert len(problem.people) == num_people

            unsolved = problem.to_text()
            assert problem.validate_problem()
            assert not problem.validate_solution()

            if scenario & 1:
                tmp = json.dumps(problem.to_dict())
                problem = Problem.from_dict(json.loads(tmp))
            if scenario & 2:
                problem = Problem.from_spreadsheet(
                        problem.to_spreadsheet(), repr)

            assert unsolved == problem.to_text()
            assert problem.validate_problem()
            assert not problem.validate_solution()

            solve(problem)

            solved = problem.to_text()
            assert problem.validate_solution()

            if scenario & 4:
                tmp = json.dumps(problem.to_dict())
                problem = Problem.from_dict(json.loads(tmp))
            if scenario & 8:
                problem = Problem.from_spreadsheet(
                        problem.to_spreadsheet(), repr)

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

def test_ysj_live() -> None:
    for scenario in ["ysj", "ysj2"]:
        problem = Problem.from_dict(json.load(open("test_{}.json".format(scenario), "rt")))
        assert problem.validate_problem()
        solve(problem)
        g_man = "G2"

        for p1 in problem.people:
            nothing_to_do = 0
            waiting_time = 0
            final_round = 0
            for (i, p2) in enumerate(p1.schedule):
                if p2 is NOBODY:
                    nothing_to_do += 1
                elif p2.name == g_man:
                    nothing_to_do = 0
                else:
                    waiting_time = max(waiting_time, nothing_to_do)
                    nothing_to_do = 0
                    final_round = i

            # Nobody has to wait for more than two rounds
            assert waiting_time <= 2, p1.name

            # Everyone finished in 10 rounds (except g_man)
            assert (final_round < 10) or (p1.name == g_man), p1.name

        assert problem.validate_solution()

        # Independently check that everybody met
        for p1 in problem.people:
            met: typing.Set[Person] = set()
            for p2 in p1.schedule:
                if p2 is not NOBODY:
                    assert p2 in problem.people
            for p2 in p1.already_met:
                assert p2 is not NOBODY
                assert p2 in problem.people
            for p2 in problem.people:
                assert p2 is not NOBODY
                assert ((p2 is p1) or
                    (p2 in p1.schedule) or (p2 in p1.already_met)), (p2.name)
                assert not ((p2 in p1.schedule) and (p2 in p1.already_met))
                
            met.update(p1.schedule)
            met.update(p1.already_met)
            met.discard(NOBODY)
            assert not (p1 in met)
            met.add(p1)
            assert met == set(problem.people)

        json.dump(problem.to_dict(), open("solution_{}.json".format(scenario), "wt"), indent=4)

def test_ysj() -> None:
    for scenario in range(2):
        # (a) Some people organised themselves into a horseshoe double ring.
        # They rotated - inner ring clockwise, outer ring anti-clockwise.
        # After some iterations, they found that everyone was talking to someone
        # they had already met.
        # (b) They stopped and attempted to assign pairs by hand.
        # It turned out to be very hard to figure out an optimal pairing and
        # some people were left out.
        # (c) Then we wrote this program to try to come up with the best solution.
        problem = Problem()
        r = random.Random(1)
        num_people = 18
        for i in range(num_people):
            problem.people.append(Person('{:03d}'.format(i), True))

        horseshoe = problem.people[:]
        met: typing.Set[typing.Tuple[str, str]] = set()

        # (a) the horseshoe
        for step in range(num_people // 2):
            # Everybody meets
            for chair in range(num_people // 2):
                p1 = horseshoe[chair]
                p2 = horseshoe[len(horseshoe) - 1 - chair]
                assert not (p1.name, p2.name) in met
                p1.already_met.append(p2)
                p2.already_met.append(p1)
                met.add((p1.name, p2.name))
                met.add((p2.name, p1.name))
            # Rotate
            horseshoe.append(horseshoe.pop(0))

        # Now, everyone is facing someone they already met
        for chair in range(num_people // 2):
            p1 = horseshoe[chair]
            p2 = horseshoe[len(horseshoe) - 1 - chair]
            assert (p1.name, p2.name) in met

        # (b) each person picks someone they haven't met (at the same time)
        pairing: typing.List[typing.Tuple[Person, Person]] = []
        for p1 in problem.people:
            r.shuffle(horseshoe)
            for p2 in horseshoe:
                if (p1 is not p2) and ((p1.name, p2.name) not in met):
                    pairing.append((p1, p2))
                    break

        r.shuffle(pairing)
        # assign pairs as far as possible
        busy: typing.Set[str] = set()
        for (p1, p2) in pairing:
            if (p1.name not in busy) and (p2.name not in busy):
                # p1 and p2 meet!
                # But in doing so, they prevent other meetings
                assert (p1.name, p2.name) not in met
                p1.already_met.append(p2)
                p2.already_met.append(p1)
                met.add((p1.name, p2.name))
                met.add((p2.name, p1.name))
                busy.add(p1.name)
                busy.add(p2.name)

        # A few people are left out
        assert len(busy) > 0
        assert len(busy) < num_people
        assert len(busy) <= (num_people - 2)

        # Scenario 1: Someone was off sick and now joins the problem
        latecomer = Person('{:03d}'.format(num_people), True)
        if scenario == 1:
            problem.people.append(latecomer)

        # (c) Then we wrote this program to try to come up with the best solution.
        assert problem.validate_problem()
        assert not problem.validate_solution()
        solve(problem)
        assert problem.validate_solution()

        # Scenario 1: Stop meetings when the only meetings involve the latecomer
        endpoint = 0
        for p1 in problem.people:
            if p1 is latecomer:
                continue

            for i in range(len(p1.schedule)):
                if ((p1.schedule[i] is not NOBODY)
                        and (p1.schedule[i] is not latecomer)):
                    endpoint = max(endpoint, i)

        # Work out the boredom factor
        max_bored = 0
        for p1 in problem.people:
            bored = 0
            for p2 in p1.schedule[:endpoint + 1]:
                if p2 is NOBODY:
                    max_bored = max(bored, max_bored)
                    bored += 1
                else:
                    bored = 0

        # Nobody has to wait for more than two rounds
        assert max_bored <= 2, scenario
