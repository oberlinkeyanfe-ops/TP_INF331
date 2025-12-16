<template>
  <div class="chart-block">
    <ChartBase
      ref="chart"
      :chart-id="chartId"
      chart-type="bar"
      :height="260"
    />
  </div>
</template>

<script>
import ChartBase from './commun/ChartBase.vue';

export default {
  name: 'WaterfallCostChart',
  components: { ChartBase },
  props: {
    consommations: { type: Array, default: () => [] },
    band: { type: Object, default: () => ({}) },
    predictions: { type: Array, default: null },
    optimalPrediction: { type: Object, default: null },
    mode: { type: String, default: 'dashboard' }, // 'dashboard' | 'predictions'
    revenueCurrent: { type: Number, default: null }
  },
  data() {
    return {
      chartId: `waterfall-cost-${Math.random().toString(36).substr(2, 9)}`
    };
  },
  mounted() { this.render(); },
  watch: {
    consommations: { deep: true, handler() { this.render(); } },
    band: { deep: true, handler() { this.render(); } }
  },
  methods: {
    render() {
      const chart = this.$refs.chart;
      if (!chart) return;
      const { labels, base, delta } = this.buildSeries();
      chart.getChartData = () => ({
        labels,
        datasets: [
          {
            label: 'Base',
            data: base,
            backgroundColor: 'rgba(0,0,0,0)',
            borderColor: 'rgba(0,0,0,0)',
            stack: 'waterfall'
          },
          {
            label: 'Coût semaine',
            data: delta,
            backgroundColor: delta.map(v => v >= 0 ? 'rgba(59,130,246,0.7)' : 'rgba(239,68,68,0.7)'),
            borderColor: delta.map(v => v >= 0 ? 'rgba(37,99,235,0.9)' : 'rgba(185,28,28,0.9)'),
            borderWidth: 1,
            stack: 'waterfall'
          }
        ]
      });
      chart.getChartOptions = () => ({
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { stacked: true, ticks: { maxRotation: 45, minRotation: 45 } },
          y: { stacked: true, beginAtZero: true, title: { display: true, text: 'FCFA cumulés' } }
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: ctx => {
                const idx = ctx.dataIndex;
                const deltaVal = delta[idx] || 0;
                const cum = (base[idx] || 0) + deltaVal;
                return [`Semaine ${labels[idx]}`, `Coût semaine: ${deltaVal.toLocaleString()} FCFA`, `Cumul: ${cum.toLocaleString()} FCFA`];
              }
            }
          }
        }
      });
      this.$nextTick(() => chart.renderChart());
    },

    buildSeries() {
      // If an optimal prediction is provided, show a single-step waterfall:
      // Revenu total -> Coûts par poste (négatifs) -> Marge nette
      // If mode is 'predictions' and an optimal prediction is provided, use predicted revenue
      if (this.mode === 'predictions' && this.optimalPrediction) {
        const opt = this.optimalPrediction || {};
        const revenue = Number(opt.valeur || 0);
        const predictedConsumptionCost = Number(opt.cout || 0);
        const treatmentCosts = Number(this.$parent?.totalTreatmentCost ?? this.$parent?.totalTreatmentCost ?? 0) || 0;
        const elementaryExpenses = Number(this.$parent?.totalExpensesElementaires ?? 0) || 0;

        const costs = [
          { key: 'consommation', label: 'Consommations', value: -predictedConsumptionCost },
          { key: 'traitements', label: 'Traitements', value: -treatmentCosts },
          { key: 'depenses', label: 'Dépenses élémentaires', value: -elementaryExpenses }
        ];

        const labels = ['Revenu total', ...costs.map(c => c.label), 'Marge nette'];
        const base = [];
        const delta = [];
        let cumul = 0;

        // Revenu
        base.push(0);
        delta.push(Math.round(revenue));
        cumul += revenue;

        // Costs as negative steps
        for (const c of costs) {
          base.push(Math.round(cumul));
          const step = Math.round(c.value || 0);
          delta.push(step);
          cumul += step;
        }

        // Final net margin (should equal cumul)
        base.push(Math.round(cumul - (Math.round(cumul) || 0)) );
        // push null for base and push value representing final margin as 0 to show final point via base+delta
        delta.push(0);

        return { labels, base, delta };
      }

      // If mode is 'dashboard', use provided current revenue (observed cumulative revenue)
      if (this.mode === 'dashboard' && (this.revenueCurrent !== null && this.revenueCurrent !== undefined)) {
        const revenue = Number(this.revenueCurrent || 0);
        const treatmentCosts = Number(this.$parent?.totalTreatmentCost ?? 0) || 0;
        const elementaryExpenses = Number(this.$parent?.totalExpensesElementaires ?? 0) || 0;

        // consumption costs come from observed weeklyCost (sum)
        const observedConsumptionTotal = (this.consommations || []).reduce((s, c) => s + (Math.round((Number(c.kg || 0) * Number(c.prix_unitaire || 0) + Number(c.eau_litres || 0) * Number(c.prix_eau_unitaire || 0))) || 0), 0);

        const costs = [
          { key: 'consommation', label: 'Consommations', value: -observedConsumptionTotal },
          { key: 'traitements', label: 'Traitements', value: -treatmentCosts },
          { key: 'depenses', label: 'Dépenses élémentaires', value: -elementaryExpenses }
        ];

        const labels = ['Revenu total', ...costs.map(c => c.label), 'Marge nette'];
        const base = [];
        const delta = [];
        let cumul = 0;

        // Revenu
        base.push(0);
        delta.push(Math.round(revenue));
        cumul += revenue;

        // Costs as negative steps
        for (const c of costs) {
          base.push(Math.round(cumul));
          const step = Math.round(c.value || 0);
          delta.push(step);
          cumul += step;
        }

        base.push(Math.round(cumul - (Math.round(cumul) || 0)) );
        delta.push(0);

        return { labels, base, delta };
      }

      const durationWeeks = Math.max(1, Math.ceil((parseInt(this.band?.duree_jours, 10) || 42) / 7));
      const labels = Array.from({ length: durationWeeks }, (_, i) => `S${i + 1}`);
      const weeklyCost = Array(durationWeeks).fill(null);
      const weeklyMargin = Array(durationWeeks).fill(null);

      (this.consommations || []).forEach(c => {
        const w = c.semaine_production;
        if (!w || w < 1 || w > durationWeeks) return;
        const idx = w - 1;
        const kg = Number(c.kg || 0);
        const eau = Number(c.eau_litres || 0);
        const pu = Number(c.prix_unitaire || 0);
        const puEau = Number(c.prix_eau_unitaire || 0);
        const total = Math.round(kg * pu + eau * puEau);
        weeklyCost[idx] = (weeklyCost[idx] || 0) + total;
      });

      // If predictions provided, compute weekly predicted margin (valeur - coût prédit)
      if (Array.isArray(this.predictions) && this.predictions.length && this.band?.date_arrivee) {
        const start = new Date(this.band.date_arrivee);
        start.setHours(0,0,0,0);
        this.predictions.forEach(p => {
          if (!p?.date) return;
          const d = new Date(p.date);
          if (Number.isNaN(d.getTime())) return;
          // week index relative to band start
          const diffDays = Math.floor((d - start) / (1000*60*60*24));
          const wk = Math.floor(diffDays / 7) + 1;
          if (wk < 1 || wk > durationWeeks) return;
          const idx = wk - 1;
          const marge = Number(p.marge || 0);
          weeklyMargin[idx] = (weeklyMargin[idx] || 0) + marge;
        });
      }

      // determine last index either from costs or margins
      const lastCostIdx = weeklyCost.reduce((acc, v, i) => (v !== null ? i : acc), -1);
      const lastMarginIdx = weeklyMargin.reduce((acc, v, i) => (v !== null ? i : acc), -1);
      const lastIdx = Math.max(lastCostIdx, lastMarginIdx);
      const base = [];
      const delta = [];
      let cumul = 0;
      for (let i = 0; i < weeklyCost.length; i += 1) {
        if (lastIdx >= 0 && i <= lastIdx) {
          base.push(cumul);
          // prefer showing margin if available, otherwise cost
          const step = (weeklyMargin[i] !== null && weeklyMargin[i] !== undefined) ? weeklyMargin[i] : (weeklyCost[i] ?? 0);
          delta.push(step);
          cumul += step;
        } else {
          base.push(null);
          delta.push(null);
        }
      }

      return { labels, base, delta };
    }
  }
};
</script>

<style scoped>
.chart-block { width: 100%; height: 260px; }
</style>
