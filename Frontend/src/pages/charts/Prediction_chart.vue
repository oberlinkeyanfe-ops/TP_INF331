<template>
  <div class="prediction-charts">
    <div class="chart-row">
      <div class="chart-item">
        <h3>Prédiction poids</h3>
        <chart-base
          :chart-id="weightChartId"
          :chart-type="'line'"
          :height="260"
          ref="weight"
        />
      </div>
      <div class="chart-item">
        <h3>Prédiction coûts</h3>
        <chart-base
          :chart-id="costChartId"
          :chart-type="'line'"
          :height="260"
          ref="cost"
        />
      </div>
    </div>
    <div class="chart-row">
      <div class="chart-item full">
        <h3>Rentabilité prédite</h3>
        <chart-base
          :chart-id="profitChartId"
          :chart-type="'line'"
          :height="260"
          ref="profit"
        />
      </div>
    </div>
  </div>
</template>

<script>
import ChartBase from './commun/ChartBase.vue';

export default {
  name: 'PredictionCharts',
  components: { ChartBase },
  props: {
    predictions: {
      type: Array,
      default: () => []
    }
  },
  data() {
    const suffix = Math.random().toString(36).slice(2, 9);
    return {
      weightChartId: `pred-weight-${suffix}`,
      costChartId: `pred-cost-${suffix}`,
      profitChartId: `pred-profit-${suffix}`
    };
  },
  mounted() {
    this.renderAll();
  },
  watch: {
    predictions: {
      deep: true,
      handler() {
        this.renderAll();
      }
    }
  },
  methods: {
    renderAll() {
      this.$nextTick(() => {
        this.renderWeight();
        this.renderCost();
        this.renderProfit();
      });
    },
    baseData(key) {
      const sorted = [...(this.predictions || [])].sort((a, b) => a.jour - b.jour);
      const labels = sorted.map(p => p.date || `J+${p.jour}`);
      const values = sorted.map(p => p[key] || 0);
      return { labels, values };
    },
    renderWeight() {
      const c = this.$refs.weight;
      if (!c) return;
      const { labels, values } = this.baseData('poids');
      c.getChartData = () => ({
        labels,
        datasets: [{
          label: 'Poids (kg)',
          data: values,
          borderColor: '#4CAF50',
          backgroundColor: 'rgba(76,175,80,0.15)',
          borderWidth: 2,
          tension: 0.25,
          fill: true
        }]
      });
      c.getChartOptions = () => ({ responsive: true, maintainAspectRatio: false });
      this.$nextTick(() => c.renderChart());
    },
    renderCost() {
      const c = this.$refs.cost;
      if (!c) return;
      const { labels, values } = this.baseData('cout');
      c.getChartData = () => ({
        labels,
        datasets: [{
          label: 'Coût (€)',
          data: values,
          borderColor: '#2196F3',
          backgroundColor: 'rgba(33,150,243,0.15)',
          borderWidth: 2,
          tension: 0.25,
          fill: true
        }]
      });
      c.getChartOptions = () => ({ responsive: true, maintainAspectRatio: false });
      this.$nextTick(() => c.renderChart());
    },
    renderProfit() {
      const c = this.$refs.profit;
      if (!c) return;
      const { labels, values } = this.baseData('marge');
      const cumulative = values.map((_, i) => values.slice(0, i + 1).reduce((a, b) => a + b, 0));
      c.getChartData = () => ({
        labels,
        datasets: [{
          label: 'Cumul des marges (€)',
          data: cumulative,
          borderColor: '#FF9800',
          backgroundColor: 'rgba(255,152,0,0.15)',
          borderWidth: 2,
          tension: 0.25,
          fill: true
        }]
      });
      c.getChartOptions = () => ({ responsive: true, maintainAspectRatio: false });
      this.$nextTick(() => c.renderChart());
    }
  }
};
</script>

<style scoped>
.prediction-charts {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.chart-row {
  display: flex;
  gap: 16px;
}
.chart-item {
  flex: 1;
  background: white;
  border-radius: 8px;
  padding: 12px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.08);
}
.chart-item.full {
  flex: 100%;
}
 h3 { margin: 0 0 8px; font-size: 14px; }
</style>
