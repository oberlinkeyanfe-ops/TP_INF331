<template>
  <div class="chart-block">
    <ChartBase
      ref="chart"
      :chart-id="chartId"
      chart-type="bar"
      :height="300"
    />
  </div>
</template>

<script>
import ChartBase from './commun/ChartBase.vue';

export default {
  name: 'PerformanceChart',
  components: { ChartBase },
  props: {
    band: { type: Object, default: () => ({}) },
    consommations: { type: Array, default: () => [] }
  },
  data() {
    return {
      chartId: `performance-${Math.random().toString(36).substr(2, 9)}`
    };
  },
  mounted() {
    this.render();
  },
  watch: {
    band: { deep: true, handler() { this.render(); } },
    consommations: { deep: true, handler() { this.render(); } }
  },
  methods: {
    render() {
      const chart = this.$refs.chart;
      if (!chart) return;
      const { labels, alimentData, cumulated, refCumul } = this.buildTimeseries();

      chart.getChartData = () => ({
        labels,
        datasets: [
          {
            label: 'Aliment (kg)',
            data: alimentData,
            backgroundColor: 'rgba(76, 175, 80, 0.35)',
            borderColor: '#4CAF50',
            borderWidth: 1
          },
          {
            label: 'Cumul (kg)',
            data: cumulated,
            type: 'line',
            borderColor: '#FF9800',
            backgroundColor: 'rgba(255, 152, 0, 0.12)',
            borderWidth: 2,
            tension: 0.25,
            fill: true,
            yAxisID: 'y1'
          },
          {
            label: 'Cumul référence (kg)',
            data: refCumul,
            type: 'line',
            borderColor: '#9C27B0',
            backgroundColor: 'rgba(156, 39, 176, 0.08)',
            borderWidth: 2,
            borderDash: [6, 6],
            tension: 0.2,
            fill: false,
            yAxisID: 'y1'
          }
        ]
      });

      chart.getChartOptions = () => ({
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: { beginAtZero: true, title: { display: true, text: 'Aliment (kg)' } },
          y1: { beginAtZero: true, position: 'right', grid: { drawOnChartArea: false }, title: { display: true, text: 'Cumul (kg)' } }
        },
        plugins: {
          legend: { position: 'top' },
          tooltip: { mode: 'index', intersect: false }
        },
        interaction: { mode: 'index', intersect: false }
      });
      this.$nextTick(() => chart.renderChart());
    },

    buildTimeseries() {
      const durationWeeks = Math.max(1, Math.ceil((parseInt(this.band?.duree_jours, 10) || 42) / 7));
      const startDate = this.band?.date_arrivee ? new Date(this.band.date_arrivee) : null;
      const labels = Array.from({ length: durationWeeks }, (_, i) => `Sem ${i + 1}`);

      const alimentData = Array(durationWeeks).fill(null);
      if (startDate) {
        (this.consommations || []).forEach(c => {
          if (!c?.date) return;
          const d = new Date(c.date);
          const dayDiff = Math.floor((d - startDate) / (1000 * 60 * 60 * 24));
          const idx = Math.floor(dayDiff / 7);
          if (idx >= 0 && idx < durationWeeks) {
            const val = c.aliment_kg || c.kg || 0;
            alimentData[idx] = (alimentData[idx] || 0) + val;
          }
        });
      }

      const refCumul = this.buildReferenceCumul(durationWeeks);
      const cumulated = [];
      let acc = 0;
      let lastIdx = -1;
      alimentData.forEach((v, i) => {
        if (v !== null) {
          acc += v;
          lastIdx = i;
        }
        cumulated.push(lastIdx >= 0 && i <= lastIdx ? acc : null);
      });

      const trimmedAliment = alimentData.map((v, i) => (lastIdx >= 0 && i <= lastIdx ? (v ?? 0) : null));
      return { labels, alimentData: trimmedAliment, cumulated, refCumul };
    },

    buildReferenceCumul(length) {
      if (length === 0) return [];
      const ref = [];
      let acc = 0;
      for (let i = 0; i < length; i += 1) {
        const weekly = 1.4 + i * 0.6;
        acc += weekly;
        ref.push(parseFloat(acc.toFixed(2)));
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
