const queryString = require('query-string');

export const paginationMixin = {
  data () {
    return {
      pagination: {
        count: 0,
        perPage: 20,
        next: null,
        prev: null
      },
      currentPage: 1
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
        perPage: 20,
        next: response.data.next,
        prev: response.data.previous
      }
    }
  },
  created () {
    const query = queryString.parse(location.search, {
      parseBooleans: true
    });
    if (query.page) {
      this.currentPage = parseInt(query.page)
    }
  }
}
