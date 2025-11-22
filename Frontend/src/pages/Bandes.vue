<template>
  <div class="bande-root">
    <header class="bande-header">
      <button class="back" @click="goBack">← Retour</button>
      <div class="title">
        <h1>Band {{ band ? band.nom_bande || band.id : '' }}</h1>
        <div class="meta">Statut: <strong>{{ band?.statut || '—' }}</strong> • Arrivée: {{ band?.date_arrivee || '—' }}</div>
      </div>
      <div class="actions">
        <button class="btn" @click="calculateKPI">Calculer KPI</button>
        <button class="btn-muted" @click="openPredictions">Prédictions</button>
      </div>
    </header>

    <nav class="bande-tabs">
      <button :class="{active: activeTab==='dashboard'}" @click="selectTab('dashboard')">Dashboard</button>
      <button :class="{active: activeTab==='consommation'}" @click="selectTab('consommation')">Consommation</button>
      <button :class="{active: activeTab==='chatbot'}" @click="selectTab('chatbot')">Chatbot</button>
      <button :class="{active: activeTab==='infos'}" @click="selectTab('infos')">Infos</button>
      <button :class="{active: activeTab==='traitements'}" @click="selectTab('traitements')">Traitements</button>
      <button :class="{active: activeTab==='interventions'}" @click="selectTab('interventions')">Interventions</button>
      <button :class="{active: activeTab==='animaux'}" @click="selectTab('animaux')">Animaux</button>
      <button :class="{active: activeTab==='depenses'}" @click="selectTab('depenses')">Dépenses</button>
      <button :class="{active: activeTab==='predictions'}" @click="selectTab('predictions')">Predictions</button>
    </nav>

    <main class="bande-main">
      <section v-if="activeTab==='dashboard'" class="tab-panel dashboard-panel">
        <h2>KPIs</h2>
        <div class="kpi-row">
          <div class="kpi">Poids moyen: <strong>{{ kpi?.poids_moyen || '—' }}</strong></div>
          <div class="kpi">Coût total: <strong>{{ kpi?.cout_total || '—' }}</strong></div>
          <div class="kpi">Taux mortalité: <strong>{{ kpi?.taux_mortalite || '—' }}</strong></div>
          <div class="kpi">Indice de consommation (IC): <strong>{{ kpi?.ic || '—' }}</strong></div>
        </div>
        <div class="charts-placeholder">(Graphiques: à intégrer — Chart.js / ECharts)</div>
      </section>

      <section v-if="activeTab==='consommation'" class="tab-panel consommation-panel">
        <h2>Consommations</h2>
        <form @submit.prevent="addConsumption" class="consumption-form">
          <input type="date" v-model="consumptionForm.date" required />
          <input type="text" v-model="consumptionForm.type" placeholder="Type d'aliment" required />
          <input type="number" v-model.number="consumptionForm.kg" placeholder="Kg" step="0.01" required />
          <input type="number" v-model.number="consumptionForm.cout" placeholder="Coût" step="0.01" />
          <button class="btn" type="submit">Ajouter</button>
        </form>

        <ul class="consumption-list">
          <li v-for="c in consommations" :key="c.id">
            <div class="c-row">
              <div>{{ c.date }} — {{ c.type }} — {{ c.kg }} kg</div>
              <div class="muted">{{ c.cout ? c.cout + ' €' : '' }}</div>
            </div>
          </li>
        </ul>
      </section>

      <section v-if="activeTab==='chatbot'" class="tab-panel chatbot-panel">
        <h2>Chatbot</h2>
        <div class="chatbox">
          <div class="messages">
            <div v-for="(m,i) in messages" :key="i" :class="['msg', m.from]">{{ m.text }}</div>
          </div>
          <form @submit.prevent="sendMessage" class="chat-form">
            <input v-model="chatInput" placeholder="Poser une question à l'IA" />
            <button class="btn" type="submit">Envoyer</button>
          </form>
        </div>
      </section>

      <section v-if="activeTab==='infos'" class="tab-panel infos-panel">
        <h2>Infos</h2>
        <dl class="info-list">
          <div><dt>Nom</dt><dd>{{ band?.nom_bande || '—' }}</dd></div>
          <div><dt>Date arrivée</dt><dd>{{ band?.date_arrivee || '—' }}</dd></div>
          <div><dt>Fournisseur</dt><dd>{{ band?.fournisseur || '—' }}</dd></div>
          <div><dt>Race</dt><dd>{{ band?.race || '—' }}</dd></div>
          <div><dt>Nombre init.</dt><dd>{{ band?.nombre_initial || '—' }}</dd></div>
        </dl>
      </section>

      <section v-if="activeTab==='animaux'" class="tab-panel animaux-panel">
        <h2>Animaux</h2>
        <ul class="animaux-list">
          <li v-for="a in animaux" :key="a.id">{{ a.nom || ('#' + a.id) }} — Âge: {{ a.age || '—' }}</li>
        </ul>
      </section>

      <section v-if="activeTab==='traitements'" class="tab-panel traitements-panel">
        <h2>Traitements</h2>
        <p>Historique des traitements (à implémenter).</p>
      </section>

      <section v-if="activeTab==='interventions'" class="tab-panel interventions-panel">
        <h2>Interventions</h2>
        <p>Historique des interventions (à implémenter).</p>
      </section>

      <section v-if="activeTab==='depenses'" class="tab-panel depenses-panel">
        <h2>Dépenses</h2>
        <p>Liste des dépenses (à implémenter).</p>
      </section>

      <section v-if="activeTab==='predictions'" class="tab-panel predictions-panel">
        <h2>Prédictions</h2>
        <div v-if="predictions.length === 0">Aucune prédiction disponible.</div>
        <ul>
          <li v-for="p in predictions" :key="p.id">{{ p.date }} — {{ p.summary }}</li>
        </ul>
      </section>
    </main>
  </div>
