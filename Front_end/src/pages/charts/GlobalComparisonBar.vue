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
  name: 'GlobalComparisonBar',
  components: { ChartBase },
  props: {
    performanceData: { type: Array, default: () => [] },
    metric: { type: String, default: 'consommation_par_animal' },
    height: { type: [String, Number], default: 260 }
  },
  data() { return { chartId: `global-compare-${Math.random().toString(36).slice(2,9)}` }; },
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
      const values = (this.performanceData || []).map(p => Number(p[this.metric] || 0));
      const ACCENT = (getComputedStyle(document.documentElement).getPropertyValue('--primary-accent') || '#6f42c1').trim();
      return { labels, datasets: [{ label: this.metric.replace(/_/g,' '), data: values, backgroundColor: ACCENT, borderColor: ACCENT }] };
    },
    getChartOptions() {
      return { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false }, tooltip: {} }, scales: { y: { beginAtZero: true, title: { display: true, text: this.metric } }, x: { title: { display: false } } } };
    }
  }
};
</script>
