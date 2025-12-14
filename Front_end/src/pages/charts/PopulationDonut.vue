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
  name: 'PopulationDonut',
  components: { ChartBase },
  props: {
    band: { type: Object, default: () => ({}) },
    survival: { type: Number, default: 0 },
    deaths: { type: Number, default: 0 },
    height: { type: [String, Number], default: 220 },
    width: { type: [String, Number], default: '100%' }
  },
  data() {
    return {
      chartId: `population-${Math.random().toString(36).slice(2, 9)}`
    };
  },
  computed: {
    initialCount() {
      return Number(this.band?.nombre_initial || 0);
    },
    deathCount() {
      return Number(this.deaths || this.band?.nombre_morts_totaux || 0);
    },
    survivors() {
      return Math.max(0, this.initialCount - this.deathCount);
    },
    survivalRate() {
      if (!this.initialCount) return 0;
      return Math.round((this.survivors / this.initialCount) * 100);
    }
  },
  watch: {
    band: { deep: true, handler() { this.render(); } },
    deaths() { this.render(); }
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
        labels: ['Survivants', 'Mortalité'],
        datasets: [{
          data: [this.survivors, this.deathCount],
          backgroundColor: ['#22c55e', '#ef4444'],
          hoverBackgroundColor: ['#16a34a', '#dc2626'],
          borderWidth: 0,
          cutout: '70%'
        }]
      };
    },
    getChartOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => {
                const total = this.survivors + this.deathCount || 1;
                const pct = Math.round((ctx.parsed / total) * 100);
                return `${ctx.label}: ${ctx.parsed} (${pct}%)`;
              }
            }
          }
        }
      };
    }
  },
  mounted() {
    this.render();
  }
};
</script>