</template>

<script>
export default {
  name: 'BandesPage',
  data() {
    return {
      band: null,
      activeTab: 'dashboard',
      kpi: null,
      consommations: [],
      consommationForm: { date: '', type: '', kg: 0, cout: 0 },
      animaux: [],
      treatments: [],
      interventions: [],
      predictions: [],
      messages: [],
      chatInput: ''
    }
  },
  methods: {
    goBack() { this.$router.push('/home') },
    selectTab(tab) { this.activeTab = tab; if (tab !== 'dashboard') this.fetchTabData(tab) },
    async fetchBand() {
      const id = this.$route.params.id
      try {
        const res = await fetch(`/bandes/${id}`)
        if (!res.ok) throw new Error('failed')
        this.band = await res.json()
      } catch (e) {
        console.warn('fetchBand', e)
      }
    },
    async fetchTabData(tab) {
      const id = this.$route.params.id
      try {
        if (tab === 'consommation') {
          const r = await fetch(`/bandes/${id}/consommations`)
          this.consommations = r.ok ? await r.json() : []
        } else if (tab === 'animaux') {
          const r = await fetch(`/bandes/${id}/animaux`)
          this.animaux = r.ok ? await r.json() : []
        } else if (tab === 'predictions') {
          const r = await fetch(`/bandes/${id}/predictions`)
          this.predictions = r.ok ? await r.json() : []
        } else if (tab === 'chatbot') {
          // nothing to fetch initially
        }
      } catch (e) { console.warn('fetchTabData', e) }
    },
    async addConsumption() {
      const id = this.$route.params.id
      try {
        const res = await fetch(`/bandes/${id}/consommations`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.consommationForm)
        })
        if (!res.ok) throw new Error('create failed')
        const created = await res.json()
        this.consommations.unshift(created)
        this.consommationForm = { date: '', type: '', kg: 0, cout: 0 }
      } catch (e) { console.warn('addConsumption', e) }
    },
    async calculateKPI() {
      const id = this.$route.params.id
      try {
        const res = await fetch(`/bandes/${id}/kpi`)
        if (!res.ok) throw new Error('kpi failed')
        this.kpi = await res.json()
        this.selectTab('dashboard')
      } catch (e) { console.warn('calculateKPI', e) }
    },
    openPredictions() { this.selectTab('predictions') },
    async sendMessage() {
      if (!this.chatInput) return
      const payload = { bande_id: this.$route.params.id, message: this.chatInput }
      this.messages.push({ from: 'user', text: this.chatInput })
      this.chatInput = ''
      try {
        const res = await fetch('/chatbot', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
        const data = res.ok ? await res.json() : { reply: 'Erreur' }
        this.messages.push({ from: 'bot', text: data.reply || JSON.stringify(data) })
      } catch (e) { this.messages.push({ from: 'bot', text: 'Erreur: ' + e.message }) }
    }
  },
  mounted() {
    this.fetchBand()
    this.calculateKPI()
  }
}
</script>

<style scoped>
.bande-root { max-width: 1100px; margin: 20px auto; padding: 12px; }
.bande-header { display:flex; align-items:center; justify-content:space-between; gap:12px }
.bande-header .title h1 { margin:0; color:#b55a1f }
.bande-tabs { display:flex; gap:8px; margin:12px 0; flex-wrap:wrap }
.bande-tabs button { padding:8px 12px; border-radius:8px; border:1px solid #eee; background:#fff }
.bande-tabs button.active { background:#b55a1f; color:white }
.bande-main { background:#fff; padding:16px; border-radius:10px }
.kpi-row { display:flex; gap:12px; flex-wrap:wrap }
.kpi { background:#fff8f0; padding:12px; border-radius:8px; border:1px solid rgba(0,0,0,0.04) }
.consumption-form { display:flex; gap:8px; align-items:center; margin-bottom:12px }
.consumption-form input { padding:8px; border-radius:6px; border:1px solid #ddd }
.consumption-list { list-style:none; padding:0 }
.chatbox { border:1px solid #eee; padding:12px; border-radius:8px }
.messages { max-height:300px; overflow:auto; margin-bottom:8px }
.msg { padding:8px; border-radius:8px; margin-bottom:6px }
.msg.user { background:#ffd166; align-self:flex-end }
.msg.bot { background:#f1f1f1 }
.btn { background:#b55a1f; color:white; padding:8px 12px; border-radius:8px; border:none }
.btn-muted { background:transparent; border:1px solid #ddd; padding:8px 12px; border-radius:8px }
.back { background:transparent; border:1px solid #ddd; padding:6px 10px; border-radius:6px }
.muted { color:#777 }
</style>
