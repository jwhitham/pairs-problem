
from check import Problem

class AutoProblem(Problem):
    def auto_allocate_once(self):
        can_do = sorted(self.meetings_to_do)
        assert len(can_do) > 0
        pairs = []
        already_busy = [False for i in range(self.num_people)]
        num_pairs = self.num_people // 2

        def allocate_next(index_start):
            for j in range(index_start, len(can_do)):
                (a, b) = can_do[j]
                if already_busy[a] or already_busy[b]:
                    continue

                pairs.append((a, b))
                already_busy[a] = True
                already_busy[b] = True

                if len(pairs) == num_pairs:
                    return True

                if allocate_next(j + 1):
                    return True

                already_busy[b] = False
                already_busy[a] = False
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
