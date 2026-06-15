<script setup lang="ts">
import { ref, watch } from 'vue'
import type { Circle, Edge } from './types'
import PuzzleGrid from './components/PuzzleGrid.vue'
import { solvePuzzle } from './api'

const EXAMPLES: Record<string, Circle[]> = {
  '4x4': [
    { row: 0, col: 1, type: 'black', number: 2 }, { row: 0, col: 2, type: 'black', number: 2 },
    { row: 1, col: 0, type: 'black', number: 2 }, { row: 2, col: 0, type: 'black', number: 2 },
    { row: 1, col: 3, type: 'black', number: 2 }, { row: 2, col: 3, type: 'black', number: 2 },
    { row: 3, col: 1, type: 'black', number: 2 }, { row: 3, col: 2, type: 'black', number: 2 },
  ],
  '5x5': [
    { row: 1, col: 1, type: 'black', number: 2 }, { row: 1, col: 3, type: 'black', number: 2 },
    { row: 3, col: 1, type: 'black', number: 2 }, { row: 3, col: 3, type: 'black', number: 2 },
    { row: 0, col: 2, type: 'black', number: 3 }, { row: 2, col: 0, type: 'black', number: 3 },
    { row: 2, col: 4, type: 'black', number: 3 }, { row: 4, col: 2, type: 'black', number: 3 },
  ],
  '6x6': [
    { row: 0, col: 0, type: 'black', number: 6 }, { row: 0, col: 2, type: 'black', number: 2 },
    { row: 0, col: 4, type: 'black', number: 3 }, { row: 1, col: 1, type: 'black', number: 2 },
    { row: 1, col: 3, type: 'white', number: 2 }, { row: 1, col: 5, type: 'white', number: 3 },
    { row: 2, col: 0, type: 'white', number: 5 }, { row: 2, col: 2, type: 'black', number: 2 },
    { row: 2, col: 4, type: 'black', number: 3 }, { row: 3, col: 1, type: 'white', number: 2 },
    { row: 3, col: 3, type: 'black', number: 3 }, { row: 3, col: 5, type: 'black', number: 4 },
    { row: 4, col: 0, type: 'white', number: 5 }, { row: 4, col: 2, type: 'black', number: 2 },
    { row: 4, col: 4, type: 'black', number: 2 }, { row: 5, col: 1, type: 'white', number: 2 },
    { row: 5, col: 3, type: 'black', number: 4 }, { row: 5, col: 5, type: 'black', number: 3 },
  ],
  '7x7': [
    { row: 2, col: 2, type: 'black', number: 3 }, { row: 2, col: 4, type: 'black', number: 3 },
    { row: 4, col: 2, type: 'black', number: 3 }, { row: 4, col: 4, type: 'black', number: 3 },
  ],
  '8x8': [
    { row: 0, col: 0, type: 'black', number: 4 }, { row: 0, col: 7, type: 'black', number: 4 },
    { row: 7, col: 0, type: 'black', number: 4 }, { row: 7, col: 7, type: 'black', number: 4 },
    { row: 2, col: 2, type: 'black', number: 3 }, { row: 2, col: 5, type: 'black', number: 3 },
    { row: 5, col: 2, type: 'black', number: 3 }, { row: 5, col: 5, type: 'black', number: 3 },
  ],
  '10x10': [
    { row: 0, col: 0, type: 'black', number: 4 }, { row: 0, col: 9, type: 'black', number: 4 },
    { row: 9, col: 0, type: 'black', number: 4 }, { row: 9, col: 9, type: 'black', number: 4 },
    { row: 2, col: 2, type: 'black', number: 3 }, { row: 2, col: 7, type: 'black', number: 3 },
    { row: 7, col: 2, type: 'black', number: 3 }, { row: 7, col: 7, type: 'black', number: 3 },
    { row: 4, col: 4, type: 'black', number: 4 }, { row: 4, col: 6, type: 'black', number: 4 },
    { row: 6, col: 4, type: 'black', number: 4 }, { row: 6, col: 6, type: 'black', number: 4 },
  ],
}

const GRID_SIZES = [4, 5, 6, 7, 8, 10]

type Mode = 'solver' | 'editor'
const mode = ref<Mode>('solver')

const SOLVER_ROWS = 6
const SOLVER_COLS = 6

const editorRows = ref(6)
const editorCols = ref(6)
const editorCircles = ref<Circle[]>([])

const edges = ref<Edge[]>([])
const loading = ref(false)
const errorMsg = ref<string | null>(null)
const validationMsg = ref<string | null>(null)
const successMsg = ref<string | null>(null)

function clearFeedback() {
  errorMsg.value = null
  validationMsg.value = null
  successMsg.value = null
}

watch(editorCircles, () => {
  edges.value = []
  successMsg.value = null
  validationMsg.value = null
})

function switchMode() {
  mode.value = mode.value === 'solver' ? 'editor' : 'solver'
  edges.value = []
  clearFeedback()
}

function onSizeChange(size: number) {
  editorRows.value = size
  editorCols.value = size
  editorCircles.value = []
  edges.value = []
  clearFeedback()
}

function onClear() {
  editorCircles.value = []
  edges.value = []
  clearFeedback()
}

