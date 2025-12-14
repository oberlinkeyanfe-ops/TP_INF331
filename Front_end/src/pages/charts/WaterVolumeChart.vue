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
  name: 'WaterVolumeChart',
  components: { ChartBase },
  props: {
    band: { type: Object, default: () => ({}) },
    consommations: { type: Array, default: () => [] },
    height: { type: [String, Number], default: 220 },
    width: { type: [String, Number], default: '100%' }
  },
  data() {
    return { chartId: `water-${Math.random().toString(36).slice(2, 9)}` };
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
      const water = Array(durationWeeks).fill(null);
      (this.consommations || []).forEach(c => {
        const w = Number(c.semaine_production || 0);
        if (!w || w < 1 || w > durationWeeks) return;
        const idx = w - 1;
        water[idx] = (water[idx] || 0) + (Number(c.eau_litres) || 0);
      });
      const lastIdx = water.reduce((acc, v, i) => (v !== null ? i : acc), -1);
      return {
        labels,
        water: water.map((v, i) => (lastIdx >= 0 && i <= lastIdx ? (v ?? 0) : null))
      };
    },
    getChartData() {
      const { labels, water } = this.buildSeries();
      return {
        labels,
        datasets: [{
          label: 'Eau (L)',
          data: water,
          borderColor: '#0ea5e9',
          backgroundColor: 'rgba(14,165,233,0.16)',
          borderWidth: 2,
          tension: 0.25,
          fill: true,
          spanGaps: false
        }]
      };
    },
    getChartOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, title: { display: true, text: 'Litres' } },
          x: { ticks: { maxRotation: 0 } }
        }
      };
    }
  }
};
</script>
