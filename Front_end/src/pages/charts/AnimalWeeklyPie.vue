<template>
  <div class="animal-weekly-pie">
    <h4>{{ title }}</h4>
    <div class="stats">
      <div class="stat">
        <span class="label">Survivants</span>
        <span class="value">{{ survived }}</span>
      </div>
      <div class="stat">
        <span class="label">Morts</span>
        <span class="value danger">{{ deaths }}</span>
      </div>
      <div class="stat" v-if="total > 0">
        <span class="label">Taux survie</span>
        <span class="value success">{{ survivalRate }}%</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  survived: { type: Number, default: 0 },
  deaths: { type: Number, default: 0 },
  title: { type: String, default: 'Survie estimée' }
});

const total = computed(() => (props.survived || 0) + (props.deaths || 0));
const survivalRate = computed(() => {
  if (!total.value) return 0;
  return ((props.survived || 0) / total.value * 100).toFixed(1);
});
</script>

<style scoped>
.animal-weekly-pie { background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px; box-shadow: 0 4px 14px rgba(0,0,0,0.05); }
.stats { display: grid; gap: 8px; }
.stat { display: flex; justify-content: space-between; font-size: 13px; color: #111827; }
.label { color: #6b7280; }
.value { font-weight: 600; }
.value.danger { color: #b91c1c; }
.value.success { color: #15803d; }
</style>
