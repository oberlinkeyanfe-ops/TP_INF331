<template>
  <link rel="stylesheet" href="/css/auth.css" />
  <div class="auth-container">
    <div class="auth-card">
      <div class="brand">
        <img src="../assets/icons/LOGO.svg" alt="Logo" />
        <h1>Inscription</h1>
      </div>
      <form @submit.prevent="submit">
        <div class = "input">
          <label>Nom</label>
          <input v-model="name" type="text" required />
          <label>Email</label>
          <input v-model="email" type="email" required />

          <label>Mot de passe</label>
          <input v-model="password" type="password" required />

          <label>Adresse</label>
          <input v-model="adresse" type="text" required />
          <label>telephone</label>
          <input v-model="tel" type="telephone" required />

          
        </div>

        <div class="button-sub">
          <button type="submit">Créer un compte</button>
        </div>
        
      </form>
      <p class="muted">Déjà inscrit ? <router-link to="/login">Se connecter</router-link></p>
      <p v-if="error" class="error">{{ error }}</p>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      name: '',
      email: '',
      password: '',
      adresse: '',
      tel: '',
      error: ''
    }
  },
  methods: {
    async submit() {
      this.error = ''
      try {
        const res = await fetch('http://localhost:5000/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'same-origin',
          body: JSON.stringify({ nom: this.name, email: this.email, mot_de_passe: this.password , adresse: this.adresse, tel: this.tel })
        })
        if (!res.ok) {
          const txt = await res.text()
          this.error = txt || 'Échec de l\'inscription'
          return
        }
        this.$router.push('/login')
      } catch (e) {
        this.error = 'Erreur réseau'
      }
    }
  }
}
</script>
