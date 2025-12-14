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
  name: 'HydrationAreaChart',
  components: { ChartBase },
  props: {
    band: { type: Object, default: () => ({}) },
    consommations: { type: Array, default: () => [] },
    height: { type: [String, Number], default: 260 },
    width: { type: [String, Number], default: '100%' }
  },
  data() {
    return { chartId: `hydration-${Math.random().toString(36).slice(2, 9)}` };
  },
  watch: {
    band: { deep: true, handler() { this.render(); } },
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
    buildSeries() {
      const durationWeeks = Math.max(1, Math.ceil((parseInt(this.band?.duree_jours, 10) || 42) / 7));
      const labels = Array.from({ length: durationWeeks }, (_, i) => `S${i + 1}`);
      const feed = Array(durationWeeks).fill(null);
      const water = Array(durationWeeks).fill(null);

      (this.consommations || []).forEach(c => {
        const week = Number(c.semaine_production || 0) || null;
        if (!week || week < 1 || week > durationWeeks) return;
        const idx = week - 1;
        feed[idx] = (feed[idx] || 0) + (Number(c.kg) || 0);
        water[idx] = (water[idx] || 0) + (Number(c.eau_litres) || 0);
      });

      const lastIdx = Math.max(
        feed.reduce((acc, v, i) => (v !== null ? i : acc), -1),
        water.reduce((acc, v, i) => (v !== null ? i : acc), -1)
      );

      return {
        labels,
        feed: feed.map((v, i) => (lastIdx >= 0 && i <= lastIdx ? (v ?? 0) : null)),
        water: water.map((v, i) => (lastIdx >= 0 && i <= lastIdx ? (v ?? 0) : null))
      };
    },
    getChartData() {
      const { labels, feed, water } = this.buildSeries();
      return {
        labels,
        datasets: [
          {
            label: 'Aliment (kg)',
            data: feed,
            fill: true,
            borderColor: '#3b82f6',
            backgroundColor: 'rgba(59, 130, 246, 0.15)',
            tension: 0.25,
            borderWidth: 2,
            spanGaps: false,
            stack: 'hydr'
          },
          {
            label: 'Eau (L)',
            data: water,
            fill: true,
            borderColor: '#14b8a6',
            backgroundColor: 'rgba(20, 184, 166, 0.16)',
            tension: 0.25,
            borderWidth: 2,
            spanGaps: false,
            stack: 'hydr'
          }
        ]
      };
    },
    getChartOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'top' },
          tooltip: { mode: 'index', intersect: false }
        },
        interaction: { mode: 'index', intersect: false },
        scales: {
          y: { beginAtZero: true, title: { display: true, text: 'Volumes' } },
          x: { ticks: { maxRotation: 0 } }
        }
      };
    }
  },
  mounted() {
    this.render();
  }
};
</script>
