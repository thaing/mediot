<template>
  <div class="battery-gauge">
    <h3>Battery</h3>
    <svg viewBox="0 0 120 120" class="gauge">
      <circle cx="60" cy="60" r="50" fill="none" stroke="#eee" stroke-width="10" />
      <circle
        cx="60" cy="60" r="50"
        fill="none"
        :stroke="color"
        stroke-width="10"
        stroke-linecap="round"
        :stroke-dasharray="circumference"
        :stroke-dashoffset="offset"
        transform="rotate(-90 60 60)"
      />
      <text x="60" y="58" text-anchor="middle" class="value">{{ value }}%</text>
    </svg>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ value: { type: Number, default: 0 } })

const circumference = 2 * Math.PI * 50
const offset = computed(() => circumference - (props.value / 100) * circumference)
const color = computed(() =>
  props.value > 50 ? '#27ae60' : props.value > 20 ? '#f39c12' : '#e74c3c'
)
</script>

<style scoped>
.battery-gauge {
  background: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 1px 8px rgba(0,0,0,0.08);
  text-align: center;
  height: 280px;
}
h3 { margin: 0 0 8px; font-size: 14px; color: #666; }
.gauge { width: 160px; height: 160px; }
.value { font-size: 28px; font-weight: bold; }
</style>
