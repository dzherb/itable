<template>
  <RouterLink :to="to" v-slot="{ isActive, navigate, href }" custom>
    <a
      :href
      @click="navigate"
      class="flex items-center gap-2.5 text-xs font-bold text-white transition-opacity lg:text-sm dark:text-primary-300"
      :class="{ 'opacity-50': !(isActive || active) }"
    >
      <slot :iconClass="'stroke-white dark:stroke-primary-300'" />
    </a>
  </RouterLink>
</template>

<script setup lang="ts">
import { type RouteLocationRaw } from 'vue-router'

const { active = false } = defineProps<{
  to: RouteLocationRaw
  active?: boolean
}>()
</script>
