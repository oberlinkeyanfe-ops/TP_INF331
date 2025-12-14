<template>
  <div class="chart-container" :style="containerStyle">
    <div class="chart-wrapper">
      <canvas :ref="chartRef" :id="chartId"></canvas>

      <div v-if="loading" class="chart-overlay">
        <div class="spinner"></div>
        <span>Chargement du graphique...</span>
      </div>

      <div v-if="error" class="chart-overlay chart-error">
        <span class="error-icon">⚠️</span>
        <span>{{ error }}</span>
      </div>
    </div>
  </div>
</template>

<script>
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);
// Désactiver globalement les animations pour éviter des frames sur des canvas déjà démontés
Chart.defaults.animation = false;
if (Chart.defaults.transitions?.active) {
  Chart.defaults.transitions.active.animation = false;
}

export default {
  name: 'ChartBase',
  
  props: {
    chartId: {
      type: String,
      default: () => `chart-${Math.random().toString(36).substr(2, 9)}`
    },
    chartType: {
      type: String,
      default: 'line'
    },
    height: {
      type: [String, Number],
      default: '300px'
    },
    width: {
      type: [String, Number],
      default: '100%'
    }
  },
  
  data() {
    return {
      chart: null,
      loading: false,
      error: null,
      chartRef: 'chartCanvas',
      isUnmounted: false
    };
  },
  
  computed: {
    containerStyle() {
      return {
        height: typeof this.height === 'number' ? `${this.height}px` : this.height,
        width: typeof this.width === 'number' ? `${this.width}px` : this.width,
        position: 'relative'
      };
    }
  },
  
  methods: {
    // Méthode à surcharger par les enfants
    getChartData() {
      return {
        labels: [],
        datasets: []
      };
    },
    
    getChartOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        animation: false
      };
    },
    
    async renderChart() {
      try {
        if (this.isUnmounted) return null;
        this.loading = true;
        this.error = null;
        
        // Détruire l'ancien graphique
        if (this.chart) {
          if (typeof this.chart.stop === 'function') {
            this.chart.stop();
          }
          this.chart.destroy();
          this.chart = null;
        }
        
        // Attendre que le canvas soit disponible
        await this.$nextTick();
        
        const canvas = this.$refs[this.chartRef];
        if (!canvas) {
          throw new Error('Canvas non trouvé');
        }

        // Si le canvas n'est plus dans le DOM, ne pas créer de graphique
        if (!canvas.isConnected) {
          this.loading = false;
          return null;
        }

        // S'assurer qu'aucun autre graphique Chart.js n'utilise déjà ce canvas
        const existing = Chart.getChart(canvas);
        if (existing) {
          existing.destroy();
        }
        
        const ctx = canvas.getContext('2d');
        if (!ctx) {
          throw new Error('Contexte 2D non disponible');
        }
        
        // Créer le nouveau graphique
        this.chart = new Chart(ctx, {
          type: this.chartType,
          data: this.getChartData(),
          options: this.getChartOptions()
        });
        
        this.loading = false;
        return this.chart;
        
      } catch (err) {
        console.error('Erreur création graphique:', err);
        this.error = err.message;
        this.loading = false;
        return null;
      }
    },
    
    updateChart() {
      if (!this.chart) return;
      
      this.chart.data = this.getChartData();
      this.chart.options = this.getChartOptions();
      this.chart.update();
    },
    
    destroyChart() {
      if (this.chart) {
        this.chart.destroy();
        this.chart = null;
      }
    }
  },
  
  mounted() {
    this.renderChart();
  },
  
  beforeUnmount() {
    this.isUnmounted = true;
    this.destroyChart();
  }
};
</script>

<style scoped>
.chart-container {
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.chart-wrapper {
  position: relative;
  height: 100%;
  width: 100%;
}

.chart-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.85);
  color: #666;
  z-index: 2;
  text-align: center;
}

.chart-error {
  color: #e74c3c;
}

.spinner {
  border: 3px solid #f3f3f3;
  border-top: 3px solid #3498db;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-icon {
  font-size: 24px;
  margin-bottom: 10px;
}

canvas {
  display: block;
  width: 100% !important;
  height: 100% !important;
}
</style>