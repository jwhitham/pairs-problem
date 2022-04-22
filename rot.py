
import typing

Pair = typing.Tuple[int, int]
Pairs = typing.List[Pair]
PairSet = typing.Set[Pair]

def name_to_string(x: int) -> str:
    if x >= 26:
        return name_to_string(x // 26) + chr((x % 26) + ord('a'))
    else:
        return chr(x + ord('A'))

def pairs_to_string(pairs: Pairs) -> str:
    out: typing.List[str] = []
    for (x, y) in pairs:
        out.append(name_to_string(min(x, y)))
        out.append(name_to_string(max(x, y)))
        out.append(" ")
    return "".join(out)

class State:
    def __init__(self, num_people: int) -> None:
        self.num_people = num_people
        self.num_pairs = num_people // 2
        self.row1 = list(range(0, num_people, 2))
        self.row2 = list(range(1, num_people, 2))

    def rotate(self, division: int) -> None:
        assert 1 <= division <= self.num_pairs
        for start in range(0, self.num_pairs, division):
            self.row2.insert(start + division, self.row2[start])
            self.row2.pop(start)

    def crossover(self) -> None:
        before = self.row1 + self.row2
        self.row1.clear()
        self.row2.clear()
        for i in range(0, self.num_people, 2):
            self.row1.append(before[i])
            self.row2.append(before[i + 1])

    def get_pairs(self) -> Pairs:
        pairs: Pairs = []
        for i in range(self.num_pairs):
            a = self.row1[i]
            b = self.row2[i]
            if a > b:
                (a, b) = (b, a)
            pairs.append((a, b))
        return pairs

    def __str__(self) -> str:
        out: typing.List[str] = []
        for i in range(self.num_pairs):
            out.append(name_to_string(self.row1[i]))
            out.append(" ")
        out.append(" -> ")
        out.append(pairs_to_string(self.get_pairs()))
        out.append("\n")
        for i in range(self.num_pairs):
            out.append(name_to_string(self.row2[i]))
            out.append(" ")
        out[-1] = ""
        return ''.join(out)


def form_pairs(num_people: int) -> typing.List[str]:
    pairs_expected: PairSet = set()
    for a in range(num_people - 1):
        for b in range(a + 1, num_people):
            pairs_expected.add((a, b))

    out: typing.List[str] = []
    s = State(num_people)
    division = num_people // 2
    j = 0
    while division >= 1:
        for i in range(division):
            #print("division {} round {}".format(division, i))
            #print(str(s))
            j += 1
            out.append("round {}: ".format(j))
            for p in s.get_pairs():
                out.append(pairs_to_string([p]))
                assert p in pairs_expected, pairs_to_string([p])
                pairs_expected.remove(p)
            s.rotate(division)
            out.append("\n")

        s.crossover()
        division = division // 2

    assert len(pairs_expected) == 0
    return out

def test() -> None:
    out: typing.List[str] = []
    for i in range(2, 11):
        print("test with {} people".format(1 << i))
        out.append("test with {} people\n".format(1 << i))
        out.extend(form_pairs(1 << i))
        out.append("\n")
        open("out.txt", "wt").write("".join(out))

if __name__ == "__main__":
    test()
