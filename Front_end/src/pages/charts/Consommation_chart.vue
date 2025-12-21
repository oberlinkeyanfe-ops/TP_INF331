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
      const { labels, perBirdData, refPerBird } = this.buildTimeseries();
      chart.getChartData = () => ({
        labels,
        datasets: [
          {
            label: 'Consommation / poule (kg)',
            data: perBirdData,
            borderColor: '#2196F3',
            backgroundColor: 'rgba(33,150,243,0.15)',
            borderWidth: 2,
            tension: 0.25,
            fill: true,
            spanGaps: false
          },
          {
            label: 'Référence / poule (kg)',
            data: refPerBird,
            borderColor: '#FF9800',
            backgroundColor: 'rgba(255, 152, 0, 0.1)',
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
          y: { beginAtZero: true, title: { display: true, text: 'Kg / poule' } },
          x: { ticks: { maxRotation: 45, minRotation: 45 } }
        }
      });
      this.$nextTick(() => chart.renderChart());
    },

    buildTimeseries() {
      const durationWeeks = Math.max(1, Math.ceil((parseInt(this.band?.duree_jours, 10) || 42) / 7));
      const startDate = this.band?.date_arrivee ? new Date(this.band.date_arrivee) : null;
      const labels = Array.from({ length: durationWeeks }, (_, i) => `Sem ${i + 1}`);

      const kgTotals = Array(durationWeeks).fill(null);
      if (startDate) {
        (this.consommations || []).forEach(c => {
          const d = c?.date ? new Date(c.date) : null;
          if (!d) return;
          const dayDiff = Math.floor((d - startDate) / (1000 * 60 * 60 * 24));
          const idx = Math.floor(dayDiff / 7);
          if (idx >= 0 && idx < durationWeeks) {
            const val = c.aliment_kg || c.kg || 0;
            kgTotals[idx] = (kgTotals[idx] || 0) + val;
          }
        });
      }

      const lastIdx = kgTotals.reduce((acc, v, i) => (v !== null ? i : acc), -1);
      const trimmedKgTotals = kgTotals.map((v, i) => (lastIdx >= 0 && i <= lastIdx ? (v ?? 0) : null));

      const population = parseFloat(this.band?.nombre_initial || 0) || 0;
      const perBirdData = trimmedKgTotals.map(v => {
        if (v === null) return null;
        if (!population) return 0;
        return +(v / population).toFixed(4);
      });

      const refBase = this.band?.consumptionReference || this.$parent?.consumptionReference || [];
      const refPerBird = labels.map((_, idx) => {
        const ref = refBase.find(r => r.week === idx + 1);
        if (!ref) return null;
        if (!population) return 0;
        // Prefer per-bird range when available
        if (ref.per_bird_low != null && ref.per_bird_high != null) {
          const perBirdAvg = (Number(ref.per_bird_low) + Number(ref.per_bird_high)) / 2.0;
          return +perBirdAvg.toFixed(4);
        }
        return +((ref.aliment_kg || 0) / population).toFixed(4);
      });

      return { labels, perBirdData, refPerBird };
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
