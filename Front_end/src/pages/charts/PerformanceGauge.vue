<template>
  <div class="gauge" :style="{ background: gradient }">
    <div class="gauge-inner">
      <div class="gauge-value">{{ displayValue }}</div>
      <div class="gauge-label">Performance</div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PerformanceGauge',
  props: {
    score: { type: Number, default: 0 }
  },
  computed: {
    clamped() {
      if (!Number.isFinite(this.score)) return 0;
      return Math.max(0, Math.min(100, this.score));
    },
    displayValue() {
      return `${Math.round(this.clamped)}%`;
    },
    color() {
      const v = this.clamped;
      if (v < 35) return '#ef4444';
      if (v < 50) return '#f59e0b';
      if (v < 75) return '#fbbf24';
      if (v < 80) return '#22c55e';
      return '#2563eb';
    },
    gradient() {
      const angle = (this.clamped / 100) * 360;
      return `conic-gradient(${this.color} ${angle}deg, #e5e7eb ${angle}deg)`;
    }
  }
};
</script>

<style scoped>
.gauge {
  width: 200px;
  height: 200px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 20px rgba(0,0,0,0.08);
}
.gauge-inner {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  background: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  box-shadow: inset 0 0 0 1px #e5e7eb;
}
.gauge-value { font-size: 28px; font-weight: 700; color: #111827; }
.gauge-label { font-size: 12px; color: #6b7280; letter-spacing: 0.5px; text-transform: uppercase; }
</style>
