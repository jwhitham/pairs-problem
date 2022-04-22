import typing
import sys

#   x=0  1  2  3 y=
#        g  g  g  0
#           g  g  1
#              g  2
#                 3

Pair = typing.Tuple[int, int]
Pairs = typing.List[Pair]
Footprint = typing.List[int]

class CantSolveError(Exception):
    pass

class BacktrackError(Exception):
    pass

class Cell:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.met_stack: typing.List[bool] = [False]
        self.busy_stack: typing.List[bool] = [False]

    def copy(self) -> "Cell":
        c = Cell(self.x, self.y)
        c.met_stack = self.met_stack[:]
        c.busy_stack = self.busy_stack[:]
        return c

    def push(self) -> None:
        self.met_stack.append(self.met_stack[-1])
        self.busy_stack.append(self.busy_stack[-1])

    def pop(self) -> None:
        self.met_stack.pop()
        self.busy_stack.pop()

class Grid:
    def __init__(self, num_people: int) -> None:
        self.num_people = num_people
        self.grid = dict()
        for x in range(1, num_people):
            for y in range(x):
                self.grid[(x, y)] = Cell(x, y)

    def copy(self) -> "Grid":
        g = Grid(self.num_people)
        for x in range(1, self.num_people):
            for y in range(x):
                g.grid[(x, y)] = self.grid[(x, y)].copy()
        return g

    def push(self) -> None:
        for x in range(1, self.num_people):
            for y in range(x):
                self.grid[(x, y)].push()

    def pop(self) -> None:
        for x in range(1, self.num_people):
            for y in range(x):
                self.grid[(x, y)].pop()

    def reset_busy(self) -> None:
        for x in range(1, self.num_people):
            for y in range(x):
                self.grid[(x, y)].busy_stack = [self.grid[(x, y)].met_stack[-1]]

    def partial_footprint(self, cr: int) -> Footprint:
        assert 0 <= cr < self.num_people
        footprint: Footprint = []

        # Column cr, downwards (height of column cr is cr)
        for i in range(cr):
            if not self.grid[(cr, i)].busy_stack[-1]:
                footprint.append(i)

        # Row y, across
        for i in range(cr + 1, self.num_people):
            if not self.grid[(i, cr)].busy_stack[-1]:
                footprint.append(i)

        return footprint 

    def footprint(self, x: int, y: int) -> Footprint:
        footprint = self.partial_footprint(x)
        footprint.extend(self.partial_footprint(y))
        footprint.remove(x)
        footprint.remove(y)
        assert not x in footprint
        assert not y in footprint
        return footprint

    def visit_related(self, cr: int, mark_busy: bool) -> int:
        assert 0 <= cr < self.num_people
        count = 0

        # Column cr, downwards (height of column cr is cr)
        for i in range(cr):
            if not self.grid[(cr, i)].busy_stack[-1]:
                count += 1
            if mark_busy:
                self.grid[(cr, i)].busy_stack[-1] = True

        # Row y, across
        for i in range(cr + 1, self.num_people):
            if not self.grid[(i, cr)].busy_stack[-1]:
                count += 1
            if mark_busy:
                self.grid[(i, cr)].busy_stack[-1] = True

        return count

    def calculate_availability(self, x: int, y: int) -> typing.Tuple[int, int]:
        assert 0 <= y < x < self.num_people
        a = self.visit_related(x, False)
        b = self.visit_related(y, False)
        if a < b:
            return (a, b)
        else:
            return (b, a)

    def set_met(self, x: int, y: int) -> None:
        assert 0 <= y < x < self.num_people
        self.visit_related(x, True)
        self.visit_related(y, True)
        self.grid[(x, y)].met_stack[-1] = True

    def __str__(self) -> str:
        out: typing.List[str] = []
        w = 5
        blank = " ".center(w)
        out.append(blank)
        for x in range(1, self.num_people):
            out.append(name_to_string(x).center(w))

        for y in range(self.num_people - 1):
            out.append("\n")
            out.append(name_to_string(y).center(w))
            for x in range(1, self.num_people):
                if y >= x:
                    out.append(blank)
                elif self.grid[(x, y)].met_stack[-1]:
                    out.append("met".center(w))
                elif self.grid[(x, y)].busy_stack[-1]:
                    out.append("bsy".center(w))
                else:
                    (a, b) = self.calculate_availability(x, y)
                    a = min(a, 9)
                    b = min(b, 9)
                    out.append("{},{}".format(a, b).center(w))

        return "".join(out)

    def find_all_available(self, debug: bool, remaining: int) -> Pairs:
        available: typing.List[typing.Tuple[typing.Any, int, int]] = []
        for y in range(self.num_people - 1):
            for x in range(y + 1, self.num_people):
                if not self.grid[(x, y)].busy_stack[-1]:
                    assert not self.grid[(x, y)].met_stack[-1]
                    (a, b) = self.calculate_availability(x, y)

                    # For original algorithm, use value = (y, x) here
                    # Availability: value = (a, b, y, x)
                    value = (a, b, y, x)
                    available.append((value, x, y))

        if len(available) != 0:
            available.sort()

            #(match, x, y) = available[0]
            #for i in range(len(available)):
            #    (score, x, y) = available[i]
            #    if score != match:
            #        available = available[:i]
            #        break

            if debug:
                indent = (self.num_people // 2) - remaining
                print(" " * indent, "remaining", remaining)
                for y in range(self.num_people):
                    a = self.visit_related(y, False)
                    if a != 0:
                        print(" " * indent, "visit_related", name_to_string(y), a)
                for (score, x, y) in available:
                    fp = self.footprint(x, y)

                    print(" " * indent, "choice", score, pairs_to_string([(x, y)]),
                            ''.join([name_to_string(b) for b in fp]),
                            len(set(fp)) != len(fp))
        return [(x, y) for (_, x, y) in available]

    def find_pairs(self, debug: bool, allow_bt: bool) -> Pairs:
        self.reset_busy()

        if debug:
            print(str(self))

        (bt, pairs) = self.find_some_pairs(debug, self.num_people // 2, allow_bt)
        #print ("backtrack", bt, flush=True)
        if bt and not allow_bt:
            raise BacktrackError()

        for p in pairs:
            (x, y) = p
            self.set_met(x, y)

        return pairs

    def find_some_pairs(self, debug: bool, remaining: int, allow_bt: bool) -> typing.Tuple[int, Pairs]:
        if remaining == 0:
            return (0, [])

        assert remaining > 0
        backtrack = 0
        indent = (self.num_people // 2) - remaining
        bad = True

        for p in self.find_all_available(debug, remaining):
            (x, y) = p

            if debug:
                print(" " * indent, "push", pairs_to_string([p]))

            self.push()
            self.set_met(x, y)
            (bt, pairs) = self.find_some_pairs(debug, remaining - 1, allow_bt)
            backtrack += bt
            if len(pairs) == (remaining - 1):
                pairs.insert(0, p)
                if debug:
                    print(" " * indent, "solved", pairs_to_string([p]))

                return (backtrack, pairs)

            if debug:
                print(" " * indent, "pop", pairs_to_string([p]))

            if not allow_bt:
                raise BacktrackError()
            backtrack += 1
            bad = False
            self.pop()

        if bad and debug:
            print(" " * indent, "nowhere to go, with", remaining, "left")

        return (backtrack, [])


    def can_solve(self, pairs: Pairs, single_round: bool) -> bool:
        target_pairs = self.num_people // 2
        if len(pairs) >= target_pairs:
            # Not valid for multiple rounds
            assert single_round
            return True

        need_to_meet = set()
        for x in range(1, self.num_people):
            for y in range(x):
                need_to_meet.add((y, x))

        busy = [False for i in range(self.num_people)]
        already_met = set()
        for x in range(1, self.num_people):
            for y in range(x):
                if self.grid[(x, y)].met_stack[-1]:
                    assert y < x
                    already_met.add((y, x))

        test_pairs = pairs[:]
        for (x, y) in test_pairs:
            busy[x] = True
            busy[y] = True
            assert y < x
            already_met.add((y, x))

        need_to_meet = need_to_meet - already_met

        while len(need_to_meet) != 0:
            def allocate_next(i1: int, i2: int) -> bool:
                # Find first person who can be allocated
                some_i2_exists = False
                while i1 < self.num_people:
                    if not busy[i1]:
                        # i1 can be allocated
                        while i2 < self.num_people:
                            if (not busy[i2]) and ((i1, i2) not in already_met):
                                # i2 can be allocated
                                some_i2_exists = True
                                test_pairs.append((i2, i1))
                                busy[i1] = True
                                busy[i2] = True
                                
                                if len(test_pairs) >= target_pairs:
                                    return True

                                if allocate_next(i1, i2):
                                    return True

                                test_pairs.pop()
                                busy[i1] = False
                                busy[i2] = False

                            # advance to next i2
                            i2 += 1

                    if some_i2_exists:
                        return False

                    # advance to next p1
                    i1 += 1
                    i2 = i1 + 1

                # No complete solution was found
                return False

            if not allocate_next(0, 1):
                # couldn't fill all pairs here
                return False

            for (x, y) in test_pairs:
                assert y < x
                already_met.add((y, x))
                need_to_meet.remove((y, x))

            for x in range(self.num_people):
                busy[x] = False

            test_pairs.clear()
            if single_round:
                return True

        return True

def name_to_string(x: int) -> str:
    if x > 26:
        return name_to_string(x // 26) + chr((x % 26) + ord('A'))
    else:
        return chr(x + ord('A'))

def pairs_to_string(pairs: Pairs) -> str:
    out: typing.List[str] = []
    for (x, y) in pairs:
        out.append(name_to_string(y))
        out.append(name_to_string(x))
        out.append(" ")
    return "".join(out)

def test(num_people: int) -> None:
    g = Grid(num_people)
    met = set()
    stop = False
    for i in range(num_people - 1):
        busy = [False for i in range(num_people)]
        g2 = g.copy()
        if not g.can_solve([], True):
            print("Problem has become unsolvable according to original algorithm", flush=True)

        try:
            pairs = g.find_pairs(False, False)
        except BacktrackError:
            g = g2.copy()
            print("Problem can't be solved without backtracking", flush=True)
            try:
                pairs = g.find_pairs(False, True)
            except CantSolveError:
                print("Problem not solvable by available heuristic", flush=True)
                g = g2.copy()
                pairs = g.find_pairs(True, True)

        print("round {}: {}".format(i, pairs_to_string(pairs)), flush=True)
        assert len(pairs) == (num_people // 2)
        for (x, y) in pairs:
            assert 0 <= y < x < num_people
            assert not busy[x]
            assert not busy[y]
            assert (x, y) not in met
            met.add((x, y))
            busy[x] = True
            busy[y] = True
        if stop:
            raise CantSolveError()


    for x in range(1, num_people):
        for y in range(x):
            assert (x, y) in met
            met.remove((x, y))

    assert len(met) == 0

for np in range(4, 100, 2):
    print("number of people = {}".format(np), flush=True)
    test(np)
