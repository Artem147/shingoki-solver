from __future__ import annotations

from dataclasses import dataclass

from ortools.sat.python import cp_model


@dataclass
class Circle:
    row: int
    col: int
    type: str
    number: int


@dataclass
class Edge:
    from_cell: tuple[int, int]
    to_cell: tuple[int, int]


def all_vertices(rows, cols):
    return [(r, c) for r in range(rows) for c in range(cols)]


def all_edges(rows, cols):
    result = []
    for r in range(rows):
        for c in range(cols - 1):
            result.append(((r, c), (r, c + 1)))
    for r in range(rows - 1):
        for c in range(cols):
            result.append(((r, c), (r + 1, c)))
    return [(min(u, v), max(u, v)) for u, v in result]


def neighbors(v, rows, cols):
    r, c = v
    nb = []
    if r > 0:
        nb.append((r - 1, c))
    if r < rows - 1:
        nb.append((r + 1, c))
    if c > 0:
        nb.append((r, c - 1))
    if c < cols - 1:
        nb.append((r, c + 1))
    return nb


def incident_edges(v, rows, cols, eidx):
    return [(min(v, nb), max(v, nb))
            for nb in neighbors(v, rows, cols)
            if (min(v, nb), max(v, nb)) in eidx]


def row_edges_of(v, cols, eidx):
    r, _ = v
    return [((r, c), (r, c + 1)) for c in range(cols - 1)
            if ((r, c), (r, c + 1)) in eidx]


def col_edges_of(v, rows, eidx):
    _, c = v
    return [((r, c), (r + 1, c)) for r in range(rows - 1)
            if ((r, c), (r + 1, c)) in eidx]


def prev_edge(e, v, eidx):
    (r1, c1), (r2, c2) = e
    vr, vc = v

    if r1 == r2:
        near_c = c1 if abs(c1 - vc) <= abs(c2 - vc) else c2
        if near_c == vc:
            return None
        step = 1 if near_c > vc else -1
        prev_c = near_c - step
        key = ((r1, min(near_c, prev_c)), (r1, max(near_c, prev_c)))
        return key if key in eidx else None
    else:
        near_r = r1 if abs(r1 - vr) <= abs(r2 - vr) else r2
        if near_r == vr:
            return None
        step = 1 if near_r > vr else -1
        prev_r = near_r - step
        key = ((min(near_r, prev_r), c1), (max(near_r, prev_r), c1))
        return key if key in eidx else None


def solve(rows: int, cols: int, circles: list[Circle]) -> list[Edge] | None:
    _type_map = {'white': 'W', 'black': 'B'}
    hints = [
        (c.row, c.col, _type_map[c.type], c.number)
        for c in circles
    ]

    if not hints:
        return None

    model = cp_model.CpModel()
    V = all_vertices(rows, cols)
    E = all_edges(rows, cols)
    eidx = set(E)

    white = {(r, c) for r, c, t, _ in hints if t == 'W'}
    black = {(r, c) for r, c, t, _ in hints if t == 'B'}
    hint_nodes = white | black

    x = {e: model.new_bool_var(f'x{e}') for e in E}
    y = {v: model.new_bool_var(f'y{v}') for v in V}

    for v in V:
        inc = incident_edges(v, rows, cols, eidx)
        model.add(sum(x[e] for e in inc) == 2 * y[v])

    for v in hint_nodes:
        model.add(y[v] == 1)

    for v in white:
        r, c = v
        nk = ((r-1, c), (r, c)) if r > 0 else None
        sk = ((r, c), (r+1, c)) if r < rows-1 else None
        wk = ((r, c-1), (r, c)) if c > 0 else None
        ek = ((r, c), (r, c+1)) if c < cols-1 else None

        xn = x[nk] if (nk and nk in eidx) else model.new_constant(0)
        xs = x[sk] if (sk and sk in eidx) else model.new_constant(0)
        xw = x[wk] if (wk and wk in eidx) else model.new_constant(0)
        xe = x[ek] if (ek and ek in eidx) else model.new_constant(0)

        model.add(xn == xs)
        model.add(xw == xe)

    for v in black:
        r, c = v
        nk = ((r-1, c), (r, c)) if r > 0 else None
        sk = ((r, c), (r+1, c)) if r < rows-1 else None
        wk = ((r, c-1), (r, c)) if c > 0 else None
        ek = ((r, c), (r, c+1)) if c < cols-1 else None

        xn = x[nk] if (nk and nk in eidx) else model.new_constant(0)
        xs = x[sk] if (sk and sk in eidx) else model.new_constant(0)
        xw = x[wk] if (wk and wk in eidx) else model.new_constant(0)
        xe = x[ek] if (ek and ek in eidx) else model.new_constant(0)

        model.add(xn + xs == 1)
        model.add(xw + xe == 1)

    source = (hints[0][0], hints[0][1])
    M = rows * cols

    L_var = model.new_int_var(0, M, 'L')
    model.add(L_var == sum(y[v] for v in V))

    f = {}
    for u, v in E:
        f[(u, v)] = model.new_int_var(0, M, f'fuv{u}{v}')
        f[(v, u)] = model.new_int_var(0, M, f'fvu{v}{u}')

    for u, v in E:
        model.add(f[(u, v)] <= M * x[(u, v)])
        model.add(f[(v, u)] <= M * x[(u, v)])

    nbs = neighbors(source, rows, cols)
    out_s = sum(f[(source, nb)] for nb in nbs if (min(source, nb), max(source, nb)) in eidx)
    in_s = sum(f[(nb, source)] for nb in nbs if (min(source, nb), max(source, nb)) in eidx)
    model.add(out_s - in_s == L_var - 1)

    for v in V:
        if v == source:
            continue
        nbv = neighbors(v, rows, cols)
        out_v = sum(f[(v, nb)] for nb in nbv if (min(v, nb), max(v, nb)) in eidx)
        in_v = sum(f[(nb, v)] for nb in nbv if (min(v, nb), max(v, nb)) in eidx)
        model.add(in_v - out_v == y[v])

    l: dict = {}

    for rv, cv, _, Nv in hints:
        v = (rv, cv)
        seg_edges = row_edges_of(v, cols, eidx) + col_edges_of(v, rows, eidx)

        for e in seg_edges:
            if (v, e) not in l:
                l[(v, e)] = model.new_bool_var(f'l{v}{e}')

        for e in seg_edges:
            lve = l[(v, e)]
            pe = prev_edge(e, v, eidx)

            model.add(lve <= x[e])

            if pe is None:
                model.add(lve == x[e])
            else:
                if (v, pe) not in l:
                    l[(v, pe)] = model.new_bool_var(f'l{v}{pe}')
                lpve = l[(v, pe)]
                model.add(lve <= lpve)
                model.add(lve >= x[e] + lpve - 1)

        model.add(sum(l[(v, e)] for e in seg_edges) == Nv)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 120.0
    solver.parameters.log_search_progress = False

    status = solver.solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None

    return [
        Edge(from_cell=e[0], to_cell=e[1])
        for e in E
        if solver.value(x[e]) == 1
    ]
