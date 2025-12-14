<template>
  <div class="timeline" v-if="eventsToShow.length">
    <div
      v-for="event in eventsToShow"
      :key="event.id"
      class="timeline-item"
    >
      <div class="date">{{ formatDate(event.date) }}</div>
      <div class="content">
        <div class="title">{{ event.label }}</div>
        <div class="meta" v-if="event.details">{{ event.details }}</div>
      </div>
    </div>
  </div>
  <div v-else class="empty">Aucun événement</div>
</template>

<script>
export default {
  name: 'KeyDatesTimeline',
  props: {
    events: { type: Array, default: () => [] },
    limit: { type: Number, default: 6 }
  },
  computed: {
    eventsToShow() {
      return (this.events || [])
        .filter(e => e?.date)
        .sort((a, b) => new Date(a.date) - new Date(b.date))
        .slice(0, this.limit)
        .map((e, idx) => ({ id: e.id || idx, ...e }));
    }
  },
  methods: {
    formatDate(d) {
      const date = new Date(d);
      if (Number.isNaN(date.getTime())) return '';
      return date.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' });
    }
  }
};
</script>

<style scoped>
.timeline {
  display: grid;
  gap: 10px;
}
.timeline-item {
  display: grid;
  grid-template-columns: 80px 1fr;
  align-items: start;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 10px;
  background: #0f172a08;
  border: 1px dashed #0ea5e94d;
}
.date {
  font-weight: 700;
  color: #0ea5e9;
}
.title {
  font-weight: 600;
}
.meta {
  color: #475569;
  font-size: 0.9em;
}
.empty {
  text-align: center;
  color: #94a3b8;
  padding: 20px 0;
}
</style>
