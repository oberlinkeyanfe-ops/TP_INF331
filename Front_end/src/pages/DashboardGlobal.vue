<template>
  <div class="dashboard-container theme-green stacked">
    <!-- Header Section -->
    <header class="dash-header">
    
      <div class="header-content">
        

        <div class="header-left">
          <h1>Vue d'Ensemble & Analyse IA</h1>
          <p class="subtitle">Pilotage, comparaisons et prédictions de performance</p>
        </div>
        
        <div class="header-actions">
          <div class="filter-wrapper">
            <div class="select-wrapper">
              <i class="fas fa-calendar-alt select-icon"></i>
              <select v-model="period" @change="fetchWithPeriod" class="custom-select">
                <option value="all">Tout l'historique</option>
                <option value="30">30 derniers jours</option>
                <option value="90">90 derniers jours</option>
                <option value="365">Cette année</option>
                <option value="custom">Personnalisé</option>
              </select>
            </div>
          </div>

          <div v-if="period === 'custom' || customOpen" class="date-range-picker">
            <input type="date" v-model="startDate" class="custom-input" />
            <span class="separator">➜</span>
            <input type="date" v-model="endDate" class="custom-input" />
            <button class="btn-icon" @click="fetchWithCustom" title="Appliquer">OK</button>
          </div>

          <button class="btn btn-primary" @click="fetchNow" :disabled="loadingDashboard">
            <i class="fas fa-sync-alt" :class="{'spin': loadingDashboard}"></i>
            {{ loadingDashboard ? 'Analyse en cours...' : 'Actualiser' }}
          </button>
        </div>
      </div>
    </header>

    <div v-if="fetchError" class="error-banner">
      <i class="fas fa-exclamation-circle"></i> <span>{{ fetchError }}</span>
      <button @click="retryFetch">Réessayer</button>
    </div>

    <div v-if="!loadingDashboard && !fetchError" class="main-grid">
      
      <!-- 1. KPI Row (12 columns) -->
      <div class="kpi-section">
        <div class="kpi-card">
          <div class="kpi-icon bg-green-100 text-green-600">📊</div>
          <div>
            <div class="kpi-value">{{ dashboardData?.bandes_actives ?? 0 }}</div>
            <div class="kpi-label">Bandes Actives</div>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon bg-emerald-100 text-emerald-600">🐔</div>
          <div>
            <div class="kpi-value">{{ formatNumber(dashboardData?.total_animaux) }}</div>
            <div class="kpi-label">Sujets Totaux</div>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon bg-orange-100 text-orange-600">📉</div>
          <div>
            <div class="kpi-value">{{ formatNumber(dashboardData?.nb_morts) }}</div>
            <div class="kpi-label">Mortalité Cumulée</div>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon bg-teal-100 text-teal-600">💰</div>
          <div>
            <div style="display:flex;  align-items:center;">
              <label style="font-size:12px; color:#6b7280;">Bande</label>
              <select v-model="selectedCoutBandId" class="custom-select" @change="onCoutBandChange" style="width: 7vw;">
                <option value="" disabled v-if="!coutsData.length">Chargement...</option>
                <option v-for="c in coutsData" :key="c.bande_id" :value="c.bande_id">{{ c.nom_bande }}</option>
              </select>
            </div>
            <div>
              <div class="kpi-value">{{ formatCurrency((selectedBandCost && selectedBandCost.cout_total) || 0) }}</div>
              <div class="kpi-label">Dépenses par bande</div>
            </div>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon bg-blue-100 text-blue-600">📈</div>
          <div>
            <div class="kpi-value">{{ globalPerformance !== null ? (globalPerformance + '%') : '—' }}</div>
            <div class="kpi-label">Performance Globale</div>
          </div>
        </div>
      </div>

      <!-- 2. Smart Insights / Predictions (12 columns) -->
      <div class="grid-col-12 insights-section">
        <div class="section-title"><i class="fas fa-robot"></i> Analyse & Recommandations</div>
        <div class="insights-grid">
          
          <!-- Recommendation Aliment -->
          <div class="insight-card best-practice">
            <div class="insight-icon"><i class="fas fa-utensils"></i></div>
            <div class="insight-content">
              <h4>Alimentation Optimale</h4>
              <p v-if="bestBandDetails?.top_aliment?.type_aliment">
                Le type <strong>{{ bestBandDetails.top_aliment.type_aliment }}</strong> offre le meilleur rendement actuel (basé sur la bande <em>{{ bestBand?.nom_bande }}</em>).
              </p>
              <p v-else class="text-muted">Données insuffisantes pour recommander un aliment.</p>
              <div class="insight-tag">Conseil Performance</div>
            </div>
          </div>

          <!-- Alert Sanitaire -->
          <div class="insight-card warning" v-if="highMortalityBands.length > 0">
            <div class="insight-icon"><i class="fas fa-first-aid"></i></div>
            <div class="insight-content">
              <h4>Attention Sanitaire</h4>
              <p>
                <strong>{{ highMortalityBands.length }} bande(s)</strong> dépassent le seuil d'alerte de 5% de mortalité. 
                <span v-if="treatmentStats?.efficacite_moyenne">L'efficacité moyenne des traitements est de {{ Math.round(treatmentStats.efficacite_moyenne * 10) / 10 }}/5.</span>
              </p>
              <div class="insight-tag alert">Action requise</div>
            </div>
          </div>
          <div class="insight-card success" v-else>
            <div class="insight-icon"><i class="fas fa-check-circle"></i></div>
            <div class="insight-content">
              <h4>État Sanitaire Stable</h4>
              <p>Aucune dérive majeure de mortalité détectée sur les bandes actives.</p>
              <div class="insight-tag ok">Situation saine</div>
            </div>
          </div>

          <!-- Best treatment per disease (based on top-performing bands) -->
          <div class="insight-card best-treatment">
            <div class="insight-icon"><i class="fas fa-pills"></i></div>
            <div class="insight-content">
              <h4>Meilleur produit par pathologie (top bandes)</h4>
              <p v-if="!bestProductsByDisease.length" class="muted">Aucune donnée de traitements disponibles pour les bandes performantes.</p>
              <ul v-else class="treatment-list">
                <li v-for="item in bestProductsByDisease" :key="item.disease">
                  <strong>{{ item.disease }}</strong> —
                  <span class="prod">{{ item.product }}</span>
                  <small class="muted">{{ item.avgEffic !== null ? `(efficacité moyenne ${item.avgEffic}%)` : `(utilisé ${item.count} fois)` }}</small>
                </li>
              </ul>
              <div class="insight-tag info">Analyse traitements</div>
            </div>
          </div>

        </div>
      </div>
      
      <!-- 3. MAIN CHARTS SECTION (2/3 + 1/3 layout) -->
      
      <!-- Left Column (2/3 width on desktop) -->
      <div class="grid-col-8 main-charts-container">
        
        <!-- Top Row: Best Band Highlight (1/2) & Weight Trends (1/2) -->
        <div class="sub-grid-2">
          <!-- Best Band Highlight (Chart 1) -->
          <div class="chart-card highlight-card" v-if="bestBand">
            <div class="card-header">
              <h3>🏆 Modèle de Réussite</h3>
              <span class="badge">Top Rentabilité</span>
            </div>
            <div class="highlight-body">
              <div class="gauge-area">
                <PerformanceGauge :score="bestBand?.performancePercent ?? 0" />
                <div class="gauge-title">{{ bestBand?.nom_bande }}</div>
              </div>
              <div class="metrics-area">
                <div class="metric-row">
                  <span>IC Moyen (Est.)</span>
                  <strong>{{ bestBandDetails?.ic_moyen || '—' }}</strong>
                </div>
                <div class="metric-row">
                  <span>Survie</span>
                  <strong class="text-green-600">{{ bestBandDetails?.taux_survie }}%</strong>
                </div>
                <div class="metric-row">
                  <span>Conso/Sujet</span>
                  <strong>{{ bestBand.consommation_par_animal }} kg</strong>
                </div>
              </div>
            </div>
          </div>

          <!-- Weight Trends (Chart 2) -->
          <div class="chart-card">
            <div class="card-header">
              <h3>📈 Courbe de Croissance</h3>
              <p>Poids moyen (kg) vs Semaine</p>
            </div>
            <div class="chart-container">
              <div class="chart-header-inline" style="display:flex;align-items:center;gap:12px;margin-bottom:10px;">
                <label style="font-weight:600;color:#6b7280;">Bande</label>
                <select v-model="selectedGrowthBandId" @change="onSelectGrowthBand" class="custom-select" style="min-width:200px;padding:6px;border-radius:8px;border:1px solid var(--border);">
                  <option value="">Toutes les bandes (moyenne)</option>
                  <option v-for="b in bandsForSelector" :key="b.bande_id || b.id" :value="b.bande_id || b.id">{{ b.nom_bande || b.nom_bande }}</option>
                </select>
                <div style="margin-left:auto;color:var(--muted);font-size:0.9rem">Affiche la courbe pour la bande sélectionnée</div>
              </div>

              <GlobalTrendsLine :trendData="growthTrendData" color="#10b981" />
              <div v-if="growthLoading" style="color:var(--muted); font-size:0.95rem;margin-top:8px">Chargement…</div>
            </div>
          </div>

          <!-- Consumption Bar Chart (Chart 3) -->
        <div class="chart-card">
          <div class="card-header">
            <h3>🍽️ Efficacité Alimentaire</h3>
            <p>Comparaison Consommation Moyenne / Sujet (kg)</p>
          </div>
          <div class="chart-container ">
            <GlobalComparisonBar :performanceData="performanceData" metric="consommation_par_animal" />
          </div>
        </div>

        <div class="chart-card">
          <div class="card-header">
            <h3>💸 Structure des Coûts</h3>
          </div>
          <div class="chart-container custom-financials">
             <div v-if="coutsData.length === 0" class="empty-mini">Pas de données financières</div>
             <div v-else class="financial-list">
                <div v-for="bande in coutsData.slice(0, 5)" :key="bande.bande_id" class="fin-item">
                  <div class="fin-header">
                    <span class="fin-name">{{ bande.nom_bande }}</span>
                    <span class="fin-total">{{ formatCurrency(bande.cout_total) }}</span>
                  </div>
                  <div class="fin-bar-bg">
                    <div class="fin-bar-segment feed" :style="{width: getPercent(bande.cout_aliment, bande.cout_total) + '%'}" title="Aliment"></div>
                    <div class="fin-bar-segment treat" :style="{width: getPercent(bande.cout_traitements, bande.cout_total) + '%'}" title="Traitements"></div>
                    <div class="fin-bar-segment other" :style="{width: getPercent(bande.cout_depenses, bande.cout_total) + '%'}" title="Autres"></div>
                  </div>
                  <div class="fin-legend-mini">
                    <span class="dot feed"></span> Alim
                    <span class="dot treat"></span> Soins
                    <span class="dot other"></span> Autre
                  </div>
                </div>
             </div>
          </div>
        </div>

        <!-- Mortality Alerts (Chart 5) -->
        <div class="chart-card mt-4">
          <div class="card-header">
            <h3>⚠️ Alertes Mortalité</h3>
          </div>
          <div class="chart-container compact">
            <GlobalMortalityBar :performanceData="performanceData" />
          </div>
        </div>

         <!-- Survival Donut (Chart 6) -->
         <div class="chart-card mt-4">
          <div class="card-header">
            <h3>❤️ Survie Globale</h3>
          </div>
          <div class="chart-container compact">
            <GlobalSurvivalDonut :performanceData="performanceData" />
          </div>
        </div>

        
        </div>

        
      </div>

      

      <!-- 4. Detailed Comparative Analysis Table (12 columns) -->
      <div class="grid-col-12 mt-4">
        <div class="chart-card table-card">
          <div class="card-header table-header">
            <div>
              <h3>📋 Analyse Comparative Détaillée</h3>
              <p>Classement et filtrage de toutes les bandes</p>
            </div>
            <div class="table-controls">
              <input type="text" v-model="tableSearch" placeholder="Rechercher une bande..." class="search-input" />
              <select v-model="tableSort" class="sort-select">
                <option value="performance">Trier par Performance</option>
                <option value="mortalite_desc">Mortalité (Haute → Basse)</option>
                <option value="mortalite_asc">Mortalité (Basse → Haute)</option>
                <option value="gains">Rentabilité Est.</option>
              </select>
            </div>
          </div>
          
          <div class="table-responsive">
            <table class="analysis-table">
              <thead>
                <tr>
                  <th>Bande</th>
                  <th>Statut</th>
                  <th>Sujets</th>
                  <th>Mortalité</th>
                  <th>Conso/Sujet</th>
                  <th>Coûts (Est.)</th>
                  <th>Score Perf.</th>
                  <th>Action Suggérée</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="bande in filteredTableData" :key="bande.bande_id">
                  <td class="fw-bold">{{ bande.nom_bande }}</td>
                  <td><span class="status-badge" :class="bande.statut">{{ bande.statut }}</span></td>
                  <td>{{ bande.nombre_animaux }}</td>
                  <td>
                    <div class="progress-cell">
                      <span>{{ bande.taux_mortalite }}%</span>
                      <div class="progress-bar-mini">
                        <div class="fill" :class="getMortalityClass(bande.taux_mortalite)" :style="{width: Math.min(bande.taux_mortalite * 5, 100) + '%'}"></div>
                      </div>
                    </div>
                  </td>
                  <td>{{ bande.consommation_par_animal }} kg</td>
                  <td>{{ formatCurrency(bande.gains) }}</td>
                  <td>
                    <div class="score-circle" :style="{borderColor: getScoreColor(bande.score)}">{{ getBandScoreDisplay(bande) }}</div>
                  </td>
                  <td>
                    <span class="recommendation-text" :class="getRecommendationClass(bande)">
                      {{ getRecommendation(bande) }}
                    </span>
                  </td>
                </tr>
                <tr v-if="filteredTableData.length === 0">
                  <td colspan="8" class="text-center py-4 text-muted">Aucune bande trouvée.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

    </div>

    <!-- Empty State -->
    <div v-else-if="isEmpty && !loadingDashboard" class="empty-dashboard">
      <div class="empty-icon">🌱</div>
      <h3>Aucune donnée pour cette période</h3>
      <p>Commencez par créer des bandes et saisir des données.</p>
    </div>
  </div>
