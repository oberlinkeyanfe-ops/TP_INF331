<template>
  <div class="dashboard-charts">
    <div class="charts-row primary-grid">
      <div class="chart-item stretch">
        <div class="chart-heading">
          <div class="heading-text">
            <p class="eyebrow">Poids</p>
            <h3>Évolution vs référence</h3>
          </div>
          <span class="chip">S{{ currentWeek }}</span>
        </div>
        <WeightChart 
          :band="band"
          :consommations="consommations"
          height="240"
        />
      </div>

      <div class="chart-item stretch">
        <div class="chart-heading">
          <div class="heading-text">
            <p class="eyebrow">Consommations</p>
            <h3>Apports hebdomadaires</h3>
          </div>
          <span class="chip secondary">{{ feedPerBird }} kg/poule</span>
        </div>
        <ConsumptionChart 
          :band="band"
          :consommations="consommations"
          height="240"
        />
      </div>

      <div class="chart-item compact">
        <div class="chart-heading">
          <div class="heading-text">
            <p class="eyebrow">Population</p>
            <h3>Survie & mortalité</h3>
          </div>
          <span class="chip ghost">{{ survivalRate }}% survie</span>
        </div>
        <PopulationDonut
          :band="band"
          :survival="survivalRate"
          :deaths="deathCount"
          height="210"
        />
        <div class="mini-metrics">
          <div class="mini">
            <span class="label">Arrivés</span>
            <strong>{{ initialCount }}</strong>
          </div>
          <div class="mini">
            <span class="label">Restants</span>
            <strong>{{ survivors }}</strong>
          </div>
          <div class="mini">
            <span class="label">Âge estimé</span>
            <strong>{{ ageLabel }}</strong>
          </div>
        </div>
      </div>
    </div>

    <div class="charts-row secondary-grid">
      <div class="chart-item">
        <div class="chart-heading">
          <div class="heading-text">
            <p class="eyebrow">Performance</p>
            <h3>Aliment & cumul</h3>
          </div>
          <span class="chip">IC: {{ feedIndex }}</span>
        </div>
        <PerformanceChart 
          :band="band"
          :consommations="consommations"
          height="280"
        />
      </div>

      <div class="chart-item">
        <div class="chart-heading">
          <div class="heading-text">
            <p class="eyebrow">Hydratation</p>
            <h3>Eau vs aliment</h3>
          </div>
          <span class="chip secondary">{{ waterPerBird }} L/poule</span>
        </div>
        <HydrationAreaChart
          :band="band"
          :consommations="consommations"
          height="280"
        />
      </div>

      <div class="chart-item">
        <div class="chart-heading">
          <div class="heading-text">
            <p class="eyebrow">Coûts</p>
            <h3>Répartition des charges</h3>
          </div>
          <span class="chip ghost">Top 5</span>
        </div>
        <CostBreakdownChart
          :consommations="consommations"
          height="280"
        />
      </div>
    </div>
  </div>
</template>

<script>
import WeightChart from './WeightChart.vue';
import ConsumptionChart from './Consommation_chart.vue';
import PerformanceChart from './PerformanceChart.vue';
import PopulationDonut from './PopulationDonut.vue';
import HydrationAreaChart from './HydrationAreaChart.vue';
import CostBreakdownChart from './CostBreakdownChart.vue';

export default {
  name: 'DashboardCharts',
  
  components: {
    WeightChart,
    ConsumptionChart,
    PerformanceChart,
    PopulationDonut,
    HydrationAreaChart,
    CostBreakdownChart
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
  },

  computed: {
    initialCount() {
      return Number(this.band?.nombre_initial || 0);
    },

    deathCount() {
      return Number(this.band?.nombre_morts_totaux || 0);
    },

    survivors() {
      return Math.max(0, this.initialCount - this.deathCount);
    },

    survivalRate() {
      if (!this.initialCount) return 0;
      return Math.round((this.survivors / this.initialCount) * 100);
    },

    currentWeek() {
      if (!this.band?.date_arrivee) return 1;
      const start = new Date(this.band.date_arrivee);
      const now = new Date();
      const diff = Math.max(0, Math.floor((now - start) / (1000 * 60 * 60 * 24)));
      return Math.max(1, Math.min(12, Math.floor(diff / 7) + 1));
    },

    feedIndex() {
      const cost = this.consommations.reduce((sum, c) => sum + (Number(c.cout) || 0), 0);
      const animals = this.survivors || this.initialCount;
      if (!animals || !cost) return 0;
      return (cost / animals).toFixed(2);
    },

    feedPerBird() {
      const animals = this.initialCount || 0;
      if (!animals) return '0.00';
      const totalKg = this.consommations.reduce((sum, c) => sum + (Number(c.kg) || 0), 0);
      return (totalKg / animals).toFixed(2);
    },

    waterPerBird() {
      const animals = this.initialCount || 0;
      if (!animals) return '0.00';
      const totalWater = this.consommations.reduce((sum, c) => sum + (Number(c.eau_litres) || 0), 0);
      return (totalWater / animals).toFixed(2);
    },

    ageLabel() {
      if (!this.band?.date_arrivee) return '—';
      const start = new Date(this.band.date_arrivee);
      const now = new Date();
      const diffDays = Math.max(0, Math.floor((now - start) / (1000 * 60 * 60 * 24)));
      if (diffDays < 14) return `${diffDays} j`;
      const weeks = Math.floor(diffDays / 7);
      return `${weeks} sem`;
    }
  }
};
</script>

<style scoped>
.dashboard-charts {
  display: flex;
  flex-direction: column;
  gap: 18px;
  width: 100%;
}

.charts-row {
  display: grid;
  gap: 18px;
}

.primary-grid {
  grid-template-columns: 2fr 2fr 1.2fr;
}

.secondary-grid {
  grid-template-columns: repeat(3, 1fr);
}

.chart-item {
  background: white;
  border-radius: 18px;
  box-shadow: 0 18px 60px rgba(27, 39, 60, 0.08);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  border: 1px solid #eef2f7;
}

.chart-item.stretch {
  min-height: 320px;
}

.chart-item.compact {
  min-height: 320px;
}

.chart-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.heading-text h3 {
  margin: 0;
  color: #1f2937;
  font-size: 16px;
  font-weight: 700;
}

.eyebrow {
  margin: 0;
  color: #6b7280;
  font-size: 12px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.chip {
  background: #eef2ff;
  color: #4338ca;
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  border: 1px solid #e0e7ff;
}

.chip.secondary {
  background: #ecfdf3;
  color: #166534;
  border-color: #d1fae5;
}

.chip.ghost {
  background: #f8fafc;
  color: #0f172a;
  border-color: #e2e8f0;
}

.mini-metrics {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.mini {
  background: #f8fafc;
  border-radius: 12px;
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.mini .label {
  font-size: 12px;
  color: #6b7280;
}

.mini strong {
  font-size: 16px;
  color: #111827;
}

@media (max-width: 1200px) {
  .primary-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .chart-item.compact {
    grid-column: span 2;
  }
  .secondary-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 900px) {
  .primary-grid,
  .secondary-grid {
    grid-template-columns: 1fr;
  }
  .chart-item.compact {
    grid-column: span 1;
  }
}
</style>