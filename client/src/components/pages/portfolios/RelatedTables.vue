<template>
  <section>
    <h2 class="font-bold text-primary dark:text-primary-200">Привязанные таблицы</h2>
    <div class="mt-4 w-full max-w-md">
      <div
        ref="sliderRef"
        class="no-scrollbar flex snap-x snap-mandatory gap-4 overflow-x-auto scroll-smooth px-0.5 py-0.5"
      >
        <ListItem
          v-for="(slide, index) in slides"
          :key="index"
          class="h-[58px]! min-w-full snap-center dark:bg-primary-900!"
        >
          <template #name>
            <span class="text-sm dark:text-primary-200">
              {{ slide.title }}
            </span>
          </template>
          <template #append>
            <span class="text-xs text-gray-500 dark:text-primary-300">
              {{ slide.label }}
            </span>
          </template>
        </ListItem>
      </div>

      <div class="mt-4 flex justify-center gap-2">
        <button
          v-for="(_, index) in slides"
          :key="'dot-' + index"
          @click="scrollToSlide(index)"
          :class="[
            'h-2 w-2 rounded-full transition-all duration-300',
            currentIndex === index
              ? 'scale-110 bg-primary-300'
              : 'bg-primary-200 dark:bg-primary-900',
          ]"
        />
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import ListItem from '@/components/reusable/lists/ListItem.vue'
import { ref, shallowRef, useTemplateRef } from 'vue'
import { useEventListener } from '@vueuse/core'

const slides = ref([
  { title: 'Таблица 1', label: 'IMOEX' },
  { title: 'Таблица 2', label: 'IMOEX' },
  { title: 'Таблица 3', label: 'IMOEX' },
  { title: 'Таблица 4', label: 'IMOEX' },
])

const currentIndex = shallowRef(0)

const sliderRef = useTemplateRef('sliderRef')

const updateIndex = () => {
  const scrollLeft = sliderRef.value!.scrollLeft
  const width = sliderRef.value!.clientWidth
  currentIndex.value = Math.round(scrollLeft / width)
}

useEventListener(sliderRef, 'scroll', updateIndex)

const scrollToSlide = (index: number) => {
  currentIndex.value = index
  const width = sliderRef.value!.clientWidth
  sliderRef.value!.scrollTo({
    left: index * width,
    behavior: 'smooth',
  })
}
</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
