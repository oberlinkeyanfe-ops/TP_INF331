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
  name: 'TreatmentUsageChart',
  components: { ChartBase },
  props: {
    treatments: { type: Array, default: () => [] },
    height: { type: [String, Number], default: 220 },
    width: { type: [String, Number], default: '100%' }
  },
  data() {
    return { chartId: `treat-${Math.random().toString(36).slice(2, 9)}` };
  },
  watch: {
    treatments: { deep: true, handler() { this.render(); } }
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
      (this.treatments || []).forEach(t => {
        const key = t?.produit || t?.name || 'Traitement';
        bucket.set(key, (bucket.get(key) || 0) + 1);
      });
      return [...bucket.entries()].sort((a, b) => b[1] - a[1]).slice(0, 6);
    },
    getChartData() {
      const data = this.aggregate();
      const labels = data.map(([k]) => k);
      const values = data.map(([, v]) => v);
      return {
        labels,
        datasets: [{
          label: 'Occurrences',
          data: values,
          backgroundColor: labels.map((_, i) => this.palette[i % this.palette.length]),
          borderRadius: 8,
          borderWidth: 0
        }]
      };
    },
    getChartOptions() {
      return {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { beginAtZero: true, ticks: { stepSize: 1 } },
          y: { grid: { display: false } }
        }
      };
    }
  },
  computed: {
    palette() {
      return ['#0ea5e9', '#22c55e', '#f59e0b', '#a855f7', '#ef4444', '#06b6d4'];
    }
  }
};
</script>
