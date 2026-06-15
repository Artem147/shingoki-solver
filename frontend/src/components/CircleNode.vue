<script setup lang="ts">
import type { Circle } from '../types'

const props = defineProps<{
  circle: Circle
  cellSize: number
}>()

const R = 18

function cx(col: number) {
  return col * props.cellSize + props.cellSize / 2
}
function cy(row: number) {
  return row * props.cellSize + props.cellSize / 2
}
</script>

<template>
  <g>
    <circle
      :cx="cx(circle.col)"
      :cy="cy(circle.row)"
      :r="R"
      :fill="circle.type === 'black' ? '#111827' : 'white'"
      stroke="#111827"
      stroke-width="2"
    />
    <text
      :x="cx(circle.col)"
      :y="cy(circle.row)"
      text-anchor="middle"
      dominant-baseline="central"
      font-size="13"
      font-weight="600"
      font-family="ui-monospace, monospace"
      :fill="circle.type === 'black' ? 'white' : '#111827'"
    >{{ circle.number }}</text>
  </g>
</template>
