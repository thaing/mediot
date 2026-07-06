<template>
  <div class="dashboard">
    <header class="top-bar">
      <h1>medIoT Dashboard</h1>
      <div class="user-info">
        <span>{{ authStore.userName }}</span>
        <button @click="authStore.logout">Sign out</button>
      </div>
    </header>

    <div class="controls">
      <span>Time range:</span>
      <button
        v-for="r in ranges" :key="r.label"
        :class="{ active: selectedRange === r.value }"
        @click="selectedRange = r.value; loadData()"
      >
        {{ r.label }}
      </button>
      <button @click="loadData" class="refresh">⟳ Refresh</button>
    </div>

    <div class="chart-grid">
      <VitalChart
        title="Heart Rate"
        :data-points="hrData"
        y-label="BPM"
        color="#e74c3c"
      />
      <VitalChart
        title="Blood Pressure"
        :data-points="bpData"
        y-label="mmHg"
        chart-type="dual-line"
      />
      <VitalChart
        title="SpO₂"
        :data-points="spo2Data"
        y-label="%"
        color="#3498db"
      />
      <BatteryGauge :value="batteryLevel" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { fetchReadings } from '../services/api'
import VitalChart from '../components/VitalChart.vue'
import BatteryGauge from '../components/BatteryGauge.vue'

const authStore = useAuthStore()

const ranges = [
  { label: '15m', value: 900 },
  { label: '1h', value: 3600 },
  { label: '6h', value: 21600 },
  { label: '24h', value: 86400 },
]

const selectedRange = ref(3600)
const hrData = ref([])
const bpData = ref([])
const spo2Data = ref([])
const batteryLevel = ref(0)
const deviceId = ref(null)
let interval = null

async function loadData() {
  const now = Math.floor(Date.now() / 1000)
  const from_ts = now - selectedRange.value

  try {
    const readings = await fetchReadings(deviceId.value, from_ts, now)
    if (!readings?.length) return

    hrData.value = readings.map(r => ({ x: r.ts, y: r.hr }))
    bpData.value = readings.map(r => ({ x: r.ts, sys: r.bp_sys, dia: r.bp_dia }))
    spo2Data.value = readings.map(r => ({ x: r.ts, y: r.spo2 }))

    const last = readings[readings.length - 1]
    batteryLevel.value = last.bat ?? 0
  } catch (e) {
    console.error('Failed to load readings:', e)
  }
}

onMounted(async () => {
  deviceId.value = localStorage.getItem('device_id') || ''
  await new Promise(r => setTimeout(r, 500))
  loadData()
  interval = setInterval(loadData, 5000)
})

onUnmounted(() => clearInterval(interval))
</script>

<style scoped>
.dashboard { padding: 20px; max-width: 1200px; margin: 0 auto; }
.top-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.top-bar h1 { font-size: 22px; }
.user-info { display: flex; align-items: center; gap: 12px; }
.user-info button { padding: 6px 16px; border: 1px solid #ddd; border-radius: 6px; background: white; cursor: pointer; }
.controls { display: flex; align-items: center; gap: 8px; margin-bottom: 20px; }
.controls button {
  padding: 4px 12px; border: 1px solid #ddd; border-radius: 6px;
  background: white; cursor: pointer; font-size: 13px;
}
.controls button.active { background: #4285f4; color: white; border-color: #4285f4; }
.controls button.refresh { background: #f0f0f0; }
.chart-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
</style>
