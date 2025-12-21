<template>
  <div class="app-layout">
    
    <header class="navbar">
      <div class="nav-container">
        <div class="brand">
          <span class= "logo"></span> 
          <span>AVIPRO</span>
        </div>

        <nav class="nav-links">
          <button @click="selectTab('home')" :class="{ active: activeTab === 'home' }">Accueil</button>
          <button @click="selectTab('bands')" :class="{ active: activeTab === 'bands' }">Mes Bandes</button>
          <button @click="selectTab('dashboard')" :class="{ active: activeTab === 'dashboard' }">Tableau de bord</button>
          <button class="ai" :class="{ active: activeTab === 'chatbot' }" @click="selectTab('chatbot')" ></button>
        </nav>

        <div class="nav-profile">
          <router-link v-if="!user" to="/login" class="btn-login">Connexion</router-link>
          <div v-else class="profile-pill" @click="toggleDropdown">
            <span class="avatar" :style="{ background: avatarColor }">
              {{ user.nom ? user.nom[0].toUpperCase() : 'U' }}
            </span>
            <span class="username">{{ user.nom }}</span>
            <div class="dropdown-menu" v-if="dropdownOpen">
              <div class="dd-header">{{ user.email }}</div>
              <router-link to="/profile" class="dd-item">Mon Profil</router-link>
              <div class="dd-divider"></div>
              <router-link to="/signout" class="dd-item text-red">Déconnexion</router-link>
            </div>
          </div>


        </div>
      </div>
    </header>

    <main class="main-container dashboard-container theme-green home-dashboard-style">
      
      <div v-if="activeTab === 'home'" class="tab-fade home-tab">
        
        <section class="hero-grid">
          <div class="hero-content">
            <span class="badge">Nouveau : Assistant IA v2.0</span>
            <h1>Pilotez votre élevage avec précision.</h1>
            <p class="hero-desc">
              Suivez la croissance, anticipez les coûts et réduisez la mortalité grâce à notre suite complète dédiée aux aviculteurs.
            </p>
            <div class="hero-buttons">
              <button class="btn-primary" @click="selectTab('dashboard')">Voir mon Dashboard</button>
              <button class="btn-secondary" @click="selectTab('bands')">Gérer mes bandes</button>
            </div>
            
            <div class="mini-stats">
              <div class="stat">
                <strong>{{ bands.length }}</strong>
                <small>Bandes</small>
              </div>
              <div class="stat">
                <strong>{{ activeBandsCount }}</strong>
                <small>Actives</small>
              </div>
              <div class="stat">
                <strong>{{ totalBirds }}</strong>
                <small>Sujets</small>
              </div>
            </div>
          </div>

          <div class="hero-slider-wrapper">
            <div class="slider-window">
              <div class="slider-track" :style="{ transform: `translateX(-${currentSlide * 100}%)` }">
                <div v-for="(slide, idx) in slides" :key="idx" class="slide-item">
                  <img :src="slide.image" :alt="slide.title" />
                </div>
              </div>
            </div>
            <div class="slide-caption">
              <h3>{{ activeSlideInfo.title }}</h3>
              <p>{{ activeSlideInfo.text }}</p>
              <div class="slider-dots">
                <span 
                  v-for="(s, idx) in slides" 
                  :key="idx" 
                  :class="{ active: idx === currentSlide }"
                  @click="goToSlide(idx)"
                ></span>
              </div>
            </div>
          </div>
        </section>

        <section class="features-section">
          <h2>Pourquoi choisir AVIPRO ?</h2>
          <div class="features-grid">
            <div class="feature-card">
              <div class="icon-circle blue">📊</div>
              <h3>Suivi Temps Réel</h3>
              <p>Des graphiques clairs pour suivre le poids et la consommation.</p>
            </div>
            <div class="feature-card">
              <div class="icon-circle purple">🤖</div>
              <h3>Intelligence Artificielle</h3>
              <p>Posez vos questions techniques et obtenez des réponses immédiates.</p>
            </div>
            <div class="feature-card">
              <div class="icon-circle green">🛡️</div>
              <h3>Alertes Santé</h3>
              <p>Notifications automatiques en cas de risque sanitaire détecté.</p>
            </div>
          </div>
        </section>
      </div>

      <div v-if="activeTab === 'dashboard'" class="tab-fade dashboard-tab ">


        <div class="dashboard-container tab-offset">

          
          <DashboardGlobal ref="dashboardGlobal" />
        </div>
      </div>

      <div v-if="activeTab === 'bands'" class="tab-fade bands-tab tab-offset" style="margin-bottom: 0;">
        <header class="page-header">
          <div>
            <h2>Mes Bandes</h2>
            <p>Gérez vos cycles de production</p>
          </div>
          <button class="btn-primary" @click="showCreate = true">+ Nouvelle Bande</button>
        </header>

        <div v-if="loadingBands" class="loading-state">Chargement...</div>

        <div v-else class="bands-grid">
          <div v-for="band in bands" :key="band.id" class="band-card" @click="openBand(band)">
            <div class="band-top">
              <span class="band-name">{{ band.nom_bande }}</span>
              <span :class="['status-badge', band.statut]">{{ band.statut }}</span>
              <button class="icon-btn danger" title="Supprimer la bande" @click.stop="deleteBande(band)">🗑️</button>
            </div>
            <div class="band-info-grid">
              <div>
                <label>Race</label>
                <span>{{ band.race }}</span>
              </div>
              <div>
                <label>Effectif</label>
                <span>{{ band.nombre_initial }}</span>
              </div>
              <div>
                <label>Départ</label>
                <span>{{ formatDate(band.date_arrivee) }}</span>
              </div>
              <div>
                <label>Performance</label>
                <span :class="{
                    'good-perf': (getBandPerformance(band.id) !== null && getBandPerformance(band.id) >= 75),
                    'warn-perf': (getBandPerformance(band.id) !== null && getBandPerformance(band.id) >= 50 && getBandPerformance(band.id) < 75),
                    'bad-perf': (getBandPerformance(band.id) !== null && getBandPerformance(band.id) < 50)
                  }">
                  {{ getBandPerformanceDisplay(band.id) }}
                </span>
                <button v-if="getBandPerformance(band.id) !== null" class="btn-small" @click.stop="showPerfBreakdown(band.id)">Détails</button>
              </div>
            </div>
          </div>
          
          <div v-if="bands.length === 0" class="empty-bands">
            <p>Aucune bande enregistrée. Créez la première !</p>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'chatbot'" class="tab-fade chatbot-tab">
        <header class="page-header">
          <div>
            <h2>Chatbot</h2>
            <p>Dialogue avec l'assistant IA — posez vos questions ou lancez une analyse globale.</p>
          </div>
        </header>
        <div class="chatbox">
          <div class="chat-controls">
            <div class="chat-mode-head">
              <label>Mode IA</label>
              <span class="chat-mode-hint">Choisissez la source d'information</span>
            </div>
            <div class="chat-mode-pills">
              <button type="button" class="pill-btn" :class="{ active: chatMode === 'data' }" @click="chatMode = 'data'">Données internes</button>
              <button type="button" class="pill-btn" :class="{ active: chatMode === 'hybrid' }" @click="chatMode = 'hybrid'">Hybride</button>
              <button type="button" class="pill-btn" :class="{ active: chatMode === 'web' }" @click="chatMode = 'web'">Web uniquement</button>
              <button @click="analyserElevage" class="pill-btn" :disabled="chatLoading">📊 Analyser mon élevage</button>
            </div>
          </div>
          <div class="messages">
            <div v-for="(m, i) in messages" :key="i" :class="['msg', m.from]">
              <span class="msg-text">{{ m.text }}</span>
              <button class="msg-close" aria-label="Fermer" @click="dismissChatMessage(i)">✕</button>
            </div>
            <div v-if="chatLoading" class="msg bot">…</div>
          </div>
          <form @submit.prevent="sendMessage" class="chat-form">
            <input v-model="chatInput" placeholder="Poser une question à l'IA" />
            <button class="btn" type="submit">Envoyer</button>
          </form>
        </div>
      </div>

      <div v-if="showCreate" class="modal-overlay" @click.self="closeAndReset">
        <div class="modal-box">
          <div class="modal-header">
            <h3>Nouvelle Bande</h3>
            <button class="close-btn" @click="closeAndReset">×</button>
          </div>
          <form @submit.prevent="createBande" class="modal-form">
            <div class="form-grid">
              <div class="form-row">
                <div class="form-group">
                  <label>Nom de la bande</label>
                  <input v-model="form.nom_bande" type="text" placeholder="Ex: Lot #45" required />
                </div>
                <div class="form-group">
                  <label>Effectif initial</label>
                  <input v-model.number="form.nombre_initial" type="number" required />
                </div>
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label>Date d'arrivée</label>
                  <input v-model="form.date_arrivee" type="date" required />
                </div>
                <div class="form-group">
                  <label>Durée (semaines)</label>
                  <input v-model.number="form.duree_semaines" type="number" min="1" />
                </div>
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label>Prix d'achat unitaire (FCFA)</label>
                  <input v-model.number="form.prix_achat_unitaire" type="number" step="1" placeholder="Ex: 1500" min="0" />
                </div>
                <div class="form-group">
                  <label>Poids moyen initial (kg)</label>
                  <input v-model.number="form.poids_moyen_initial" type="number" step="0.01" placeholder="Ex: 0.04" min="0" max="2" />
                </div>
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label>Race</label>
                  <select v-model="form.race">
                    <option value="">-- Sélectionner --</option>
                    <option value="Ross308">Ross308</option>
                    <option value="Cobb500">Cobb500</option>
                    <option value="Bobb500">Bobb500</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>Fournisseur</label>
                  <select v-model="form.fournisseur">
                    <option value="">-- Sélectionner --</option>
                    <option value="FournisseurA">FournisseurA</option>
                    <option value="FournisseurB">FournisseurB</option>
                    <option value="FournisseurC">FournisseurC</option>
                    <option value="FournisseurD">FournisseurD</option>
                  </select>
                </div>
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label>Statut</label>
                  <select v-model="form.statut">
                    <option value="active">Active</option>
                    <option value="archive">Archivée</option>
                    <option value="terminee">Terminée</option>
                  </select>
                </div>
                <div class="form-group"></div>
              </div>
            </div>
              
            
            <div class="modal-actions">
              <button type="button" class="btn-secondary" @click="closeAndReset">Annuler</button>
              <button type="submit" class="btn-primary">Créer</button>
            </div>
          </form>
        </div>
      </div>

    </main>
  </div>
    <footer class="home-footer">
        <div class="footer-content">
          <div class="footer-top">
            <div class="footer-brand">
              <span class="footer-logo"><span class="logo"></span> <span>AVIPRO</span></span>
              <small class="footer-desc">Plateforme intelligente pour la gestion et l’analyse de l’aviculture moderne.</small>
            </div>
            <div class="footer-socials">
              <a href="mailto:contact@avipro.com" class="footer-social" title="Mail">
                <span class="footer-icon-circle"><img src="/src/assets/icons/mail.svg" alt="Mail" class="footer-icon" /></span>
                <span class="footer-social-label">contact@avipro.com</span>
              </a>
              <a href="https://instagram.com/avipro" class="footer-social" target="_blank" title="Instagram">
                <span class="footer-icon-circle"><img src="/src/assets/icons/instagram.svg" alt="Instagram" class="footer-icon" /></span>
                <span class="footer-social-label">Instagram</span>
              </a>
              <a href="https://facebook.com/avipro" class="footer-social" target="_blank" title="Facebook">
                <span class="footer-icon-circle"><img src="/src/assets/icons/facebook.svg" alt="Facebook" class="footer-icon" /></span>
                <span class="footer-social-label">Facebook</span>
              </a>
              <a href="tel:+237674663399" class="footer-social" title="Téléphone">
                <span class="footer-icon-circle"><img src="/src/assets/icons/phone.svg" alt="Téléphone" class="footer-icon" /></span>
                <span class="footer-social-label">+237 674663399</span>
              </a>
            </div>
          </div>
          <div class="footer-bottom">
            <span>© 2025 Aviculture Pro — Tous droits réservés</span>
          </div>
        </div>
    </footer>
