export const paginationMixin = {
  data () {
    return {
      pagination: {
        count: 0,
        perPage: 10,
        next: null,
        prev: null
      }
    }
  },
  methods: {
    jumpTo (event, page) {
      this.currentPage = page
      this.updateContents(page)
    },
    previousPage () {
      this.updateContents(--this.currentPage)
    },
    nextPage () {
      this.updateContents(++this.currentPage)
    },
    updatePagination (response) {
      this.pagination = {
        count: response.data.count,
        perPage: 10,
        next: response.data.next,
        prev: response.data.previous
      }
    }
  },
  updateContents (page) {}
}