</template>

<script>
import { api } from '../services/api.js';
import GlobalComparisonBar from './charts/GlobalComparisonBar.vue';
import GlobalMortalityBar from './charts/GlobalMortalityBar.vue';
import GlobalTrendsLine from './charts/GlobalTrendsLine.vue';
import GlobalGainsBar from './charts/GlobalGainsBar.vue';
import GlobalSurvivalDonut from './charts/GlobalSurvivalDonut.vue';
import PerformanceGauge from './charts/PerformanceGauge.vue';

export default {
  name: 'DashboardGlobal',
  components: { 
    GlobalComparisonBar, 
    GlobalMortalityBar, 
    GlobalTrendsLine, 
    GlobalGainsBar, 
    GlobalSurvivalDonut, 
    PerformanceGauge 
  },
  data() {
    return {
      dashboardData: null,
      performanceData: [],
      coutsData: [],
      selectedCoutBandId: null,
      treatmentStats: null,
      loadingDashboard: false,
      fetchError: null,
      period: 'all',
      customOpen: false,
      startDate: null,
      endDate: null,
      bestBand: null,
      bestBandDetails: null,
      tableSearch: '',
      tableSort: 'performance',
      avgGrowthRate: 0,
      estWeeksToTarget: 0,
      globalPerformance: null,

      // Best treatments per disease (computed from top-performing bands)
      bestProductsByDisease: [],
      treatmentProductDiseases: {
        'Baytril': ['salmonellose','colibacillose','entérite'],
        'Lévomycétine': ['entérite','respiratoire'],
        'Dithrim': ['respiratoire','entérite'],
        'Furazolidone': ['entérite'],
        'Tétracycline': ['respiratoire','digestif'],
        'Biomycine': ['croissance','prévention'],
        'Sulfadimezin': ['coccidiose','respiratoire','typhoïde'],
        'Chlortétracycline': ['coccidiose','pneumonie','mycoplasmose']
      },

      // Growth chart per-band
      selectedGrowthBandId:'',
      growthLabels: [],
      growthSeries: [],
      growthLoading: false
    };
  },
  watch: {
    // When coutsData is loaded, default to first band if none selected
    coutsData(newVal) {
      if ((!this.selectedCoutBandId || this.selectedCoutBandId === null) && Array.isArray(newVal) && newVal.length) {
        this.selectedCoutBandId = newVal[0].bande_id;
      }
    }
  },
  computed: {
    isEmpty() {
      return (!this.dashboardData || Object.keys(this.dashboardData).length === 0) && 
             (!this.performanceData || this.performanceData.length === 0);
    },
    totalCoutsGlobal() {
      if (!this.coutsData) return 0;
      return this.coutsData.reduce((acc, curr) => acc + (curr.cout_total || 0), 0);
    },
    // Selected band's cost details used by the KPI selector
    selectedBandCost() {
      try {
        if (!this.coutsData || !this.coutsData.length) return null;
        if (!this.selectedCoutBandId) return this.coutsData[0];
        return this.coutsData.find(c => String(c.bande_id) === String(this.selectedCoutBandId)) || null;
      } catch (e) { return null; }
    },
    highMortalityBands() {
      return this.performanceData.filter(b => b.taux_mortalite > 5);
    },
    filteredTableData() {
      let data = [...this.performanceData];
      
      // Filter
      if (this.tableSearch) {
        const q = this.tableSearch.toLowerCase();
        data = data.filter(b => b.nom_bande.toLowerCase().includes(q));
      }

      // Sort
      data.sort((a, b) => {
        if (this.tableSort === 'performance') return (b.score || 0) - (a.score || 0);
        if (this.tableSort === 'mortalite_desc') return b.taux_mortalite - a.taux_mortalite;
        if (this.tableSort === 'mortalite_asc') return a.taux_mortalite - b.taux_mortalite;
        if (this.tableSort === 'gains') return b.gains - a.gains;
        return 0;
      });

      return data;
    },
    // Bands available for the growth selector (prefer performanceData, else coutsData)
    bandsForSelector() {
      if (this.performanceData && this.performanceData.length) return this.performanceData;
      if (this.coutsData && this.coutsData.length) return this.coutsData;
      return [];
    },
    // Growth trend to feed the GlobalTrendsLine: per-band if selected, else aggregated dashboard weight_trend
    growthTrendData() {
      if (this.growthSeries && this.growthSeries.length) {
        return this.growthLabels.map((lbl, idx) => ({ week: Number(lbl.replace(/^S/, '')) || idx + 1, mean_weight: this.growthSeries[idx] || 0 }));
      }
      return this.dashboardData?.weight_trend || [];
    }
  },
  methods: {

    async computeBestProductsByDisease() {
      this.bestProductsByDisease = [];
      try {
        const bands = (this.performanceData || []).filter(b => typeof b.score === 'number').sort((a, b) => (b.score || 0) - (a.score || 0)).slice(0, 3);
        if (!bands.length) return;
        const prodStats = {};
        for (const b of bands) {
          try {
            const resp = await api.get(`/traitements/bande/${b.bande_id}`);
            const treatments = Array.isArray(resp) ? resp : (resp.traitements || []);
            for (const t of treatments) {
              const prod = (t.produit || t.produit || '').trim();
              if (!prod) continue;
              const eff = (t.efficacite != null && !isNaN(Number(t.efficacite))) ? Number(t.efficacite) : null;
              if (!prodStats[prod]) prodStats[prod] = { sumE: 0, cntE: 0, cnt: 0 };
              if (eff !== null) { prodStats[prod].sumE += eff; prodStats[prod].cntE += 1; }
              prodStats[prod].cnt += 1;
            }
          } catch (e) {
            console.warn('Failed fetch treatments for band', b, e);
          }
        }

        const diseaseMap = {};
        for (const prod of Object.keys(prodStats)) {
          const stat = prodStats[prod];
          const avg = stat.cntE ? (stat.sumE / stat.cntE) : null;
          const count = stat.cnt;
          const diseases = (this.treatmentProductDiseases && this.treatmentProductDiseases[prod]) ? this.treatmentProductDiseases[prod] : [];
          if (!diseases.length) {
            const d = 'Général';
            diseaseMap[d] = diseaseMap[d] || [];
            diseaseMap[d].push({ product: prod, avgEffic: avg, count });
          } else {
            for (const d of diseases) {
              diseaseMap[d] = diseaseMap[d] || [];
              diseaseMap[d].push({ product: prod, avgEffic: avg, count });
            }
          }
        }

        const result = [];
        for (const d of Object.keys(diseaseMap)) {
          const candidates = diseaseMap[d];
          candidates.sort((a, b) => {
            if (a.avgEffic === null && b.avgEffic !== null) return 1;
            if (b.avgEffic === null && a.avgEffic !== null) return -1;
            if (a.avgEffic !== null && b.avgEffic !== null) {
              if (b.avgEffic !== a.avgEffic) return b.avgEffic - a.avgEffic;
            }
            return b.count - a.count;
          });
          const win = candidates[0];
          result.push({ disease: d, product: win.product, avgEffic: win.avgEffic !== null ? Math.round(win.avgEffic * 100) / 100 : null, count: win.count });
        }

        this.bestProductsByDisease = result.sort((a,b) => a.disease.localeCompare(b.disease));
      } catch (e) {
        console.warn('computeBestProductsByDisease error', e);
        this.bestProductsByDisease = [];
      }
    },
    onCoutBandChange() {
      // no-op for now — computed selectedBandCost will reflect selection
    },
    formatNumber(num) { return num ? num.toLocaleString('fr-FR') : '0'; },
    formatCurrency(num) { return num ? num.toLocaleString('fr-FR', { style: 'currency', currency: 'XAF' }) : '0 FCFA'; },
    getPercent(val, total) { return (!total || total === 0) ? 0 : Math.round((val / total) * 100); },

    applyLocalPerformanceMap() {
      try {
        const raw = localStorage.getItem('band_performance_map');
        if (!raw) {
          console.log('applyLocalPerformanceMap: no map in localStorage');
          return;
        }
        const map = JSON.parse(raw);
        if (!map || typeof map !== 'object') return;
        console.log('applyLocalPerformanceMap: applying map', map);
        // Apply map to performanceData entries
        this.performanceData = (this.performanceData || []).map(b => {
          const id = Number(b.bande_id || b.bandeId || b.id);
          if (!id) return b;
          // prefer explicit numeric mapping
          if (Object.prototype.hasOwnProperty.call(map, String(id)) && typeof map[String(id)] === 'number') {
            const val = Number(map[String(id)]);
            return { ...b, performance_percent: val, score: val, performance_status: null };
          }
          // also accept components_{id}
          const compKey = `components_${id}`;
          if (Object.prototype.hasOwnProperty.call(map, compKey) && map[compKey]) {
            const subs = Object.values(map[compKey]).filter(v => typeof v === 'number');
            const avg = subs.length ? Math.round(subs.reduce((a, c) => a + c, 0) / subs.length) : null;
            if (avg !== null) return { ...b, performance_percent: avg, score: avg, performance_status: null };
          }
          // check for status_{id}
          const statusKey = `status_${id}`;
          if (Object.prototype.hasOwnProperty.call(map, statusKey)) {
            return { ...b, performance_percent: null, score: null, performance_status: map[statusKey] };
          }
          return b;
        });
        // recompute best band from updated data
        const sorted = [...this.performanceData].sort((a, b) => (b.score || 0) - (a.score || 0));
        this.bestBand = sorted[0];
        if (this.bestBand) this.bestBand.performancePercent = Math.round(this.bestBand.score || 0);
      } catch (e) {
        console.warn('applyLocalPerformanceMap failed', e);
      }
    },


    // Fetch and update growth data for selected band
    async onSelectGrowthBand() {
      const id = this.selectedGrowthBandId;
      if (!id) {
        this.growthLabels = [];
        this.growthSeries = [];
        this.calculateProjections();
        return;
      }

      try {
        this.growthLoading = true;
        const res = await api.get(`/animal-info/bande/${id}`);
        const infos = Array.isArray(res.animal_info) ? res.animal_info : [];
        infos.sort((a, b) => (a.semaine_production || 0) - (b.semaine_production || 0));
        this.growthLabels = infos.map(i => `S${i.semaine_production}`);
        this.growthSeries = infos.map(i => (typeof i.poids_moyen === 'number' ? i.poids_moyen : (i.poids_moyen ? Number(i.poids_moyen) : 0)));
        this.calculateProjections();
      } catch (e) {
        console.error('Erreur onSelectGrowthBand:', e);
        this.growthLabels = [];
        this.growthSeries = [];
      } finally {
        this.growthLoading = false;
      }
    },

    
    getMortalityClass(val) {
      if (val < 2) return 'bg-success';
      if (val < 5) return 'bg-warning';
      return 'bg-danger';
    },
    getScoreColor(score) {
      if (typeof score !== 'number') return '#9ca3af';
      if (score > 80) return '#10b981';
      if (score > 50) return '#f59e0b';
      return '#ef4444';
    },
    getBandScoreDisplay(bande) {
      if (bande && bande.performance_status === 'no_consumption') return '∞';
      if (bande && typeof bande.score === 'number') return Math.round(bande.score * 10) / 10;
      return '—';
    },
    getRecommendation(bande) {
      if (bande.taux_mortalite > 5) return '🚨 Vérifier Protocole Sanitaire';
      if (bande.consommation_par_animal > 5 && bande.taux_mortalite < 2) return '📉 Optimiser Ration (Gaspillage?)';
      if (typeof bande.score === 'number' && bande.score > 80) return '⭐ Modèle à reproduire';
      return '✔️ Performance Standard';
    },
    getRecommendationClass(bande) {
      if (bande.taux_mortalite > 5) return 'text-danger';
      if (typeof bande.score === 'number' && bande.score > 80) return 'text-success';
      return 'text-muted';
    },

    async fetchDashboardGlobal() {
      this.loadingDashboard = true;
      this.fetchError = null;
      try {
        const qs = this.buildQueryString();
        
        // 1. Data Global
        let resp;
        try { resp = await api.get(`/dashboard/global-v2${qs}`); } 
        catch (e) { resp = await api.get(`/dashboard/${qs}`); }

        if (resp) {
          this.dashboardData = {
            bandes_actives: resp.bandes_actives ?? 0,
            total_animaux: resp.total_animaux ?? 0,
            nb_morts: resp.nb_morts ?? 0,
            weight_trend: resp.weight_trend || [],
            consommation_trend: resp.consommation_trend || []
          };
          this.performanceData = (resp.performance && Array.isArray(resp.performance)) ? resp.performance : [];
        }

        // 2. Perf fallback
        if (!this.performanceData || !this.performanceData.length) {
          try {
            const perf = await api.get(`/dashboard/performance/bandes${qs}`);
            this.performanceData = perf.performance || perf || [];
          } catch (e) { console.warn('Perf fallback failed'); }
        }
        console.log('Dashboard: performanceData after fetch', this.performanceData);

        // 2.5 Fetch authoritative performance map from backend and persist
        try {
          const mapResp = await api.get('/dashboard/performance/map');
          const mapObj = (mapResp && mapResp.band_performance_map) ? mapResp.band_performance_map : {};
          try { localStorage.setItem('band_performance_map', JSON.stringify(mapObj)); } catch (e) { /* ignore */ }
          console.log('Dashboard: fetched band_performance_map from backend', mapObj);
        } catch (e) {
          console.warn('Failed to fetch performance map from backend for dashboard', e);
        }

        // Apply local precomputed performance map if present (override server values)
        this.applyLocalPerformanceMap();


        // 3. Financials
        try {
          const coutsResp = await api.get(`/dashboard/couts/par_bande${qs}`);
          this.coutsData = coutsResp.couts_par_bande || [];
        } catch (e) { this.coutsData = []; }

        // 4. Treatments Stats (New)
        try {
          const treatResp = await api.get(`/traitements/statistiques`);
          this.treatmentStats = treatResp; // Expecting { efficacite_moyenne, ... }
        } catch (e) { this.treatmentStats = null; }

        // 5. Calculations
        this.computeScoresAndBestBand();
        this.calculateProjections();
        // 5.5 Compute best treatment per disease based on top-performing bands
        try { await this.computeBestProductsByDisease(); } catch (e) { console.warn('computeBestProductsByDisease failed', e); }

        // Set default growth band selector if none (prefer performanceData then coutsData)
        try {
          const source = (this.performanceData && this.performanceData.length) ? this.performanceData : (this.coutsData && this.coutsData.length ? this.coutsData : []);
          if (source.length && !this.selectedGrowthBandId) {
            // default to first band
            this.selectedGrowthBandId = source[0].bande_id || source[0].id || '';
            await this.onSelectGrowthBand();
          }
        } catch (e) { /* ignore */ }

        // 6. Fetch Best Band Details for Recommendation
        if (this.bestBand && this.bestBand.bande_id) {
          try {
            this.bestBandDetails = await api.get(`/dashboard/bande/details/${this.bestBand.bande_id}`);
          } catch (e) { console.warn(e); }
        }

        // Fetch global performance (weighted) and set KPI
        try {
          const gp = await api.get('/dashboard/performance/global');
          if (gp && gp.global_performance_percent !== undefined) this.globalPerformance = gp.global_performance_percent;
        } catch (e) { console.warn('Failed to fetch global performance', e); }

        // Listen for local storage perf map updates and re-apply if they occur
        if (!this._storageListenerAdded) {
          window.addEventListener('storage', (ev) => {
            if (ev.key === 'band_performance_map') this.applyLocalPerformanceMap();
          });
          this._storageListenerAdded = true;
        }

      } catch (err) {
        console.error(err);
        this.fetchError = "Erreur de chargement. Vérifiez votre connexion.";
      } finally {
        this.loadingDashboard = false;
      }
    },

    // Fetch and update growth data for selected band
    async onSelectGrowthBand() {
      const id = this.selectedGrowthBandId;
      if (!id) {
        this.growthLabels = [];
        this.growthSeries = [];
        this.calculateProjections();
        return;
      }

      try {
        this.growthLoading = true;
        const res = await api.get(`/animal-info/bande/${id}`);
        const infos = Array.isArray(res.animal_info) ? res.animal_info : [];
        infos.sort((a, b) => (a.semaine_production || 0) - (b.semaine_production || 0));
        this.growthLabels = infos.map(i => `S${i.semaine_production}`);
        this.growthSeries = infos.map(i => (typeof i.poids_moyen === 'number' ? i.poids_moyen : (i.poids_moyen ? Number(i.poids_moyen) : 0)));
        this.calculateProjections();
      } catch (e) {
        console.error('Erreur onSelectGrowthBand:', e);
        this.growthLabels = [];
        this.growthSeries = [];
      } finally {
        this.growthLoading = false;
      }
    },


    buildQueryString() {
      const parts = [];
      if (this.period && this.period !== 'all' && this.period !== 'custom') parts.push(`period_days=${this.period}`);
      if (this.period === 'custom' && this.startDate) parts.push(`start=${this.startDate}`);
      if (this.period === 'custom' && this.endDate) parts.push(`end=${this.endDate}`);
      return parts.length ? `?${parts.join('&')}` : '';
    },

    fetchNow() { this.fetchDashboardGlobal(); },
    fetchWithPeriod() {
      if (this.period === 'custom') { this.customOpen = true; } 
      else { this.customOpen = false; this.startDate = null; this.endDate = null; this.fetchDashboardGlobal(); }
    },
    fetchWithCustom() { 
      if (!this.startDate || !this.endDate) return alert('Dates invalides');
      this.fetchDashboardGlobal(); 
    },
    retryFetch() { this.fetchDashboardGlobal(); },

    computeScoresAndBestBand() {
      if (!this.performanceData || !this.performanceData.length) { this.bestBand = null; return; }

      // Prefer server/client precomputed performance only — do not compute local fallback scores
      this.performanceData = this.performanceData.map(b => {
        if (typeof b.performance_percent === 'number') {
          return { ...b, score: b.performance_percent };
        }
        // mark score as unknown when server did not provide a value
        return { ...b, score: null };
      });

      // select among bands that have a numeric score
      const valid = (this.performanceData || []).filter(b => typeof b.score === 'number');
      if (!valid.length) { this.bestBand = null; return; }

      const sorted = [...valid].sort((a, b) => (b.score || 0) - (a.score || 0));
      this.bestBand = sorted[0];
      if (this.bestBand) this.bestBand.performancePercent = Math.round(this.bestBand.score || 0);

      // ensure growth selector options reflect current bands
      // no-op here; we will use a computed that picks from performanceData/coutsData
    },


    calculateProjections() {
      // Simple linear projection based on weight trend (use growthTrendData computed)
      const trends = this.growthTrendData || [];
      if (trends.length < 2) {
        this.avgGrowthRate = 0;
        return;
      }

      // Avg growth per week (last few points)
      const last = trends[trends.length - 1];
      const prev = trends[0]; // simplistic over total period
      const weeks = last.week - prev.week;
      if (weeks > 0) {
        this.avgGrowthRate = Math.round((last.mean_weight - prev.mean_weight) / weeks);
      }

      const targetWeight = 2500; // Example target for broilers
      if (last.mean_weight < targetWeight && this.avgGrowthRate > 0) {
        this.estWeeksToTarget = Math.ceil((targetWeight - last.mean_weight) / this.avgGrowthRate);
      } else {
        this.estWeeksToTarget = 0;
      }
    }
  },
  mounted() { this.fetchDashboardGlobal(); }
};
</script>

