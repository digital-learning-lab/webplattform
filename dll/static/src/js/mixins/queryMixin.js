const queryString = require('query-string');


export const queryMixin = {
  data () {
    return {
      query: {},
      inited: false
    }
  },
  methods: {
    updateQueryString () {
      let params = this.getParams(this.currentPage)
      Object.keys(params).forEach((key) => (params[key] === null || params[key] === "") && delete params[key]);
      if (params) {
        window.history.pushState(
          {},
          "",
          location.pathname + '?' + queryString.stringify(params)
        );
      }
    }
  },
  created () {
    const query = queryString.parse(location.search, {
      parseBooleans: true
    });
    let keys = Object.keys(query)
    for (let i = 0; i < keys.length; i++) {
      const value = query[keys[i]]
      if (value) {
        if (query[keys[i]] === 'false') {
          query[keys[i]] = false
        }
        if (query[keys[i]] === 'true') {
          query[keys[i]] = true
        }
        if (this[keys[i]] && Array.isArray(this[keys[i]]) && !Array.isArray(query[keys[i]])) {
          this[keys[i]] = [query[keys[i]]]
        } else {
          this[keys[i]] = query[keys[i]]
        }
      }
    }
    this.inited = true
    this.updateContents()
  }
}
