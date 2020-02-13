<template>
  <div class="pagination" v-if="pagination && pagination.count > 0">
    <button class="pagination__button pagination__previous" @click="$emit('prev')" :disabled="pagination.prev === null">
      <span><</span>
    </button>
    <div v-for="(page, index) in pages" class="pagination__number">
      <button class="pagination__button" disabled v-if="pages[index - 1] !== page - 1 && page > 1">...</button>
      <button class="pagination__button" :disabled="page === '...'" :class="{'pagination__button--active': page === currentPage}" @click="$emit('jump', $event, page)">{{page}}</button>
      <button class="pagination__button" disabled v-if="pages.length < 4 && pages[index + 1] !== page + 1 && page < pages.length - 1">...</button>
    </div>
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
      },
      paginateBy: {
        type: Number,
        default: 20,
        required: false
      },
      margin: {
        type: Number,
        default: 2,
        required: false
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
            if (page === 1 || page === Math.ceil(this.pagination.count / this.paginateBy) || (page >= this.currentPage - this.margin && page <= this.currentPage + this.margin)) {
              pages.push(page)
            }
            page++
            counter -= this.paginateBy
          }
          return pages
        }
      }
    }
  }
</script>

<style scoped>

</style>