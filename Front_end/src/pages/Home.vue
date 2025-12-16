<template>
  <div class="app-layout">
    
    <header class="navbar">
      <div class="nav-container">
        <div class="brand">
          <img src="../assets/icons/LOGO.svg" alt="AVIPRO" />
          <span>AVIPRO</span>
        </div>

        <nav class="nav-links">
          <button @click="selectTab('home')" :class="{ active: activeTab === 'home' }">Accueil</button>
          <button @click="selectTab('bands')" :class="{ active: activeTab === 'bands' }">Mes Bandes</button>
          <button @click="selectTab('dashboard')" :class="{ active: activeTab === 'dashboard' }">Tableau de bord</button>
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

    <main class="main-container">
      
      <div v-if="activeTab === 'home'" class="tab-fade">
        
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

      <div v-if="activeTab === 'bands'" class="tab-fade">
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
            </div>
          </div>
          
          <div v-if="bands.length === 0" class="empty-bands">
            <p>Aucune bande enregistrée. Créez la première !</p>
          </div>
        </div>
      </div>

      <div v-if="showCreate" class="modal-overlay" @click.self="closeAndReset">
        <div class="modal-box">
          <div class="modal-header">
            <h3>Nouvelle Bande</h3>
            <button class="close-btn" @click="closeAndReset">×</button>
          </div>
          <form @submit.prevent="createBande" class="modal-form">
            <div class="form-group">
              <label>Nom de la bande</label>
              <input v-model="form.nom_bande" type="text" placeholder="Ex: Lot #45" required />
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Race</label>
                <select v-model="form.race">
                  <option value="Ross308">Ross308</option>
                  <option value="Cobb500">Cobb500</option>
                </select>
              </div>
              <div class="form-group">
                <label>Effectif initial</label>
                <input v-model.number="form.nombre_initial" type="number" required />
              </div>
            </div>
            <div class="form-group">
              <label>Date d'arrivée</label>
              <input v-model="form.date_arrivee" type="date" required />
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
</template>

<script>
// Importation directe des images pour éviter les erreurs de chemin
// Assure-toi que les fichiers existent dans src/assets/
import img1 from '../assets/slide/slide1.png';
import img2 from '../assets/slide/slide2.png';
import img3 from '../assets/slide/slide3.png';

export default {
  name: 'Home',
  data() {
    return {
      activeTab: 'home',
      dropdownOpen: false,
      showCreate: false,
      loadingBands: false,
      user: null,
      bands: [],
      form: { nom_bande: '', date_arrivee: '', race: 'Ross308', fournisseur: '', nombre_initial: 0, statut: 'active' },
      avatarColor: '#6366f1',
      // Configuration Slides
      slides: [
        { title: 'Suivi de croissance', text: 'Visualisez les courbes de poids.', image: img1 },
        { title: 'IA Avicole', text: 'Détectez les anomalies rapidement.', image: img2 },
        { title: 'Rentabilité', text: 'Calculez vos marges en temps réel.', image: img3 }
      ],
      currentSlide: 0,
      slideTimer: null
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
      } catch (error) {
        console.error('Erreur fetchBandes:', error);
        this.bandsError = 'Impossible de charger les bandes: ' + error.message;
        this.bands = [];
      } finally {
        this.loadingBands = false;
      }
    },

    resetForm() {
      this.form = { nom_bande: '', date_arrivee: '', race: 'Ross308', fournisseur: '', nombre_initial: 0, statut: 'active' };
      this.bandsError = '';
    },

    async createBande() {
      this.bandsError = '';
      try {
        if (!this.form.nom_bande || !this.form.nom_bande.trim()) {
          this.bandsError = 'Le nom de la bande est requis';
          return;
        }
        const res = await fetch('http://localhost:5000/bandes/create', {
          method: 'POST',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.form)
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

    selectTab(t) { this.activeTab = t; if (t === 'bands') this.fetchBandes(); },
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

    loadUser() {
      try {
        const stored = localStorage.getItem('user');
        this.user = stored ? JSON.parse(stored) : null;
        if (this.user) this.generateRandomColor();
      } catch (error) {
        console.error('Erreur loadUser:', error);
        this.user = null;
      }
    },

    generateRandomColor() {
      const letters = '0123456789ABCDEF';
      let color = '#';
      for (let i = 0; i < 6; i++) color += letters[Math.floor(Math.random() * 16)];
      this.avatarColor = color;
    }
  },
  mounted() {
    this.loadUser();
    // Fermer le dropdown si on clique ailleurs
    this._closeDropdownHandler = () => { this.dropdownOpen = false; };
    document.addEventListener('click', this._closeDropdownHandler);
    this.startSlideAuto();
    if (this.activeTab === 'bands') this.fetchBandes();
  },
  beforeUnmount() { document.removeEventListener('click', this._closeDropdownHandler); this.stopSlideAuto(); }
};
</script>
<style src="../../css/home.css"></style>