</template>

<script>
// Importation directe des images pour éviter les erreurs de chemin
import img1 from '../assets/slide/slide1.png';
import img2 from '../assets/slide/slide2.png';
import img3 from '../assets/slide/slide3.jpg';
import * as chatbotMethods from './methods/chatbotMethods.js';
import { api } from '../services/api.js';
import DashboardGlobal from './DashboardGlobal.vue';
import AnimalWeeklyLine from './charts/AnimalWeeklyLine.vue';

export default {
  name: 'Home',
  components: { DashboardGlobal, AnimalWeeklyLine },
  data() {
    return {
      selectedBandIdForChart: '',
      bandWeeklyLabels: [],
      bandWeeklySeries: [],
      chartLoading: false,
      activeTab: 'home',
      dropdownOpen: false,
      showCreate: false,
      loadingBands: false,
      user: null,
      bands: [],
      // lists start empty; user can add new race/fournisseur from the modal
      races: [],
      fournisseurs: [],
      showAddRace: false,
      showAddFournisseur: false,
      newRace: '',
      newFournisseur: '',

      form: {
        nom_bande: '',
        date_arrivee: '',
        race: '',
        fournisseur: '',
        nombre_initial: 0,
        duree_semaines: 8,
        poids_moyen_initial: 0,
        statut: 'active'
      },
      avatarColor: '#6366f1',
      // Per-band performance mapping (id -> percent)
      bandPerformanceMap: {},
      coutsMap: {},
      // Configuration Slides
      slides: [
        { title: 'Suivi de croissance', text: 'Visualisez les courbes de poids.', image: img1 },
        { title: 'IA Avicole', text: 'Détectez les anomalies rapidement.', image: img2 },
        { title: 'Rentabilité', text: 'Calculez vos marges en temps réel.', image: img3 }
      ],
      currentSlide: 0,
      slideTimer: null,
      // Chatbot state
      chatInput: '',
      messages: [],
      chatMode: 'data',
      chatLoading: false,
      // Dashboard global handled by DashboardGlobal component
    };
  },
  computed: {
    activeSlideInfo() { return this.slides[this.currentSlide]; },
    activeBandsCount() { return this.bands.filter(b => b.statut === 'active').length; },
    totalBirds() { return (this.bands || []).reduce((acc, b) => acc + (b.nombre_initial || 0), 0); }
  },
  methods: {
    // Logique Slider
    nextSlide() { this.currentSlide = (this.currentSlide + 1) % this.slides.length; },
    goToSlide(i) { this.currentSlide = i; },
    startSlideAuto() { this.slideTimer = setInterval(this.nextSlide, 4000); },
    stopSlideAuto() { clearInterval(this.slideTimer); },
    // UI Helpers
    async fetchBandes() {
      // Try to show cached results immediately
      if (!this.bands || !this.bands.length) {
        const cached = localStorage.getItem('bands_cache');
        if (cached) {
          try { this.bands = JSON.parse(cached); } catch (e) { /* ignore */ }
        }
      }

      this.loadingBands = true;
      this.bandsError = '';
      try {
        const res = await fetch('http://localhost:5000/bandes/', {
          method: 'GET',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' }
        });
        if (!res.ok) throw new Error(`Erreur HTTP: ${res.status}`);
        const data = await res.json();
        this.bands = Array.isArray(data) ? data : [];
        // cache for instant reloads
        try { localStorage.setItem('bands_cache', JSON.stringify(this.bands)); } catch (e) { /* ignore */ }

        // Set default selected band for dashboard charts if on dashboard
        try {
          if (this.activeTab === 'dashboard' && this.bands.length && !this.selectedBandIdForChart) {
            this.selectedBandIdForChart = this.bands[0].id;
            // load series for the default band
            this.loadBandWeekly(this.selectedBandIdForChart);
          }
        } catch (err) { /* ignore */ }

        // Fetch per-band performance & costs to display on home cards
        this.fetchBandPerformances().catch(e => console.warn('Erreur fetchBandPerformances:', e));
      } catch (error) {
        console.error('Erreur fetchBandes:', error);
        this.bandsError = 'Impossible de charger les bandes: ' + error.message;
        // keep prior cached bands if any
      } finally {
        this.loadingBands = false;
      }

    },

    resetForm() {
      this.form = {
        nom_bande: '',
        date_arrivee: '',
        race: '',
        fournisseur: '',
        nombre_initial: 0,
        duree_semaines: 8,
        poids_moyen_initial: 0,
        prix_achat_unitaire: 0,
        statut: 'active'
      };
      this.bandsError = '';
      this.showAddRace = false;
      this.showAddFournisseur = false;
      this.newRace = '';
      this.newFournisseur = '';
    },


    async createBande() {
      this.bandsError = '';
      try {
        if (!this.form.nom_bande || !this.form.nom_bande.trim()) {
          this.bandsError = 'Le nom de la bande est requis';
          return;
        }
        if (!this.form.fournisseur || !this.form.fournisseur.trim()) {
          this.bandsError = 'Le fournisseur est requis';
          return;
        }
        if (!this.form.nombre_initial || this.form.nombre_initial <= 0) {
          this.bandsError = "L'effectif initial doit être supérieur à 0";
          return;
        }
        if (!this.form.duree_semaines || this.form.duree_semaines <= 0) {
          this.bandsError = 'La durée en semaines doit être au moins 1';
          return;
        }

        const payload = {
          ...this.form,
          nombre_initial: Number(this.form.nombre_initial),
          duree_semaines: Number(this.form.duree_semaines),
          poids_moyen_initial: Number(this.form.poids_moyen_initial || 0)
        };

        const res = await fetch('http://localhost:5000/bandes/create', {
          method: 'POST',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (!res.ok) {
          this.bandsError = data.error || data.message || 'Erreur lors de la création de la bande';
          return;
        }
        await this.fetchBandes();
        this.resetForm();
        this.showCreate = false;
        console.log('Bande créée avec succès:', data);
      } catch (error) {
        console.error('Erreur createBande:', error);
        this.bandsError = 'Erreur de connexion au serveur';
      }
    },


    closeAndReset() { this.resetForm(); this.showCreate = false; },

    selectTab(t) { this.activeTab = t; if (t === 'bands' || t === 'dashboard') this.fetchBandes(); },

    onSelectBandForChart() {
      const id = this.selectedBandIdForChart;
      if (!id) {
        this.bandWeeklyLabels = [];
        this.bandWeeklySeries = [];
        return;
      }
      this.loadBandWeekly(id);
    },

    async loadBandWeekly(bandId) {
      try {
        this.chartLoading = true;
        const res = await fetch(`http://localhost:5000/animal-info/bande/${bandId}`, {
          method: 'GET',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' }
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        const infos = Array.isArray(data.animal_info) ? data.animal_info : [];
        // sort by semaine_production asc
        infos.sort((a, b) => (a.semaine_production || 0) - (b.semaine_production || 0));
        this.bandWeeklyLabels = infos.map(i => `S${i.semaine_production}`);
        this.bandWeeklySeries = infos.map(i => (typeof i.poids_moyen === 'number' ? i.poids_moyen : (i.poids_moyen ? Number(i.poids_moyen) : 0)));
      } catch (e) {
        console.error('Erreur loadBandWeekly:', e);
        this.bandWeeklyLabels = [];
        this.bandWeeklySeries = [];
      } finally {
        this.chartLoading = false;
      }
    },
    // Dashboard handled by `DashboardGlobal` component
    toggleDropdown() { this.dropdownOpen = !this.dropdownOpen; },
    formatDate(d) { return d ? new Date(d).toLocaleDateString('fr-FR') : '—'; },

    openBand(band) {
      const bandData = {
        id: band.id,
        nom_bande: band.nom_bande,
        date_arrivee: band.date_arrivee,
        race: band.race,
        fournisseur: band.fournisseur,
        nombre_initial: band.nombre_initial,
        poids_moyen_initial: band.poids_moyen_initial,
        age_moyen: band.age_moyen,
        nombre_nouveaux_nes: band.nombre_nouveaux_nes,
        nombre_morts_totaux: band.nombre_morts_totaux,
        statut: band.statut
      };
      localStorage.setItem('current_band', JSON.stringify(bandData));
      this.$router.push(`/bandes/${band.id}`);
    },

    async deleteBande(band) {
      if (!band || !band.id) return;
      if (!confirm(`Supprimer la bande "${band.nom_bande}" et toutes ses données ?`)) return;
      try {
        const res = await fetch(`http://localhost:5000/bandes/${band.id}/delete`, {
          method: 'POST',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' }
        });

        // Try to parse JSON but fall back to text when response isn't JSON
        let bodyText = '';
        let data = null;
        try {
          data = await res.json();
          bodyText = JSON.stringify(data);
        } catch (parseErr) {
          bodyText = await res.text().catch(() => '<unreadable body>');
        }

        if (!res.ok) {
          // Provide a detailed error message for easier debugging
          const statusMsg = `HTTP ${res.status} ${res.statusText}`;
          const serverMsg = (data && (data.error || data.message)) || bodyText || 'Erreur lors de la suppression de la bande';
          const composed = `${statusMsg} — ${serverMsg}`;
          console.error('deleteBande failed:', composed);
          this.bandsError = serverMsg;

          // If not authenticated, suggest re-login
          if (res.status === 401) {
            this.bandsError = 'Non connecté — veuillez vous reconnecter.';
          }
          return;
        }

        // refresh the list
        await this.fetchBandes();
      } catch (e) {
        console.error('Erreur deleteBande (network):', e);
        this.bandsError = 'Erreur réseau lors de la suppression de la bande';
      }
    },


    loadUser() {
      try {
        // accept both localStorage and sessionStorage so login 'remember' option works
        const storedLocal = localStorage.getItem('user');
        const storedSession = sessionStorage.getItem('user');
        const stored = storedLocal || storedSession;
        this.user = stored ? JSON.parse(stored) : null;
        if (this.user) this.generateRandomColor();
        return this.user;
      } catch (error) {
        console.error('Erreur loadUser:', error);
        this.user = null;
        return null;
      }
    },

    // ---- Performance helpers for Home (per-band)
    ratioScore(refValue, actualValue) {
      // Return null when comparison is not meaningful (avoid treating missing data as perfect)
      if (refValue == null || refValue <= 0) return null;
      if (actualValue == null || actualValue <= 0) return null;
      if (actualValue <= refValue) return 100;
      return Math.max(0, Math.min(100, Math.round((refValue / actualValue) * 100)));
    },

    async fetchBandPerformances() {
      try {
        // authoritative: fetch the precomputed map from backend
        const resp = await api.get('/dashboard/performance/map');
        const map = resp && resp.band_performance_map ? resp.band_performance_map : {};
        this.bandPerformanceMap = map;
        console.log('Home: fetched band_performance_map from backend', map);
        try { localStorage.setItem('band_performance_map', JSON.stringify(map)); } catch (e) { /* ignore */ }
      } catch (e) {
        console.warn('Failed to fetch performance map from backend:', e);
        // If the backend fetch fails, prefer using any previously cached map from localStorage;
        // do NOT compute new performance values in the frontend.
        try {
          const existing = localStorage.getItem('band_performance_map');
          if (existing) {
            const parsed = JSON.parse(existing);
            if (parsed && typeof parsed === 'object') this.bandPerformanceMap = parsed;
            else this.bandPerformanceMap = {};
          } else {
            this.bandPerformanceMap = this.bandPerformanceMap || {};
          }
        } catch (err) {
          console.warn('Failed to load cached performance map from localStorage', err);
          this.bandPerformanceMap = this.bandPerformanceMap || {};
        }
      }
    },

    getBandPerformance(bandId) {
      const val = this.bandPerformanceMap && this.bandPerformanceMap[bandId];
      return typeof val === 'number' ? val : null;
    },

    getBandPerformanceDisplay(bandId) {
      // If backend explicitly flagged no consumption data, show infinity symbol
      const statusKey = this.bandPerformanceMap && this.bandPerformanceMap[`status_${bandId}`];
      if (statusKey === 'no_consumption') return '∞';
      const val = this.getBandPerformance(bandId);
      return (typeof val === 'number') ? val + '%' : '—';
    },

    loadCachedData() {
      // Load lightweight cache to make UI instant
      try {
        const bandsCache = localStorage.getItem('bands_cache');
        if (bandsCache) {
          this.bands = JSON.parse(bandsCache);
        }
        const dashCache = localStorage.getItem('dashboard_cache');
        if (dashCache) {
          this.dashboardData = JSON.parse(dashCache);
        }
        // load precomputed band performance map if available
        const perfMapRaw = localStorage.getItem('band_performance_map');
        if (perfMapRaw) {
          const parsed = JSON.parse(perfMapRaw);
          if (parsed && typeof parsed === 'object') this.bandPerformanceMap = parsed;
        }
      } catch (e) {
        console.warn('Erreur loading cached data', e);
      }
    },

    showPerfBreakdown(bandId) {
      const components = this.bandPerformanceMap && this.bandPerformanceMap[`components_${bandId}`];
      const serverVal = this.bandPerformanceMap && this.bandPerformanceMap[bandId];
      const msg = `Bande ${bandId}\nPerformance: ${serverVal ?? '—'}%\nDétails: ${components ? JSON.stringify(components) : '—'}`;
      alert(msg);
    },

    _onStorageChange(e) {
      if (e.key === 'user') {
        this.loadUser();
        if (this.user) {
          this.loadCachedData();
          this.fetchBandes();
          if (this.$refs.dashboardGlobal && this.$refs.dashboardGlobal.fetchDashboardGlobal) this.$refs.dashboardGlobal.fetchDashboardGlobal();
        }
      }

      // react to per-band perf updates saved by Bandes.vue
      if (e.key && e.key.startsWith('band_performance_')) {
        try {
          const idStr = e.key.replace('band_performance_', '');
          const id = Number(idStr);
          const val = e.newValue ? JSON.parse(e.newValue) : null;
          if (id && val) {
            // val might be an object with subscores and performance_percent
            const perf = typeof val.performance_percent === 'number' ? val.performance_percent : null;
            if (perf !== null) this.bandPerformanceMap = { ...this.bandPerformanceMap, [id]: perf };
            if (val.subscores) this.bandPerformanceMap = { ...this.bandPerformanceMap, [`components_${id}`]: val.subscores };
            console.log('Home detected band performance update from storage', id, perf);
          }
        } catch (err) { /* ignore parse errors */ }
      }
    },

    _onBandPerfUpdated(e) {
      try {
        const detail = e && e.detail;
        if (!detail) return;
        const id = Number(detail.id);
        const performance = detail.performance;
        if (!id || !performance) return;
        const perf = typeof performance.performance_percent === 'number' ? performance.performance_percent : null;
        if (perf !== null) this.bandPerformanceMap = { ...this.bandPerformanceMap, [id]: perf };
        if (performance.subscores) this.bandPerformanceMap = { ...this.bandPerformanceMap, [`components_${id}`]: performance.subscores };
        // persist merged map to localStorage
        try {
          const existing = localStorage.getItem('band_performance_map');
          const parsed = existing ? JSON.parse(existing) : {};
          const merged = { ...(parsed || {}), ...(this.bandPerformanceMap || {}) };
          localStorage.setItem('band_performance_map', JSON.stringify(merged));
        } catch (err) { /* ignore storage errors */ }
        console.log('Home detected band performance update via event', id, perf);
      } catch (err) { /* ignore */ }
    },

    generateRandomColor() {
      const letters = '0123456789ABCDEF';
      let color = '#';
      for (let i = 0; i < 6; i++) color += letters[Math.floor(Math.random() * 16)];
      this.avatarColor = color;
    },
    // Chatbot helpers
    async analyserElevage() { return await chatbotMethods.analyserElevage(this); },
    async sendMessage() { return await chatbotMethods.sendMessage(this); },
    dismissChatMessage(i) { this.messages.splice(i, 1); }
  },
  mounted() {
    this.loadUser();
    // Fermer le dropdown si on clique ailleurs
    this._closeDropdownHandler = () => { this.dropdownOpen = false; };
    document.addEventListener('click', this._closeDropdownHandler);
    this.startSlideAuto();
    // Try to refresh band performance map on mount (will succeed if session cookie exists)
    this.fetchBandPerformances().catch(e => console.warn('Failed refresh band performances (mount):', e));

    // on mount, load data immediately for a snappy UX
    if (this.activeTab === 'bands') this.fetchBandes();
    // Load bands and dashboard immediately if user present
    if (this.user) {
      // use cached values first for instant UI, then refresh in background
      this.loadCachedData();
      // run both in parallel. DashboardGlobal is a child component; call its method if present
      const dashPromise = (this.$refs.dashboardGlobal && this.$refs.dashboardGlobal.fetchDashboardGlobal) ? this.$refs.dashboardGlobal.fetchDashboardGlobal() : Promise.resolve();
      Promise.all([this.fetchBandes(), dashPromise]).catch(err => console.warn('Background refresh error', err));
      // Also attempt another refresh after user-specific initialization (best-effort)
      this.fetchBandPerformances().catch(e => console.warn('Failed refresh band performances (user):', e));
    }
    window.addEventListener('storage', this._onStorageChange);
    // Listen for same-tab perf updates
    window.addEventListener('bandPerformanceUpdated', this._onBandPerfUpdated);
  },
  beforeUnmount() { document.removeEventListener('click', this._closeDropdownHandler); window.removeEventListener('storage', this._onStorageChange); window.removeEventListener('bandPerformanceUpdated', this._onBandPerfUpdated); this.stopSlideAuto(); }
};
</script>
<style src="../../css/home.css"></style>
<style scoped>
/* Reduced top margin for tab content to improve layout */
.tab-offset { margin-top: 1.5rem !important; }
.home-footer {

  width: 100%;
  background: linear-gradient(90deg, #101820 60%, #1a2a36 100%);
  color: #fff;
  padding: 0;
  margin-top: 32px;
  box-shadow: 0 -2px 16px 0 rgba(0,0,0,0.08);
}
.footer-content {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 24px 0 24px;
}
.footer-top {

  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 18px 0 8px 0;
}
.footer-brand {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}
.footer-logo {
  font-size: 1.5rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  gap: 10px;
  letter-spacing: 0.04em;
}
.footer-logo .logo {
  width: 36px;
  height: 36px;
  display: inline-block;
  background-image: url('/src/assets/icons/LOGO.svg');
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center;
}
.footer-desc {
  font-size: 0.92rem;
  opacity: 0.78;
  max-width: 420px;
  text-align: center;
  font-weight: 400;
  letter-spacing: 0.01em;
}
.footer-socials {
  display: flex;
  flex-wrap: wrap;
  gap: 22px;
  justify-content: center;
  margin-top: 8px;
}
.footer-social {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #fff;
  text-decoration: none;
  font-size: 1.05rem;
  transition: color 0.2s;
}
.footer-social:hover .footer-social-label {
  color: #10b981;
}
.footer-icon-circle {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: #232b33;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(16,24,32,0.08);
  transition: background 0.2s;
}
.footer-social:hover .footer-icon-circle {
  background: #10b981;
}
.footer-icon {
  width: 22px;
  height: 22px;
  filter: invert(1);
  transition: filter 0.2s;
}
.footer-social-label {
  font-size: 1.05rem;
  font-weight: 500;
  letter-spacing: 0.01em;
  transition: color 0.2s;
}
.footer-bottom {

  border-top: 1px solid #222c36;
  padding: 8px 0 4px 0;
  text-align: center;
  font-size: 0.98rem;
  opacity: 0.8;
}
@media (max-width: 700px) {
  .footer-content { padding: 0 6px; }
  .footer-desc { font-size: 0.98rem; }
  .footer-logo { font-size: 1.1rem; }
  .footer-social-label { font-size: 0.98rem; }
  .footer-top { padding: 24px 0 10px 0; }
}
</style>