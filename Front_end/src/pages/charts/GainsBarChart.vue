<template>
  <ChartBase
    ref="chart"
    :chart-id="chartId"
    chart-type="bar"
    :height="height"
    :width="width"
  />
</template>

<script>
import ChartBase from './commun/ChartBase.vue';

export default {
  name: 'GainsBarChart',
  components: { ChartBase },
  props: {
    labels: { type: Array, default: () => [] },
    actual: { type: Array, default: () => [] },
    reference: { type: Array, default: () => [] },
    height: { type: [String, Number], default: 260 },
    width: { type: [String, Number], default: '100%' }
  },
  data() {
    return { chartId: `gains-bar-${Math.random().toString(36).slice(2, 9)}` };
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
            label: 'Observé',
            data: this.actual,
            backgroundColor: 'rgba(34,197,94,0.6)',
            borderColor: '#16a34a',
            borderWidth: 1
          },
          {
            label: 'Référence',
            data: this.reference,
            backgroundColor: 'rgba(37,99,235,0.5)',
            borderColor: '#2563eb',
            borderWidth: 1
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
          x: {
            title: { display: true, text: 'Semaines' },
            stacked: false
          },
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
