<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="brand">
        <img src="/assets/LOGO.svg" alt="Logo" />
        <h1>Connexion</h1>
      </div>
      <form @submit.prevent="submit">
        <div class="input">
          <label>Email</label>
          <input v-model="email" type="email" required />
        
          <label>Mot de passe</label>
          <input v-model="password" type="password" required />
        </div>
        <div class="button-sub">
          <button type="submit">Se connecter</button>
        </div>
      </form>
      <p class="muted">
        Pas encore inscrit ? <router-link to="/register">Créer un compte</router-link>
      </p>
      <p v-if="error" class="error">{{ error }}</p>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      email: '',
      password: '',
      error: '',
      user: null
    }
  },
  methods: {
    async submit() {
      this.error = ''
      try {
        const res = await fetch('http://localhost:5000/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include', // pour envoyer les cookies si nécessaire
          body: JSON.stringify({ email: this.email, mot_de_passe: this.password })
        })

        if (!res.ok) {
          const txt = await res.text()
          this.error = txt || 'Échec de la connexion'
          return
        }

        // Transformer la réponse en JSON
        const data = await res.json()

        // Sauvegarder l'utilisateur dans la session
        sessionStorage.setItem("user", JSON.stringify(data.user))

        // Mettre à jour le state local
        this.user = data.user

        // Redirection
        this.$router.push('/home')
      } catch (e) {
        this.error = e
      }
    }
  }
}
</script>
