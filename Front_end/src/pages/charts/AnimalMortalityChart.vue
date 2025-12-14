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
  name: 'AnimalMortalityChart',
  components: { ChartBase },
  props: {
    labels: { type: Array, default: () => [] },
    series: { type: Array, default: () => [] },
    refLow: { type: Array, default: () => [] },
    refHigh: { type: Array, default: () => [] },
    height: { type: [String, Number], default: 280 },
    width: { type: [String, Number], default: '100%' }
  },
  data() {
    return { chartId: `animal-mortality-${Math.random().toString(36).slice(2, 9)}` };
  },
  watch: {
    labels: { handler() { this.render(); }, deep: true },
    series: { handler() { this.render(); }, deep: true },
    refLow: { handler() { this.render(); }, deep: true },
    refHigh: { handler() { this.render(); }, deep: true }
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
            label: 'Mortalité observée (%)',
            data: this.series,
            borderColor: '#ef4444',
            backgroundColor: 'rgba(239,68,68,0.15)',
            borderWidth: 3,
            pointRadius: 4,
            tension: 0.3,
            fill: false
          },
          {
            label: 'Réf. basse (%)',
            data: this.refLow,
            borderColor: '#16a34a',
            backgroundColor: 'rgba(22,163,74,0.08)',
            borderDash: [6, 6],
            borderWidth: 2,
            pointRadius: 0,
            tension: 0.2,
            fill: false
          },
          {
            label: 'Réf. haute (%)',
            data: this.refHigh,
            borderColor: '#eab308',
            backgroundColor: 'rgba(234,179,8,0.1)',
            borderDash: [4, 6],
            borderWidth: 2,
            pointRadius: 0,
            tension: 0.2,
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
          tooltip: { callbacks: { label: ctx => `${ctx.dataset.label}: ${ctx.parsed.y ?? 0}%` } }
        },
        scales: {
          x: { title: { display: true, text: 'Semaines' } },
          y: {
            title: { display: true, text: 'Taux (%)' },
            beginAtZero: true,
            suggestedMax: 5
          }
        }
      };
    }
  }
};
</script>
