<template>
  <ChartBase
    ref="chart"
    :chart-id="chartId"
    chart-type="line"
    :height="height"
    :width="width"
  />
</template>

<script>
import ChartBase from './commun/ChartBase.vue';

export default {
  name: 'GainsLineChart',
  components: { ChartBase },
  props: {
    labels: { type: Array, default: () => [] },
    actual: { type: Array, default: () => [] },
    reference: { type: Array, default: () => [] },
    height: { type: [String, Number], default: 280 },
    width: { type: [String, Number], default: '100%' }
  },
  data() {
    return { chartId: `gains-line-${Math.random().toString(36).slice(2, 9)}` };
  },
  watch: {
    labels: { handler() { this.render(); }, deep: true },
    actual: { handler() { this.render(); }, deep: true },
    reference: { handler() { this.render(); }, deep: true }
  },
  mounted() {
    this.render();
  },
  methods: {
    render() {
      const chart = this.$refs.chart;
      if (!chart) return;
      chart.getChartData = this.getChartData;
      chart.getChartOptions = this.getChartOptions;
      this.$nextTick(() => chart.renderChart());
    },
    getChartData() {
      return {
        labels: this.labels,
        datasets: [
          {
            label: 'Gains observés',
            data: this.actual,
            borderColor: '#16a34a',
            backgroundColor: 'rgba(22,163,74,0.15)',
            borderWidth: 3,
            pointRadius: 4,
            tension: 0.3,
            fill: true
          },
          {
            label: 'Gains de référence',
            data: this.reference,
            borderColor: '#2563eb',
            backgroundColor: 'rgba(37,99,235,0.1)',
            borderDash: [6, 6],
            borderWidth: 2,
            pointRadius: 3,
            tension: 0.25,
            fill: false
          }
        ]
      };
    },
    getChartOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom' },
          tooltip: {
            callbacks: {
              label: ctx => `${ctx.dataset.label}: ${Number(ctx.parsed.y || 0).toLocaleString('fr-FR')} FCFA`
            }
          }
        },
        scales: {
          x: { title: { display: true, text: 'Semaines' } },
          y: {
            title: { display: true, text: 'Gains (FCFA)' },
            beginAtZero: true
          }
        }
      };
    }
  }
};
</script>
