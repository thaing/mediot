<template>
  <div class="dashboard">
    <header class="top-bar">
      <h1>medIoT Dashboard</h1>
      <div class="user-info">
        <span>{{ authStore.userName }}</span>
        <button @click="authStore.logout">Sign out</button>
      </div>
    </header>
    <main class="chart-grid">
      <div class="chart-placeholder">Heart Rate — to be implemented in plan 01-08</div>
      <div class="chart-placeholder">Blood Pressure</div>
      <div class="chart-placeholder">SpO2</div>
      <div class="chart-placeholder">Battery</div>
    </main>
  </div>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'
const authStore = useAuthStore()
</script>

<style scoped>
.dashboard { padding: 20px; }
.top-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.chart-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.chart-placeholder { background: #f5f5f5; border: 1px dashed #ccc; border-radius: 8px; padding: 40px; text-align: center; color: #999; }
</style>
