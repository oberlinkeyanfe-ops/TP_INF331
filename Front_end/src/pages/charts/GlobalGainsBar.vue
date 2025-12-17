<template>
  <ChartBase
    ref="chart"
    :chart-id="chartId"
    chart-type="bar"
    :height="height"
  />
</template>

<script>
import ChartBase from './commun/ChartBase.vue';

export default {
  name: 'GlobalGainsBar',
  components: { ChartBase },
  props: {
    performanceData: { type: Array, default: () => [] },
    height: { type: [String, Number], default: 260 }
  },
  data() { return { chartId: `global-gains-${Math.random().toString(36).slice(2,9)}` }; },
  watch: { performanceData: { handler() { this.render(); }, deep: true } },
  mounted() { this.render(); },
  methods: {
    render() {
      const chart = this.$refs.chart;
      if (!chart) return;
      chart.getChartData = this.getChartData;
      chart.getChartOptions = this.getChartOptions;
      this.$nextTick(() => chart.renderChart());
    },
    getChartData() {
      const labels = (this.performanceData || []).map(p => p.nom_bande || `#${p.bande_id}`);
      const gains = (this.performanceData || []).map(p => Number(p.gains || 0));
      const SUCCESS = (getComputedStyle(document.documentElement).getPropertyValue('--success') || '#10b981').trim();
      return {
        labels,
        datasets: [
          { label: 'Gains estimés (FCFA)', data: gains, backgroundColor: labels.map(() => SUCCESS), borderColor: SUCCESS }
        ]
      };
    },
    getChartOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, title: { display: true, text: 'FCFA' } }
        }
      };
    }
  }
};
</script>
