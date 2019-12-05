import { debounce } from 'lodash'
import axios from 'axios'
import ContentTeaser from '../components/ContentTeaser.vue'
import CompetenceFilter from '../components/CompetenceFilter.vue'
import Pagination from '../components/Pagination.vue'
import { preventEnter } from './preventEnterMixin'
import { paginationMixin } from './paginationMixin'

export const contentFilter = {
  components: {
    'AppContentTeaser': ContentTeaser,
    'AppCompetenceFilter': CompetenceFilter,
    'AppPagination': Pagination
  },
  mixins: [preventEnter, paginationMixin],
  data () {
    return {
      dataUrl: null,
      contents: [],
      loading: true,
      sortBy: '-latest',
      searchTerm: '',
      competences: []
    }
  },
  methods: {
    getQueryParams () {
      return {}
    },
    updateContents (page) {
      this.loading = true
      if (!page || typeof page === 'object') {
        // Reset page to 1 if there is no page given or page object is an event (object)
        this.currentPage = 1
      }
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
          this.updatePagination(response)
          this.loading = false
        })
        .catch(error => {
          console.log(error)
          this.loading = false
        })
    }
  },
  computed: {
    window () {
      return window
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
      this.updateContents()
    }
  }
}