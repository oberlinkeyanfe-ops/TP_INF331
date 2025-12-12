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
            <span>Âge moyen:</span>
            <strong>{{ kpis.croissance.age_moyen }} jours</strong>
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
          marge_estimee: 0,
          roi: 0,
          benefice_animal: 0,
          tendance: 0
        },
        alertes: []
      },
      kpiEvolutionChart: null,
      kpiComparisonChart: null
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
    }
  },
  methods: {
    calculateKPIs() {
      if (!this.bandData) return;

      // Calcul des KPIs de croissance
      this.kpis.croissance.poids_moyen = this.bandData.poids_moyen_initial || 0;
      this.kpis.croissance.age_moyen = this.bandData.age_moyen || 0;
      this.kpis.croissance.uniformite = this.calculateUniformity();
      this.kpis.croissance.gain_quotidien = this.calculateDailyGain();
      this.kpis.croissance.tendance = this.calculateGrowthTrend();

      // Calcul des KPIs de santé
      this.kpis.sante.taux_mortalite = this.calculateMortalityRate();
      this.kpis.sante.taux_survie = 100 - this.kpis.sante.taux_mortalite;
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
      if (!this.bandData.nombre_initial || this.bandData.nombre_initial === 0) return 0;
      const morts = this.bandData.nombre_morts_totaux || 0;
      return (morts / this.bandData.nombre_initial * 100).toFixed(1);
    },

    calculateFeedConversionRatio() {
      if (!this.consommationData.length || !this.bandData.poids_moyen_initial) return 0;
      const totalConsumption = this.consommationData.reduce((sum, c) => sum + (c.kg || 0), 0);
      const totalWeight = this.bandData.poids_moyen_initial * this.calculateCurrentAnimals();
      return totalConsumption > 0 ? (totalConsumption / totalWeight).toFixed(2) : 0;
    },

    calculateCurrentAnimals() {
      return (this.bandData.nombre_initial || 0) + 
             (this.bandData.nombre_nouveaux_nes || 0) - 
             (this.bandData.nombre_morts_totaux || 0);
    },

    calculateDailyGain() {
      // Simulation de gain quotidien
      return this.bandData.age_moyen > 0 ? 
             (this.bandData.poids_moyen_initial / this.bandData.age_moyen * 1000).toFixed(0) : 0;
    },

    calculateProductionCost() {
      const totalCost = this.consommationData.reduce((sum, c) => sum + (c.cout || 0), 0);
      const totalWeight = this.bandData.poids_moyen_initial * this.calculateCurrentAnimals();
      return totalWeight > 0 ? (totalCost / totalWeight).toFixed(2) : 0;
    },

    calculateEstimatedMargin() {
      const prixVenteKilo = 1.85; // Prix de vente moyen par kg
      const poidsTotal = this.bandData.poids_moyen_initial * this.calculateCurrentAnimals();
      const coutTotal = this.consommationData.reduce((sum, c) => sum + (c.cout || 0), 0);
      return (poidsTotal * prixVenteKilo - coutTotal).toFixed(2);
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
      return isNaN(num) ? '0.00 €' : `${num.toFixed(2)} €`;
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
    },

    createEvolutionChart() {
      const ctx = this.$refs.kpiEvolutionChart?.getContext('2d');
      if (!ctx) return;

      if (this.kpiEvolutionChart) {
        this.kpiEvolutionChart.destroy();
      }

      // Données simulées pour l'évolution
      const labels = ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4', 'Sem 5', 'Sem 6'];
      
      this.kpiEvolutionChart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [
            {
              label: 'Poids (kg)',
              data: [1.8, 1.9, 2.0, 2.1, 2.2, this.kpis.croissance.poids_moyen],
              borderColor: '#4CAF50',
              backgroundColor: 'rgba(76, 175, 80, 0.1)',
              yAxisID: 'y'
            },
            {
              label: 'Survie (%)',
              data: [98, 97.5, 97, 96.8, 96.5, this.kpis.sante.taux_survie],
              borderColor: '#F44336',
              backgroundColor: 'rgba(244, 67, 54, 0.1)',
              yAxisID: 'y1'
            },
            {
              label: 'IC',
              data: [1.8, 1.75, 1.72, 1.68, 1.65, this.kpis.consommation.indice],
              borderColor: '#2196F3',
              backgroundColor: 'rgba(33, 150, 243, 0.1)',
              yAxisID: 'y'
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
              position: 'left'
            },
            y1: {
              type: 'linear',
              display: true,
              position: 'right',
              grid: {
                drawOnChartArea: false
              },
              min: 90,
              max: 100
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

      // Données pour comparaison radar
      this.kpiComparisonChart = new Chart(ctx, {
        type: 'radar',
        data: {
          labels: ['Croissance', 'Santé', 'Alimentation', 'Rentabilité', 'Uniformité'],
          datasets: [
            {
              label: 'Valeurs actuelles',
              data: [
                this.kpis.croissance.poids_moyen * 10,
                this.kpis.sante.score * 10,
                100 - (this.kpis.consommation.indice * 20),
                this.kpis.finances.roi,
                this.kpis.croissance.uniformite
              ],
              backgroundColor: 'rgba(255, 152, 0, 0.2)',
              borderColor: '#FF9800',
              borderWidth: 2
            },
            {
              label: 'Objectifs',
              data: [25, 80, 70, 25, 85],
              backgroundColor: 'rgba(76, 175, 80, 0.2)',
              borderColor: '#4CAF50',
              borderWidth: 2
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            r: {
              beginAtZero: true,
              max: 100
            }
          }
        }
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
  }
};
</script>

<style src="../../css/kpi.css" type="text/css"></style>

 