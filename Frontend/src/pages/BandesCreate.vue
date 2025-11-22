<template>
  <div class="create-root">
    <h1>Créer une nouvelle bande</h1>
    <form @submit.prevent="create" class="create-form">
      <input v-model="form.nom_bande" placeholder="Nom de la bande" required />
      <input type="date" v-model="form.date_arrivee" required />
      <input v-model="form.race" placeholder="Race" />
      <input v-model="form.fournisseur" placeholder="Fournisseur" />
      <input type="number" v-model.number="form.nombre_initial" placeholder="Nombre initial" required />
      <input type="number" step="0.01" v-model.number="form.poids_moyen_initial" placeholder="Poids moyen initial" />
      <button class="btn" type="submit">Créer</button>
      <button class="btn-muted" type="button" @click="$router.back()">Annuler</button>
    </form>
    <div v-if="error" class="error">{{ error }}</div>
  </div>
</template>

<script>
export default {
  name: 'BandesCreate',
  data() {
    return {
      form: { nom_bande: '', date_arrivee: '', race: '', fournisseur: '', nombre_initial: 0, poids_moyen_initial: 0 },
      error: null
    }
  },
  methods: {
    async create() {
      try {
        const fd = new FormData()
        for (const k in this.form) fd.append(k, this.form[k])
        const res = await fetch('/bandes/create', { method: 'POST', body: fd, credentials: 'same-origin' })
        // backend redirects on success; if we get HTML redirect, navigate back to list
        if (res.ok) {
          this.$router.push('/bandes')
        } else {
          const txt = await res.text()
          this.error = 'Erreur création: ' + (txt || res.statusText)
        }
      } catch (e) { this.error = e.message }
    }
  }
}
</script>

<style scoped>
.create-root { max-width:600px; margin:24px auto }
.create-form { display:flex; flex-direction:column; gap:8px }
.create-form input { padding:8px; border-radius:6px; border:1px solid #ddd }
.btn { background:#b55a1f; color:white; padding:8px 12px; border-radius:6px; border:none }
.btn-muted { background:transparent; border:1px solid #ddd; padding:8px 12px; border-radius:6px }
.error { color:#b00020; margin-top:8px }
</style>
