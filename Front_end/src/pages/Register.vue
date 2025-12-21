<template>
  <link rel="stylesheet" href="/css/auth.css" />
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
            <h2 style="font-size: 1.95rem; font-weight: 700; margin-top: 10px;margin-left: 20vw;">Inscription</h2>
        </div>

        <form @submit.prevent="submit" style="width: 100%; max-width: 500px; margin: 0 auto;">
            <div class="form-row" style="display: flex; flex-wrap: wrap; gap: 19px;">
              <div class="input-group" style="flex: 1 1 48%; min-width: 140px; max-width: 200px; margin-bottom: 0;">
                <label style="font-size: 1rem; font-weight: 600; margin-bottom: 4px;">Nom <span class="required-star">*</span></label>
                <input v-model="name" type="text" required placeholder="Votre nom complet" style="font-size: 1rem; padding: 6px 10px; height: 32px; width: 100%;" />
              </div>
              <div class="input-group" style="flex: 1 1 48%; min-width: 140px; max-width: 200px; margin-bottom: 0;">
                <label style="font-size: 1rem; font-weight: 600; margin-bottom: 4px;">Email <span class="required-star">*</span></label>
                <input v-model="email" type="email" required placeholder="votre@email.com" style="font-size: 1rem; padding: 6px 10px; height: 32px; width: 100%;" />
                <div class="input-hint" style="font-size: 0.9rem; margin-top: 2px;">Une adresse valide est nécessaire pour la connexion.</div>
              </div>
              <div class="input-group" style="flex: 1 1 48%; min-width: 140px; max-width: 200px; margin-bottom: 0;">
                <label style="font-size: 1rem; font-weight: 600; margin-bottom: 4px;">Mot de passe <span class="required-star">*</span></label>
                <input v-model="password" type="password" required placeholder="Choisissez un mot de passe" style="font-size: 1rem; padding: 6px 10px; height: 32px; width: 100%;" />
              </div>
              <div class="input-group" style="flex: 1 1 48%; min-width: 140px; max-width: 200px; margin-bottom: 0;">
                <label style="font-size: 1rem; font-weight: 600; margin-bottom: 4px;">Adresse</label>
                <input v-model="adresse" type="text" placeholder="Ville, quartier" style="font-size: 1rem; padding: 6px 10px; height: 32px; width: 100%;" />
              </div>
              <div class="input-group" style="flex: 1 1 48%; min-width: 140px; max-width: 200px; margin-bottom: 0;">
                <label style="font-size: 1rem; font-weight: 600; margin-bottom: 4px;">Téléphone</label>
                <input v-model="tel" type="tel" placeholder="+226 70 00 00 00" style="font-size: 1rem; padding: 6px 10px; height: 32px; width: 100%;" />
              </div>
            </div>

          <div class="button-sub" style="margin-top: 24px;">
             <button class="button-primary" type="submit" style="font-size: 1rem; padding: 10px 18px;">Créer un compte</button>
          </div>
        </form>

        <p class="muted" style="font-size: 1.05rem; margin-top: 24px; text-align: center;">Déjà inscrit ? <router-link to="/login">Se connecter</router-link></p>
          <p v-if="error" class="error" style="font-size: 0.95rem; margin-top: 10px; text-align: center;">{{ error }}</p>
    </div>
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
