<template>
  <div class="donut-placeholder">
    <PerformanceGauge :score="score" />
    <div class="caption">{{ band?.nom_bande || '—' }}</div>
  </div>
</template>

<script>
import PerformanceGauge from './PerformanceGauge.vue';

export default {
  name: 'BestBandDonut',
  components: { PerformanceGauge },
  props: {
    band: { type: Object, default: null },
    height: { type: [String, Number], default: 220 }
  },
  computed: {
    score() { return Math.max(0, Math.min(100, Math.round(this.band?.performancePercent ?? 0))); }
  }
};
</script>

<style scoped>
.donut-placeholder { position: relative; width: 220px; height: 220px; display:flex; align-items:center; justify-content:center }
.donut-overlay { position: absolute; top: 50%; left: 0; right: 0; transform: translateY(-50%); display:flex; flex-direction:column; align-items:center; pointer-events:none }
.caption { font-size:12px; color:var(--text-muted); margin-bottom:6px; }
.percent { font-size:22px; font-weight:900; color:var(--primary); background: transparent }
.donut-placeholder .chart-container { background: transparent !important; box-shadow: none !important; border: none !important; padding: 0 !important }
.donut-placeholder canvas { background: transparent !important }
@media (max-width:600px){ .donut-placeholder{ width:160px; height:160px } .percent{ font-size:18px } }
</style>