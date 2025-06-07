<template>
  <BaseNavigationBar>
    <NavigationLink :active="true" :to="{ name: backTo }">
      <template #default="{ iconClass }">
        <BackIcon :class="iconClass" />
        Назад
      </template>
    </NavigationLink>
    <span class="grow"></span>
  </BaseNavigationBar>
</template>

<script setup lang="ts">
import NavigationLink from '@/components/navigation/NavigationLink.vue'
import BackIcon from '@/components/icons/BackIcon.vue'
import BaseNavigationBar from '@/components/navigation/BaseNavigationBar.vue'

defineProps<{
  backTo: string
}>()
</script>