function onLoadExample() {
  const key = `${editorRows.value}x${editorCols.value}`
  const example = EXAMPLES[key]
  if (!example) {
    validationMsg.value = `No example for ${editorRows.value}×${editorCols.value}.`
    return
  }
  editorCircles.value = example.map((c) => ({ ...c }))
  edges.value = []
  clearFeedback()
}

function validate(): boolean {
  if (mode.value === 'editor' && editorCircles.value.length < 2) {
    validationMsg.value = 'Place at least 2 circles before solving.'
    return false
  }
  validationMsg.value = null
  return true
}

async function onSolve() {
  if (!validate()) return
  loading.value = true
  errorMsg.value = null
  successMsg.value = null
  edges.value = []

  const puzzle =
    mode.value === 'solver'
      ? { rows: SOLVER_ROWS, cols: SOLVER_COLS, circles: EXAMPLES['6x6'] }
      : { rows: editorRows.value, cols: editorCols.value, circles: editorCircles.value }

  try {
    const result = await solvePuzzle(puzzle)
    if (result.solved) {
      edges.value = result.edges
      successMsg.value = `Solved — ${result.edges.length} edges in the loop.`
    } else {
      errorMsg.value = 'No solution found for this puzzle.'
    }
  } catch {
    errorMsg.value = 'Failed to reach the solver. Is the backend running on port 8000?'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex flex-col items-center py-10 px-4 gap-6">

    <div class="w-full max-w-2xl flex items-start justify-between">
      <div>
        <h1 class="text-2xl font-semibold tracking-tight text-gray-900">Shingoki Solver</h1>
        <p class="text-sm text-gray-500 mt-0.5">
          <template v-if="mode === 'solver'">
            6 × 6 — white circles go straight, black circles turn
          </template>
          <template v-else>
            {{ editorRows }} × {{ editorCols }} grid — editor mode
          </template>
        </p>
      </div>

      <button
        class="mt-1 px-4 py-1.5 text-sm font-medium rounded-md border transition-colors"
        :class="
          mode === 'editor'
            ? 'border-blue-500 text-blue-600 hover:bg-blue-50'
            : 'border-gray-300 text-gray-600 hover:bg-gray-100'
        "
        @click="switchMode"
      >
        {{ mode === 'solver' ? 'Editor mode' : 'Solver mode' }}
      </button>
    </div>

    <div v-if="mode === 'editor'" class="w-full max-w-2xl flex flex-col gap-2">
      <div class="flex items-center gap-2 flex-wrap">
        <span class="text-sm text-gray-500 font-medium w-20">Grid size:</span>
        <button
          v-for="size in GRID_SIZES"
          :key="size"
          class="px-3 py-1 text-sm rounded-md border transition-colors"
          :class="
            editorRows === size
              ? 'bg-blue-600 text-white border-blue-600'
              : 'border-gray-300 text-gray-600 hover:bg-gray-100'
          "
          @click="onSizeChange(size)"
        >
          {{ size }}×{{ size }}
        </button>
      </div>

      <div class="flex items-center justify-between">
        <p class="text-xs text-gray-400 leading-relaxed">
          Click: cycle empty → black → white → empty
          &nbsp;·&nbsp;
          Right-click: edit number
        </p>
        <span class="text-xs text-gray-500 whitespace-nowrap pl-4">
          {{ editorCircles.length }} circle{{ editorCircles.length !== 1 ? 's' : '' }}
        </span>
      </div>
    </div>

    <PuzzleGrid
      v-if="mode === 'solver'"
      :circles="EXAMPLES['6x6']"
      :rows="SOLVER_ROWS"
      :cols="SOLVER_COLS"
      :edges="edges"
      :editable="false"
    />

    <PuzzleGrid
      v-else
      v-model:circles="editorCircles"
      :rows="editorRows"
      :cols="editorCols"
      :edges="edges"
      :editable="true"
    />

    <div class="flex items-center gap-3">
      <button
        class="px-8 py-2 bg-blue-600 text-white rounded-md text-sm font-semibold tracking-wide
               hover:bg-blue-700 active:bg-blue-800 disabled:opacity-50 disabled:cursor-not-allowed
               transition-colors duration-150 shadow-sm"
        :disabled="loading"
        @click="onSolve"
      >
        <span v-if="loading" class="inline-flex items-center gap-2">
          <svg class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          Solving…
        </span>
        <span v-else>Solve</span>
      </button>

      <template v-if="mode === 'editor'">
        <button
          class="px-4 py-2 text-sm font-medium rounded-md border border-gray-300
                 text-gray-600 hover:bg-gray-100 transition-colors"
          @click="onClear"
        >
          Clear
        </button>
        <button
          class="px-4 py-2 text-sm font-medium rounded-md border border-gray-300
                 text-gray-600 hover:bg-gray-100 transition-colors"
          @click="onLoadExample"
        >
          Load example
        </button>
      </template>
    </div>

    <div class="flex flex-col items-center gap-1 min-h-[1.5rem]">
      <p v-if="validationMsg" class="text-sm text-amber-600 font-medium">{{ validationMsg }}</p>
      <p v-if="errorMsg"      class="text-sm text-red-600   font-medium">{{ errorMsg }}</p>
      <p v-if="successMsg"    class="text-sm text-green-600 font-medium">{{ successMsg }}</p>
    </div>

  </div>
</template>
