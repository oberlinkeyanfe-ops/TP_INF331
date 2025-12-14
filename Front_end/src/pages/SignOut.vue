<template>
  <link rel="stylesheet" href="/css/auth.css" />
  <div style="display:flex;align-items:center;justify-content:center;height:60vh">
    <div class="auth-card">
      <div class="brand"><img src="../assets/icons/LOGO.svg" alt="Logo" /><h1>Déconnexion</h1></div>
      <div style="padding:12px">
        <p>Déconnexion en cours…</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  async mounted() {
    try {
      await fetch('/auth/logout', { method: 'POST', credentials: 'same-origin' })
    } catch (e) {
      try {
        await fetch('/auth/logout', { method: 'GET', credentials: 'same-origin' })
      } catch (e2) {
        console.warn('Logout request failed', e2)
      }
    } finally {
      window.location.href = '/login'
    }
  }
}
</script>
