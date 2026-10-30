<template>
  <svg
    :width="size" :height="size" viewBox="0 0 24 24" fill="none"
    xmlns="http://www.w3.org/2000/svg"
    :stroke="color" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"
    :aria-label="name"
  >
    <template v-if="name === 'home'">
      <path d="M3 10.5 12 3l9 7.5" />
      <path d="M5 9.5V20a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V9.5" />
    </template>
    <template v-else-if="name === 'user'">
      <path d="M12 11a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7Z" />
      <path d="M4.5 20.5c1.2-3.2 4-4.8 7.5-4.8s6.3 1.6 7.5 4.8" />
    </template>
    <template v-else-if="name === 'arrowRight'">
      <path d="M4 12h16m-6-6 6 6-6 6" />
    </template>
    <template v-else-if="name === 'arrowLeft'">
      <path d="M20 12H4m6-6-6 6 6 6" />
    </template>
    <template v-else-if="name === 'chevronRight'">
      <path d="m9 6 6 6-6 6" />
    </template>
    <template v-else-if="name === 'calendar'">
      <path d="M4 6h16v14H4zM4 10h16M8 3v4m8-4v4" />
    </template>
    <template v-else-if="name === 'check'">
      <path d="m5 12.5 4.5 4.5L19 7.5" />
    </template>
    <template v-else-if="name === 'checkCircle'">
      <path d="M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Z" />
      <path d="m8.5 12 2.3 2.3 4.7-4.6" />
    </template>
    <template v-else-if="name === 'trophy'">
      <path d="M8 4h8v5a4 4 0 0 1-8 0zM8 6H4.5v1.5A3.5 3.5 0 0 0 8 11M16 6h3.5v1.5A3.5 3.5 0 0 1 16 11" />
      <path d="M12 13v3m-3.5 4h7M12 16c-2.5 0-4.5-1.5-4.5-4V8h9v4c0 2.5-2 4-4.5 4Z" />
    </template>
    <template v-else-if="name === 'flame'">
      <path d="M12 21c4 0 6.5-2.4 6.5-6.2 0-3.4-2.4-5.6-3.7-6.6.1 1.4-.5 2.7-1.7 3.2.1-2.4-.7-5.1-2.5-7.4.2 2.6-.8 4.2-2.6 5.7-2 1.6-3.5 3.6-3.5 6.3C4.5 19 7 21 12 21Z" />
    </template>
    <template v-else-if="name === 'clock'">
      <path d="M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Z" />
      <path d="M12 7v5l3.5 2" />
    </template>
    <template v-else-if="name === 'play'">
      <path d="M7 4.8v14.4c0 .8.9 1.3 1.6.9l11-7.2c.6-.4.6-1.4 0-1.8l-11-7.2c-.7-.4-1.6.1-1.6.9Z" />
    </template>
    <template v-else-if="name === 'pause'">
      <path d="M8 5v14M16 5v14" />
    </template>
    <template v-else-if="name === 'target'">
      <path d="M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Z" />
      <path d="M12 16.5a4.5 4.5 0 1 0 0-9 4.5 4.5 0 0 0 0 9Z" />
      <circle cx="12" cy="12" r="1.4" fill="currentColor" stroke="none" />
    </template>
    <template v-else-if="name === 'activity'">
      <path d="M3 12h4l2.5-6 5 12L17 12h4" />
    </template>
    <template v-else-if="name === 'close'">
      <path d="m6 6 12 12M18 6 6 18" />
    </template>
    <template v-else-if="name === 'settings'">
      <path d="M12 15.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7Z" />
      <path d="M19 12a7 7 0 0 0-.1-1.2l2-1.5-2-3.4-2.3 1a7 7 0 0 0-2.1-1.2L14.2 3h-4l-.3 2.7a7 7 0 0 0-2.1 1.2l-2.3-1-2 3.4 2 1.5a7 7 0 0 0 0 2.4l-2 1.5 2 3.4 2.3-1a7 7 0 0 0 2.1 1.2l.3 2.7h4l.3-2.7a7 7 0 0 0 2.1-1.2l2.3 1 2-3.4-2-1.5c.1-.4.1-.8.1-1.2Z" />
    </template>
    <template v-else-if="name === 'refresh'">
      <path d="M20 12a8 8 0 1 1-2.3-5.6M20 3v4h-4" />
    </template>
    <template v-else-if="name === 'bell'">
      <path d="M12 3.5a5.5 5.5 0 0 1 5.5 5.5v4l1.5 2.5H5l1.5-2.5V9A5.5 5.5 0 0 1 12 3.5ZM9.5 18a2.5 2.5 0 0 0 5 0" />
    </template>
    <template v-else-if="name === 'spark'">
      <path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8Z" />
    </template>
    <template v-else-if="name === 'hourglass'">
      <path d="M7 3h10M7 21h10M7 3v4l4 4v2l-4 4v4M17 3v4l-4 4v2l4 4v4" />
    </template>
    <template v-else-if="name === 'heart'">
      <path d="M12 20.8 4.9 13.9a4.7 4.7 0 0 1 6.6-6.7l.5.5.5-.5a4.7 4.7 0 0 1 6.6 6.7L12 20.8Z" />
    </template>
  </svg>
</template>

<script setup>
defineProps({
  name: { type: String, required: true },
  size: { type: [Number, String], default: 22 },
  color: { type: String, default: 'currentColor' },
})
</script>
