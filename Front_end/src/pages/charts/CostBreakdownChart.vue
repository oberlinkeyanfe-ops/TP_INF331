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
  name: 'CostBreakdownChart',
  components: { ChartBase },
  props: {
    consommations: { type: Array, default: () => [] },
    height: { type: [String, Number], default: 260 },
    width: { type: [String, Number], default: '100%' }
  },
  data() {
    return { chartId: `cost-break-${Math.random().toString(36).slice(2, 9)}` };
  },
  watch: {
    consommations: { deep: true, handler() { this.render(); } }
  },
  methods: {
    render() {
      const chart = this.$refs.chart;
      if (!chart) return;
      chart.getChartData = this.getChartData;
      chart.getChartOptions = this.getChartOptions;
      this.$nextTick(() => chart.renderChart());
    },
    aggregate() {
      const bucket = new Map();
      (this.consommations || []).forEach(c => {
        const label = c?.type || 'Autre';
        const value = Number(c?.cout) || ((Number(c?.kg) || 0) * (Number(c?.prix_unitaire) || 0));
        bucket.set(label, (bucket.get(label) || 0) + value);
      });
      const sorted = [...bucket.entries()]
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5);
      return {
        labels: sorted.map(([k]) => k),
        values: sorted.map(([, v]) => +v.toFixed(2))
      };
    },
    getChartData() {
      const { labels, values } = this.aggregate();
      return {
        labels,
        datasets: [{
          label: 'Coût (FCFA)',
          data: values,
          backgroundColor: labels.map((_, idx) => this.palette[idx % this.palette.length]),
          borderWidth: 0,
          borderRadius: 10
        }]
      };
    },
    getChartOptions() {
      return {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { beginAtZero: true, ticks: { callback: (v) => `${v}` } },
          y: { grid: { display: false } }
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: ctx => `${ctx.formattedValue} FCFA`
            }
          }
        }
      };
    }
  },
  computed: {
    palette() {
      return ['#6366f1', '#22c55e', '#f59e0b', '#0ea5e9', '#ef4444'];
    }
  },
  mounted() {
    this.render();
  }
};
</script>
