<!-- src/components/KPI.vue -->
<template>
  <div class="kpi-dashboard">
    <!-- Section KPIs principaux -->
    <div class="kpi-section">
      <h3 class="section-title">Indicateurs Clés de Performance</h3>
      
      <!-- Cartes KPIs -->
      <div class="kpi-grid">
        <!-- Croissance -->
        <div class="kpi-card growth">
          <div class="kpi-icon">📈</div>
          <div class="kpi-content">
            <div class="kpi-label">Croissance</div>
            <div class="kpi-value">{{ formatNumber(kpis.croissance.poids_moyen) }} kg</div>
            <div class="kpi-trend" :class="getTrendClass(kpis.croissance.tendance)">
              {{ formatTrend(kpis.croissance.tendance) }}
            </div>
          </div>
        </div>

        <!-- Santé -->
        <div class="kpi-card health">
          <div class="kpi-icon">❤️</div>
          <div class="kpi-content">
            <div class="kpi-label">Taux de survie</div>
            <div class="kpi-value">{{ formatNumber(kpis.sante.taux_survie) }}%</div>
            <div class="kpi-trend" :class="getTrendClass(kpis.sante.tendance)">
              {{ formatTrend(kpis.sante.tendance) }}
            </div>
          </div>
        </div>

        <!-- Consommation -->
        <div class="kpi-card consumption">
          <div class="kpi-icon">🌾</div>
          <div class="kpi-content">
            <div class="kpi-label">Indice Consommation</div>
            <div class="kpi-value">{{ formatNumber(kpis.consommation.indice) }}</div>
            <div class="kpi-trend" :class="getTrendClass(kpis.consommation.tendance)">
              {{ formatTrend(kpis.consommation.tendance) }}
            </div>
          </div>
        </div>

        <!-- Rentabilité -->
        <div class="kpi-card profitability">
          <div class="kpi-icon">💰</div>
          <div class="kpi-content">
            <div class="kpi-label">ROI estimé</div>
            <div class="kpi-value">{{ formatNumber(kpis.finances.roi) }}%</div>
            <div class="kpi-trend" :class="getTrendClass(kpis.finances.tendance)">
              {{ formatTrend(kpis.finances.tendance) }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Détails des KPIs -->
    <div class="kpi-details">
      <!-- Croissance -->
      <div class="detail-section">
        <h4>📈 Croissance et Performance</h4>
        <div class="detail-grid">
          <div class="detail-item">
            <span>Poids moyen:</span>
            <strong>{{ formatNumber(kpis.croissance.poids_moyen) }} kg</strong>
          </div>
          <div class="detail-item">
            <span>Gain quotidien:</span>
            <strong>{{ formatNumber(kpis.croissance.gain_quotidien) }} g/j</strong>
          </div>
          <div class="detail-item">
            <span>Âge (semaines):</span>
            <strong>{{ kpis.croissance.age_moyen }} sem</strong>
          </div>
          <div class="detail-item">
            <span>Uniformité:</span>
            <strong>{{ formatNumber(kpis.croissance.uniformite) }}%</strong>
          </div>
        </div>
      </div>

      <!-- Santé -->
      <div class="detail-section">
        <h4>❤️ Santé et Bien-être</h4>
        <div class="detail-grid">
          <div class="detail-item">
            <span>Taux mortalité:</span>
            <strong>{{ formatNumber(kpis.sante.taux_mortalite) }}%</strong>
          </div>
          <div class="detail-item">
            <span>Survie:</span>
            <strong>{{ formatNumber(kpis.sante.taux_survie) }}%</strong>
          </div>
          <div class="detail-item">
            <span>Taux traitements:</span>
            <strong>{{ formatNumber(kpis.sante.traitement_taux) }}%</strong>
          </div>
          <div class="detail-item">
            <span>Animaux traités:</span>
            <strong>{{ kpis.sante.animaux_traitement }}%</strong>
          </div>
          <div class="detail-item">
            <span>Score santé:</span>
            <strong>{{ kpis.sante.score }}/10</strong>
          </div>
        </div>
      </div>

      <!-- Consommation -->
      <div class="detail-section">
        <h4>🌾 Alimentation</h4>
        <div class="detail-grid">
          <div class="detail-item">
            <span>IC (Indice):</span>
            <strong>{{ formatNumber(kpis.consommation.indice) }}</strong>
          </div>
          <div class="detail-item">
            <span>Consom./jour:</span>
            <strong>{{ formatNumber(kpis.consommation.quotidienne) }} kg</strong>
          </div>
          <div class="detail-item">
            <span>Coût aliment:</span>
            <strong>{{ formatCurrency(kpis.consommation.cout_quotidien) }}</strong>
          </div>
          <div class="detail-item">
            <span>Efficacité:</span>
            <strong>{{ formatNumber(kpis.consommation.efficacite) }}%</strong>
          </div>
        </div>
      </div>

      <!-- Finances -->
      <div class="detail-section">
        <h4>💰 Rentabilité</h4>
        <div class="detail-grid">
          <div class="detail-item">
            <span>Coût production:</span>
            <strong>{{ formatCurrency(kpis.finances.cout_production) }}/kg</strong>
          </div>
          <div class="detail-item">
            <span>Coût alim/kg:</span>
            <strong>{{ formatCurrency(kpis.finances.cout_alim_kg) }}/kg</strong>
          </div>
          <div class="detail-item">
            <span>Coût total/kg:</span>
            <strong>{{ formatCurrency(kpis.finances.cout_total_kg) }}/kg</strong>
          </div>
          <div class="detail-item">
            <span>Marge/kg:</span>
            <strong>{{ formatCurrency(kpis.finances.marge_par_kg) }}</strong>
          </div>
          <div class="detail-item">
            <span>Marge estimée:</span>
            <strong>{{ formatCurrency(kpis.finances.marge_estimee) }}</strong>
          </div>
          <div class="detail-item">
            <span>ROI:</span>
            <strong>{{ formatNumber(kpis.finances.roi) }}%</strong>
          </div>
          <div class="detail-item">
            <span>Bénéfice/animal:</span>
            <strong>{{ formatCurrency(kpis.finances.benefice_animal) }}</strong>
          </div>
          <div class="detail-item">
            <span>Cashburn/jour:</span>
            <strong>{{ formatCurrency(kpis.finances.cashburn_jour) }}</strong>
          </div>
        </div>
      </div>
    </div>

    <!-- Graphiques KPIs -->
    <div class="kpi-charts">
      <div class="chart-container">
        <h4>Évolution des KPIs</h4>
        <canvas ref="kpiEvolutionChart"></canvas>
      </div>
      <div class="chart-container">
        <h4>Comparaison des performances</h4>
        <canvas ref="kpiComparisonChart"></canvas>
      </div>
      <div class="chart-container">
        <h4>Top dépenses</h4>
        <div class="expense-chart-wrap">
          <canvas ref="kpiExpenseChart"></canvas>
          <ul class="expense-legend" v-if="expenseBreakdown.length">
            <li v-for="item in expenseBreakdown" :key="item.label">
              <span class="dot" :style="{ backgroundColor: item.color }"></span>
              <span class="label">{{ item.label }}</span>
              <span class="cost">{{ formatCurrency(item.value) }}</span>
              <span class="percent">{{ formatNumber(item.percent) }}%</span>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Alertes et recommandations -->
    <div class="kpi-alerts" v-if="kpis.alertes.length > 0">
      <h4>⚠️ Alertes et recommandations</h4>
      <div class="alerts-container">
        <div v-for="alerte in kpis.alertes" :key="alerte.id" 
             :class="['alert-item', alerte.niveau]">
          <div class="alert-icon">
            <span v-if="alerte.niveau === 'critique'">🔴</span>
            <span v-else-if="alerte.niveau === 'avertissement'">🟡</span>
            <span v-else>🔵</span>
          </div>
          <div class="alert-content">
            <div class="alert-title">{{ alerte.titre }}</div>
            <div class="alert-message">{{ alerte.message }}</div>
            <div class="alert-recommendation" v-if="alerte.recommandation">
              💡 {{ alerte.recommandation }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

export default {
  name: 'KPIDashboard',
  props: {
    bandData: {
      type: Object,
      required: true
    },
    consommationData: {
      type: Array,
      default: () => []
    },
    animalInfos: {
      type: Array,
      default: () => []
    },
    expenseRecords: {
      type: Array,
      default: () => []
    },
    treatmentRecords: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      kpis: {
        croissance: {
          poids_moyen: 0,
          gain_quotidien: 0,
          age_moyen: 0,
          uniformite: 0,
          tendance: 0
        },
        sante: {
          taux_mortalite: 0,
          taux_survie: 0,
          traitement_taux: 0,
          animaux_traitement: 0,
          score: 0,
          tendance: 0
        },
        consommation: {
          indice: 0,
          quotidienne: 0,
          cout_quotidien: 0,
          efficacite: 0,
          tendance: 0
        },
        finances: {
          cout_production: 0,
          cout_alim_kg: 0,
          cout_total_kg: 0,
          marge_par_kg: 0,
          cashburn_jour: 0,
          marge_estimee: 0,
          roi: 0,
          benefice_animal: 0,
          tendance: 0
        },
        alertes: []
      },
      kpiEvolutionChart: null,
      kpiComparisonChart: null,
      kpiExpenseChart: null,
      expenseBreakdown: []
    };
  },
  watch: {
    bandData: {
      immediate: true,
      handler() {
        this.calculateKPIs();
      }
    },
    consommationData: {
      immediate: true,
      handler() {
        this.calculateKPIs();
      }
    },
    animalInfos: {
      immediate: true,
      handler() {
        this.calculateKPIs();
      }
    },
    expenseRecords: {
      immediate: true,
      handler() {
        this.calculateKPIs();
      }
    },
    treatmentRecords: {
      immediate: true,
      handler() {
        this.calculateKPIs();
      }
    }
  },
  methods: {
    calculateKPIs() {
      if (!this.bandData) return;

      const latestWeight = this.getLatestAnimalWeight();
      const latestWeek = this.getLatestAnimalWeek();

      // Calcul des KPIs de croissance
      this.kpis.croissance.poids_moyen = latestWeight ?? (this.bandData.poids_moyen_initial || 0);
      this.kpis.croissance.age_moyen = latestWeek || 0;
      this.kpis.croissance.uniformite = this.calculateUniformity();
      this.kpis.croissance.gain_quotidien = this.calculateDailyGain();
      this.kpis.croissance.tendance = this.calculateGrowthTrend();

      // Calcul des KPIs de santé
      this.kpis.sante.taux_mortalite = this.calculateMortalityRate();
      this.kpis.sante.taux_survie = 100 - this.kpis.sante.taux_mortalite;
      this.kpis.sante.traitement_taux = this.calculateTreatmentRate();
      this.kpis.sante.score = this.calculateHealthScore();
      this.kpis.sante.tendance = this.calculateHealthTrend();

      // Calcul des KPIs de consommation
      this.kpis.consommation.indice = this.calculateFeedConversionRatio();
      this.kpis.consommation.quotidienne = this.calculateDailyConsumption();
      this.kpis.consommation.cout_quotidien = this.calculateDailyFeedCost();
      this.kpis.consommation.efficacite = this.calculateFeedEfficiency();
      this.kpis.consommation.tendance = this.calculateConsumptionTrend();

      // Calcul des KPIs financiers
      this.kpis.finances.cout_production = this.calculateProductionCost();
      this.kpis.finances.cout_alim_kg = this.calculateFeedCostPerKg();
      this.kpis.finances.cout_total_kg = this.calculateTotalCostPerKg();
      this.kpis.finances.marge_par_kg = this.calculateMarginPerKg();
      this.kpis.finances.cashburn_jour = this.calculateCashburnPerDay();
      this.kpis.finances.marge_estimee = this.calculateEstimatedMargin();
      this.kpis.finances.roi = this.calculateROI();
      this.kpis.finances.benefice_animal = this.calculateProfitPerAnimal();
      this.kpis.finances.tendance = this.calculateFinancialTrend();

      // Générer les alertes
      this.kpis.alertes = this.generateAlerts();

      // Mettre à jour les graphiques
      this.$nextTick(() => {
        this.updateCharts();
      });
    },

    // Méthodes de calcul
    calculateMortalityRate() {
      const initial = this.bandData.nombre_initial || 0;
      if (!initial) return 0;

      const lastRestants = this.getLatestRemainingAnimals();
      const mortsViaRestants = lastRestants !== null ? Math.max(initial - lastRestants, 0) : null;
      const mortsSemaine = this.totalDeathsFromAnimalInfos();
      const morts = mortsViaRestants !== null ? mortsViaRestants : (mortsSemaine || this.bandData.nombre_morts_totaux || 0);

      return (morts / initial * 100).toFixed(1);
    },

    calculateTreatmentRate() {
      const animaux = this.calculateCurrentAnimals();
      if (!animaux) return 0;
      const totalTreatments = (this.treatmentRecords || []).length;
      return ((totalTreatments / animaux) * 100).toFixed(1);
    },

    calculateFeedConversionRatio() {
      if (!this.consommationData.length) return 0;
      const totalConsumption = this.consommationData.reduce((sum, c) => sum + (c.kg || 0), 0);
      const weight = this.getLatestAnimalWeight() || this.bandData.poids_moyen_initial || 0;
      const totalWeight = weight * this.calculateCurrentAnimals();
      if (totalWeight <= 0) return 0;
      return totalConsumption > 0 ? (totalConsumption / totalWeight).toFixed(2) : 0;
    },

    calculateCurrentAnimals() {
      const initial = this.bandData.nombre_initial || 0;
      if (!initial) return 0;

      if (this.animalInfos.length) {
        const restants = this.getLatestRemainingAnimals();
        if (restants !== null) return restants;
        const deaths = this.totalDeathsFromAnimalInfos();
        return Math.max(0, initial - deaths);
      }

      return (this.bandData.nombre_initial || 0) + 
             (this.bandData.nombre_nouveaux_nes || 0) - 
             (this.bandData.nombre_morts_totaux || 0);
    },

    calculateDailyGain() {
      const weights = this.animalInfos
        .filter(i => i.poids_moyen !== null && i.poids_moyen !== undefined && i.semaine_production)
        .sort((a, b) => a.semaine_production - b.semaine_production);

      if (weights.length >= 2) {
        const first = weights[0];
        const last = weights[weights.length - 1];
        const weekDiff = Math.max(1, (last.semaine_production || 0) - (first.semaine_production || 0));
        const gainKg = (last.poids_moyen || 0) - (first.poids_moyen || 0);
        const gainPerDay = (gainKg * 1000) / (weekDiff * 7);
        return gainPerDay.toFixed(0);
      }

      const ageWeeks = this.getLatestAnimalWeek() || 0;
      const weight = this.getLatestAnimalWeight() || this.bandData.poids_moyen_initial || 0;
      const ageDays = ageWeeks * 7;
      return ageDays > 0 ? (weight / ageDays * 1000).toFixed(0) : 0;
    },

    calculateProductionCost() {
      const totalCost = this.consommationData.reduce((sum, c) => sum + (c.cout || 0), 0);
      const weight = this.getLatestAnimalWeight() || this.bandData.poids_moyen_initial || 0;
      const totalWeight = weight * this.calculateCurrentAnimals();
      return totalWeight > 0 ? (totalCost / totalWeight).toFixed(2) : 0;
    },

    calculateFeedCostPerKg() {
      const totalFeed = this.consommationData.reduce((sum, c) => sum + (c.cout || 0), 0);
      const totalWeight = this.getLatestTotalWeight();
      return totalWeight > 0 ? (totalFeed / totalWeight).toFixed(2) : 0;
    },

    calculateTotalCostPerKg() {
      const totalAll = this.getTotalAllCosts();
      const totalWeight = this.getLatestTotalWeight();
      return totalWeight > 0 ? (totalAll / totalWeight).toFixed(2) : 0;
    },

    calculateMarginPerKg() {
      const prixVenteKilo = 1.85;
      const totalCostKg = parseFloat(this.calculateTotalCostPerKg());
      return (prixVenteKilo - (isNaN(totalCostKg) ? 0 : totalCostKg)).toFixed(2);
    },

    calculateEstimatedMargin() {
      const prixVenteKilo = 1.85; // Prix de vente moyen par kg
      const poidsTotal = (this.getLatestAnimalWeight() || this.bandData.poids_moyen_initial || 0) * this.calculateCurrentAnimals();
      const coutTotal = this.consommationData.reduce((sum, c) => sum + (c.cout || 0), 0);
      return (poidsTotal * prixVenteKilo - coutTotal).toFixed(2);
    },

    calculateCashburnPerDay() {
      const totalAll = this.getTotalAllCosts();
      const days = this.getDaysElapsed();
      return days > 0 ? (totalAll / days).toFixed(0) : 0;
    },

    calculateROI() {
      const investissement = this.consommationData.reduce((sum, c) => sum + (c.cout || 0), 0);
      const benefice = parseFloat(this.calculateEstimatedMargin());
      return investissement > 0 ? ((benefice / investissement) * 100).toFixed(1) : 0;
    },

    calculateUniformity() {
      // Simulation d'uniformité
      return Math.min(100, Math.max(70, 100 - (this.kpis.sante.taux_mortalite * 2))).toFixed(0);
    },

    calculateHealthScore() {
      const baseScore = 8;
      const mortaliteImpact = this.kpis.sante.taux_mortalite > 3 ? -2 : 0;
      return Math.max(1, Math.min(10, baseScore + mortaliteImpact));
    },

    calculateDailyConsumption() {
      return this.consommationData.length > 0 ? 
             (this.consommationData.reduce((sum, c) => sum + (c.kg || 0), 0) / this.consommationData.length).toFixed(0) : 0;
    },

    calculateDailyFeedCost() {
      return this.consommationData.length > 0 ? 
             (this.consommationData.reduce((sum, c) => sum + (c.cout || 0), 0) / this.consommationData.length).toFixed(2) : 0;
    },

    calculateFeedEfficiency() {
      const ic = parseFloat(this.kpis.consommation.indice);
      return ic > 0 ? (1.5 / ic * 100).toFixed(0) : 0;
    },

    calculateProfitPerAnimal() {
      const benefice = parseFloat(this.calculateEstimatedMargin());
      const animaux = this.calculateCurrentAnimals();
      return animaux > 0 ? (benefice / animaux).toFixed(2) : 0;
    },

    getTotalAllCosts() {
      const feed = (this.consommationData || []).reduce((sum, c) => sum + (c.cout || 0), 0);
      const treatments = (this.treatmentRecords || []).reduce((sum, t) => sum + (Number(t.cout) || 0), 0);
      const expenses = (this.expenseRecords || []).reduce((sum, e) => sum + (Number(e.montant) || 0), 0);
      return feed + treatments + expenses;
    },

    getLatestTotalWeight() {
      const weight = this.getLatestAnimalWeight() || this.bandData.poids_moyen_initial || 0;
      return weight * this.calculateCurrentAnimals();
    },

    getDaysElapsed() {
      if (this.bandData?.date_arrivee) {
        const start = new Date(this.bandData.date_arrivee);
        const now = new Date();
        const diffDays = Math.floor((now.setHours(0, 0, 0, 0) - start.setHours(0, 0, 0, 0)) / (1000 * 60 * 60 * 24));
        return Math.max(1, diffDays + 1);
      }
      // fallback: use durationWeeks * 7 if date missing
      return Math.max(1, (this.durationWeeks || 1) * 7);
    },

    getTopExpenses() {
      const alimentation = (this.consommationData || []).reduce((sum, c) => sum + (Number(c.cout) || 0), 0);
      const traitements = (this.treatmentRecords || []).reduce((sum, t) => sum + (Number(t.cout) || 0), 0);

      const dépenses = (this.expenseRecords || []).reduce((acc, exp) => {
        const key = exp.tache || 'Autres dépenses';
        acc[key] = (acc[key] || 0) + (Number(exp.montant) || 0);
        return acc;
      }, {});

      const buckets = [
        { label: 'Alimentation', value: alimentation },
        { label: 'Traitements', value: traitements },
        ...Object.entries(dépenses).map(([label, value]) => ({ label, value }))
      ];

      const sorted = buckets.sort((a, b) => b.value - a.value);

      return sorted.length ? sorted : [{ label: 'Aucune dépense', value: 0 }];
    },

    getLatestAnimalWeek() {
      if (!this.animalInfos.length) return 0;
      const ordered = [...this.animalInfos]
        .filter(i => i.semaine_production)
        .sort((a, b) => b.semaine_production - a.semaine_production);
      return ordered.length ? ordered[0].semaine_production : 0;
    },

    getLatestAnimalWeight() {
      const withWeight = this.animalInfos
        .filter(i => i.semaine_production && i.poids_moyen !== null && i.poids_moyen !== undefined)
        .sort((a, b) => b.semaine_production - a.semaine_production);
      if (withWeight.length) {
        return Number(withWeight[0].poids_moyen) || 0;
      }
      return null;
    },

    totalDeathsFromAnimalInfos() {
      if (!this.animalInfos.length) return 0;
      return this.animalInfos.reduce((sum, info) => sum + (Number(info.morts_semaine) || 0), 0);
    },

    getLatestRemainingAnimals() {
      if (!this.animalInfos.length) return null;
      const withRestants = [...this.animalInfos]
        .filter(i => i.animaux_restants !== null && i.animaux_restants !== undefined)
        .sort((a, b) => (b.semaine_production || 0) - (a.semaine_production || 0));
      if (!withRestants.length) return null;
      return Number(withRestants[0].animaux_restants) || 0;
    },

    // Méthodes de tendance (simulées)
    calculateGrowthTrend() { return 2.5; },
    calculateHealthTrend() { return -0.3; },
    calculateConsumptionTrend() { return 1.2; },
    calculateFinancialTrend() { return 3.1; },

    // Génération d'alertes
    generateAlerts() {
      const alertes = [];
      
      if (this.kpis.sante.taux_mortalite > 3) {
        alertes.push({
          id: 1,
          niveau: 'critique',
          titre: 'Mortalité élevée',
          message: `Le taux de mortalité (${this.kpis.sante.taux_mortalite}%) dépasse le seuil critique`,
          recommandation: 'Vérifier la ventilation et la qualité de l\'eau immédiatement'
        });
      }

      if (this.kpis.consommation.indice > 1.8) {
        alertes.push({
          id: 2,
          niveau: 'avertissement',
          titre: 'Indice de consommation élevé',
          message: `L'IC (${this.kpis.consommation.indice}) est supérieur à la norme`,
          recommandation: 'Ajuster les rations et vérifier la qualité des aliments'
        });
      }

      if (this.kpis.croissance.poids_moyen < 2.0 && this.kpis.croissance.age_moyen > 30) {
        alertes.push({
          id: 3,
          niveau: 'avertissement',
          titre: 'Croissance insuffisante',
          message: `Le poids moyen (${this.kpis.croissance.poids_moyen} kg) est faible pour l'âge`,
          recommandation: 'Augmenter les protéines dans la ration'
        });
      }

      return alertes;
    },

    // Méthodes de formatage
    formatNumber(value) {
      if (typeof value === 'string') value = parseFloat(value);
      return isNaN(value) ? '0.00' : value.toFixed(2);
    },

    formatCurrency(value) {
      const num = typeof value === 'string' ? parseFloat(value) : value;
      return isNaN(num) ? '0 FCFA' : `${num.toFixed(0)} FCFA`;
    },

    formatTrend(trend) {
      return trend > 0 ? `+${trend.toFixed(1)}%` : `${trend.toFixed(1)}%`;
    },

    getTrendClass(trend) {
      return trend > 0 ? 'positive' : trend < 0 ? 'negative' : 'neutral';
    },

    // Graphiques
    updateCharts() {
      this.createEvolutionChart();
      this.createComparisonChart();
      this.createExpenseChart();
    },

    createEvolutionChart() {
      const ctx = this.$refs.kpiEvolutionChart?.getContext('2d');
      if (!ctx) return;

      if (this.kpiEvolutionChart) {
        this.kpiEvolutionChart.destroy();
      }

      // Données réelles ou fallback
      const entries = [...(this.consommationData || [])]
        .filter(e => e.semaine_production)
        .sort((a, b) => (a.semaine_production || 0) - (b.semaine_production || 0));

      const labels = entries.length
        ? entries.map(e => `S${e.semaine_production}`)
        : ['S1', 'S2', 'S3', 'S4', 'S5', 'S6'];

      const costSeries = entries.length ? entries.map(e => Number(e.cout || 0)) : [120, 140, 160, 150, 170, 180];
      const consoSeries = entries.length ? entries.map(e => Number(e.kg || 0)) : [150, 420, 730, 1100, 1450, 1750];

      const animals = this.calculateCurrentAnimals();
      const poids = this.bandData?.poids_moyen_initial || 1;
      const icSeries = consoSeries.map((kg, idx) => {
        const denom = Math.max(poids * animals, 1);
        return +(kg / denom).toFixed(2) || 0;
      });
      
      this.kpiEvolutionChart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [
            {
              label: 'Coût alim (FCFA)',
              data: costSeries,
              borderColor: '#4CAF50',
              backgroundColor: 'rgba(76, 175, 80, 0.16)',
              yAxisID: 'y'
            },
            {
              label: 'Consommation (kg)',
              data: consoSeries,
              borderColor: '#0EA5E9',
              backgroundColor: 'rgba(14, 165, 233, 0.16)',
              yAxisID: 'y1'
            },
            {
              label: 'IC (kg/kg)',
              data: icSeries,
              borderColor: '#F97316',
              backgroundColor: 'rgba(249, 115, 22, 0.16)',
              yAxisID: 'y2'
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: {
            mode: 'index',
            intersect: false
          },
          scales: {
            y: {
              type: 'linear',
              display: true,
              position: 'left',
              title: { display: true, text: 'Coût (FCFA)' }
            },
            y1: {
              type: 'linear',
              display: true,
              position: 'right',
              grid: { drawOnChartArea: false },
              title: { display: true, text: 'Consommation (kg)' }
            },
            y2: {
              type: 'linear',
              display: true,
              position: 'right',
              grid: { drawOnChartArea: false },
              title: { display: true, text: 'IC' },
              min: 0,
              max: Math.max(...icSeries, 2) + 0.5
            }
          }
        }
      });
    },

    createComparisonChart() {
      const ctx = this.$refs.kpiComparisonChart?.getContext('2d');
      if (!ctx) return;

      if (this.kpiComparisonChart) {
        this.kpiComparisonChart.destroy();
      }

      const totalCost = (this.consommationData || []).reduce((s, c) => s + (c.cout || 0), 0);
      const marge = parseFloat(this.calculateEstimatedMargin()) || 0;
      const roi = parseFloat(this.kpis.finances.roi) || 0;

      this.kpiComparisonChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: ['Coûts alimentation', 'Marge estimée', 'ROI (%)'],
          datasets: [{
            data: [totalCost, Math.max(marge, 0), roi],
            backgroundColor: ['#0EA5E9', '#22C55E', '#F97316'],
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'bottom' }
          }
        }
      });
    },

    createExpenseChart() {
      const ctx = this.$refs.kpiExpenseChart?.getContext('2d');
      if (!ctx) return;

      if (this.kpiExpenseChart) {
        this.kpiExpenseChart.destroy();
      }

      const buckets = this.getTopExpenses();
      const totalAll = buckets.reduce((s, b) => s + b.value, 0);
      const topBucket = buckets[0] || { label: 'Aucune dépense', value: 0 };
      const otherValue = Math.max(0, totalAll - topBucket.value);

      const labels = [topBucket.label, 'Autres'];
      const data = [topBucket.value, otherValue];
      const colors = ['#EF4444', '#E5E7EB'];

      const topPercent = totalAll ? (topBucket.value / totalAll) * 100 : 0;
      this.expenseBreakdown = [
        { label: topBucket.label, value: topBucket.value, percent: topPercent, color: '#EF4444' },
        { label: 'Autres', value: otherValue, percent: 100 - topPercent, color: '#E5E7EB' }
      ];

      const centerPercentPlugin = {
        id: 'centerPercentPlugin',
        afterDraw: (chart) => {
          const { width, height, ctx } = chart;
          const percentText = `${Math.round(topPercent)}%`;
          ctx.save();
          ctx.font = 'bold 18px sans-serif';
          ctx.fillStyle = '#111827';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(percentText, width / 2, height / 2);
          ctx.restore();
        }
      };

      this.kpiExpenseChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels,
          datasets: [{
            data,
            backgroundColor: colors,
            borderWidth: 1,
            hoverOffset: 4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: '60%',
          plugins: {
            legend: { position: 'bottom' },
            tooltip: {
              callbacks: {
                label: (context) => {
                  const value = context.parsed;
                  const percent = totalAll ? ((value / totalAll) * 100).toFixed(1) : 0;
                  return `${context.label}: ${this.formatCurrency(value)} (${percent}%)`;
                }
              }
            }
          }
        },
        plugins: [centerPercentPlugin]
      });
    }
  },
  mounted() {
    this.calculateKPIs();
  },
  beforeUnmount() {
    if (this.kpiEvolutionChart) {
      this.kpiEvolutionChart.destroy();
    }
    if (this.kpiComparisonChart) {
      this.kpiComparisonChart.destroy();
    }
    if (this.kpiExpenseChart) {
      this.kpiExpenseChart.destroy();
    }
  }
};
</script>

<style src="../../css/kpi.css" type="text/css"></style>

 