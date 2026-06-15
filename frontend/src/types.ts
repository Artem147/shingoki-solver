export interface Circle {
  row: number
  col: number
  type: 'white' | 'black'
  number: number
}

export interface Puzzle {
  rows: number
  cols: number
  circles: Circle[]
}

export interface Edge {
  from_: [number, number]
  to: [number, number]
}

export interface SolveResponse {
  edges: Edge[]
  solved: boolean
}
