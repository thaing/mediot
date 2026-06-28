<template>
  <div class="vital-chart">
    <h3>{{ title }}</h3>
    <Line v-if="chartData" :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  TimeScale,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'

ChartJS.register(
  LineElement, PointElement, CategoryScale, LinearScale,
  TimeScale, Title, Tooltip, Legend, Filler
)

const props = defineProps({
  title: String,
  dataPoints: { type: Array, default: () => [] },
  yLabel: { type: String, default: '' },
  color: { type: String, default: '#4285f4' },
  chartType: { type: String, default: 'line' },
})

const chartData = computed(() => {
  if (!props.dataPoints?.length) return null

  const labels = props.dataPoints.map(p => {
    const d = new Date(p.x * 1000)
    return d.toLocaleTimeString()
  })

  if (props.chartType === 'dual-line') {
    return {
      labels,
      datasets: [
        {
          label: 'Systolic',
          data: props.dataPoints.map(p => p.sys),
          borderColor: '#e74c3c',
          backgroundColor: 'rgba(231,76,60,0.1)',
          fill: true,
          tension: 0.3,
        },
        {
          label: 'Diastolic',
          data: props.dataPoints.map(p => p.dia),
          borderColor: '#3498db',
          backgroundColor: 'rgba(52,152,219,0.1)',
          fill: true,
          tension: 0.3,
        },
      ],
    }
  }

  return {
    labels,
    datasets: [{
      label: props.title,
      data: props.dataPoints.map(p => p.y),
      borderColor: props.color,
      backgroundColor: props.color + '20',
      fill: true,
      tension: 0.3,
    }],
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: true } },
  scales: {
    y: { title: { display: true, text: props.yLabel } },
  },
}
</script>

<style scoped>
.vital-chart {
  background: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 1px 8px rgba(0,0,0,0.08);
  height: 280px;
}
h3 { margin: 0 0 12px; font-size: 14px; color: #666; }
</style>
