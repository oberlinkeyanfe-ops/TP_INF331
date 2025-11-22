<template>
  <div class="home-root">
    <header class="page-header">
      <div class="brand">
        <img src="/assets/LOGO.svg" alt="Logo" />
        <span>AVIPRO</span>
      </div>

      <nav id="onglet" class="onglet">
        <a href="#" 
           @click.prevent="selectTab('home')" 
           :class="{ active: activeTab === 'home' }">Accueil</a>
        <a href="#" 
           @click.prevent="selectTab('bands')" 
           :class="{ active: activeTab === 'bands' }">Bands</a>
        <a href="#" 
           @click.prevent="selectTab('dashboard')" 
           :class="{ active: activeTab === 'dashboard' }">Dashboard</a>
        <a href="#" 
           @click.prevent="selectTab('help')" 
           :class="{ active: activeTab === 'help' }">Aide</a>
      </nav>

        <!-- Icône paramètres -->
        <span class="settings" @click="openSettings">
          <i class="fas fa-cog"> </i>
          
        </span>
    </header>

    <main class="main-area">
        <header2 class="user-header">
            <h1 style="color:green;">{{ title }}</h1>
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
                    {{ user?.nom ? user.nom[0].toUpperCase() : '?' }}
                </span>

                <!-- Dropdown infos -->
                <div class="dropdown" v-if="dropdownOpen">
                    <span>{{ user.nom }}</span>
                    <span>{{ user.email }}</span>
                    <router-link to="/signout">Déconnexion</router-link>
                </div>

            </div>
        </header2>

    

    
        <div v-if="activeTab === 'home'" class="accueil-onglet">
            <h2>Bienvenue sur AVIPRO Mr/Mme {{ user ? user.nom : '' }}</h2>
            <p>Votre plateforme de gestion avicole.</p>
            <router-link to="/bandes" class="btn-primary">Commencer</router-link>
        </div>

        <div v-if="activeTab === 'bands'" class="bands-onglet">
            <h2>Gestion des Bands</h2>
            <ul class="band-list">
                <li v-for="band in bands" :key="band.id" class="band-item" @click="openBand(band.id)">
                    <h3>Band {{ band.id }}</h3>
                    <p>Type de volaille: {{ band.type }}</p>
                    <p>Nombre de volailles: {{ band.count }}</p>
                    <p>Date de création: {{ band.creationDate }}</p>
                </li>
            </ul>
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
      user: null,
      bands: [],
      avatarColor:'',
      query: '',
      title:'HOME'
    }
  },
  methods: {
    selectTab(tab) {
      this.activeTab = tab
      this.title = tab.charAt(0).toUpperCase() + tab.slice(1)
    },
    toggleDropdown() {
      this.dropdownOpen = !this.dropdownOpen
    },
    openBand(id) {
      this.$router.push(`/bandes/${id}`)
    },
    loadUser() {
      try {
        const stored = sessionStorage.getItem("user")
        this.user = stored ? JSON.parse(stored) : null
        if (this.user) this.generateRandomColor()
      } catch {
        this.user = null
      }
    },
    generateRandomColor() {
        const letters = '0123456789ABCDEF'
        let color = '#'
        for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)]
        }
        this.avatarColor = color
    },
  },
  mounted() {
    this.loadUser()
  }
}
</script>

<style src="/css/home.css"></style>
