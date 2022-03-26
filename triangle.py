import typing
import sys

#   x=0  1  2  3 y=
#        g  g  g  0
#           g  g  1
#              g  2
#                 3

Pair = typing.Tuple[int, int]
Pairs = typing.List[Pair]

class Cell:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.met = False
        self.busy = False

class Grid:
    def __init__(self, num_people: int) -> None:
        self.num_people = num_people
        self.grid = dict()
        for x in range(1, num_people):
            for y in range(x):
                self.grid[(x, y)] = Cell(x, y)


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
                    value = self.count_not_busy(x, y)
                    out.append(str(value).center(w))

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
            p = self.find_next_available()
            if debug:
                if p:
                    print("choose", pairs_to_string([p]))
                else:
                    print("none left")

        return pairs

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
        pairs = g.find_pairs(debug)
        if not debug:
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
