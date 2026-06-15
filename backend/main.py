from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from shingoki import Circle as SolverCircle, solve

app = FastAPI(title="Shingoki Solver API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class CircleIn(BaseModel):
    row: int
    col: int
    type: str
    number: int


class PuzzleIn(BaseModel):
    rows: int
    cols: int
    circles: list[CircleIn]


class EdgeOut(BaseModel):
    from_: list[int]
    to: list[int]

    class Config:
        populate_by_name = True

    @classmethod
    def from_tuple(cls, f: tuple[int, int], t: tuple[int, int]) -> "EdgeOut":
        return cls(from_=list(f), to=list(t))


class SolveResponse(BaseModel):
    edges: list[EdgeOut]
    solved: bool


@app.post("/solve", response_model=SolveResponse)
def solve_puzzle(puzzle: PuzzleIn) -> SolveResponse:
    circles = [
        SolverCircle(row=c.row, col=c.col, type=c.type, number=c.number)
        for c in puzzle.circles
    ]
    result = solve(puzzle.rows, puzzle.cols, circles)
    if result is None:
        return SolveResponse(edges=[], solved=False)
    edges = [EdgeOut.from_tuple(e.from_cell, e.to_cell) for e in result]
    return SolveResponse(edges=edges, solved=True)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
