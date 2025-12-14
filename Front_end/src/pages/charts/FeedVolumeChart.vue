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
  name: 'FeedVolumeChart',
  components: { ChartBase },
  props: {
    band: { type: Object, default: () => ({}) },
    consommations: { type: Array, default: () => [] },
    height: { type: [String, Number], default: 220 },
    width: { type: [String, Number], default: '100%' }
  },
  data() {
    return { chartId: `feed-${Math.random().toString(36).slice(2, 9)}` };
  },
  watch: {
    band: { deep: true, handler() { this.render(); } },
    consommations: { deep: true, handler() { this.render(); } }
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
    buildSeries() {
      const durationWeeks = Math.max(1, Math.ceil((parseInt(this.band?.duree_jours, 10) || 42) / 7));
      const labels = Array.from({ length: durationWeeks }, (_, i) => `S${i + 1}`);
      const feed = Array(durationWeeks).fill(null);
      (this.consommations || []).forEach(c => {
        const w = Number(c.semaine_production || 0);
        if (!w || w < 1 || w > durationWeeks) return;
        const idx = w - 1;
        feed[idx] = (feed[idx] || 0) + (Number(c.kg) || 0);
      });
      const lastIdx = feed.reduce((acc, v, i) => (v !== null ? i : acc), -1);
      return {
        labels,
        feed: feed.map((v, i) => (lastIdx >= 0 && i <= lastIdx ? (v ?? 0) : null))
      };
    },
    getChartData() {
      const { labels, feed } = this.buildSeries();
      return {
        labels,
        datasets: [{
          label: 'Aliment (kg)',
          data: feed,
          backgroundColor: '#6366f1',
          borderRadius: 8,
          borderWidth: 0
        }]
      };
    },
    getChartOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, title: { display: true, text: 'Kg' } },
          x: { ticks: { maxRotation: 0 } }
        }
      };
    }
  }
};
</script>
