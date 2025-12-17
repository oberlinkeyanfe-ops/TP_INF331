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

// Apply theme defaults from CSS variables (to match styles in band.css)
function getCssVar(name, fallback) {
  try {
    const v = getComputedStyle(document.documentElement).getPropertyValue(name);
    return (v && v.trim()) || fallback;
  } catch (e) {
    return fallback;
  }
}
const CSS_FONT = getCssVar('--font-family', 'Inter, system-ui, -apple-system, sans-serif');
const CSS_TEXT_MAIN = getCssVar('--text-main', '#111827');
const CSS_TEXT_MUTED = getCssVar('--text-muted', '#64748b');
const CSS_BG_CARD = getCssVar('--bg-card', '#ffffff');
const CSS_BORDER_COLOR = getCssVar('--border-color', '#e6edf7');
const CSS_GRID_COLOR = getCssVar('--border-color', '#e6edf7');
const CSS_PRIMARY = getCssVar('--primary', '#0f172a');
const CSS_PRIMARY_ACCENT = getCssVar('--primary-accent', '#6f42c1'); // band.css main action color

// Chart.js sensible defaults inspired by band.css
Chart.defaults.font.family = CSS_FONT;
Chart.defaults.font.size = 13;
Chart.defaults.color = CSS_TEXT_MAIN;
Chart.defaults.plugins.legend = Chart.defaults.plugins.legend || {};
Chart.defaults.plugins.legend.labels = Chart.defaults.plugins.legend.labels || {};
Chart.defaults.plugins.legend.labels.color = CSS_TEXT_MUTED;
Chart.defaults.plugins.legend.labels.font = { family: CSS_FONT, size: 12 };
Chart.defaults.plugins.tooltip = Chart.defaults.plugins.tooltip || {};
Chart.defaults.plugins.tooltip.backgroundColor = CSS_BG_CARD;
Chart.defaults.plugins.tooltip.titleColor = CSS_TEXT_MAIN;
Chart.defaults.plugins.tooltip.bodyColor = CSS_TEXT_MAIN;
Chart.defaults.plugins.tooltip.borderColor = CSS_BORDER_COLOR;
Chart.defaults.plugins.tooltip.borderWidth = 1;
Chart.defaults.elements.line.borderWidth = 2;
Chart.defaults.elements.point.radius = 3;
Chart.defaults.elements.point.hoverRadius = 5;

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

    // Merge user options with base themed options
    _mergeOptions(userOptions = {}) {
      const base = {
        responsive: true,
        maintainAspectRatio: false,
        animation: false,
        plugins: {
          legend: { labels: { color: CSS_TEXT_MUTED, font: { family: CSS_FONT, size: 12 } } },
          tooltip: { backgroundColor: CSS_BG_CARD, titleColor: CSS_TEXT_MAIN, bodyColor: CSS_TEXT_MAIN, borderColor: CSS_BORDER_COLOR }
        },
        scales: {
          x: { ticks: { color: CSS_TEXT_MUTED, font: { family: CSS_FONT } }, grid: { color: CSS_GRID_COLOR } },
          y: { ticks: { color: CSS_TEXT_MUTED, font: { family: CSS_FONT } }, grid: { color: CSS_GRID_COLOR } }
        }
      };

      function mergeDeep(target, source) {
        for (const key in source) {
          if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
            if (!target[key]) target[key] = {};
            mergeDeep(target[key], source[key]);
          } else {
            target[key] = source[key];
          }
        }
        return target;
      }

      return mergeDeep(base, userOptions);
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
        
        // Try to obtain the canvas reference; retry a few times if not yet rendered
        let canvas = this.$refs[this.chartRef];
        const maxAttempts = 6;
        let attempt = 0;
        while ((!canvas || !canvas.isConnected) && attempt < maxAttempts) {
          // try alternative selector inside component root
          canvas = this.$refs[this.chartRef] || (this.$el && this.$el.querySelector && this.$el.querySelector('canvas'));
          if (canvas && canvas.isConnected) break;
          attempt += 1;
          // small delay to allow DOM to render when used inside tab transitions
          // eslint-disable-next-line no-await-in-loop
          await new Promise(r => setTimeout(r, 50));
        }

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
        const userOptions = (typeof this.getChartOptions === 'function') ? this.getChartOptions() : {};
        const options = this._mergeOptions(userOptions);
        this.chart = new Chart(ctx, {
          type: this.chartType,
          data: this.getChartData(),
          options
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
  background: var(--bg-card, #fff);
  border-radius: 8px;
  padding: 12px;
  box-shadow: var(--shadow-card, 0 6px 20px rgba(0,0,0,0.04));
  border: 1px solid var(--border-color, #eef2f7);
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