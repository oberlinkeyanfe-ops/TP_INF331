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
  name: 'GlobalMortalityBar',
  components: { ChartBase },
  props: {
    performanceData: { type: Array, default: () => [] },
    height: { type: [String, Number], default: 260 }
  },
  data() { return { chartId: `global-mort-${Math.random().toString(36).slice(2,9)}` }; },
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
      const values = (this.performanceData || []).map(p => Number(p.taux_mortalite || 0));
      const DANGER = (getComputedStyle(document.documentElement).getPropertyValue('--danger') || '#ef4444').trim();
      return { labels, datasets: [{ label: 'Taux mortalité (%)', data: values, backgroundColor: DANGER, borderColor: DANGER }] };
    },
    getChartOptions() {
      return { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, title: { display: true, text: '%' } } } };
    }
  }
};
</script>
