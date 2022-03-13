
num_people = 8
state = [chr(x + ord('A')) for x in range(num_people)]

with open("test.txt", "wt") as fd:
    fd.write("{}\n".format(num_people))
    for step in range(num_people - 1):
        print(state)
        for pair in range(num_people // 2):
            a = state[pair]
            b = state[(num_people // 2) + pair]
            if a > b:
                (a, b) = (b, a)
            fd.write("{}{} ".format(a, b))
            print("{}{} ".format(a, b), end="")
        fd.write("\n")
        state.insert(0, state.pop())
        print("")

from check import check_file
check_file("test.txt")

