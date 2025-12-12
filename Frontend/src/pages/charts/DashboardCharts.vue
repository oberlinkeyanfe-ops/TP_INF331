<template>
  <div class="dashboard-charts">
    <div class="charts-row">
      <div class="chart-item">
        <h3>Évolution du poids</h3>
        <WeightChart 
          :band="band"
          :consommations="consommations"
          height="220"
        />
      </div>
      
      <div class="chart-item">
        <h3>Consommation quotidienne</h3>
        <ConsumptionChart 
          :band="band"
          :consommations="consommations"
          height="220"
        />
      </div>
    </div>
    
    <div class="charts-row">
      <div class="chart-item full-width">
        <h3>Performances globales</h3>
        <PerformanceChart 
          :band="band"
          :consommations="consommations"
          height="300"
        />
      </div>
    </div>
  </div>
</template>

<script>
import WeightChart from './WeightChart.vue';
import ConsumptionChart from './Consommation_chart.vue';
import PerformanceChart from './PerformanceChart.vue';

export default {
  name: 'DashboardCharts',
  
  components: {
    WeightChart,
    ConsumptionChart,
    PerformanceChart
  },
  
  props: {
    band: {
      type: Object,
      default: () => ({})
    },
    consommations: {
      type: Array,
      default: () => []
    }
  }
};
</script>

<style scoped>
.dashboard-charts {
  margin-top: 20px;
}

.charts-row {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.chart-item {
  flex: 1;
}

.chart-item.full-width {
  flex: 100%;
}

h3 {
  margin-bottom: 10px;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}
</style>