<style scoped>

html { font-size: 1px; }
/* Base Theme */
.theme-green {
  --primary: #10b981; --primary-dark: #059669; --primary-light: #d1fae5;
  --bg-page: #f0fdf4; --text-main: #064e3b; --text-sec: #374151; --border: #e5e7eb;
}
.dashboard-container {margin-top: 10vh; font-family: 'Inter', sans-serif; background-color: var(--bg-page); min-height: 100vh; padding: 18px; font-size: 1px; color: var(--text-sec); }

/* Header & Controls */
.dash-header { margin-bottom: 32px; }
.header-content { display: flex; justify-content: space-between; align-items: flex-end; flex-wrap: wrap; gap: 16px; }
.header-left h1 { font-size: 24px; font-weight: 800; color: var(--text-main); margin: 0; }
.subtitle { color: #6b7280; margin: 4px 0 0 0; font-size: 13px; }
.header-actions { display: flex; gap: 12px; background: white; padding: 8px 16px; border-radius: 50px; box-shadow: 0 2px 10px rgba(16, 185, 129, 0.1); }
.custom-select { border: none; background: transparent; font-weight: 600; color: var(--text-main); cursor: pointer; outline: none; }
.btn { border: none; padding: 6px 12px; border-radius: 16px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 6px; font-size: 13px; }
.btn-primary { background-color: var(--primary); color: white; box-shadow: 0 3px 4px rgba(16, 185, 129, 0.25); }
.spin { animation: spin 1s infinite linear; }
@keyframes spin { 100% { transform: rotate(360deg); } }
.filter-wrapper, .date-range-picker { display: flex; align-items: center; gap: 8px; }
.custom-input { padding: 4px 8px; border: 1px solid #e5e7eb; border-radius: 8px; }

/* Grid */
.main-grid { display: grid; grid-template-columns: repeat(12, 1fr); gap: 24px; }
.grid-col-12 { grid-column: span 12; } .grid-col-8 { grid-column: span 8; } .grid-col-4 { grid-column: span 4; }
.sub-grid-2 {width: 90vw;  display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 24px; align-items: stretch; grid-auto-rows: 1fr ; /* ensure equal-height columns */ }
@media (max-width: 1024px) { 
  .grid-col-8, .grid-col-4 { grid-column: span 12; }
  .header-content { flex-direction: column; align-items: flex-start; }
  .header-actions { border-radius: 12px; padding: 8px; box-shadow: none; background: none; width: 100%; flex-wrap: wrap; }
}
@media (max-width: 768px) { .sub-grid-2 { grid-template-columns: 1fr; } }


/* KPI */
.kpi-section { grid-column: span 12; display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px; margin-bottom: 6px; }
.kpi-card { background: white; padding: 16px; border-radius: 14px; display: flex; align-items: center; gap: 12px; box-shadow: 0 3px 4px -1px rgba(0,0,0,0.05); }
.kpi-icon { width: 44px; height: 44px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; }
.kpi-value { font-size: 18px; font-weight: 800; color: var(--text-main); }
.kpi-label { font-size: 12px; color: #6b7280; font-weight: 500; }

/* Insights Section */
.insights-section { margin-bottom: 8px; }
.section-title { font-size: 18px; font-weight: 700; color: var(--text-main); margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }
.insights-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }
.insight-card { background: white; padding: 12px; border-radius: 12px; display: flex; gap: 12px; border-left: 4px solid transparent; box-shadow: 0 2px 4px rgba(0,0,0,0.04); }
.insight-card.best-practice { border-color: #3b82f6; }
.insight-card.warning { border-color: #ef4444; background: #fef2f2; }
.insight-card.success { border-color: #10b981; }
.insight-card.prediction { border-color: #8b5cf6; }
.insight-icon { font-size: 20px; padding-top: 4px; }
.best-practice .insight-icon { color: #3b82f6; }
.warning .insight-icon { color: #ef4444; }
.success .insight-icon { color: #10b981; }
.prediction .insight-icon { color: #8b5cf6; }
.insight-content h4 { margin: 0 0 4px 0; font-size: 15px; font-weight: 700; color: var(--text-main); }
.insight-content p { margin: 0 0 8px 0; font-size: 13px; color: #4b5563; line-height: 1.4; }
.insight-tag { display: inline-block; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 10px; background: #e5e7eb; color: #374151; }
.insight-tag.alert { background: #fee2e2; color: #991b1b; }
.insight-tag.ok { background: #d1fae5; color: #065f46; }
.insight-tag.info { background: #ede9fe; color: #5b21b6; }
/* Treatment list (best products by disease) — larger, clearer text */
.treatment-list { margin: 8px 0 12px; padding: 0; list-style: none; }
.treatment-list li { font-size: 10px; line-height: 1.35; margin-bottom: 6px; color: var(--text-sec); }
.treatment-list .prod { font-size: 11px; font-weight: 700; margin-left: 6px; color: var(--text-main); }
.treatment-list small.muted { font-size: 13px; color: #6b7280; margin-left: 8px; }
/* Charts & Tables */
.chart-card { background: white; border-radius: 20px; padding: 24px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05); display: flex; flex-direction: column; height: 100%; }
.card-header { margin-bottom: 20px; }
.card-header h3 { font-size: 16px; font-weight: 700; color: var(--text-main); margin: 0; }
.chart-container { flex: 1; min-height: 180px; min-width: 20vw; position: relative; }
.chart-container.large { min-height: 300px; }
.chart-container.compact { min-height: 180px; }

/* Smaller layout for the wide consumption chart */
.full-width-chart { align-self: start; }
.full-width-chart .chart-container.large { min-height: 170px; max-height: 260px; }
.full-width-chart .chart-card { padding: 12px; }

/* Ensure chart-cards stretch to fill the grid row and keep consistent heights */
.sub-grid-2 .chart-card { height: 100%; display: flex; flex-direction: column; }
.sub-grid-2 .chart-card .chart-container { flex: 1; }

/* Right column: vertical stack with consistent spacing */
.secondary-charts-container { display: flex; flex-direction: column; gap: 16px; align-items: stretch; }
.secondary-charts-container .chart-card { width: 100%; }

/* Highlight Card */
.highlight-card { background: linear-gradient(145deg, #ffffff 0%, #ecfdf5 100%); border: 1px solid #a7f3d0; }
.highlight-body { display: flex; align-items: center; gap: 20px; }
.gauge-area { flex: 1; text-align: center; }
.gauge-title { font-weight: 700; color: var(--primary-dark); margin-top: 8px; font-size: 14px; }
.metrics-area { flex: 1; display: flex; flex-direction: column; gap: 12px; }
.metric-row { display: flex; justify-content: space-between; font-size: 13px; border-bottom: 1px dashed #d1fae5; padding-bottom: 4px; }
.metric-row span { color: #6b7280; }
.metric-row strong { color: var(--text-main); }
.badge { background: #fcd34d; color: #78350f; font-size: 10px; padding: 4px 8px; border-radius: 12px; font-weight: 800; text-transform: uppercase; float: right; }

/* Table Section */
.table-header { display: flex; justify-content: space-between; align-items: flex-end; flex-wrap: wrap; gap: 16px; }
.table-controls { display: flex; gap: 8px; }
.search-input, .sort-select { padding: 6px 12px; border: 1px solid #e5e7eb; border-radius: 8px; font-size: 13px; outline: none; }
.table-responsive { overflow-x: auto; }
.analysis-table { width: 100%; border-collapse: collapse; font-size: 14px; }
.analysis-table th { text-align: left; padding: 12px; background: #f9fafb; color: #6b7280; font-weight: 600; border-bottom: 2px solid #e5e7eb; white-space: nowrap; }
.analysis-table td { padding: 12px; border-bottom: 1px solid #f3f4f6; vertical-align: middle; }
.status-badge { padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: 700; text-transform: uppercase; }
.status-badge.active { background: #d1fae5; color: #065f46; }
.status-badge.terminee { background: #e5e7eb; color: #374151; }
.progress-cell { display: flex; align-items: center; gap: 8px; }
.progress-bar-mini { flex: 1; height: 6px; background: #e5e7eb; border-radius: 3px; min-width: 60px; }
.progress-bar-mini .fill { height: 100%; border-radius: 3px; }
.bg-success { background-color: #10b981; } .bg-warning { background-color: #f59e0b; } .bg-danger { background-color: #ef4444; }
.score-circle { width: 32px; height: 32px; border-radius: 50%; border: 3px solid; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 12px; color: #374151; }
.recommendation-text { font-size: 12px; font-weight: 600; }
.text-danger { color: #ef4444; } .text-success { color: #10b981; } .text-muted { color: #9ca3af; }
.fw-bold { font-weight: 600; color: #111827; }

/* Financial Custom Chart */
.custom-financials { overflow-y: auto; max-height: 250px; }
.fin-item { margin-bottom: 12px; }
.fin-header { display: flex; justify-content: space-between; font-size: 13px; font-weight: 600; margin-bottom: 4px; }
.fin-bar-bg { height: 8px; background: #f3f4f6; border-radius: 4px; overflow: hidden; display: flex; }
.fin-bar-segment { height: 100%; }
.fin-bar-segment.feed { background: var(--primary); }
.fin-bar-segment.treat { background: #f87171; }
.fin-bar-segment.other { background: #94a3b8; }
.fin-legend-mini { display: flex; gap: 12px; margin-top: 4px; font-size: 11px; color: #6b7280; }
.dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; margin-right: 4px; }
.dot.feed { background: var(--primary); } .dot.treat { background: #f87171; } .dot.other { background: #94a3b8; }

/* Empty State */
.empty-dashboard { grid-column: span 12; text-align: center; padding: 60px; color: #9ca3af; }
.empty-icon { font-size: 48px; margin-bottom: 16px; opacity: 0.5; }
.mt-4 { margin-top: 24px; }
</style>