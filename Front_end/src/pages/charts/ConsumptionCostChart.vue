<template>
  <div class="chart-block">
    <ChartBase
      ref="chart"
      :chart-id="chartId"
      chart-type="line"
      :height="300"
    />
  </div>
</template>

<script>
import ChartBase from './commun/ChartBase.vue';

export default {
  name: 'ConsumptionCostChart',
  components: { ChartBase },
  props: {
    consommations: { type: Array, default: () => [] },
    band: { type: Object, default: () => ({}) },
    consumptionReference: { type: Array, default: () => [] }
  },
  data() {
    return {
      chartId: `consumption-cost-${Math.random().toString(36).substr(2, 9)}`
    };
  },
  mounted() { this.render(); },
  watch: {
    consommations: { deep: true, handler() { this.render(); } },
    band: { deep: true, handler() { this.render(); } },
    consumptionReference: { deep: true, handler() { this.render(); } }
  },
  methods: {
    render() {
      const chart = this.$refs.chart;
      if (!chart) return;
      const { labels, actualCost, refCost } = this.buildSeries();
      chart.getChartData = () => ({
        labels,
        datasets: [
          {
            label: 'Coût réel (FCFA)',
            data: actualCost,
            borderColor: '#ef4444',
            backgroundColor: 'rgba(239, 68, 68, 0.15)',
            borderWidth: 2,
            tension: 0.25,
            fill: true,
            spanGaps: false
          },
          {
            label: 'Référence (FCFA)',
            data: refCost,
            borderColor: '#f97316',
            backgroundColor: 'rgba(249, 115, 22, 0.1)',
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
          y: { beginAtZero: true, title: { display: true, text: 'FCFA' } },
          x: { ticks: { maxRotation: 45, minRotation: 45 } }
        }
      });
      this.$nextTick(() => chart.renderChart());
    },

    buildSeries() {
      const durationWeeks = Math.max(1, Math.ceil((parseInt(this.band?.duree_jours, 10) || 42) / 7));
      const labels = Array.from({ length: durationWeeks }, (_, i) => `Sem ${i + 1}`);

      const actualCost = Array(durationWeeks).fill(null);
      (this.consommations || []).forEach(c => {
        const w = c.semaine_production;
        if (!w || w < 1 || w > durationWeeks) return;
        const idx = w - 1;
        const kg = Number(c.kg || 0);
        const eau = Number(c.eau_litres || 0);
        const pu = Number(c.prix_unitaire || 0);
        const puEau = Number(c.prix_eau_unitaire || 0);
        const total = kg * pu + eau * puEau;
        actualCost[idx] = (actualCost[idx] || 0) + Math.round(total);
      });

      const avgFeedPrice = this.averageUnitPrice(this.consommations, 'aliment');
      const avgWaterPrice = this.averageUnitPrice(this.consommations, 'eau');

      const refCost = Array(durationWeeks).fill(null);
      for (let i = 0; i < durationWeeks; i += 1) {
        const ref = (this.consumptionReference || []).find(r => r.week === i + 1);
        if (!ref) continue;
        const cost = (avgFeedPrice || 0) * (ref.aliment_kg || 0) + (avgWaterPrice || 0) * (ref.eau_litres || 0);
        refCost[i] = Math.round(cost);
      }

      const lastIdx = actualCost.reduce((acc, v, i) => (v !== null ? i : acc), -1);
      const trimmedActual = actualCost.map((v, i) => (lastIdx >= 0 && i <= lastIdx ? (v ?? 0) : null));
      const trimmedRef = refCost.map((v, i) => (lastIdx >= 0 && i <= lastIdx ? (v ?? null) : null));

      return { labels, actualCost: trimmedActual, refCost: trimmedRef };
    },

    averageUnitPrice(consommations, type) {
      const values = (consommations || [])
        .map(c => type === 'eau' ? Number(c.prix_eau_unitaire || 0) : Number(c.prix_unitaire || 0))
        .filter(v => Number.isFinite(v) && v > 0);
      if (!values.length) return 0;
      return values.reduce((a, b) => a + b, 0) / values.length;
    }
  }
};
</script>

<style scoped>
.chart-block { width: 100%; height: 320px; }
</style>
