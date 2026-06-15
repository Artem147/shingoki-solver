<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import type { Circle, Edge } from '../types'
import CircleNode from './CircleNode.vue'
import SolutionOverlay from './SolutionOverlay.vue'

const props = defineProps<{
  circles: Circle[]
  rows: number
  cols: number
  edges: Edge[]
  editable: boolean
}>()

const emit = defineEmits<{
  'update:circles': [circles: Circle[]]
}>()

const CELL = 60

const svgW = computed(() => props.cols * CELL)
const svgH = computed(() => props.rows * CELL)

const cells = computed(() => {
  const out: { row: number; col: number }[] = []
  for (let r = 0; r < props.rows; r++)
    for (let c = 0; c < props.cols; c++)
      out.push({ row: r, col: c })
  return out
})

const editingAt = ref<{ row: number; col: number } | null>(null)

const editingMax = computed(() => {
  if (!editingAt.value) return 1
  const circle = getCircle(editingAt.value.row, editingAt.value.col)
  if (!circle) return 1
  return circle.type === 'black'
    ? (props.rows - 1) + (props.cols - 1)
    : Math.max(props.rows - 1, props.cols - 1)
})
const editingValue = ref('')
const numberInput = ref<HTMLInputElement | null>(null)

watch(editingAt, async (val) => {
  if (val) {
    await nextTick()
    numberInput.value?.focus()
    numberInput.value?.select()
  }
})

function editorStyle(row: number, col: number): Record<string, string> {
  const rightX = col * CELL + CELL + 4
  const x = rightX + 68 > svgW.value ? col * CELL - 72 : rightX
  const y = row * CELL + CELL / 2 - 18
  return { left: x + 'px', top: y + 'px' }
}

function getCircle(row: number, col: number): Circle | undefined {
  return props.circles.find((c) => c.row === row && c.col === col)
}

function handleClick(row: number, col: number) {
  if (!props.editable) return
  editingAt.value = null

  const existing = getCircle(row, col)
  let next: Circle[]

  if (!existing) {
    next = [...props.circles, { row, col, type: 'black', number: 1 }]
  } else if (existing.type === 'black') {
    next = props.circles.map((c) =>
      c.row === row && c.col === col ? { ...c, type: 'white' as const } : c,
    )
  } else {
    next = props.circles.filter((c) => !(c.row === row && c.col === col))
  }

  emit('update:circles', next)
}

function handleRightClick(e: MouseEvent, row: number, col: number) {
  if (!props.editable) return
  e.preventDefault()
  const circle = getCircle(row, col)
  if (!circle) return
  editingAt.value = { row, col }
  editingValue.value = String(circle.number)
}

function confirmEdit() {
  if (!editingAt.value) return
  const raw = parseInt(editingValue.value, 10)
  if (!isNaN(raw) && raw >= 1) {
    const n = Math.min(raw, editingMax.value)
    const { row, col } = editingAt.value
    emit(
      'update:circles',
      props.circles.map((c) =>
        c.row === row && c.col === col ? { ...c, number: n } : c,
      ),
    )
  }
  editingAt.value = null
}

function cancelEdit() {
  editingAt.value = null
}
</script>

<template>
  <div class="relative inline-block">
    <svg
      :width="svgW"
      :height="svgH"
      class="block border border-gray-300 rounded shadow-sm bg-white"
    >
      <line
        v-for="r in rows + 1"
        :key="'h' + r"
        x1="0"
        :y1="(r - 1) * CELL"
        :x2="svgW"
        :y2="(r - 1) * CELL"
        stroke="#e5e7eb"
        stroke-width="1"
      />
      <line
        v-for="c in cols + 1"
        :key="'v' + c"
        :x1="(c - 1) * CELL"
        y1="0"
        :x2="(c - 1) * CELL"
        :y2="svgH"
        stroke="#e5e7eb"
        stroke-width="1"
      />

      <SolutionOverlay v-if="edges.length > 0" :edges="edges" :cell-size="CELL" />

      <CircleNode
        v-for="circle in circles"
        :key="`${circle.row}-${circle.col}`"
        :circle="circle"
        :cell-size="CELL"
      />

      <g v-if="editable">
        <rect
          v-for="cell in cells"
          :key="`t-${cell.row}-${cell.col}`"
          :x="cell.col * CELL"
          :y="cell.row * CELL"
          :width="CELL"
          :height="CELL"
          fill="transparent"
          class="cursor-pointer"
          @click="handleClick(cell.row, cell.col)"
          @contextmenu="handleRightClick($event, cell.row, cell.col)"
        />
      </g>
    </svg>

    <div
      v-if="editingAt"
      class="absolute z-20 flex items-center gap-1.5 bg-white border border-gray-300
             rounded-md shadow-lg px-2 py-1.5"
      :style="editorStyle(editingAt.row, editingAt.col)"
      @click.stop
    >
      <input
        ref="numberInput"
        v-model="editingValue"
        type="number"
        min="1"
        :max="editingMax"
        class="w-14 text-center text-sm font-mono border border-gray-300 rounded
               px-1 py-0.5 focus:outline-none focus:border-blue-500
               [appearance:textfield]
               [&::-webkit-outer-spin-button]:appearance-none
               [&::-webkit-inner-spin-button]:appearance-none"
        @keydown.enter="confirmEdit"
        @keydown.escape="cancelEdit"
        @blur="confirmEdit"
      />
      <span class="text-xs text-gray-400 select-none">1–{{ editingMax }}</span>
    </div>
  </div>
</template>
