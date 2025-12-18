<template>
  <div class="bande-root">
    <nav class="bande-tabs">
      <div class="logo">
        <img src="../assets/icons/LOGO.svg" alt="Logo" />
        <span>AVIPRO</span>
      </div>

      <div class="tabs">
        <span class="logo-section">
          <img src="../assets/icons/dashboard.svg"/>
          <button :class="{ active: activeTab === 'dashboard' }" @click="selectTab('dashboard')">
            Dashboard
          </button>
        </span>

        <span class="logo-section">
          <img src="../assets/icons/consommation.svg"/>
          <button :class="{ active: activeTab === 'consommation' }" @click="selectTab('consommation')">
            Consommation
          </button>
        </span>

        <span class="logo-section">
          <img src="../assets/icons/predictions.svg"/>
          <button :class="{ active: activeTab === 'predictions' }" @click="selectTab('predictions')">
            Prédictions
          </button> 
        </span>

        <span class="logo-section">
          <img src="../assets/icons/kpi.svg"/>
          <button :class="{ active: activeTab === 'kpi' }" @click="selectTab('kpi')">
            KPIs
          </button> 
        </span>

        <span class="logo-section">
          <img src="../assets/icons/sante.svg"/>
          <button @click="tachesOpen = !tachesOpen" class="taches">Sante</button>
          <ul class="subtabs">
            <div v-show="tachesOpen">
              <li class="subtab-item">
                <button
                  :class="{ active: activeTab === 'traitements' }"
                  @click="selectTab('traitements')"
                >
                  Traitements
                </button>
              </li>
              <li class="subtab-item">
                <button
                  :class="{ active: activeTab === 'interventions' }"
                  @click="selectTab('interventions')"
                >
                  Interventions
                </button>
              </li>
              <li class="subtab-item">
                <button
                  :class="{ active: activeTab === 'animaux' }"
                  @click="selectTab('animaux')"
                >
                  Animaux
                </button>
              </li>
            </div>
          </ul>
        </span>

        <span class="logo-section">
          <img src="../assets/icons/finances.svg"/>
          <button
            :class="{ active: activeTab === 'finances' }"
            @click="selectTab('finances')"
          >
            Finances
          </button>
        </span>

        <span class="logo-section">
          <img src="../assets/icons/infos.svg"/>
          <button
            :class="{ active: activeTab === 'infos' }"
            @click="selectTab('infos')"
          >
            Infos
          </button>
        </span>
      </div>

      <div class="sidebar-footer">
        <span class="settings" @click="openSettings">
          <i class="fas fa-cog"></i>
        </span>
      </div>
    </nav>

    <div class="main-section">
      <header class="bande-header">
        <div class="title">
          <h1>{{ activeTab }}</h1>
          <div class="meta" v-show="activeTab=='dashboard'">
            Statut: <strong>{{ band?.statut || "—" }}</strong> • Arrivée:
            {{ band?.date_arrivee || "—" }}
          </div>
        </div>

        <div class="search">
          <input class="search" @click="showSearchBande"
            placeholder="Rechercher"/>
          <img src="../assets/icons/search.svg">
        </div>

        <div>
          <button class="ai" :class="{ active: activeTab === 'chatbot' }"
            @click="selectTab('chatbot')"></button>
        </div>
      </header>

      <main class="bande-main">
        <!-- Dashboard Tab -->
        <section
          v-if="activeTab === 'dashboard'"
          class="tab-panel dashboard-panel"
        >
          <!-- KPIs row -->
          <div class="kpi-row">
            <div class="kpi-card">
              <div class="kpi-label">Poids moyen</div>
              <div class="kpi-value">{{ (band?.poids_moyen_initial || 0).toFixed(2) }} kg</div>
              <div class="kpi-trend" :class="getTrendClass('poids')">
                {{ trends.poids }}%
              </div>
            </div>
            <div class="kpi-card">
              <div class="kpi-label">Coût total</div>
              <div class="kpi-value">{{ totalCost.toFixed(2) }} €</div>
              <div class="kpi-trend" :class="getTrendClass('cout')">
                {{ trends.cout }}%
              </div>
            </div>
            <div class="kpi-card">
              <div class="kpi-label">Taux mortalité</div>
              <div class="kpi-value">{{ mortalityRate }}%</div>
              <div class="kpi-trend" :class="getTrendClass('mortalite')">
                {{ trends.mortalite }}%
              </div>
            </div>
            <div class="kpi-card">
              <div class="kpi-label">IC</div>
              <div class="kpi-value">{{ consumptionIndex }}</div>
              <div class="kpi-trend" :class="getTrendClass('ic')">
                {{ trends.ic }}%
              </div>
            </div>
          </div>

          <!-- Charts Section now delegated to reusable component -->
          <DashboardCharts :band="band" :consommations="consommations" />

          <!-- Recent entries -->
          <div class="orders-list">
            <h3>Dernières consommations</h3>
            <div class="consumption-header">
              <span>Date</span>
              <span>Type</span>
              <span>Quantité</span>
              <span>Coût</span>
            </div>
            <ul class="consumption-items">
              <li v-for="c in consommations.slice(0, 6)" :key="c.id">
                <span>{{ formatDate(c.date) }}</span>
                <span>{{ c.type }}</span>
                <span>{{ c.kg }} kg</span>
                <span>{{ c.cout }} €</span>
              </li>
              <li v-if="consommations.length === 0" class="no-data">
                Aucune consommation enregistrée
              </li>
            </ul>
          </div>

          <!-- Widgets -->
          <div class="widgets-section">
            <div class="widget">
              <h4>Statistiques</h4>
              <div class="widget-stats">
                <div class="stat">
                  <div class="stat-label">Animaux actuels</div>
                  <div class="stat-value">{{ currentAnimals }}</div>
                </div>
                <div class="stat">
                  <div class="stat-label">Âge moyen</div>
                  <div class="stat-value">{{ band?.age_moyen || 0 }} jours</div>
                </div>
                <div class="stat">
                  <div class="stat-label">Coût/jour</div>
                  <div class="stat-value">{{ averageDailyCost }} €</div>
                </div>
                <div class="stat">
                  <div class="stat-label">Productivité</div>
                  <div class="stat-value">{{ productivityScore }}%</div>
                </div>
              </div>
            </div>

            <div class="widget">
              <h4>Alertes</h4>
              <div class="alerts-list">
                <div v-for="alert in alerts" :key="alert.id" 
                     :class="['alert', alert.level]">
                  <span class="alert-icon">!</span>
                  <span class="alert-text">{{ alert.message }}</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Consommation Tab -->
        <section
          v-if="activeTab === 'consommation'"
          class="tab-panel consommation-panel"
        >
          <h2>Consommations</h2>
          <form @submit.prevent="addConsumption" class="consumption-form">
            <input type="date" v-model="consumptionForm.date" required />
            <input
              type="text"
              v-model="consumptionForm.type"
              placeholder="Type d'aliment"
              required
            />
            <input
              type="number"
              v-model.number="consumptionForm.kg"
              placeholder="Kg"
              step="0.01"
              required
            />
            <input
              type="number"
              v-model.number="consumptionForm.cout"
              placeholder="Coût"
              step="0.01"
            />
            <input
              type="number"
              v-model.number="consumptionForm.poids"
              placeholder="Poids moyen actuel (kg)"
              step="0.01"
            />
            <div class="consumption-actions">
              <button class="btn" type="submit">
                {{ editingConsumptionId ? 'Mettre à jour' : 'Ajouter' }}
              </button>
              <button
                v-if="editingConsumptionId"
                class="btn secondary"
                type="button"
                @click="resetConsumptionForm"
              >
                Annuler
              </button>
            </div>
          </form>

          <!-- Graphique de consommation -->
          <div class="consumption-chart">
            <h3>Historique des consommations</h3>
            <ConsumptionHistoryChart :consommations="consommations" :band="band" />
          </div>

          <ul class="consumption-list">
            <li v-for="c in consommations" :key="c.id">
              <div class="c-row">
                <div>
                  {{ c.date }} — {{ c.type }} — {{ c.kg }} kg
                  <span v-if="c.semaine_production" class="muted">(Semaine {{ c.semaine_production }})</span>
                </div>
                <div class="consumption-row-actions">
                  <span class="muted">{{ c.cout ? c.cout + " €" : "" }}</span>
                  <button class="link" @click="startEditConsumption(c)">Modifier</button>
                  <button class="link danger" @click="deleteConsumption(c)">Supprimer</button>
                </div>
              </div>
            </li>
          </ul>
        </section>

        <!-- Prédictions Tab -->
        <section
          v-if="activeTab === 'predictions'"
          class="tab-panel predictions-panel"
        >
          <h2>Prédictions</h2>
          
          <div class="prediction-controls">
            <div class="control-group">
              <label>Horizon:</label>
              <select v-model="predictionDays">
                <option value="7">7 jours</option>
                <option value="14">14 jours</option>
                <option value="30">30 jours</option>
              </select>
            </div>
            <div class="control-group">
              <label>Modèle:</label>
              <select v-model="predictionModel">
                <option value="lineaire">Linéaire</option>
                <option value="exponentiel">Exponentiel</option>
                <option value="saisonnier">Saisonnier</option>
              </select>
            </div>
            <button @click="generatePredictions" class="btn-primary">
              Générer
            </button>
          </div>

          <!-- Graphiques de prédiction -->
          <div class="prediction-charts">
            <PredictionCharts :predictions="predictions" />
          </div>

          <!-- Tableau des prédictions -->
          <div class="predictions-table">
            <h3>Détail des prédictions</h3>
            <table>
              <thead>
                <tr>
                  <th>Jour</th>
                  <th>Date</th>
                  <th>Poids (kg)</th>
                  <th>Consom. (kg)</th>
                  <th>Coût (€)</th>
                  <th>Marge (€)</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="p in predictions" :key="p.jour">
                  <td>J+{{ p.jour }}</td>
                  <td>{{ p.date }}</td>
                  <td>{{ p.poids.toFixed(2) }}</td>
                  <td>{{ p.consommation.toFixed(1) }}</td>
                  <td>{{ p.cout.toFixed(2) }}</td>
                  <td :class="getMarginClass(p.marge)">{{ p.marge.toFixed(2) }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Résumé -->
          <div class="prediction-summary">
            <div class="summary-card">
              <h4>Résumé</h4>
              <div class="summary-content">
                <div class="summary-item">
                  <span>Gain total estimé:</span>
                  <strong :class="getProfitClass(totalPredictedProfit)">
                    {{ totalPredictedProfit.toFixed(2) }} €
                  </strong>
                </div>
                <div class="summary-item">
                  <span>ROI estimé:</span>
                  <strong :class="getROIClass(roi)">
                    {{ roi.toFixed(1) }}%
                  </strong>
                </div>
                <div class="summary-item">
                  <span>Date optimale:</span>
                  <strong>{{ optimalSellingDate }}</strong>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- KPIs Tab -->
        <section v-if="activeTab === 'kpi'" class="tab-panel kpi-panel">
          <KPIDashboard 
            :band-data="band"
            :consommation-data="consommations"
            v-if="band"
          />
        </section>

        <!-- Chatbot Tab -->
        <section v-if="activeTab === 'chatbot'" class="tab-panel chatbot-panel">
          <h2>Chatbot</h2>
          <div class="chatbox">
            <div class="messages">
              <div v-for="(m, i) in messages" :key="i" :class="['msg', m.from]">
                {{ m.text }}
              </div>
            </div>
            <form @submit.prevent="sendMessage" class="chat-form">
              <input
                v-model="chatInput"
                placeholder="Poser une question à l'IA"
              />
              <button class="btn" type="submit">Envoyer</button>
            </form>
          </div>
        </section>

        <!-- Infos Tab -->
        <section v-if="activeTab === 'infos'" class="tab-panel infos-panel">
          <h2>Infos</h2>
          <dl class="info-list">
            <div>
              <dt>Nom</dt>
              <dd>{{ band?.nom_bande || "—" }}</dd>
            </div>
            <div>
              <dt>Date arrivée</dt>
              <dd>{{ band?.date_arrivee || "—" }}</dd>
            </div>
            <div>
              <dt>Fournisseur</dt>
              <dd>{{ band?.fournisseur || "—" }}</dd>
            </div>
            <div>
              <dt>Race</dt>
              <dd>{{ band?.race || "—" }}</dd>
            </div>
            <div>
              <dt>Nombre init.</dt>
              <dd>{{ band?.nombre_initial || "—" }}</dd>
            </div>
          </dl>
        </section>

        <!-- Animaux Tab -->
        <section v-if="activeTab === 'animaux'" class="tab-panel animaux-panel">
          <h2>Animaux</h2>
          <ul class="animaux-list">
            <li v-for="a in animaux" :key="a.id">
              {{ a.nom || "#" + a.id }} — Âge: {{ a.age || "—" }}
            </li>
          </ul>
        </section>

        <section
          v-if="activeTab === 'traitements'"
          class="tab-panel traitements-panel"
        >
          <h2>Traitements</h2>
          <p>Historique des traitements (à implémenter).</p>
        </section>

        <section
          v-if="activeTab === 'interventions'"
          class="tab-panel interventions-panel"
        >
          <h2>Interventions</h2>
          <p>Historique des interventions (à implémenter).</p>
        </section>

        <section
          v-if="activeTab === 'finances'"
          class="tab-panel depenses-panel"
        >
          <h2>Finances</h2>
          <p>Liste des dépenses (à implémenter).</p>
        </section>
      </main>
    </div>
  </div>
</template>

<script>
import KPIDashboard from './Kpi.vue';
import DashboardCharts from './charts/DashboardCharts.vue';
import ConsumptionHistoryChart from './charts/Consommation_chart.vue';
import PredictionCharts from './charts/Prediction_chart.vue';

export default {
  name: 'Bandes',

  components: {
    KPIDashboard,
    DashboardCharts,
    ConsumptionHistoryChart,
    PredictionCharts
  },

  data() {
    return {
      id: null,
      band: null,
      activeTab: "dashboard",
      kpi: null,
      tachesOpen: false,
      consommations: [],
      consumptionForm: { 
        date: new Date().toISOString().slice(0, 10), 
        type: "", 
        kg: 0, 
        cout: 0,
        poids: null
      },
      editingConsumptionId: null,

      animaux: [],
      treatments: [],
      interventions: [],
      predictions: [],
      _fetchingTab: null,
      messages: [
        { from: 'bot', text: 'Bonjour ! Comment puis-je vous aider avec votre bande avicole ?' }
      ],
      chatInput: "",
      
      // Prediction data
      predictionDays: '7',
      predictionModel: 'lineaire',
      
      // Trends dans un objet pour éviter les erreurs
      trends: {
        poids: 2.5,
        cout: -1.2,
        mortalite: 0.5,
        ic: -0.8
      },
      
      // Metrics
      totalPredictedProfit: 0,
      optimalSellingDate: '',
      roi: 0,
      
      // Alerts
      alerts: [
        { id: 1, level: 'medium', message: 'Consommation élevée cette semaine' },
        { id: 2, level: 'low', message: 'Poids dans la moyenne' },
        { id: 3, level: 'high', message: 'Taux de mortalité à surveiller' }
      ]
    };
  },
  
  computed: {
    currentAnimals() {
      if (!this.band) return 0;
      return (this.band.nombre_initial || 0) + 
             (this.band.nombre_nouveaux_nes || 0) - 
             (this.band.nombre_morts_totaux || 0);
    },
    
    mortalityRate() {
      if (!this.band || !this.band.nombre_initial || this.band.nombre_initial === 0) return 0;
      const morts = this.band.nombre_morts_totaux || 0;
      return ((morts / this.band.nombre_initial) * 100).toFixed(1);
    },
    
    totalCost() {
      return this.consommations.reduce((total, c) => total + (c.cout || 0), 0);
    },
    
    consumptionIndex() {
      if (this.currentAnimals === 0 || this.totalCost === 0) return 0;
      return (this.totalCost / this.currentAnimals).toFixed(2);
    },
    
    averageDailyCost() {
      if (this.consommations.length === 0) return 0;
      const days = Math.max(1, this.consommations.length);
      return (this.totalCost / days).toFixed(2);
    },
    
    productivityScore() {
      const weightScore = (this.band?.poids_moyen_initial || 0) * 10;
      const mortalityScore = 100 - this.mortalityRate;
      return ((weightScore + mortalityScore) / 2).toFixed(0);
    }
  },
  
  methods: {
    async fetchBand() {
      try {
        const storedBand = localStorage.getItem('current_band');
        
        if (!storedBand) {
          this.band = null;
          this.id = null;
          return;
        }
        
        let bandData;
        try {
          bandData = JSON.parse(storedBand);
        } catch (e) {
          console.error('Error parsing band data:', e);
          this.band = null;
          this.id = null;
          return;
        }
        
        this.band = bandData;
        
        // Récupérer l'ID correctement
        this.id = bandData?.id || bandData?.bande_id || null;
        
        console.log('Band data from localStorage:', bandData);
        console.log('Original ID from band data:', this.id);
        
        // Nettoyer l'ID pour l'API
        if (this.id) {
          // Si l'ID est un objet, extraire la valeur
          if (typeof this.id === 'object') {
            this.id = this.id.id || this.id.value || null;
          }
          
          // Si c'est une string avec ":", prendre seulement la première partie
          if (typeof this.id === 'string') {
            this.id = this.id.split(':')[0].trim();
            
            // Convertir en nombre si possible
            const numericId = parseInt(this.id);
            if (!isNaN(numericId)) {
              this.id = numericId;
            }
          }
        }
        
        console.log('Final cleaned band ID for API:', this.id, 'Type:', typeof this.id);
        
        // Charger les données de la BD après avoir l'ID
        await this.loadBandDataFromDB();
        
      } catch (e) {
        console.error("fetchBand error:", e);
        this.band = null;
        this.id = null;
      }
    },

    async loadBandDataFromDB() {
      try {
        if (!this.id) return;
        
        // Charger les données complètes de la bande depuis l'API
        const response = await fetch(`http://localhost:5000/bandes/${this.id}`, {
          credentials: 'include'
        });
        
        if (response.ok) {
          const bandData = await response.json();
          
          // Fusionner les données du localStorage avec celles de la BD
          this.band = { ...this.band, ...bandData };
          
          // Mettre à jour les trends avec des données réelles
          this.updateTrendsFromData();
          
          console.log('Band data loaded from DB:', bandData);
        }
      } catch (error) {
        console.warn('Error loading band data from DB:', error);
      }
    },

    updateTrendsFromData() {
      // Calculer des trends basées sur les données réelles
      if (this.band?.poids_moyen_initial) {
        this.trends.poids = this.calculateWeightTrend();
        this.trends.cout = this.calculateCostTrend();
        this.trends.mortalite = this.calculateMortalityTrend();
        this.trends.ic = this.calculateICTrend();
      }
    },

    calculateWeightTrend() {
      // Simuler un trend basé sur les données
      if (!this.band?.poids_moyen_initial) return 0;
      
      // Exemple : si le poids moyen est bon (> 2.5kg), trend positif
      return this.band.poids_moyen_initial > 2.5 ? 2.5 : -1.0;
    },

    calculateCostTrend() {
      // Calculer basé sur le coût total
      const totalConsommations = this.totalCost;
      // Exemple : si coût < 500€, trend négatif (bon)
      return totalConsommations < 500 ? -1.2 : 3.5;
    },

    calculateMortalityTrend() {
      if (!this.band?.nombre_initial || this.band.nombre_initial === 0) return 0;
      
      const mortalityRate = ((this.band.nombre_morts_totaux || 0) / this.band.nombre_initial) * 100;
      // Exemple : si mortalité < 5%, trend bas
      return mortalityRate < 5 ? 0.5 : 2.5;
    },

    calculateICTrend() {
      // Indice de consommation (plus bas = mieux)
      const totalConsommations = this.totalCost;
      const currentAnimals = this.currentAnimals;
      
      if (currentAnimals === 0 || totalConsommations === 0) return 0;
      
      const ic = totalConsommations / currentAnimals;
      // Exemple : si IC < 2, trend négatif (bon)
      return ic < 2 ? -0.8 : 1.5;
    },

    async calculateKPI() {
      try {
        if (!this.id) return;
        
        const data = await fetch(`http://localhost:5000/bandes/${this.id}`, {
          credentials: 'include'
        }).then(res => res.ok ? res.json() : null);
        
        if (!data) {
          this.kpi = {
            poids_moyen: this.band?.poids_moyen_initial || null,
            cout_total: 0,
            taux_mortalite: this.band?.nombre_initial > 0 ? 
              ((this.band?.nombre_morts_totaux || 0) / this.band?.nombre_initial * 100).toFixed(2) : 0,
            ic: 0,
          };
          return;
        }
        
        const total_animaux = data.total_animaux_actuels || 
          (data.nombre_initial || 0) + (data.nbre_ajoute || 0) - (data.nombre_morts_totaux || 0);
        
        this.kpi = {
          poids_moyen: data.poids_moyen_initial || null,
          cout_total: 0,
          taux_mortalite: total_animaux > 0 ? 
            ((data.nombre_morts_totaux || 0) / (data.nombre_initial || 1) * 100).toFixed(2) : 0,
          ic: 0,
        };
      } catch (e) {
        console.warn("calculateKPI error:", e);
        this.kpi = {
          poids_moyen: "—",
          cout_total: "—",
          taux_mortalite: "—",
          ic: "—"
        };
      }
    },

    async fetchTabData(tab) {
      // Éviter les appels en double
      if (this._fetchingTab === tab) {
        console.log(`⏳ Données ${tab} déjà en cours de chargement`);
        return;
      }
      
      this._fetchingTab = tab;
      
      try {
        if (!this.id) {
          console.warn('No band ID available');
          return;
        }
        
        if (tab === "consommation") {
          const url = `http://localhost:5000/consommations/bande/${this.id}`;
          console.log('📥 Chargement consommations depuis:', url);
          
          const response = await fetch(url, {
            credentials: 'include'
          });
          
          if (response.ok) {
            const data = await response.json();
            console.log('📊 Données reçues:', data.count || 0, 'consommations');
            
            const raw = data.consommations || [];
            this.consommations = raw.map(c => ({
              id: c.id,
              date: c.date,
              type: c.type_aliment || '',
              kg: c.aliment_kg || 0,
              cout: c.cout_aliment || 0,
              bande_id: c.bande_id,
              eau_litres: c.eau_litres || 0,
              semaine_production: c.semaine_production || null
            }));
            
            console.log('🔄 Consommations transformées:', this.consommations.length, 'items');
            
          } else {
            const error = await response.json().catch(() => ({ error: 'Unknown error' }));
            console.warn('❌ Erreur API:', response.status, error);
            this.consommations = [];
          }
        }
        // ... autres onglets ...
        
      } catch (error) {
        console.warn("❌ Erreur fetchTabData:", error);
        this.consommations = [];
      } finally {
        this._fetchingTab = null;
      }
    },
    

    async addConsumption() {
      try {
        if (!this.id) {
          alert("⚠️ Veuillez sélectionner une bande d'abord");
          return;
        }

        const durationWeeks = Math.max(1, Math.ceil((parseInt(this.band?.duree_jours, 10) || 42) / 7));
        const startDate = this.band?.date_arrivee ? new Date(this.band.date_arrivee) : null;
        if (!startDate) {
          alert('❌ Date d\'arrivée manquante pour calculer la semaine');
          return;
        }
        
        const isEditing = !!this.editingConsumptionId;
        
        // Validation
        if (!this.consumptionForm.type || this.consumptionForm.type.trim() === '') {
          alert("❌ Le type d'aliment est obligatoire");
          return;
        }
        
        const kgValue = parseFloat(this.consumptionForm.kg);
        if (!this.consumptionForm.kg || isNaN(kgValue) || kgValue <= 0) {
          alert("❌ La quantité (kg) doit être un nombre supérieur à 0");
          return;
        }

        // Calcul semaine de production (1-indexed)
        const dateStr = this.consumptionForm.date || new Date().toISOString().split('T')[0];
        const consumptionDate = new Date(dateStr);
        const deltaDays = Math.floor((consumptionDate - startDate) / (1000 * 60 * 60 * 24));
        if (deltaDays < 0) {
          alert('❌ La date de consommation est avant la date d\'arrivée');
          return;
        }
        const weekNumber = Math.floor(deltaDays / 7) + 1;
        if (weekNumber > durationWeeks) {
          alert(`❌ La semaine ${weekNumber} dépasse la durée prévue (${durationWeeks} sem.)`);
          return;
        }

        // Interdire plusieurs consommations la même semaine côté frontend (sauf même enregistrement)
        const existingWeek = this.consommations.find(c => c.semaine_production === weekNumber && c.id !== this.editingConsumptionId);
        if (existingWeek) {
          alert(`❌ Une consommation existe déjà pour la semaine ${weekNumber}. Supprimez-la ou modifiez-la avant d'ajouter.`);
          return;
        }
        
        // Préparer les données exactement comme l'API les attend
        const payload = {
          bande_id: parseInt(this.id),
          date: dateStr,
          type_aliment: this.consumptionForm.type.trim(),
          aliment_kg: kgValue,
          cout_aliment: parseFloat(this.consumptionForm.cout || 0),
          eau_litres: 0,
          semaine_production: weekNumber,
          poids_moyen_actuel: this.consumptionForm.poids || null
        };
        
        console.log('📤 Envoi à l\'API:', payload);
        
        const url = isEditing
          ? `http://localhost:5000/consommations/${this.editingConsumptionId}`
          : 'http://localhost:5000/consommations/';
        const method = isEditing ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
          method,
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          credentials: 'include',
          body: JSON.stringify(payload)
        });
        
        console.log('📥 Réponse API:', response.status, response.statusText);
        
        let responseData;
        try {
          responseData = await response.json();
        } catch (e) {
          responseData = { error: 'Réponse non valide' };
        }
        
        if (response.ok) {
          const updated = {
            id: responseData.id,
            date: responseData.date,
            type: responseData.type_aliment,
            kg: responseData.aliment_kg,
            cout: responseData.cout_aliment,
            bande_id: responseData.bande_id,
            semaine_production: responseData.semaine_production || weekNumber
          };
          
          if (isEditing) {
            const idx = this.consommations.findIndex(c => c.id === this.editingConsumptionId);
            if (idx !== -1) {
              this.consommations.splice(idx, 1, updated);
            }
            alert('✅ Consommation mise à jour');
          } else {
            this.consommations.unshift(updated);
            alert('✅ Consommation ajoutée avec succès !');
          }

          this.resetConsumptionForm();
          this.updateTrendsFromData();
          this.calculateKPI();
          console.log('Consommation sauvegardée:', updated);
        } else {
          const errorMsg = responseData.error || `Erreur ${response.status}`;
          console.error('❌ Erreur détaillée:', { 
            status: response.status, 
            error: errorMsg,
            payload 
          });
          alert(`❌ Erreur : ${errorMsg}`);
        }
        
      } catch (error) {
        console.error('💥 Erreur complète:', error);
        
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
          alert('🌐 Erreur de connexion au serveur');
        } else {
          alert(`💥 Erreur : ${error.message}`);
        }
      }
    },

    startEditConsumption(cons) {
      this.editingConsumptionId = cons.id;
      this.consumptionForm = {
        date: cons.date,
        type: cons.type,
        kg: cons.kg,
        cout: cons.cout,
        poids: this.band?.poids_moyen_actuel || null
      };
    },

    resetConsumptionForm() {
      this.editingConsumptionId = null;
      this.consumptionForm = {
        date: new Date().toISOString().slice(0, 10),
        type: '',
        kg: 0,
        cout: 0,
        poids: null
      };
    },

    async deleteConsumption(cons) {
      const confirmDelete = confirm('Supprimer cette consommation ?');
      if (!confirmDelete) return;

      try {
        const response = await fetch(`http://localhost:5000/consommations/${cons.id}`, {
          method: 'DELETE',
          credentials: 'include'
        });

        if (response.ok) {
          this.consommations = this.consommations.filter(c => c.id !== cons.id);
          if (this.editingConsumptionId === cons.id) {
            this.resetConsumptionForm();
          }
          this.updateTrendsFromData();
          this.calculateKPI();
          alert('🗑️ Consommation supprimée');
        } else {
          const err = await response.json().catch(() => ({ error: 'Erreur inconnue' }));
          alert(`❌ Erreur : ${err.error || response.statusText}`);
        }
      } catch (error) {
        console.error('💥 Erreur suppression:', error);
        alert('🌐 Erreur de connexion au serveur');
      }
    },

    async sendMessage() {
      if (!this.chatInput.trim()) return;
      
      const userMessage = this.chatInput;
      this.messages.push({ from: "user", text: userMessage });
      this.chatInput = "";
      
      try {
        setTimeout(() => {
          const responses = [
            `Pour la bande "${this.band?.nom_bande || ''}", que souhaitez-vous savoir ?`,
            "Je peux vous aider à analyser les performances de votre bande.",
            "Consultez les prédictions pour voir les tendances futures."
          ];
          const randomResponse = responses[Math.floor(Math.random() * responses.length)];
          this.messages.push({ from: "bot", text: randomResponse });
        }, 1000);
      } catch (e) {
        this.messages.push({ from: "bot", text: "Erreur de connexion" });
      }
    },

    selectTab(tab) {
      this.activeTab = tab;
      this.fetchTabData(tab);
    },

    showSearchBande() {
      console.log("Recherche de bandes");
    },

    openSettings() {
      console.log("Ouverture des paramètres");
    },
    
    formatDate(dateString) {
      if (!dateString) return '—';
      const date = new Date(dateString);
      return date.toLocaleDateString('fr-FR');
    },
    
    generatePredictions() {
      const days = parseInt(this.predictionDays);
      this.predictions = [];
      this.totalPredictedProfit = 0;
      
      // Utiliser les données réelles de la bande
      const currentWeight = this.band?.poids_moyen_initial || 2.0;
      const currentAnimals = this.currentAnimals;
      const totalCostToDate = this.totalCost;
      
      let totalProfit = 0;
      const today = new Date();
      
      for (let i = 1; i <= days; i++) {
        const date = new Date(today);
        date.setDate(date.getDate() + i);
        const dateStr = date.toISOString().slice(0, 10);
        
        // Utiliser les données de la bande pour des prédictions plus réalistes
        const weightIncrease = this.calculateWeightIncrease(i);
        const predictedWeight = currentWeight * (1 + weightIncrease);
        
        // Baser la consommation sur la moyenne historique
        const avgConsumption = this.calculateAverageConsumption();
        const predictedConsumption = avgConsumption * (1 + (i * 0.02)); // +2% par jour
        
        const predictedCost = predictedConsumption * this.getAverageCostPerKg();
        const predictedValue = predictedWeight * this.getPricePerKg() * currentAnimals;
        const predictedMargin = predictedValue - (totalCostToDate + predictedCost);
        
        this.predictions.push({
          jour: i,
          date: dateStr,
          poids: predictedWeight,
          consommation: predictedConsumption,
          cout: predictedCost,
          marge: predictedMargin
        });
        
        totalProfit += predictedMargin;
      }
      
      this.totalPredictedProfit = totalProfit;
      this.roi = (totalProfit / (totalCostToDate || 1)) * 100 || 0;
      this.optimalSellingDate = this.findOptimalSellingDate();
    },
    
    calculateWeightIncrease(day) {
      // Basé sur le modèle sélectionné
      switch(this.predictionModel) {
        case 'exponentiel': return 0.04;
        case 'saisonnier': return 0.03;
        default: return 0.035; // linéaire
      }
    },

    calculateAverageConsumption() {
      if (this.consommations.length === 0) return 0;
      const totalKg = this.consommations.reduce((sum, c) => sum + (c.kg || 0), 0);
      return totalKg / this.consommations.length;
    },

    getAverageCostPerKg() {
      if (this.consommations.length === 0) return 1.8;
      const totalCost = this.consommations.reduce((sum, c) => sum + (c.cout || 0), 0);
      const totalKg = this.consommations.reduce((sum, c) => sum + (c.kg || 0), 0);
      return totalKg > 0 ? totalCost / totalKg : 1.8;
    },

    getPricePerKg() {
      // Prix de vente moyen basé sur la race
      return this.band?.race === 'Poulet de chair' ? 3.5 : 4.0;
    },

    findOptimalSellingDate() {
      if (this.predictions.length === 0) return '';
      // Trouver le jour avec la marge maximale
      const maxMarginDay = this.predictions.reduce((max, p) => 
        p.marge > max.marge ? p : max, this.predictions[0]);
      return maxMarginDay.date;
    },
    
    // Utility methods
    getTrendClass(type) {
      const trendValue = this.trends[type];
      if (typeof trendValue !== 'number') return 'neutral';
      if (trendValue > 0) return 'positive';
      if (trendValue < 0) return 'negative';
      return 'neutral';
    },
    
    getMarginClass(margin) {
      return margin > 0 ? 'positive' : margin < 0 ? 'negative' : 'neutral';
    },
    
    getProfitClass(profit) {
      return profit > 0 ? 'positive' : profit < 0 ? 'negative' : 'neutral';
    },
    
    getROIClass(roi) {
      return roi > 15 ? 'good' : roi > 5 ? 'medium' : 'low';
    }
  },
  
  mounted() {
    console.log('Component mounted');
    
    this.fetchBand().then(() => {
      // Une fois la bande chargée, charger les consommations
      this.fetchTabData(this.activeTab);
    });
  },
  
  beforeUnmount() {
    // Rien à nettoyer : les composants enfants gèrent leurs propres graphiques
  }
};
</script>

<style src="../../css/chart.css" type="text/css"></style>
<style src="../../css/band.css" type="text/css"></style>