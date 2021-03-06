import typing
import sys


Pair = typing.Tuple[int, int]
Pairs = typing.List[Pair]
Choice = typing.Tuple[typing.Any, int, int, int]

class CantSolveError(Exception):
    pass

class Cell:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.met = False
        self.busy = False

class Slice:
    def __init__(self, z: int, num_people: int) -> None:
        self.z = z
        self.num_people = num_people
        self.pairs: Pairs = []
        self.grid = dict()
        for x in range(1, num_people):
            for y in range(x):
                self.grid[(x, y)] = Cell(x, y)

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

    def calculate_availability(self, x: int, y: int) -> typing.Tuple[int, int]:
        assert 0 <= y < x < self.num_people
        a = self.visit_related(x, False)
        b = self.visit_related(y, False)
        if a < b:
            return (a, b)
        else:
            return (b, a)

    def set_met_elsewhere(self, x: int, y: int) -> None:
        self.grid[(x, y)].met = True
        self.grid[(x, y)].busy = True

    def set_met(self, x: int, y: int) -> None:
        assert 0 <= y < x < self.num_people
        self.visit_related(x, True)
        self.visit_related(y, True)
        self.grid[(x, y)].met = True
        self.pairs.append((x, y))

    def __str__(self) -> str:
        out: typing.List[str] = []
        w = 5
        blank = " ".center(w)
        out.append("round {}: ".format(self.z + 1))
        out.append(pairs_to_string(self.pairs))
        out.append("\n")
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
                    (a, b) = self.calculate_availability(x, y)
                    a = min(a, 9)
                    b = min(b, 9)
                    out.append("{},{}".format(a, b).center(w))

        out.append("\n")
        return "".join(out)

    def find_choices(self) -> typing.List[Choice]:
        available: typing.List[Choice] = []
        for y in range(self.num_people - 1):
            for x in range(y + 1, self.num_people):
                if not self.grid[(x, y)].busy:
                    assert not self.grid[(x, y)].met
                    (a, b) = self.calculate_availability(x, y)

                    # For original algorithm, use value = (y, x) here
                    # Availability: value = (a, b, y, x)
                    value = (a, b, self.z, y, x)
                    available.append((value, x, y, self.z))

        return available

class Prism:
    def __init__(self, num_people: int) -> None:
        self.num_people = num_people
        self.slices: typing.List[Slice] = []
        for z in range(num_people - 1):
            self.slices.append(Slice(z, num_people))

    def find_choices(self) -> typing.List[Choice]:
        available: typing.List[Choice] = []
        for s in self.slices:
            available.extend(s.find_choices())

        return available

    def fill(self) -> None:
        todo_count = (self.num_people // 2) * (self.num_people - 1)
        while todo_count > 0:
            todo_count -= 1
            available = self.find_choices()
            if len(available) == 0:
                raise CantSolveError()
            (_, x, y, z) = min(available)
            self.slices[z].set_met(x, y)
            for s in self.slices:
                s.set_met_elsewhere(x, y)

    def check(self) -> None:
        all_pairs: Pairs = []
        assert len(self.slices) == (self.num_people - 1)
        for sl in self.slices:
            assert (len(sl.pairs) * 2) == self.num_people
            all_pairs.extend(sl.pairs)

        all_pairs.sort()
        (x1, y1) = (-1, -1)
        for (x, y) in all_pairs:
            assert 0 <= y < x < self.num_people
            assert (x, y) != (x1, y1)
            (x1, y1) = (x, y)

    def __str__(self) -> str:
        out: typing.List[str] = []
        for s in self.slices:
            out.append(str(s))

        return ''.join(out)


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


if __name__ == "__main__":
    for i in range(4, 40, 2):
        print(i, flush=True)
        t = Prism(i)
        try:
            t.fill()
        except CantSolveError as e:
            print(str(t))
            raise e from None
        t.check()
