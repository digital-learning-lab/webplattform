<template>
  <div class="pagination" v-if="pagination && pagination.count > 0">
    <button class="pagination__button pagination__previous" @click="$emit('prev')" :disabled="pagination.prev === null">
      <span><</span>
    </button>
    <button class="pagination__button pagination__number" :class="{'pagination__button--active': page === currentPage}" v-for="page in pages" @click="$emit('jump', $event, page)">{{ page }}</button>
    <button class="pagination__button pagination__next" @click="$emit('next')" :disabled="pagination.next === null">
      <span>></span>
    </button>
  </div>
</template>

<script>
  export default {
    name: 'Pagination',
    props: {
      currentPage: {
        type: Number,
        default: 1
      },
      pagination: {
        type: Object,
        default () {
          return {}
        }
      }
    },
    methods: {},
    computed: {
      pages () {
        if (this.pagination.count) {
          let counter = this.pagination.count
          let pages = []
          let page = 1
          while (counter > 0) {
            pages.push(page++)
            counter -= 10
          }
          return pages
        }
      }
    }
  }
</script>

<style scoped>

</style>