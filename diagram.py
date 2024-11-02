import itertools
import time

import numpy
import scipy


def is_complete(power, e, v, diagram):
    for i in range(e):
        if sum(diagram[i]) != 1:
            return False
    for i in range(e, e + v):
        if sum(diagram[i]) != power:
            return False
    return True


def is_not_overdrawn(power, e, v, diagram):
    for i in range(e):
        if sum(diagram[i]) > 1:
            return False
    for i in range(e, e + v):
        if sum(diagram[i]) > power:
            return False
    return True


def next_line(power, e, v, diagram, drawnx, drawny):
    n = e + v

    ret = []
    if drawny == n - 1:
        if drawnx == n - 1:
            if is_complete(power, e, v, diagram):
                return [diagram]
            else:
                return None
        x = y = drawnx + 1
    else:
        x = drawnx
        y = drawny + 1
    max_line_x = 1 if x == 1 else power
    max_line_x_remaining = max_line_x - sum(diagram[x])
    max_line_y = 1 if y == 1 else power
    max_line_y_remaining = max_line_y - sum(diagram[y])
    max_line_remaining = min(max_line_x_remaining, max_line_y_remaining)
    assert max_line_remaining >= 0

    step = 2 if x == y else 1

    for i in range(0, max_line_remaining + 1, step):
        diagram[x][y] = diagram[y][x] = i
        leaves = next_line(power, e, v, diagram.copy(), x, y)
        if leaves != None:
            ret += leaves
    return ret


def create_all_diagrams(power=3, e=2, v=2):
    if v == 0:
        return [[[0, 1], [1, 0]]] if e == 2 else []

    diagram = numpy.zeros((e + v, e + v), dtype=int)
    diagram[e][0] = diagram[0][e] = 1
    return next_line(power, e, v, diagram, 1, e - 1)


def allPermutation(n, offset=0):
    permutation = []
    for i in range(n):
        permutation.append(i + offset)
    permutations = list(itertools.permutations(permutation))
    prefix = []
    for i in range(offset):
        prefix.append(i)
    all_permutation = []
    for p in permutations:
        all_permutation.append(prefix + list(p))
    return all_permutation


def has_same_diagram(all_diagram, diagram, e, v):
    n = e + v
    permutations = allPermutation(v, offset=e)
    for p in permutations:
        new_diagram = numpy.empty((n, n), dtype=int)
        for x in range(n):
            for y in range(n):
                new_diagram[p[x]][p[y]] = diagram[x][y]
        for d in all_diagram:
            if not (diagram == d).all() and (new_diagram == d).all():
                return True
    return False


def is_connected(diagram, n):
    connected_vertices = [True] + [False] * (n - 1)
    queue = [0]
    while len(queue) > 0:
        vertex = queue[0]
        for i in range(n):
            if i == vertex:
                continue
            if connected_vertices[i]:
                continue
            if diagram[vertex][i] != 0:
                queue.append(i)
                connected_vertices[i] = True
        queue.pop(0)
    return all(connected_vertices)


def is_connected_from_external(diagram, e, v):
    n = e + v
    connected_vertices = [True] * e + [False] * v
    queue = []
    for i in range(e):
        queue.append(i)
    while len(queue) > 0:
        vertex = queue[0]
        for i in range(n):
            if i == vertex:
                continue
            if connected_vertices[i]:
                continue
            if diagram[vertex][i] != 0:
                queue.append(i)
                connected_vertices[i] = True
        queue.pop(0)
    return all(connected_vertices)


def has_tadpole_rough(diagram, e, v):
    for i in range(e, e + v):
        if diagram[i][i] != 0:
            return True
    return False


def has_tadpole(diagram, e, v):
    for i in range(e, e + v - 1):
        for j in range(i + 1, e + v):
            new_diagram = diagram.copy()
            new_diagram[i][j] -= 1
            new_diagram[j][i] -= 1
            if not is_connected_from_external(new_diagram, e, v):
                return True
    return False


def count_F(diagram, e, v):
    f = 0
    n = e + v
    permutations = allPermutation(v, offset=e)
    for p in permutations:
        new_diagram = numpy.empty((n, n), dtype=int)
        for x in range(n):
            for y in range(n):
                new_diagram[p[x]][p[y]] = diagram[x][y]
        if (new_diagram == diagram).all():
            f += 1
    return f


def calculate_S(diagram, e, v):
    s = count_F(diagram, e, v)
    n = e + v
    for i in range(n - 1):
        for j in range(i + 1, n):
            s *= scipy.special.factorial(diagram[i][j])
    for i in range(n):
        s *= scipy.special.factorial2(diagram[i][i])
    return s


def create_diagrams(power, e, v):
    print("[Info] Draw all possible diagrams.")
    diagrams = create_all_diagrams(power=power, e=e, v=v)
    print(f"[Info] Complete. {len(diagrams)} drawn.")
    if power == 3:
        print("[Info] Remove diagrams that contains tadpole roughly.")
        i = 0
        while i < len(diagrams):
            diagram = diagrams[i]
            if has_tadpole_rough(diagram, e, v):
                diagrams.pop(i)
                continue
            i += 1
        print(f"[Info] Complete. {len(diagrams)} remains.")

    print("[Info] Remove unconnected diagrams.")
    i = 0
    while i < len(diagrams):
        diagram = diagrams[i]
        if not is_connected(diagram, e + v):
            diagrams.pop(i)
            continue
        i += 1
    print(f"[Info] Complete. {len(diagrams)} remains.")

    print("[Info] Remove diagrams that contains tadpole precisely.")
    i = 0
    while i < len(diagrams):
        diagram = diagrams[i]
        if has_tadpole(diagram, e, v):
            diagrams.pop(i)
            continue
        i += 1
    print(f"[Info] Complete. {len(diagrams)} remains.")

    print("[Info] Remove same diagrams.")
    i = 0
    while i < len(diagrams):
        diagram = diagrams[i]
        if has_same_diagram(diagrams, diagram, e, v):
            diagrams.pop(i)
            continue
        i += 1
    print(f"[Info] Complete. {len(diagrams)} remains.")
    return diagrams


if __name__ == "__main__":

    power = 4
    e = 4
    v = 2
    diagrams = create_diagrams(power, e, v)
    print("[Info] Calculate S for all diagrams")
    all_s = {}

    for diagram in diagrams:
        s = int(calculate_S(diagram, e, v))
        print(diagram, s)
        if s in all_s:
            all_s[s] += 1
        else:
            all_s[s] = 1
    print(f"[Info] Complete. {len(diagrams)} diagrams in total.")
    for s in all_s:
        print(
            f"Symmetry factor equal to {s}, the number of diagrams with symmetry factor equal to {all_s[s]}"
        )
