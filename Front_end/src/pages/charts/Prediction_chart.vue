<template>
  <div class="prediction-charts">
    <div class="chart-row">
      <div class="chart-item">
        <div class="chart-header">
          <h3>Prédiction poids</h3>
          <div class="muted small">Poids projeté par jour</div>
        </div>
        <chart-base
          :chart-id="weightChartId"
          :chart-type="'line'"
          :height="260"
          ref="weight"
        />
      </div>
      <div class="chart-item">
        <div class="chart-header">
          <h3>Dépenses élémentaires</h3>
          <label class="small">Jour :
            <select v-model="selectedCostWeek" style="margin-right: 6px;">
              <option value="">Toutes les semaines</option>
              <option v-for="w in weekOptions" :key="w" :value="w">Semaine {{ w }}</option>
            </select>
            <select v-model="selectedCostDate">
              <option v-for="d in filteredDateOptions" :key="d" :value="d">{{ d }}</option>
            </select>
          </label>
        </div>
        <chart-base
          :chart-id="costPieChartId"
          :chart-type="'pie'"
          :height="260"
          ref="costPie"
        />
      </div>
    </div>
    <div class="chart-row">
      <div class="chart-item">
        <div class="chart-header">
          <h3>Survie projetée</h3>
        </div>
        <chart-base
          :chart-id="survivalChartId"
          :chart-type="'line'"
          :height="260"
          ref="survival"
        />
      </div>
      <div class="chart-item">
        <h3>Gains projetés</h3>
        <chart-base
          :chart-id="revenueChartId"
          :chart-type="'line'"
          :height="260"
          ref="revenue"
        />
      </div>
    </div>
    <div class="chart-row">
      <div class="chart-item">
        <h3>Meilleur jour de vente</h3>
        <div class="muted small">Marge = revenus - couts ; le point le plus haut indique le jour de vente cible.</div>
        <chart-base
          :chart-id="profitChartId"
          :chart-type="'line'"
          :height="260"
          ref="profit"
        />
      </div>
      <div class="chart-item">
        <h3>Consommation projetée</h3>
        <chart-base
          :chart-id="consumptionChartId"
          :chart-type="'line'"
          :height="260"
          ref="consumption"
        />
      </div>
      <div class="chart-item">
        <h3>Coûts projetés</h3>
        <chart-base
          :chart-id="costChartId"
          :chart-type="'bar'"
          :height="260"
          ref="cost"
        />
      </div>
    </div>

    <div class="chart-row">
      <div class="chart-item">
        <h3>Planning prévisionnel (Gantt)</h3>
        <chart-base
          :chart-id="ganttChartId"
          :chart-type="'bar'"
          :height="260"
          ref="gantt"
        />
        <div class="muted small">Jalons : passage 1,5 kg / 2,5 kg, fenetre de vente optimale, pic de cout et meilleure marge. Axe X = jours depuis le demarrage (ex : J14).</div>
      </div>
      <div class="chart-item">
        <h3>IC / feed-to-gain prévu</h3>
        <div class="muted small">Axe Y = indice de consommation (kg aliment / kg poids). Ex : 1,8 signifie 1,8 kg d'aliment pour 1 kg gagne.</div>
        <chart-base
          :chart-id="feedGainChartId"
          :chart-type="'line'"
          :height="260"
          ref="feedgain"
        />
      </div>
    </div>

    <div class="chart-row">
      <div class="chart-item">
        <h3>Radar profil semaine</h3>
        <label class="small">Semaine :
          <select v-model="selectedRadarWeek">
            <option v-for="w in weekOptions" :key="w" :value="w">S{{ w }}</option>
          </select>
        </label>
        <chart-base
          :chart-id="radarChartId"
          :chart-type="'radar'"
          :height="260"
          ref="radar"
        />
      </div>
      <div class="chart-item">
        <h3>Heatmap hebdo (coût)</h3>
        <div class="muted small">Coût moyen par semaine (FCFA). Ex : si S3 est plus haute, la semaine 3 est la plus chere.</div>
        <chart-base
          :chart-id="heatmapChartId"
          :chart-type="'bar'"
          :height="260"
          ref="heatmap"
        />
      </div>
      <div class="chart-item">
        <h3>Waterfall coût → marge</h3>
        <div class="muted small">Revenu total → couts par poste (negatifs) → marge nette (profit final).</div>
        <chart-base
          :chart-id="waterfallChartId"
          :chart-type="'bar'"
          :height="260"
          ref="waterfall"
        />
      </div>
    </div>

    <div class="chart-row">
      <div class="chart-item">
        <h3>Boxplots conso (par semaine)</h3>
        <div class="muted small">Min / max / moyenne de consommation hebdo. Ex : ecart large en S2 ⇒ consommation dispersee.</div>
        <chart-base
          :chart-id="boxplotChartId"
          :chart-type="'line'"
          :height="260"
          ref="boxplot"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { Chart } from 'chart.js';
