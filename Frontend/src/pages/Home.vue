<template>
  <div class="home-root">
    <!-- Sidebar -->
    <header class="page-header">
      <div class="brand">
        <img src="../assets/icons/LOGO.svg" alt="Logo" />
        <span>AVIPRO</span>
      </div>

      <nav id="onglet" class="onglet">
        <div class="sub-onglet">
          <img src="../assets/icons/home.svg" alt="Logo" />
          <a href="#"
            @click.prevent="selectTab('home')"
            :class="{ active: activeTab === 'home' }">Accueil</a>
        </div>

        <div class="sub-onglet">
          <img src="../assets/icons/bands.svg" alt="Logo" />        
          <a href="#"
            @click.prevent="selectTab('bands')"
            :class="{ active: activeTab === 'bands' }">Bands</a>
        </div>

        <div class="sub-onglet">
          <img src="../assets/icons/dashboard.svg" alt="Logo" />
          <a href="#"
            @click.prevent="selectTab('dashboard')"
            :class="{ active: activeTab === 'dashboard' }">Dashboard</a>
        </div>  

        <div class="sub-onglet">
          <img src="../assets/icons/aide.svg" alt="Logo" />
          <a href="#"
            @click.prevent="selectTab('help')"
            :class="{ active: activeTab === 'help' }">Aide</a>
        </div>
      </nav>

      <!-- Icône paramètres en bas de la sidebar -->
      <div class="sidebar-footer">
        <span class="settings" @click="openSettings">
          <i class="fas fa-cog"></i>
        </span>
      </div>
    </header>

    <!-- Main content -->
    <main class="main-area">
      <!-- User header fixé en haut -->
      <div class="user-header">
        <div class="title">
          <h1>{{ title }}</h1>
          <p v-if="activeTab=='home'"> Bienvenue {{user ? user.nom : ''}}</p>
        </div>
        <div class="actions">
          <div v-if="!user" class="user-actions">
            <router-link to="/register">Se connecter</router-link>
          </div>

          <div v-else class="profile">
            <!-- Avatar cercle avec couleur aléatoire -->
            <span
              class="avatar"
              :style="{ backgroundColor: avatarColor }"
              @click="toggleDropdown"
            >
              {{ user && user.nom ? user.nom[0].toUpperCase() : '?' }}
            </span>

            <!-- Dropdown infos -->
            <div class="dropdown" v-if="dropdownOpen" @click.stop>
              <span>{{ user.nom }}</span>
              <span>{{ user.email }}</span>
              <router-link to="/signout">Déconnexion</router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- Onglets -->
      <div v-if="activeTab === 'home'" class="accueil-onglet">
        <h2>Bienvenue sur AVIPRO Mr/Mme {{ user ? user.nom : '' }}</h2>
        <p>Votre plateforme de gestion avicole.</p>
        <router-link to="#" class="btn-primary">Commencer</router-link>
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
      title: 'HOME'
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
          headers: {
            'Content-Type': 'application/json',
          }
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
        // Validation
        if (!this.form.nom_bande.trim()) {
          this.bandsError = 'Le nom de la bande est requis';
          return;
        }

        const res = await fetch('http://localhost:5000/bandes/create', {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(this.form)
        })

        const data = await res.json();
        
        if (!res.ok) {
          this.bandsError = data.error || data.message || 'Erreur lors de la création de la bande';
          return;
        }

        // Rafraîchir la liste
        await this.fetchBandes();
        this.resetForm();
        this.showCreate = false;
        
        // Afficher un message de succès
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
      // CORRECTION: Stocker les données essentielles uniquement
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
      
      console.log('Storing band data:', bandData);
      localStorage.setItem('current_band', JSON.stringify(bandData));
      this.$router.push(`/bandes/${band.id}`);
    },
    openSettings() {
      console.log("Ouverture des paramètres");
      // Implémentez la logique d'ouverture des paramètres
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
    }
  },
  mounted() {
    this.loadUser();
    // Fermer le dropdown si on clique ailleurs
    document.addEventListener('click', () => {
      this.dropdownOpen = false;
    });
    
    // Charger les bandes si on arrive directement sur l'onglet bands
    if (this.activeTab === 'bands') {
      this.fetchBandes();
    }
  },
  beforeUnmount() {
    // Nettoyer l'event listener
    document.removeEventListener('click', () => {
      this.dropdownOpen = false;
    });
  }
}
</script>

<style src="../../css/home.css"></style>