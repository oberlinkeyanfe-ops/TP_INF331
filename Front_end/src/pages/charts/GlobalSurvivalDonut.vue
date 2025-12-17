<template>
  <ChartBase
    ref="chart"
    :chart-id="chartId"
    chart-type="pie"
    :height="height"
  />
</template>

<script>
import ChartBase from './commun/ChartBase.vue';

export default {
  name: 'GlobalSurvivalDonut',
  components: { ChartBase },
  props: {
    performanceData: { type: Array, default: () => [] },
    height: { type: [String, Number], default: 260 }
  },
  data() { return { chartId: `global-surv-${Math.random().toString(36).slice(2,9)}` }; },
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
      // survival in % or compute from nombre_animaux and taux_mortalite
      const values = (this.performanceData || []).map(p => {
        if (p.taux_mortalite !== undefined) return Math.max(0, 100 - Number(p.taux_mortalite));
        return Number(p.survival_rate || 0);
      });
      const ACCENT = (getComputedStyle(document.documentElement).getPropertyValue('--primary-accent') || '#6f42c1').trim();
      const SUCCESS = (getComputedStyle(document.documentElement).getPropertyValue('--success') || '#10b981').trim();
      const WARNING = (getComputedStyle(document.documentElement).getPropertyValue('--warning') || '#f59e0b').trim();
      const DANGER = (getComputedStyle(document.documentElement).getPropertyValue('--danger') || '#ef4444').trim();
      const palette = [ACCENT, SUCCESS, WARNING, DANGER];
      return { labels, datasets: [{ label: 'Taux de survie (%)', data: values, backgroundColor: labels.map((_,i) => palette[i % palette.length]) }] };
    },
    getChartOptions() {
      return { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right' } } };
    }
  }
};
</script>
