import axios from 'axios'
import type { Puzzle, SolveResponse } from './types'

export async function solvePuzzle(puzzle: Puzzle): Promise<SolveResponse> {
  const { data } = await axios.post<SolveResponse>('http://localhost:8000/solve', puzzle)
  return data
}
