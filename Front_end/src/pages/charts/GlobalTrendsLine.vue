<template>
  <ChartBase
    ref="chart"
    :chart-id="chartId"
    chart-type="line"
    :height="height"
  />
</template>

<script>
import ChartBase from './commun/ChartBase.vue';

export default {
  name: 'GlobalTrendsLine',
  components: { ChartBase },
  props: {
    trendData: { type: Array, default: () => [] },
    height: { type: [String, Number], default: 260 }
  },
  data() { return { chartId: `global-trends-${Math.random().toString(36).slice(2,9)}` }; },
  watch: { trendData: { handler() { this.render(); }, deep: true } },
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
      const labels = (this.trendData || []).map(t => t.week ? `S${t.week}` : t.label || '');
      const values = (this.trendData || []).map(t => Number(t.mean_weight || 0));
      const ACCENT = (getComputedStyle(document.documentElement).getPropertyValue('--primary-accent') || '#6f42c1').trim();
      const fill = ACCENT.includes('rgba') ? ACCENT : `${ACCENT}1A`;
      return { labels, datasets: [{ label: 'Poids moyen (g)', data: values, borderColor: ACCENT, backgroundColor: fill, tension: 0.3, fill: true }] };
    },
    getChartOptions() {
      return { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: false, title: { display: true, text: 'g' } } } };
    }
  }
};
</script>
