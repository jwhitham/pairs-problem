import typing
import sys

#   x=0  1  2  3 y=
#        g  g  g  0
#           g  g  1
#              g  2
#                 3

Pair = typing.Tuple[int, int]
Pairs = typing.List[Pair]

class CantSolveError(Exception):
    pass

class Cell:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.met = False
        self.busy = False

    def copy(self) -> "Cell":
        c = Cell(self.x, self.y)
        c.met = self.met
        c.busy = self.busy
        return c

class Grid:
    def __init__(self, num_people: int) -> None:
        self.num_people = num_people
        self.grid = dict()
        for x in range(1, num_people):
            for y in range(x):
                self.grid[(x, y)] = Cell(x, y)

    def copy(self) -> "Grid":
        g = Grid(self.num_people)
        for x in range(1, num_people):
            for y in range(x):
                g.grid[(x, y)] = self.grid[(x, y)].copy()
        return g

    def reset_busy(self) -> None:
        for x in range(1, self.num_people):
            for y in range(x):
                self.grid[(x, y)].busy = self.grid[(x, y)].met

    def visit_related(self, cr: int, mark_busy: bool) -> int:
        assert 0 <= cr < self.num_people
        count = 0

        # Column cr, downwards (height of column cr is cr)
        for i in range(cr):
            if not self.grid[(cr, i)].busy:
                count += 1
            if mark_busy:
                self.grid[(cr, i)].busy = True

        # Row y, across
        for i in range(cr + 1, self.num_people):
            if not self.grid[(i, cr)].busy:
                count += 1
            if mark_busy:
                self.grid[(i, cr)].busy = True

        return count

    def count_not_busy(self, x: int, y: int) -> typing.Tuple[int, int]:
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
        self.grid[(x, y)].met = True

    def __str__(self) -> None:
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
                elif self.grid[(x, y)].met:
                    out.append("met".center(w))
                elif self.grid[(x, y)].busy:
                    out.append("bsy".center(w))
                else:
                    (a, b) = self.count_not_busy(x, y)
                    a = min(a, 9)
                    b = min(b, 9)
                    out.append("{},{}".format(a, b).center(w))

        return "".join(out)

    def find_next_available(self) -> typing.Optional[Pair]:
        best_value = (sys.maxsize, sys.maxsize)
        best_x = -1
        best_y = -1
        #for x in range(1, self.num_people):
        #    for y in range(x):

        for y in range(self.num_people - 1):
            for x in range(y + 1, self.num_people):
                if not self.grid[(x, y)].busy:
                    assert not self.grid[(x, y)].met
                    value = self.count_not_busy(x, y)
                    if value < best_value:
                        best_value = value
                        best_x = x
                        best_y = y
        if best_x < 0:
            return None
        else:
            return (best_x, best_y)

    def find_pairs(self, debug: bool) -> Pairs:
        pairs: Pairs = []
        self.reset_busy()
        if debug:
            print(self)
        p = self.find_next_available()
        if debug:
            print("choose", pairs_to_string([p]))
        while p is not None:
            (x, y) = p
            self.set_met(x, y)
            pairs.append((x, y))
            if debug:
                print(self)
            if not self.can_solve(pairs):
                raise CantSolveError()
            p = self.find_next_available()
            if debug:
                if p:
                    print("choose", pairs_to_string([p]))
                else:
                    print("none left")

        return pairs

    def can_solve(self, pairs: typing.List[Pairs]) -> bool:
        target_pairs = self.num_people // 2
        if len(pairs) >= target_pairs:
            return True

        need_to_meet = set()
        for x in range(1, self.num_people):
            for y in range(x):
                need_to_meet.add((y, x))

        busy = [False for i in range(self.num_people)]
        already_met = set()
        for x in range(1, self.num_people):
            for y in range(x):
                if self.grid[(x, y)].met:
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
                need_to_meet.discard((y, x))

            for x in range(num_people):
                busy[x] = False

            test_pairs.clear()

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


def test(num_people: int, debug: bool) -> None:
    g = Grid(num_people)
    met = set()
    for i in range(num_people - 1):
        if debug:
            print("")
            print("round", i)
        busy = [False for i in range(num_people)]
        g2 = g.copy()
        try:
            pairs = g.find_pairs(debug)
        except CantSolveError:
            debug = True
            g = g2.copy()
            try:
                pairs = g.find_pairs(debug)
            except CantSolveError as e:
                raise e from None
                

        print("round {}: {}".format(i, pairs_to_string(pairs)))
        assert len(pairs) == (num_people // 2)
        for (x, y) in pairs:
            assert 0 <= y < x < num_people
            assert not busy[x]
            assert not busy[y]
            assert (x, y) not in met
            met.add((x, y))
            busy[x] = True
            busy[y] = True

    for x in range(1, num_people):
        for y in range(x):
            assert (x, y) in met
            met.remove((x, y))

    assert len(met) == 0

for num_people in range(4, 100, 2):
    print("number of people = {}".format(num_people), flush=True)
    test(num_people, False)
