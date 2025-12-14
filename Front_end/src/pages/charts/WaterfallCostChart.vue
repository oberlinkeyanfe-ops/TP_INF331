<template>
  <div class="chart-block">
    <ChartBase
      ref="chart"
      :chart-id="chartId"
      chart-type="bar"
      :height="260"
    />
  </div>
</template>

<script>
import ChartBase from './commun/ChartBase.vue';

export default {
  name: 'WaterfallCostChart',
  components: { ChartBase },
  props: {
    consommations: { type: Array, default: () => [] },
    band: { type: Object, default: () => ({}) }
  },
  data() {
    return {
      chartId: `waterfall-cost-${Math.random().toString(36).substr(2, 9)}`
    };
  },
  mounted() { this.render(); },
  watch: {
    consommations: { deep: true, handler() { this.render(); } },
    band: { deep: true, handler() { this.render(); } }
  },
  methods: {
    render() {
      const chart = this.$refs.chart;
      if (!chart) return;
      const { labels, base, delta } = this.buildSeries();
      chart.getChartData = () => ({
        labels,
        datasets: [
          {
            label: 'Base',
            data: base,
            backgroundColor: 'rgba(0,0,0,0)',
            borderColor: 'rgba(0,0,0,0)',
            stack: 'waterfall'
          },
          {
            label: 'Coût semaine',
            data: delta,
            backgroundColor: delta.map(v => v >= 0 ? 'rgba(59,130,246,0.7)' : 'rgba(239,68,68,0.7)'),
            borderColor: delta.map(v => v >= 0 ? 'rgba(37,99,235,0.9)' : 'rgba(185,28,28,0.9)'),
            borderWidth: 1,
            stack: 'waterfall'
          }
        ]
      });
      chart.getChartOptions = () => ({
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { stacked: true, ticks: { maxRotation: 45, minRotation: 45 } },
          y: { stacked: true, beginAtZero: true, title: { display: true, text: 'FCFA cumulés' } }
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: ctx => {
                const idx = ctx.dataIndex;
                const deltaVal = delta[idx] || 0;
                const cum = (base[idx] || 0) + deltaVal;
                return [`Semaine ${labels[idx]}`, `Coût semaine: ${deltaVal.toLocaleString()} FCFA`, `Cumul: ${cum.toLocaleString()} FCFA`];
              }
            }
          }
        }
      });
      this.$nextTick(() => chart.renderChart());
    },

    buildSeries() {
      const durationWeeks = Math.max(1, Math.ceil((parseInt(this.band?.duree_jours, 10) || 42) / 7));
      const labels = Array.from({ length: durationWeeks }, (_, i) => `S${i + 1}`);
      const weeklyCost = Array(durationWeeks).fill(null);

      (this.consommations || []).forEach(c => {
        const w = c.semaine_production;
        if (!w || w < 1 || w > durationWeeks) return;
        const idx = w - 1;
        const kg = Number(c.kg || 0);
        const eau = Number(c.eau_litres || 0);
        const pu = Number(c.prix_unitaire || 0);
        const puEau = Number(c.prix_eau_unitaire || 0);
        const total = Math.round(kg * pu + eau * puEau);
        weeklyCost[idx] = (weeklyCost[idx] || 0) + total;
      });

      const lastIdx = weeklyCost.reduce((acc, v, i) => (v !== null ? i : acc), -1);
      const base = [];
      const delta = [];
      let cumul = 0;
      for (let i = 0; i < weeklyCost.length; i += 1) {
        if (lastIdx >= 0 && i <= lastIdx) {
          base.push(cumul);
          const step = weeklyCost[i] ?? 0;
          delta.push(step);
          cumul += step;
        } else {
          base.push(null);
          delta.push(null);
        }
      }

      return { labels, base, delta };
    }
  }
};
</script>

<style scoped>
.chart-block { width: 100%; height: 260px; }
</style>
