<template>
  <form @submit.prevent class="w-full rounded-soft bg-white px-4 py-6 dark:bg-primary-800">
    <p>123 test</p>
    <p>123 test</p>
    <p>123 test</p>
    <p>123 test</p>
    <p>123 test</p>
    <p>123 test</p>
    <p>123 test</p>
    <div class="flex items-center gap-2">
      <span class="basis-1/2">
        <a class="text-xs text-primary-400 dark:text-primary-300">Забыли пароль?</a>
      </span>
      <BaseButton class="basis-1/2">Войти</BaseButton>
    </div>
  </form>
</template>

<script setup lang="ts">
import BaseButton from "@/components/reusable/buttons/BaseButton.vue";
</script>
