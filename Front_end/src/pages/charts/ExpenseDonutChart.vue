<template>
  <ChartBase
    ref="chart"
    :chart-id="chartId"
    chart-type="doughnut"
    :height="height"
    :width="width"
  />
</template>

<script>
import ChartBase from './commun/ChartBase.vue';

export default {
  name: 'ExpenseDonutChart',
  components: { ChartBase },
  props: {
    expenses: { type: Array, default: () => [] },
    height: { type: [String, Number], default: 220 },
    width: { type: [String, Number], default: '100%' }
  },
  data() {
    return { chartId: `expense-${Math.random().toString(36).slice(2, 9)}` };
  },
  watch: {
    expenses: { deep: true, handler() { this.render(); } }
  },
  mounted() { this.render(); },
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
      (this.expenses || []).forEach(e => {
        const key = e?.tache || e?.name || 'Autre';
        bucket.set(key, (bucket.get(key) || 0) + (Number(e?.montant) || 0));
      });
      return [...bucket.entries()].sort((a, b) => b[1] - a[1]).slice(0, 6);
    },
    getChartData() {
      const data = this.aggregate();
      const labels = data.map(([k]) => k);
      const values = data.map(([, v]) => +v.toFixed(0));
      return {
        labels,
        datasets: [{
          data: values,
          backgroundColor: labels.map((_, i) => this.palette[i % this.palette.length]),
          borderWidth: 1,
          cutout: '65%'
        }]
      };
    },
    getChartOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: 'bottom' } }
      };
    }
  },
  computed: {
    palette() {
      return ['#6366f1', '#22c55e', '#f59e0b', '#0ea5e9', '#ef4444', '#a855f7'];
    }
  }
};
</script>
