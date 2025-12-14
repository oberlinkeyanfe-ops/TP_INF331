<template>
  <div class="animal-weekly-line">
    <h4>{{ title }}</h4>
    <div class="summary">
      <span v-if="labels && labels.length">Semaines: {{ labels.join(', ') }}</span>
      <span v-else>Pas de données</span>
    </div>
    <div class="grid">
      <div class="row" v-for="(label, idx) in labels" :key="label">
        <div class="cell">{{ label }}</div>
        <div class="cell">{{ format(series[idx]) }}{{ unit }}</div>
        <div class="cell ref">({{ format(refLow[idx]) }} - {{ format(refHigh[idx]) }}){{ unit }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  labels: { type: Array, default: () => [] },
  series: { type: Array, default: () => [] },
  refLow: { type: Array, default: () => [] },
  refHigh: { type: Array, default: () => [] },
  title: { type: String, default: 'Mortalité hebdomadaire vs réf.' },
  yLabel: { type: String, default: '' },
  unit: { type: String, default: '%' }
});

const normalized = computed(() => {
  const len = Math.max(props.labels.length, props.series.length, props.refLow.length, props.refHigh.length);
  const safe = (arr, idx) => (Array.isArray(arr) && idx < arr.length ? arr[idx] : 0);
  return Array.from({ length: len }, (_, idx) => ({
    label: props.labels[idx] || `S${idx + 1}`,
    value: safe(props.series, idx),
    low: safe(props.refLow, idx),
    high: safe(props.refHigh, idx)
  }));
});

const format = val => typeof val === 'number' ? val.toFixed(2) : val ?? 0;
</script>

<style scoped>
.animal-weekly-line { background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px; box-shadow: 0 4px 14px rgba(0,0,0,0.05); }
.summary { color: #6b7280; font-size: 12px; margin-bottom: 8px; }
.grid { display: grid; gap: 6px; }
.row { display: grid; grid-template-columns: 80px 1fr 1fr; align-items: center; padding: 6px 10px; background: #f9fafb; border-radius: 8px; }
.cell { font-size: 13px; color: #111827; }
.cell.ref { color: #6b7280; font-size: 12px; text-align: right; }
</style>
