<template>
  <ChartBase
    ref="chart"
    :chart-id="chartId"
    chart-type="line"
    :height="height"
    :width="width"
  />
</template>

<script>
import ChartBase from './commun/ChartBase.vue';
import { formatDate } from './commun/chartUtils';

export default {
  name: 'WeightChart',
  
  components: {
    ChartBase
  },

  props: {
    band: {
      type: Object,
      default: () => ({})
    },
    consommations: {
      type: Array,
      default: () => []
    },
    height: {
      type: [String, Number],
      default: '300'
    },
    width: {
      type: [String, Number],
      default: '100%'
    }
  },
  
  data() {
    return {
      chartId: `weight-chart-${Math.random().toString(36).substr(2, 9)}`
    };
  },
  
  computed: {
    durationWeeks() {
      const days = parseInt(this.band?.duree_jours, 10) || 42;
      return Math.max(1, Math.ceil(days / 7));
    },

    startDate() {
      return this.band?.date_arrivee ? new Date(this.band.date_arrivee) : null;
    },

    lastUpdateWeekIndex() {
      // Dernière mise à jour = max(date consommation) sinon âge moyen
      let dayIdx = -1;
      if (this.startDate && Array.isArray(this.consommations)) {
        this.consommations.forEach(c => {
          if (!c?.date) return;
          const d = new Date(c.date);
          const diff = Math.floor((d - this.startDate) / (1000 * 60 * 60 * 24));
          if (!Number.isNaN(diff)) dayIdx = Math.max(dayIdx, diff);
        });
      }
      if (dayIdx < 0 && this.band?.age_moyen) {
        dayIdx = Math.floor(this.band.age_moyen);
      }
      const weekIdx = Math.floor(dayIdx / 7);
      return Math.min(Math.max(weekIdx, -1), this.durationWeeks - 1);
    },

    chartLabels() {
      // Labels hebdomadaires sur toute la durée
      return Array.from({ length: this.durationWeeks }, (_, i) => `Sem ${i + 1}`);
    },
    
    referenceWeights() {
      // Courbe de référence hebdomadaire dérivée d'un profil standard
      const base = this.band?.poids_moyen_initial || 2.0;
      const ref = [];
      for (let i = 0; i < this.durationWeeks; i += 1) {
        const progress = Math.min(i / Math.max(this.durationWeeks - 1, 1), 1);
        const gain = (progress ** 1.4) * base * 0.6;
        ref.push(parseFloat((base * 0.4 + gain).toFixed(2)));
      }
      return ref;
    },

    actualWeights() {
      // Notre courbe s'arrête à la dernière mise à jour; après: null pour ne pas relier
      const ref = this.referenceWeights;
      const last = this.lastUpdateWeekIndex;
      const arr = Array(ref.length).fill(null);
      // Mettre le poids initial sur la première semaine
      if (ref.length > 0) {
        arr[0] = this.band?.poids_moyen_initial || ref[0];
      }
      if (last >= 0 && last < ref.length) {
        const current = this.band?.poids_moyen_actuel;
        arr[last] = current || ref[last];
      }
      return arr;
    }
  },
  
  watch: {
    band: {
      handler() {
        this.render();
      },
      deep: true
    },
    
    consommations: {
      handler() {
        this.render();
      },
      deep: true
    }
  },
  
  methods: {
    render() {
      const chart = this.$refs.chart;
      if (!chart) return;
      chart.getChartData = this.getChartData;
      chart.getChartOptions = this.getChartOptions;
      this.$nextTick(() => chart.renderChart());
    },

    getChartData() {
      return {
        labels: this.chartLabels,
        datasets: [{
          label: 'Poids suivi (kg)',
          data: this.actualWeights,
          borderColor: '#4CAF50',
          backgroundColor: 'rgba(76, 175, 80, 0.1)',
          borderWidth: 3,
          spanGaps: false,
          fill: true,
          tension: 0.4
        }, {
          label: 'Référence (kg)',
          data: this.referenceWeights,
          borderColor: '#9C27B0',
          backgroundColor: 'rgba(156, 39, 176, 0.08)',
          borderDash: [6, 6],
          borderWidth: 2,
          fill: false,
          tension: 0.25
        }]
      };
    },
    
    getChartOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: 'top'
          },
          tooltip: {
            callbacks: {
              label: (context) => `${context.parsed.y.toFixed(2)} kg`
            }
          }
        },
        scales: {
          y: {
            beginAtZero: false,
            title: {
              display: true,
              text: 'Poids (kg)'
            }
          }
        }
      };
    }
  },
  
  mounted() {
    this.render();
  }
};
</script>