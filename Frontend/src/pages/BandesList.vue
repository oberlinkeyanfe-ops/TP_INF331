<template>
  <div class="bandes-list-root">
    <header class="list-header">
      <h1>Mes Bandes</h1>
      <div class="controls">
        <input v-model="q" placeholder="Rechercher une bande" @input="fetchBands" />
        <button class="btn" @click="createBande">Créer une bande</button>
      </div>
    </header>

    <ul class="band-list">
      <li v-for="b in bandes" :key="b.id" class="band-item" @click="openBand(b.id)">
        <h3>{{ b.nom_bande || ('Bande ' + b.id) }}</h3>
        <div class="meta">Arrivée: {{ b.date_arrivee || '—' }} • Statut: {{ b.statut || '—' }}</div>
        <div class="stats">Nb init.: {{ b.nombre_initial || 0 }} • Ajoutés: {{ b.nbre_ajoute || 0 }}</div>
      </li>
    </ul>

    <div v-if="error" class="error">{{ error }}</div>
  </div>
</template>

<script>
export default {
  name: 'BandesList',
  data() {
    return {
      bandes: [],
      q: '',
      error: null
    }
  },
  methods: {
    async fetchBands() {
      try {
        const params = this.q ? `?q=${encodeURIComponent(this.q)}` : ''
        const res = await fetch(`/bandes/search${params}`, { credentials: 'same-origin' })
        if (!res.ok) throw new Error('Erreur réseau')
        this.bandes = await res.json()
      } catch (e) {
        this.error = e.message || String(e)
      }
    },
    openBand(id) { this.$router.push(`/bandes/${id}`) },
    createBande() { this.$router.push('/bandes/create') }
  },
  mounted() { this.fetchBands() }
}
</script>

<style scoped>
.bandes-list-root { max-width: 1000px; margin: 20px auto; padding: 12px }
.list-header { display:flex; align-items:center; justify-content:space-between; gap:12px }
.controls { display:flex; gap:8px }
.band-list { list-style:none; padding:0; display:grid; grid-template-columns: repeat(auto-fill, minmax(260px,1fr)); gap:12px }
.band-item { background:#fff; padding:12px; border-radius:8px; border:1px solid #eee; cursor:pointer }
.error { color: #b00020; margin-top:12px }
.btn { background:#b55a1f; color:#fff; padding:8px 12px; border-radius:6px; border:none }
</style>
