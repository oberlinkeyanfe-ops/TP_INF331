<template>
  <div class="auth-container">
    <div class="auth-wrapper">
    <div class="auth-left">
      <div class="brand-top">
        <img src="../assets/icons/LOGO.svg" alt="Logo" />
        <h1>AVICULTURE PRO</h1>
      </div>

      <div class="poster-text">
        <p>Bienvenue sur Aviculture Pro</p>
        <p>Rejoignez notre communauté<br /> d'éleveurs et accédez à des <br />ressources,conseils et outils <br />pour optimiser votre activité <br />avicole.</p>
      </div>
      
    </div>

    <div class="auth-right auth-card">
        <div class="brand-small" style="margin-bottom: 32px; text-align: center;">
            <h2 style="font-size: 1.95rem; font-weight: 700; margin-top: 10px;margin-left: 20vw;">Connexion</h2>
        </div>

        <form @submit.prevent="submit" style="width: 100%; max-width: 420px; margin: 0 auto;">
            <div class="form-row login" style="display: flex;flex-direction: column; flex-wrap: wrap; gap: 12px;">
              <div class="input-group" style="flex: 1 1 48%; min-width: 160px; max-width: 200px; margin-bottom: 0;">
                <label style="font-size: 1rem; font-weight: 600; margin-bottom: 4px;margin-left: 0;">Email <span class="required-star">*</span></label>
                <input v-model="email" type="email" required placeholder="votre@email.com" style="font-size: 1rem; padding: 6px 10px; height: 32px; width: 20vw;" />
                <div class="input-hint" style="font-size: 0.9rem; margin-top: 2px;">Entrez l'adresse utilisée pour votre compte.</div>
              </div>
              <div class="input-group" style="flex: 1 1 48%; min-width: 160px; max-width: 200px; margin-bottom: 0;">
                <label style="font-size: 1rem; font-weight: 600; margin-bottom: 4px;">Mot de passe <span class="required-star">*</span></label>
                <input v-model="password" type="password" required placeholder="Mot de passe" style="font-size: 1rem; padding: 6px 10px; height: 32px; width: 20vw;" />
              </div>
            </div>

          <div class="form-actions" style="margin-top: 38px; display: flex; align-items: center; justify-content: space-between; gap: 18px;">
             <label class="remember" style="font-size: 0.95rem;"><input type="checkbox" v-model="remember"/> Se souvenir de moi</label>
             <a class="forgot-link" href="#" style="font-size: 0.95rem;">Mot de passe oublié ?</a>
          </div>

          <div class="button-sub" style="margin-top: 24px;">
             <button class="button-primary" type="submit" style="font-size: 1rem; padding: 10px 18px;">Se connecter</button>
          </div>
        </form>

        <p class="muted" style="font-size: 1.05rem; margin-top: 24px; text-align: center;">Pas encore inscrit ? <router-link to="/register">Créer un compte</router-link></p>
          <p v-if="error" class="error" style="font-size: 0.95rem; margin-top: 10px; text-align: center;">{{ error }}</p>
    </div>
  </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      email: '',
      password: '',
      remember: false,
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
          body: JSON.stringify({ email: this.email, mot_de_passe: this.password, remember: this.remember })
        })

        if (!res.ok) {
          const txt = await res.text()
          this.error = txt || 'Échec de la connexion'
          return
        }

        // Transformer la réponse en JSON
        const data = await res.json()

        // Sauvegarder l'utilisateur côté client : si 'remember' alors localStorage sinon sessionStorage
        if (this.remember) {
          localStorage.setItem("user", JSON.stringify(data.user))
        } else {
          sessionStorage.setItem("user", JSON.stringify(data.user))
        }

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
