
from check import Problem

class AutoProblem(Problem):
    def auto_allocate_once(self):
        can_do = sorted(self.meetings_to_do)
        assert len(can_do) > 0
        pairs = []
        already_busy = set()
        num_pairs = self.num_people // 2

        def allocate_next(index_start):
            for j in range(index_start, len(can_do)):
                (a, b) = can_do[j]
                if (a in already_busy) or (b in already_busy):
                    continue

                pairs.append((a, b))
                already_busy.add(a)
                already_busy.add(b)

                if len(pairs) == num_pairs:
                    return True

                if allocate_next(j + 1):
                    return True

                already_busy.discard(b)
                already_busy.discard(a)
                pairs.pop()

            return False

        rc = allocate_next(0)
        assert rc
        assert len(pairs) == num_pairs

        self.allocate([chr(a + ord('A')) + chr(b + ord('A'))
                            for (a, b) in pairs])


    def auto_allocate_full(self):
        for i in range(self.num_people - 1):
            self.auto_allocate_once()

if __name__ == "__main__":
    for i in range(2, 21, 1):
        p = AutoProblem(i)
        p.auto_allocate_full()
        p.check()
        p.show()
