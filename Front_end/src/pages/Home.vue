<template>
  <div class="home-root">
    <header class="topbar">
      <div class="brand">
        <img src="../assets/icons/LOGO.svg" alt="Logo" />
        <span>AVIPRO</span>
      </div>

      <nav class="top-nav">
        <button class="top-link" @click.prevent="selectTab('home')" :class="{ active: activeTab === 'home' }">Accueil</button>
        <button class="top-link" @click.prevent="selectTab('bands')" :class="{ active: activeTab === 'bands' }">Bands</button>
        <button class="top-link" @click.prevent="selectTab('dashboard')" :class="{ active: activeTab === 'dashboard' }">Dashboard</button>
        <button class="top-link" @click.prevent="selectTab('help')" :class="{ active: activeTab === 'help' }">Aide</button>
      </nav>

      <div class="top-actions">
        <router-link v-if="!user" to="/login" class="btn-secondary">Se connecter</router-link>
        <div v-else class="profile">
          <span
            class="avatar"
            :style="{ backgroundColor: avatarColor }"
            @click="toggleDropdown"
          >
            {{ user && user.nom ? user.nom[0].toUpperCase() : '?' }}
          </span>
          <div class="dropdown" v-if="dropdownOpen" @click.stop>
            <span>{{ user.nom }}</span>
            <span>{{ user.email }}</span>
            <router-link to="/signout">Déconnexion</router-link>
          </div>
        </div>
      </div>
    </header>

    <!-- Main content -->
    <main class="main-area">
      <!-- User header fixé en haut -->
      <div class="user-header">
        <div class="title">
          <h1>{{ title }}</h1>
          <p v-if="activeTab=='home'">Bienvenue {{ user ? user.nom : '' }}</p>
        </div>
        <div class="header-actions">
          <button class="btn-secondary" @click="selectTab('bands')">Voir les bandes</button>
          <router-link to="/contact" class="btn-ghost">Support</router-link>
        </div>
      </div>

      <!-- Onglets -->
      <div v-if="activeTab === 'home'" class="accueil-onglet">
        <!-- Hero / présentation entreprise -->
        <section class="home-hero">
          <div class="home-hero-text">
            <p class="eyebrow">Plateforme avicole</p>
            <h2>AVIPRO : piloter, anticiper, protéger</h2>
            <p class="lede">
              Une suite complète pour l'aviculture : suivi en temps réel, alertes sanitaires, prévisions, et assistant IA
              relié à vos données et à la veille web. Réduisez les risques et sécurisez vos marges.
            </p>
            <div class="hero-actions">
              <router-link to="/bandes/1" class="btn-primary">Ouvrir le tableau de bord</router-link>
              <button class="btn-ghost" @click="selectTab('bands')">Créer une bande</button>
            </div>
            <div class="hero-badges">
              <span class="pill">Suivi temps réel</span>
              <span class="pill">Assistant IA</span>
              <span class="pill">Alertes sanitaires</span>
              <span class="pill">Prédictions</span>
            </div>
          </div>
          <div class="home-hero-visual">
            <div class="home-header-card">
              <div>
                <p class="eyebrow">Aperçu global</p>
                <h3>Vue multi-bandes</h3>
              </div>
              <div class="mini-metrics">
                <div><span>Bandes</span><strong>{{ bands.length || 0 }}</strong></div>
                <div><span>Actives</span><strong>{{ bands.filter(b => b.statut === 'active').length }}</strong></div>
                <div><span>Effectif</span><strong>{{ totalBirds }}</strong></div>
              </div>
              <div class="header-gradient"></div>
            </div>
          </div>
        </section>

        <!-- Slider visuel -->
        <section class="home-slider" @mouseenter="stopSlideAuto" @mouseleave="startSlideAuto">
          <div class="slide-visual" :style="slideStyle(activeSlide)">
            <div class="slide-overlay">
              <p class="slide-kicker">{{ activeSlide?.kicker || '' }}</p>
              <h3>{{ activeSlide?.title || '' }}</h3>
              <p>{{ activeSlide?.text || '' }}</p>
            </div>
          </div>
          <div class="slide-nav">
            <button class="nav-btn" @click="prevSlide">←</button>
            <div class="dots">
              <button
                v-for="(s, idx) in slides"
                :key="s.title"
                :class="['dot', { active: idx === currentSlide }]"
                @click="goToSlide(idx)"
                :aria-label="'Aller au slide ' + (idx+1)"
              ></button>
            </div>
            <button class="nav-btn" @click="nextSlide">→</button>
          </div>
        </section>

        <!-- Fonctionnalités détaillées -->
        <section class="features-section">
          <div class="feature-card">
            <div class="icon-pill">📊</div>
            <h4>Tableaux de bord</h4>
            <p>Coûts, consommations, mortalité, poids : tout en un coup d'œil, avec benchmarks intégrés.</p>
          </div>
          <div class="feature-card">
            <div class="icon-pill">🤖</div>
            <h4>Assistant IA</h4>
            <p>Questions en langage naturel, réponses basées sur vos données et la recherche web.</p>
          </div>
          <div class="feature-card">
            <div class="icon-pill">🛡️</div>
            <h4>Alertes Santé</h4>
            <p>Notifications critiques, suivi des traitements et réduction de la mortalité.</p>
          </div>
          <div class="feature-card">
            <div class="icon-pill">📈</div>
            <h4>Prédictions & marge</h4>
            <p>Anticipation des coûts et date de vente optimale pour sécuriser vos marges.</p>
          </div>
        </section>

        <!-- Footer -->
        <footer class="home-footer">
          <div class="footer-brand">
            <img src="../assets/icons/LOGO.svg" alt="AVIPRO" />
            <p>La plateforme avicole pour piloter, anticiper et protéger vos élevages.</p>
          </div>
          <div class="footer-links">
            <h5>Contact</h5>
            <a href="mailto:contact@avipro.com">contact@avipro.com</a>
            <a href="tel:+237600000000">+237 60 00 00 000</a>
          </div>
          <div class="footer-links">
            <h5>Réseaux</h5>
            <a href="#">Facebook</a>
            <a href="#">Instagram</a>
            <a href="#">LinkedIn</a>
          </div>
          <div class="footer-links">
            <h5>Support</h5>
            <router-link to="/contact">Nous écrire</router-link>
            <router-link to="/aide">Centre d'aide</router-link>
          </div>
        </footer>
      </div>

      <div v-if="activeTab === 'bands'" class="bands-onglet">
        <h2>Gestion des Bands</h2>
          <!-- Bouton + Créer -->
          <div class="create-control">
            <button class="create-toggle" @click.prevent="showCreate = !showCreate">
              <span class="plus">+</span> Créer
            </button>
          </div>

          <!-- Formulaire de création d'une nouvelle bande (dropdown intégré) -->
          <transition name="fade">
            <div v-if="showCreate" class="modal-overlay" @click.self="closeAndReset">
              <div class="modal">
                <form class="create-bande form-grid" @submit.prevent="createBande">
                  <div>
                    <label>Nom de la bande</label>
                    <input v-model="form.nom_bande" type="text" required />
                  </div>
                  <div>
                    <label>Date d'arrivée</label>
                    <input v-model="form.date_arrivee" type="date" required />
                  </div>
                  <div>
                    <label>Race</label>
                    <select v-model="form.race">
                      <option value="Ross308">Ross308</option>
                      <option value="Ross708">Ross708</option>
                      <option value="Cobb500">Coob500</option>
                      <option value="Cobb700">Coob700</option>
                      <option value="Hybro6">Hybro6</option>
                      <option value="Poulet de chair 61">Poulet de chair 61</option>
                      <option value="Broiler-M">Broiler-M</option>
                    </select>

                  </div>
                  <div>
                    <label>Fournisseur</label>
                    <select v-model="form.fournisseur">
                      <option value="EspaceAgro Cameroun">EspaceAgro Cameroun</option>
                      <option value="BonCoin Cameroun">BonCoin Cameroun</option>
                      <option value="CoinAfrique Cameroun">CoinAfrique Cameroun</option>
                    </select>
                  </div>
                  <div>
                    <label>Nombre initial</label>
                    <input v-model.number="form.nombre_initial" type="number" min="0" required />
                  </div>
                  <div>
                    <label>Poids moyen initial (kg)</label>
                    <input v-model.number="form.poids_moyen_initial" type="number" step="0.01" />
                  </div>
                  <div>
                    <label>Âge moyen (jours)</label>
                    <input v-model.number="form.age_moyen" type="number" />
                  </div>
                  <div>
                    <label>Nombre morts totaux</label>
                    <input v-model.number="form.nombre_morts_totaux" type="number" />
                  </div>
                  <div>
                    <label>Statut</label>
                    <select v-model="form.statut">
                      <option value="active">active</option>
                      <option value="terminee">terminée</option>
                      <option value="archivee">archivée</option>
                    </select>
                  </div>
                  
                  <div>
                    <input type="number" step="25"
                  </div>

                  <div class="row actions">
                    <button type="submit" class="btn-primary">Créer la bande</button>
                    <button type="button" @click.prevent="closeAndReset" class="btn-secondary">Annuler</button>
                  </div>
                  
                </form>
              </div>
            </div>
          </transition>

        <!-- Liste des bandes existantes -->
        <div class="band-list-container">
          <div v-if="loadingBands" class="loading">Chargement des bandes...</div>
          <ul v-else-if="bands.length > 0" class="band-list">
            <li v-for="band in bands" :key="band.id" class="band-item" @click="openBand(band)">
              <h3>{{ band.nom_bande }} (ID: {{ band.id }})</h3>
              <p>Race: {{ band.race || '—' }}</p>
              <p>Nombre initial: {{ band.nombre_initial }}</p>
              <p>Date arrivée: {{ formatDate(band.date_arrivee) }}</p>
              <p>Statut: <span :class="['status', band.statut]">{{ band.statut }}</span></p>
            </li>
          </ul>
          <div v-else class="no-bands">
            <p>Aucune bande disponible. Créez votre première bande !</p>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'dashboard'" class="dashboard-onglet">
        <h2>Tableau de bord</h2>
        <p>Visualisez les performances de vos élevages avicoles en un coup d'œil.</p>
      </div>

      <div v-if="activeTab === 'help'" class="aide-onglet">
        <h2>Centre d'aide</h2>
        <router-link to="/contact" class="btn-secondary">Contactez-nous</router-link>
      </div>
    </main>
  </div>
