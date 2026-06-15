<script setup lang="ts">
import type { Edge } from '../types'

const props = defineProps<{
  edges: Edge[]
  cellSize: number
}>()

function cx(col: number) {
  return col * props.cellSize + props.cellSize / 2
}
function cy(row: number) {
  return row * props.cellSize + props.cellSize / 2
}
</script>

<template>
  <g>
    <line
      v-for="(edge, i) in edges"
      :key="i"
      :x1="cx(edge.from_[1])"
      :y1="cy(edge.from_[0])"
      :x2="cx(edge.to[1])"
      :y2="cy(edge.to[0])"
      stroke="#2563EB"
      stroke-width="3"
      stroke-linecap="round"
    />
  </g>
</template>
