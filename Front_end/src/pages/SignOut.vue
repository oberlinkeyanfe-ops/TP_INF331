<template>
  <link rel="stylesheet" href="/css/auth.css" />
  <div class="auth-wrapper" style="min-height:60vh;">
    <div class="auth-left">
      <div class="brand-top">
        <img src="../assets/icons/LOGO.svg" alt="Logo" />
        <h1>AVICULTURE PRO</h1>
      </div>
      <div class="poster-text">Vous êtes en train de vous déconnecter. À bientôt !</div>
    </div>
    <div class="auth-right auth-card" style="display:flex;align-items:center;justify-content:center;">
      <div style="text-align:center;padding:18px;">
          <div class="brand-small" style="margin-bottom: 32px; text-align: center;">
             <img src="../assets/icons/LOGO.svg" alt="Logo" style="width: 60px; height: 60px;" />
             <h2 style="font-size: 1.35rem; font-weight: 700; margin-top: 10px;">Déconnexion</h2>
          </div>
          <div style="margin-top:18px; font-size: 1.25rem; font-weight: 500;">Déconnexion en cours…</div>
            <div style="margin-top:16px; font-size: 1rem; font-weight: 400;">Déconnexion en cours…</div>
            <div style="margin-top:16px"><svg width="40" height="40" viewBox="0 0 50 50" xmlns="http://www.w3.org/2000/svg" fill="none"><circle cx="25" cy="25" r="20" stroke="#10b981" stroke-width="4" stroke-linecap="round" stroke-dasharray="31.415,31.415"><animateTransform attributeName="transform" type="rotate" from="0 25 25" to="360 25 25" dur="1s" repeatCount="indefinite"/></circle></svg></div>
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