import ChartBase from './commun/ChartBase.vue';

// Plugin global pour afficher les labels au bord des secteurs du pie
const pieLabelsPlugin = {
  id: 'pieLabelsPlugin',
  afterDatasetsDraw(chart) {
    if (chart.config.type !== 'pie') return;
    const { ctx } = chart;
    const meta = chart.getDatasetMeta(0);
    if (!meta?.data) return;
    const labels = chart.data.labels || [];
    ctx.save();
    ctx.font = '11px sans-serif';
    ctx.fillStyle = '#111';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    meta.data.forEach((arc, idx) => {
      const label = labels[idx] || '';
      const { x, y } = arc.tooltipPosition();
      ctx.fillText(label, x, y);
    });
    ctx.restore();
  }
};

if (!Chart._pieLabelsPluginRegistered) {
  Chart.register(pieLabelsPlugin);
  Chart._pieLabelsPluginRegistered = true;
}

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
      survivalChartId: `pred-survival-${suffix}`,
      revenueChartId: `pred-revenue-${suffix}`,
      profitChartId: `pred-profit-${suffix}`,
      consumptionChartId: `pred-consumption-${suffix}`,
      costChartId: `pred-cost-${suffix}`,
      costPieChartId: `pred-cost-pie-${suffix}`,
      selectedCostDate: '',
      selectedCostWeek: '',
      ganttChartId: `pred-gantt-${suffix}`,
      feedGainChartId: `pred-feedgain-${suffix}`,
      radarChartId: `pred-radar-${suffix}`,
      heatmapChartId: `pred-heatmap-${suffix}`,
      waterfallChartId: `pred-waterfall-${suffix}`,
      boxplotChartId: `pred-boxplot-${suffix}`,
      selectedRadarWeek: ''
    };
  },
  computed: {
    dateOptions() {
      return [...(this.predictions || [])]
        .sort((a, b) => a.jour - b.jour)
        .map(p => p.date || `J+${p.jour}`);
    },
    weekOptions() {
      const set = new Set(
        [...(this.predictions || [])].map(p => Math.ceil((p.jour || 1) / 7) || 1)
      );
      return Array.from(set).sort((a, b) => a - b);
    },
    filteredDateOptions() {
      if (!this.selectedCostWeek) return this.dateOptions;
      const weekNum = Number(this.selectedCostWeek);
      return [...(this.predictions || [])]
        .filter(p => Math.ceil((p.jour || 1) / 7) === weekNum)
        .sort((a, b) => a.jour - b.jour)
        .map(p => p.date || `J+${p.jour}`);
    }
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
    },
    selectedCostWeek() {
      this.selectedCostDate = '';
      this.syncSelectedDate();
      this.renderCostPie();
    },
    selectedCostDate() {
      this.renderCostPie();
    },
    selectedRadarWeek() {
      this.renderRadar();
    }
  },
  methods: {
    renderAll() {
      this.$nextTick(() => {
        this.renderWeight();
        this.syncSelectedDate();
        this.renderCostPie();
        this.renderSurvival();
        this.renderRevenue();
        this.renderProfit();
        this.renderConsumption();
        this.renderCost();
        this.renderGantt();
        this.renderFeedGain();
        this.renderRadar();
        this.renderHeatmap();
        this.renderWaterfall();
        this.renderBoxplot();
      });
    },
    syncSelectedDate() {
      const list = this.filteredDateOptions;
      const first = list[0] || '';
      // Ne pré-sélectionner un jour que si une semaine est filtrée
      if (this.selectedCostWeek && !this.selectedCostDate && first) {
        this.selectedCostDate = first;
      }
    },
    predictedForDate(dateStr) {
      return (this.predictions || []).find(p => p.date === dateStr) || null;
    },
    expenseBreakdownForDay(pred) {
      if (!pred) return { labels: [], values: [] };
      const jour = pred.jour || 1;
      const stage = jour <= 7 ? 'arrivee' : jour <= 21 ? 'chauffage' : jour <= 35 ? 'croissance' : 'finition';
      const cost = pred.cout || 0;
      const dist = {
        arrivee: { chauffage: 0.28, transport: 0.18, installation: 0.12, maintenance: 0.07, electricite: 0.10, litiere: 0.10, nettoyage: 0.10, taxes: 0.05 },
        chauffage: { chauffage: 0.25, litiere: 0.20, electricite: 0.20, transport: 0.10, maintenance: 0.10, nettoyage: 0.10, taxes: 0.05 },
        croissance: { electricite: 0.25, litiere: 0.20, maintenance: 0.15, nettoyage: 0.10, chauffage: 0.05, transport: 0.05, taxes: 0.05, autres: 0.15 },
        finition: { electricite: 0.30, maintenance: 0.20, nettoyage: 0.15, litiere: 0.10, transport: 0.05, chauffage: 0.05, taxes: 0.05, autres: 0.10 }
      }[stage];
      const labels = Object.keys(dist);
      const values = labels.map(k => Math.round(cost * dist[k]));
      return { labels, values };
    },
    expenseBreakdownAggregate(preds) {
      if (!preds || !preds.length) return { labels: [], values: [] };
      const totals = new Map();
      preds.forEach(p => {
        const { labels, values } = this.expenseBreakdownForDay(p);
        labels.forEach((lbl, idx) => {
          totals.set(lbl, (totals.get(lbl) || 0) + (values[idx] || 0));
        });
      });
      const labels = Array.from(totals.keys());
      const values = labels.map(l => totals.get(l) || 0);
      return { labels, values };
    },
    baseDataScaled(key) {
      const sorted = [...(this.predictions || [])].sort((a, b) => a.jour - b.jour);
      if (!sorted.length) return { labels: [], values: [], margins: [] };

      const maxDay = sorted[sorted.length - 1].jour || sorted.length;

      // Helper moyenne
      const avg = arr => arr.length ? arr.reduce((a, b) => a + b, 0) / arr.length : 0;

      // Agrégation par semaine si horizon > 30 jours
      if (maxDay >= 30) {
        const byWeek = new Map();
        sorted.forEach(p => {
          const w = Math.ceil((p.jour || 1) / 7) || 1;
          if (!byWeek.has(w)) byWeek.set(w, []);
          byWeek.get(w).push(p);
        });
        const labels = Array.from(byWeek.keys()).sort((a, b) => a - b).map(w => `S${w}`);
        const values = labels.map(lbl => {
          const w = Number(lbl.slice(1));
          const arr = byWeek.get(w) || [];
          return avg(arr.map(p => Number(p[key] || 0)));
        });
        const margins = labels.map(lbl => {
          const w = Number(lbl.slice(1));
          const arr = byWeek.get(w) || [];
          return avg(arr.map(p => Number(p.marge || 0)));
        });
        return { labels, values, margins };
      }

      // Echantillon tous les 2 jours si horizon > 7 jours
      if (maxDay > 7) {
        const filtered = sorted.filter((p, idx) => idx === sorted.length - 1 || ((p.jour || (idx + 1)) - 1) % 2 === 0);
        const labels = filtered.map(p => p.date || `J+${p.jour}`);
        const values = filtered.map(p => p[key] || 0);
        const margins = filtered.map(p => p.marge || 0);
        return { labels, values, margins };
      }

      // Sinon, toutes les données quotidiennes
      const labels = sorted.map(p => p.date || `J+${p.jour}`);
      const values = sorted.map(p => p[key] || 0);
      const margins = sorted.map(p => p.marge || 0);
      return { labels, values, margins };
    },
    groupByWeek() {
      const map = new Map();
      (this.predictions || []).forEach(p => {
        const week = Math.ceil((p.jour || 1) / 7) || 1;
        if (!map.has(week)) map.set(week, []);
        map.get(week).push(p);
      });
      return map;
    },
    weeklyStats() {
      const map = this.groupByWeek();
      const stats = [];
      map.forEach((arr, week) => {
        const pick = key => arr.map(p => Number(p[key] || 0));
        const agg = vals => {
          if (!vals.length) return { min: 0, max: 0, avg: 0 };
          const sorted = [...vals].sort((a, b) => a - b);
          const sum = vals.reduce((a, b) => a + b, 0);
          const avg = sum / vals.length;
          return { min: sorted[0], max: sorted[sorted.length - 1], avg };
        };
        stats.push({
          week,
          poids: agg(pick('poids')),
          consommation: agg(pick('consommation')),
          cout: agg(pick('cout')),
          survie: agg(pick('taux_survie')),
          marge: agg(pick('marge'))
        });
      });
      return stats.sort((a, b) => a.week - b.week);
    },
    renderWeight() {
      const c = this.$refs.weight;
      if (!c) return;
      const { labels, values } = this.baseDataScaled('poids');
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
    renderConsumption() {
      const c = this.$refs.consumption;
      if (!c) return;
      const { labels, values } = this.baseDataScaled('consommation');
      c.getChartData = () => ({
        labels,
        datasets: [{
          label: 'Consommation (kg)',
          data: values,
          borderColor: '#2563EB',
          backgroundColor: 'rgba(37,99,235,0.15)',
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
      const { labels, values } = this.baseDataScaled('cout');
      c.getChartData = () => ({
        labels,
        datasets: [{
          label: 'Coûts projetés (FCFA)',
          data: values,
          backgroundColor: 'rgba(220,38,38,0.25)',
          borderColor: '#DC2626',
          borderWidth: 1.5
        }]
      });
      c.getChartOptions = () => ({
        responsive: true,
        maintainAspectRatio: false,
        scales: { x: { stacked: false }, y: { stacked: false } }
      });
      this.$nextTick(() => c.renderChart());
    },
    renderCostPie() {
      const c = this.$refs.costPie;
      if (!c) return;
      let labels = [];
      let values = [];

      const preds = [...(this.predictions || [])];
      const weekNum = this.selectedCostWeek ? Number(this.selectedCostWeek) : null;

      if (weekNum) {
        const weekPreds = preds.filter(p => Math.ceil((p.jour || 1) / 7) === weekNum);
        if (this.selectedCostDate) {
          const selectedPred = weekPreds.find(p => p.date === this.selectedCostDate) || weekPreds[0] || null;
          ({ labels, values } = this.expenseBreakdownForDay(selectedPred));
        } else {
          ({ labels, values } = this.expenseBreakdownAggregate(weekPreds));
        }
      } else {
        // Toutes les semaines : agrégation sur tout l'horizon
        ({ labels, values } = this.expenseBreakdownAggregate(preds));
      }

      const palette = ['#DC2626', '#F97316', '#F59E0B', '#84CC16', '#22C55E', '#14B8A6', '#0EA5E9', '#6366F1'];
      c.getChartData = () => ({
        labels,
        datasets: [{
          label: 'Dépenses élémentaires (FCFA)',
          data: values,
          backgroundColor: labels.map((_, i) => palette[i % palette.length]),
          borderWidth: 0
        }]
      });
      c.getChartOptions = () => ({
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } }
      });
      this.$nextTick(() => c.renderChart());
    },
    renderGantt() {
      const c = this.$refs.gantt;
      if (!c) return;
      const preds = [...(this.predictions || [])].sort((a, b) => a.jour - b.jour);
      if (!preds.length) return;
      const lastDay = preds[preds.length - 1].jour || preds.length || 1;
      const best = preds.reduce((max, p) => p.marge > max.marge ? p : max, preds[0]);
      const bestDay = best.jour || 1;
      const sellStart = Math.max(1, bestDay - 2);
      const sellEnd = Math.min(lastDay, bestDay + 2);

      const dayWeight15 = preds.find(p => p.poids >= 1.5)?.jour || 1;
      const dayWeight25 = preds.find(p => p.poids >= 2.5)?.jour || dayWeight15;
      const peakCost = preds.reduce((max, p) => p.cout > max.cout ? p : max, preds[0]).jour || 1;

      const milestones = [
        { label: 'Atteinte 1.5 kg', range: [dayWeight15, dayWeight15] },
        { label: 'Atteinte 2.5 kg', range: [dayWeight25, dayWeight25] },
        { label: 'Fenetre vente optimale', range: [sellStart, sellEnd] },
        { label: 'Pic de cout', range: [peakCost, peakCost] },
        { label: 'Meilleure marge', range: [bestDay, bestDay] }
      ];

      const labels = milestones.map(m => m.label);
      const data = milestones.map(m => m.range);

      c.getChartData = () => ({
        labels,
        datasets: [{
          label: 'Jour',
          data,
          backgroundColor: '#6366F1',
          borderRadius: 6,
          barThickness: 18
        }]
      });
      c.getChartOptions = () => ({
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label(ctx) {
                const [start, end] = ctx.raw || [0, 0];
                return start === end ? `Jour ${start}` : `J${start} à J${end}`;
              }
            }
          }
        },
        scales: {
          x: {
            min: 1,
            max: lastDay,
            ticks: { stepSize: Math.max(1, Math.round(lastDay / 7)), precision: 0 }
          },
          y: { stacked: false }
        }
      });
      this.$nextTick(() => c.renderChart());
    },
    renderFeedGain() {
      const c = this.$refs.feedgain;
      if (!c) return;
      const stats = this.weeklyStats();
      const labels = stats.map(s => `S${s.week}`);
      const ratios = stats.map(s => {
        const conso = s.consommation.avg || 0;
        const poids = s.poids.avg || 1;
        return conso && poids ? conso / poids : 0;
      });
      c.getChartData = () => ({
        labels,
        datasets: [{
          label: 'IC prévisionnel (conso / poids)',
          data: ratios,
          borderColor: '#0EA5E9',
          backgroundColor: 'rgba(14,165,233,0.15)',
          borderWidth: 2,
          tension: 0.3,
          fill: true
        }]
      });
      c.getChartOptions = () => ({ responsive: true, maintainAspectRatio: false });
      this.$nextTick(() => c.renderChart());
    },
    renderRadar() {
      const c = this.$refs.radar;
      if (!c) return;
      const week = this.selectedRadarWeek || this.weekOptions[0];
      const stats = this.weeklyStats().find(s => s.week === Number(week));
      const labels = ['Poids', 'Survie', 'Coût', 'Marge'];
      const values = stats ? [stats.poids.avg, stats.survie.avg, stats.cout.avg, stats.marge.avg] : [0, 0, 0, 0];
      // Normalisation simple pour radar
      const norm = (val, scale) => scale ? (val / scale) * 100 : val;
      const maxWeight = Math.max(...this.weeklyStats().map(s => s.poids.max || 0), 1);
      const maxCost = Math.max(...this.weeklyStats().map(s => s.cout.max || 1));
      const maxMargin = Math.max(...this.weeklyStats().map(s => Math.abs(s.marge.max) || 1));
      const scaled = [
        norm(values[0], maxWeight),
        values[1],
        norm(values[2], maxCost),
        norm(Math.abs(values[3]), maxMargin)
      ];
      c.getChartData = () => ({
        labels,
        datasets: [{
          label: `Profil S${week}`,
          data: scaled,
          backgroundColor: 'rgba(99,102,241,0.15)',
          borderColor: '#4F46E5',
          borderWidth: 2,
          pointRadius: 4
        }]
      });
      c.getChartOptions = () => ({ responsive: true, maintainAspectRatio: false, scales: { r: { suggestedMin: 0, suggestedMax: 120 } }, plugins: { legend: { display: false } } });
      this.$nextTick(() => c.renderChart());
    },
    renderHeatmap() {
      const c = this.$refs.heatmap;
      if (!c) return;
      const stats = this.weeklyStats();
      const labels = stats.map(s => `S${s.week}`);
      const cout = stats.map(s => s.cout.avg || 0);
      c.getChartData = () => ({
        labels,
        datasets: [
          { label: 'Coût moyen (FCFA)', data: cout, backgroundColor: '#EF4444' }
        ]
      });
      c.getChartOptions = () => ({ responsive: true, maintainAspectRatio: false, scales: { x: { stacked: false }, y: { stacked: false } } });
      this.$nextTick(() => c.renderChart());
    },
    renderWaterfall() {
      const c = this.$refs.waterfall;
      if (!c) return;
      const preds = [...(this.predictions || [])];
      const totalRevenue = preds.reduce((s, p) => s + (p.valeur || 0), 0);
      const totalCost = preds.reduce((s, p) => s + (p.cout || 0), 0);
      const totalMargin = preds.reduce((s, p) => s + (p.marge || 0), 0);

      // Décomposer les coûts par poste sur tout l'horizon
      const costTotals = new Map();
      preds.forEach(p => {
        const { labels, values } = this.expenseBreakdownForDay(p);
        labels.forEach((lbl, idx) => {
          costTotals.set(lbl, (costTotals.get(lbl) || 0) + (values[idx] || 0));
        });
      });

      const costLabels = Array.from(costTotals.keys());
      const costValues = costLabels.map(l => costTotals.get(l) || 0);

      const labels = ['Revenu', ...costLabels, 'Marge nette'];
      const data = [totalRevenue, ...costValues.map(v => -v), totalMargin];

      c.getChartData = () => ({
        labels,
        datasets: [{
          label: 'Waterfall',
          data,
          backgroundColor: labels.map(l => l === 'Marge nette' ? '#22C55E' : l === 'Revenu' ? '#0EA5E9' : '#F97316'),
          borderWidth: 1
        }]
      });
      c.getChartOptions = () => ({ responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { stacked: false } } });
      this.$nextTick(() => c.renderChart());
    },
    renderBoxplot() {
      const c = this.$refs.boxplot;
      if (!c) return;
      const stats = this.weeklyStats();
      const labels = stats.map(s => `S${s.week}`);
      const consoMin = stats.map(s => s.consommation.min || 0);
      const consoMax = stats.map(s => s.consommation.max || 0);
      const consoMed = stats.map(s => s.consommation.avg || 0);
      c.getChartData = () => ({
        labels,
        datasets: [
          { label: 'Conso min (kg)', data: consoMin, borderColor: '#94A3B8', backgroundColor: 'rgba(148,163,184,0.15)', tension: 0.1, fill: false },
          { label: 'Conso max (kg)', data: consoMax, borderColor: '#0EA5E9', backgroundColor: 'rgba(14,165,233,0.15)', tension: 0.1, fill: false },
          { label: 'Conso moyenne (kg)', data: consoMed, borderColor: '#F97316', backgroundColor: 'rgba(249,115,22,0.12)', tension: 0.2, fill: false }
        ]
      });
      c.getChartOptions = () => ({ responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } });
      this.$nextTick(() => c.renderChart());
    },
      renderSurvival() {
        const c = this.$refs.survival;
        if (!c) return;
        const { labels, values } = this.baseDataScaled('taux_survie');
        const clamped = values.map(v => Math.min(100, Math.max(0, v)));
        c.getChartData = () => ({
          labels,
          datasets: [{
            label: 'Taux de survie (%)',
            data: clamped,
            borderColor: '#2563EB',
            backgroundColor: 'rgba(37,99,235,0.12)',
            borderWidth: 2.2,
            tension: 0.35,
            pointRadius: 4,
            pointHoverRadius: 6,
            fill: true,
            segment: {
              borderDash: ctx => ctx.p0DataIndex % 2 === 0 ? [6, 4] : undefined
            }
          }]
        });
        c.getChartOptions = () => ({
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: { suggestedMin: 0, suggestedMax: 100, grid: { color: 'rgba(0,0,0,0.06)' } },
            x: { grid: { display: false } }
          },
          plugins: {
            legend: { display: false },
            tooltip: { enabled: true }
          }
        });
        this.$nextTick(() => c.renderChart());
      },
      renderRevenue() {
        const c = this.$refs.revenue;
      if (!c) return;
        const { labels, values, margins } = this.baseDataScaled('valeur');
        const bestIdx = this.bestMarginIndexScaled(margins);
        const pointRadius = labels.map((_, idx) => idx === bestIdx ? 6 : 3);
      c.getChartData = () => ({
        labels,
        datasets: [{
            label: 'Gains projetés (FCFA)',
          data: values,
            borderColor: '#059669',
            backgroundColor: 'rgba(5,150,105,0.12)',
            borderWidth: 2,
            tension: 0.25,
            fill: true,
            pointRadius
        }]
      });
      c.getChartOptions = () => ({ responsive: true, maintainAspectRatio: false });
      this.$nextTick(() => c.renderChart());
    },
    renderProfit() {
      const c = this.$refs.profit;
      if (!c) return;
      const { labels, values } = this.baseDataScaled('marge');
        const cumulative = values.map((_, i) => values.slice(0, i + 1).reduce((a, b) => a + b, 0));
        const bestIdx = this.bestMarginIndexScaled(values);
        const pointRadius = labels.map((_, idx) => idx === bestIdx ? 7 : 3);
      c.getChartData = () => ({
        labels,
        datasets: [{
          label: 'Cumul des marges (FCFA)',
          data: cumulative,
          borderColor: '#FF9800',
          backgroundColor: 'rgba(255,152,0,0.15)',
          borderWidth: 2,
            tension: 0.25,
            fill: true,
            pointRadius
          }, {
            label: 'Marge quotidienne (FCFA)',
            data: values,
            borderColor: '#F97316',
            backgroundColor: 'rgba(249,115,22,0.12)',
            borderDash: [6, 6],
            tension: 0.25,
            fill: false,
            pointRadius
        }]
      });
      c.getChartOptions = () => ({ responsive: true, maintainAspectRatio: false });
      this.$nextTick(() => c.renderChart());
      },
      bestMarginIndexScaled(arr) {
        if (!arr || !arr.length) return -1;
        let maxVal = -Infinity;
        let idx = 0;
        arr.forEach((v, i) => {
          if (v > maxVal) {
            maxVal = v;
            idx = i;
          }
        });
        return idx;
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
 h3 { margin: 0 0 8px; font-size: 14px; }
</style>
