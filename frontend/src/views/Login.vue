<template>
  <div class="login-container">
    <div class="login-card">
      <h1>medIoT</h1>
      <p class="subtitle">Medical IoT Monitoring Platform</p>

      <div class="providers">
        <button class="provider google" @click="login('google')">
          Sign in with Google
        </button>
        <button class="provider apple" @click="login('apple')">
          Sign in with Apple
        </button>
        <button class="provider facebook" @click="login('facebook')">
          Sign in with Facebook
        </button>
      </div>

      <p v-if="loading" class="loading">Redirecting...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { initOAuthLogin, handleOAuthCallback } from '../services/auth'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)

function login(provider) {
  loading.value = true
  initOAuthLogin(provider)
}

onMounted(() => {
  const result = handleOAuthCallback()
  if (result?.token) {
    authStore.login(result.token, result.user)
    router.push('/')
  }
})
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f0f2f5;
}

.login-card {
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 2px 16px rgba(0,0,0,0.1);
  text-align: center;
  max-width: 400px;
  width: 100%;
}

h1 {
  margin: 0;
  font-size: 28px;
  color: #1a73e8;
}

.subtitle {
  color: #666;
  margin: 8px 0 32px;
}

.providers {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.provider {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.provider:hover { opacity: 0.9; }

.google { background: #4285f4; color: white; }
.apple { background: #000; color: white; }
.facebook { background: #1877f2; color: white; }

.loading { margin-top: 20px; color: #999; }
</style>
