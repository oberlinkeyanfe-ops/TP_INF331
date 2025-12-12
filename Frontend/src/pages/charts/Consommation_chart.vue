<template>
  <div class="chart-block">
    <chart-base
      :chart-id="chartId"
      :chart-type="'line'"
      :height="300"
      ref="chart"
    />
  </div>
</template>

<script>
import ChartBase from './commun/ChartBase.vue';

export default {
  name: 'ConsumptionHistoryChart',
  components: { ChartBase },
  props: {
    consommations: {
      type: Array,
      default: () => []
    },
    band: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      chartId: `consumption-${Math.random().toString(36).substr(2, 9)}`
    };
  },
  mounted() {
    this.render();
  },
  watch: {
    consommations: {
      deep: true,
      handler() {
        this.render();
      }
    },
    band: {
      deep: true,
      handler() {
        this.render();
      }
    }
  },
  methods: {
    render() {
      const chart = this.$refs.chart;
      if (!chart) return;
      const { labels, kgData, refData } = this.buildTimeseries();
      chart.getChartData = () => ({
        labels,
        datasets: [
          {
            label: 'Consommation aliment (kg)',
            data: kgData,
            borderColor: '#2196F3',
            backgroundColor: 'rgba(33,150,243,0.15)',
            borderWidth: 2,
            tension: 0.25,
            fill: true,
            spanGaps: false
          },
          {
            label: 'Référence (kg)',
            data: refData,
            borderColor: '#FF9800',
            backgroundColor: 'rgba(255, 152, 0, 0.08)',
            borderDash: [6, 6],
            borderWidth: 2,
            tension: 0.2,
            fill: false
          }
        ]
      });
      chart.getChartOptions = () => ({
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: { beginAtZero: true, title: { display: true, text: 'Kg' } },
          x: { ticks: { maxRotation: 45, minRotation: 45 } }
        }
      });
      this.$nextTick(() => chart.renderChart());
    },

    buildTimeseries() {
      const durationWeeks = Math.max(1, Math.ceil((parseInt(this.band?.duree_jours, 10) || 42) / 7));
      const startDate = this.band?.date_arrivee ? new Date(this.band.date_arrivee) : null;
      const labels = Array.from({ length: durationWeeks }, (_, i) => `Sem ${i + 1}`);

      const kgData = Array(durationWeeks).fill(null);
      if (startDate) {
        (this.consommations || []).forEach(c => {
          if (!c?.date) return;
          const d = new Date(c.date);
          const dayDiff = Math.floor((d - startDate) / (1000 * 60 * 60 * 24));
          const idx = Math.floor(dayDiff / 7);
          if (idx >= 0 && idx < durationWeeks) {
            const val = c.aliment_kg || c.kg || 0;
            kgData[idx] = (kgData[idx] || 0) + val;
          }
        });
      }
      const lastIdx = kgData.reduce((acc, v, i) => (v !== null ? i : acc), -1);
      const refData = this.buildReferenceConsumption(durationWeeks);
      const trimmedKgData = kgData.map((v, i) => (lastIdx >= 0 && i <= lastIdx ? (v ?? 0) : null));
      return { labels, kgData: trimmedKgData, refData };
    },

    buildReferenceConsumption(length) {
      // Valeurs indicatives par semaine (kg)
      const base = [1.5, 2.1, 2.8, 3.6, 4.5, 5.2];
      const ref = [];
      for (let i = 0; i < length; i += 1) {
        ref.push(base[i] !== undefined ? base[i] : parseFloat((ref[i - 1] + 0.5).toFixed(2)));
      }
      return ref;
    }
  }
};
</script>

<style scoped>
.chart-block {
  width: 100%;
  height: 320px;
}
</style>