</template>

<script>
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
      form: {
        nom_bande: '',
        date_arrivee: '',
        race: '',
        fournisseur: '',
        nombre_initial: 0,
        poids_moyen_initial: 0,
        age_moyen: 0,
        nombre_nouveaux_nes: 0,
        nombre_morts_totaux: 0,
        statut: 'active'
      },
      bandsError: '',
      avatarColor: '',
      title: 'HOME',
      slides: [
        {
          title: 'Pilotage en temps réel',
          text: 'Suivez vos bandes, vos coûts et vos consommations avec des métriques claires et des alertes immédiates.',
          kicker: 'Tableau de bord',
          image: '/assets/slide1.png',
          gradient: 'linear-gradient(135deg, #6f42c1 0%, #4f46e5 100%)'
        },
        {
          title: 'Assistant IA avicole',
          text: 'Questions en français, données internes + recherche web pour décider plus vite.',
          kicker: 'IA & contexte',
          image: '/assets/slide2.png',
          gradient: 'linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%)'
        },
        {
          title: 'Prédictions et marge',
          text: 'Anticipez les coûts, la mortalité et la date de vente optimale pour sécuriser votre marge.',
          kicker: 'Prévisions',
          image: '/assets/slide3.png',
          gradient: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)'
        }
      ],
      currentSlide: 0,
      slideTimer: null
    }
  },
  computed: {
    activeSlide() {
      if (!this.slides || !this.slides.length) return null;
      const idx = Math.min(Math.max(this.currentSlide, 0), this.slides.length - 1);
      return this.slides[idx];
    },
    totalBirds() {
      return (this.bands || []).reduce((acc, b) => acc + (b.nombre_initial || 0), 0);
    }
  },
  methods: {
    async fetchBandes() {
      this.loadingBands = true;
      this.bandsError = '';
      try {
        const res = await fetch('http://localhost:5000/bandes/', {
          method: 'GET',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' }
        })
        if (!res.ok) {
          throw new Error(`Erreur HTTP: ${res.status}`);
        }
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
      this.form = {
        nom_bande: '',
        date_arrivee: '',
        race: '',
        fournisseur: '',
        nombre_initial: 0,
        poids_moyen_initial: 0,
        age_moyen: 0,
        nombre_nouveaux_nes: 0,
        nombre_morts_totaux: 0,
        statut: 'active'
      }
      this.bandsError = '';
    },

    async createBande() {
      this.bandsError = '';
      try {
        if (!this.form.nom_bande.trim()) {
          this.bandsError = 'Le nom de la bande est requis';
          return;
        }

        const res = await fetch('http://localhost:5000/bandes/create', {
          method: 'POST',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.form)
        })

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

    closeAndReset() {
      this.resetForm();
      this.showCreate = false;
    },
    
    selectTab(tab) {
      this.activeTab = tab;
      this.title = tab.toUpperCase();
      if (tab === 'bands') {
        this.fetchBandes();
      }
    },
    
    toggleDropdown() {
      this.dropdownOpen = !this.dropdownOpen;
    },
    
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
    openSettings() {
      console.log("Ouverture des paramètres");
    },
    
    loadUser() {
      try {
        const stored = localStorage.getItem("user");
        this.user = stored ? JSON.parse(stored) : null;
        if (this.user) {
          this.generateRandomColor();
        }
      } catch (error) {
        console.error('Erreur loadUser:', error);
        this.user = null;
      }
    },
    
    generateRandomColor() {
      const letters = '0123456789ABCDEF';
      let color = '#';
      for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
      }
      this.avatarColor = color;
    },
    
    formatDate(dateString) {
      if (!dateString) return '—';
      const date = new Date(dateString);
      return date.toLocaleDateString('fr-FR');
    },

    nextSlide() {
      if (!this.slides.length) return;
      this.currentSlide = (this.currentSlide + 1) % this.slides.length;
    },
    prevSlide() {
      if (!this.slides.length) return;
      this.currentSlide = (this.currentSlide - 1 + this.slides.length) % this.slides.length;
    },
    goToSlide(idx) {
      if (idx < 0 || idx >= this.slides.length) return;
      this.currentSlide = idx;
    },
    startSlideAuto() {
      if (this.slideTimer || this.slides.length < 2) return;
      this.slideTimer = setInterval(() => this.nextSlide(), 5200);
    },
    stopSlideAuto() {
      if (this.slideTimer) {
        clearInterval(this.slideTimer);
        this.slideTimer = null;
      }
    },
    slideStyle(slide) {
      if (!slide) {
        return { background: '#111827' };
      }
      if (slide.image) {
        return {
          backgroundImage: `linear-gradient(120deg, rgba(0,0,0,0.35), rgba(0,0,0,0.15)), url(${slide.image})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center'
        };
      }
      return { backgroundImage: slide.gradient };
    }
  },
  mounted() {
    this.loadUser();
    const closeDropdown = () => { this.dropdownOpen = false; };
    this._closeDropdownHandler = closeDropdown;
    document.addEventListener('click', closeDropdown);
    if (this.activeTab === 'bands') {
      this.fetchBandes();
    }
    this.startSlideAuto();
  },
  beforeUnmount() {
    if (this._closeDropdownHandler) {
      document.removeEventListener('click', this._closeDropdownHandler);
    }
    this.stopSlideAuto();
  }
}
</script>

<style src="../../css/home.css"></style>