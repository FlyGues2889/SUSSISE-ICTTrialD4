<template>
  <div class="app-card fade-up">
    <slot />
  </div>
</template>

<style scoped>
.app-card {
  background: var(--card);
  border: 1px solid var(--card-border);
  border-radius: var(--radius-lg);
  padding: 24px;
}
</style>