import { debounce } from 'lodash'
import axios from 'axios'
import ContentTeaser from '../components/ContentTeaser.vue'
import CompetenceFilter from '../components/CompetenceFilter.vue'

export const contentFilter = {
  components: {
    'AppContentTeaser': ContentTeaser,
    'AppCompetenceFilter': CompetenceFilter
  },
  data () {
    return {
      dataUrl: null,
      contents: [],
      sortBy: 'az',
      searchTerm: '',
      currentPage: 1,
      competences: [],
      pagination: {
        count: 0,
        perPage: 10,
        next: null,
        prev: null
      }
    }
  },
  methods: {
    jumpTo (page) {
      this.updateContents(page)
    },
    previousPage () {
      this.updateContents(--this.currentPage)
    },
    nextPage () {
      this.updateContents(++this.currentPage)
    },
    sortContents (a, b) {
      const nameA = a.name.toUpperCase();
      const nameB = b.name.toUpperCase();

      let comparison = 0;
      if (nameA > nameB) {
        comparison = 1;
      } else if (nameA < nameB) {
        comparison = -1;
      }

      return this.sortBy === 'az' ? comparison : -comparison;
    },
    getQueryParams () {
      return {}
    },
    updateContents (page) {

      axios.get(this.dataUrl, {
        params: {
          q: this.searchTerm,
          sorting: this.sortBy,
          competence: this.window.competenceSlug,
          page: Number.isInteger(page) ? page : 1,
          competences: this.competences,
          ...this.getQueryParams()
        }
      })
        .then(response => {
          this.contents = response.data.results
          this.pagination = {
            count: response.data.count,
            perPage: 10,
            next: response.data.next,
            prev: response.data.previous
          }
        })
        .catch(error => {
          console.log(error)
        })
    }
  },
  computed: {
    window () {
      return window
    },
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
  },
  created () {
    this.updateContents()
    this.debouncedUpdate = debounce(this.updateContents, 500)
  },
  watch: {
    searchTerm () {
      this.debouncedUpdate()
    },
    competences () {
      this.debouncedUpdate()
    }
  }
}