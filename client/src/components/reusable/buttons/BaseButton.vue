<template>
  <button
    class="rounded-xl bg-primary-400 px-8 py-4 text-sm leading-3 text-white transition-colors select-none disabled:bg-gray-300 dark:text-primary-200 dark:disabled:bg-primary-900 dark:disabled:text-gray-500 [&:not(:disabled)]:hover:bg-primary-500"
  >
    <slot />
  </button>
</template>
