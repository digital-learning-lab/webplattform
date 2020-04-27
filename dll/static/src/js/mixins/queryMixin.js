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
      let params = this.getParams()
      Object.keys(params).forEach((key) => (!params[key]) && delete params[key]);
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
    const query = queryString.parse(location.search);
    let keys = Object.keys(query)
    for (let i = 0; i < keys.length; i++) {
      const value = query[keys[i]]
      if (value) {
        if (this[keys[i]] && Array.isArray(this[keys[i]]) && !Array.isArray(query[keys[i]])) {
          this[keys[i]] = [query[keys[i]]]
        } else {
          this[keys[i]] = query[keys[i]]
        }
      }
    }
    console.log(this.competences)
    this.inited = true
  }
}
