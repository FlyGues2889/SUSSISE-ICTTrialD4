<template>
  <div class="page guides-page">
    <button class="back" @click="back">← 返回</button>

    <h1 class="page-title">指南依据</h1>
    <p class="page-sub">以下内容节选自权威机构的公开指南</p>

    <div class="filters">
      <button
        v-for="f in filters"
        :key="f.value"
        class="chip"
        :class="{ on: active === f.value }"
        @click="active = f.value"
      >
        {{ f.label }}
      </button>
    </div>

    <div class="list">
      <article
        v-for="g in list"
        :key="g.id"
        class="item"
        :class="{ danger: g.kind === 'safety' }"
      >
        <p class="item-text">{{ g.excerpt }}</p>
        <p v-if="g.original" class="item-original">{{ g.original }}</p>
        <a class="item-src" :href="g.url" target="_blank" rel="noopener">
          <span class="item-abbr">{{ g.abbr }}</span>
          <span class="item-name">{{ g.publisher }} · {{ g.title }}（{{ g.year }}）</span>
          <span class="item-arrow">↗</span>
        </a>
      </article>
    </div>

    <p v-if="!list.length" class="empty">该分类暂无节选</p>

    <p class="disclaimer">以上为公开指南节选，仅作运动指导参考，不替代医疗诊断。</p>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { healthEvidence } from '../mock/healthEvidence'

const router = useRouter()

const filters = [
  { label: '全部', value: 'all' },
  { label: '肩颈', value: 'neck' },
  { label: '腰背', value: 'back' },
  { label: '久坐', value: 'sitting' },
  { label: '全身', value: 'full' },
]

const active = ref('all')

const list = computed(() =>
  active.value === 'all'
    ? healthEvidence.guidelines
    : healthEvidence.getGuidelinesByArea(active.value)
)

const back = () => (window.history.length > 1 ? router.back() : router.push('/'))
</script>

<style scoped>
.back {
  font-size: 13px;
  color: var(--fg-3);
  padding: 2px 0;
  margin-bottom: 10px;
  transition: color 0.15s;
}
.back:hover { color: var(--fg); }

.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.chip {
  padding: 6px 14px;
  border-radius: var(--radius-pill);
  border: 1px solid var(--line);
  background: var(--card);
  font-size: 13px;
  color: var(--fg-2);
  transition: all 0.15s;
}
.chip:hover { border-color: var(--fg-3); }
.chip.on {
  background: var(--fg);
  border-color: var(--fg);
  color: #fff;
  font-weight: 600;
}

.item {
  padding: 2px 0 2px 14px;
  border-left: 2px solid var(--accent-soft);
  margin-bottom: 14px;
}

.item.danger { border-left-color: var(--danger); }

.item-text {
  font-size: 14px;
  line-height: 1.65;
  color: var(--fg);
}

.item.danger .item-text { color: var(--danger); }

.item-original {
  margin-top: 6px;
  font-size: 12px;
  line-height: 1.6;
  color: var(--fg-3);
}

.item-src {
  display: flex;
  align-items: baseline;
  gap: 6px;
  margin-top: 8px;
  font-size: 11px;
  color: var(--fg-3);
  text-decoration: none;
}
.item-src:hover .item-name { color: var(--accent-2); }

.item-abbr {
  font-weight: 700;
  color: var(--accent-2);
  letter-spacing: 0.04em;
}

.item.danger .item-abbr { color: var(--danger); }

.item-name { flex: 1; }

.item-arrow { flex-shrink: 0; }

.empty {
  font-size: 13px;
  color: var(--fg-3);
  padding: 20px 0;
}

.disclaimer {
  margin-top: 8px;
  padding-top: 20px;
  border-top: 1px solid var(--line);
  font-size: 11px;
  line-height: 1.7;
  color: var(--fg-3);
}
</style>