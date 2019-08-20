<template>
  <div class="row mt-5 mb-5">
    <div class="col col-12 col-lg-5 col-xl-4">
      <div class="section-info">
        <form action="">
          <h2>Filtern nach</h2>

          <h3 class="form-subhead">Sortierung</h3>
          <select name="sortby" id="sortby-select" v-model="sortBy" @change="updateContents" class="form-control">
            <option value="az">A-Z</option>
            <option value="za">Z-A</option>
          </select>
          <h3 class="form-subhead">Schlagwortsuche</h3>
          <input type="text" v-model="searchTerm" name="searchTerm" class="form-control">
          <h3 class="form-subhead">Auswahl</h3>
          <ul class="list-unstyled">
            <li class="form-check">
              <input type="checkbox" id="teaching-modules-checkbox" @change="updateContents" v-model="showTeachingModules" class="form-check-input">
              <label class="form-check-label" for="teaching-modules-checkbox">Unterrichtsbausteine</label>
            </li>
            <li class="form-check">
              <input type="checkbox" id="tools-checkbox" @change="updateContents" v-model="showTools" class="form-check-input">
              <label class="form-check-label" for="tools-checkbox">Tools</label>
            </li>
            <li class="form-check">
              <input type="checkbox" id="trends-checkbox" @change="updateContents" v-model="showTrends" class="form-check-input">
              <label class="form-check-label" for="trends-checkbox">Trends</label>
            </li>
          </ul>
        </form>
      </div>
    </div>
    <div class="col col-12 col-lg-7 col-xl-8">
      <h1 v-html="window.competenceName"></h1>
      <p class="mb-5" v-html="window.competenceText"></p>
      <div class="row" v-if="contents.length > 0 || loading">
        <div class="col col-12 col-xl-6 mb-4" v-for="content in contents">
          <app-content-teaser :content="content"></app-content-teaser>
        </div>
        <app-pagination :current-page="currentPage" :pagination="pagination" @prev="previousPage" @next="nextPage" @jump="jumpTo"></app-pagination>
      </div>
      <div class="row" v-else>
        <div class="col">
          <h2>Ihre Suchanfrage ergab keine Treffer.</h2>
          <p>Bitte versuchen Sie es mit einer anderen Auswahl.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import { debounce } from 'lodash'
  import axios from 'axios'
  import ContentTeaser from './components/ContentTeaser.vue'
  import Pagination from './components/Pagination.vue'

  export default {
    name: 'CompetenceFilterApp',
    components: {
      'AppContentTeaser': ContentTeaser,
      'AppPagination': Pagination
    },
    data () {
      return {
        contents: [],
        competence: {
          name: 'Kommunizieren & Kooperieren',
          description: 'Um im digitalen Raum adäquat KOMMUNIZIEREN & KOOPERIEREN zu können, braucht es entsprechende Kompetenzen, digitale Werkzeuge zur angemessenen und effektiven Kommunikation einsetzen und in digitalen Umgebungen zielgerichtet kooperieren zu können. Dabei geht es vor allem darum, entsprechend der jeweiligen Situation und ausgerichtet an den Kommunikations- bzw. Kooperationspartnern die passenden Werkzeuge auszuwählen und entsprechende Umgangsregeln einzuhalten.'
        },
        loading: true,
        sortBy: 'az',
        searchTerm: '',
        showTeachingModules: true,
        showTrends: true,
        showTools: true,
        currentPage: 1,
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
      updateContents (page) {
        this.loading = true
        axios.get('/api/inhalte', {
          params: {
            q: this.searchTerm,
            sorting: this.sortBy,
            teachingModules: this.showTeachingModules,
            trends: this.showTrends,
            tools: this.showTools,
            competence: this.window.competenceSlug,
            page: Number.isInteger(page) ? page : 1
          }
        })
          .then(response => {
            this.loading = false
            this.contents = response.data.results
            this.pagination = {
              count: response.data.count,
              perPage: 10,
              next: response.data.next,
              prev: response.data.previous
            }
          })
          .catch(error => {
            this.loading = false
            console.log(error)
          })
      }
    },
    computed: {
      window () {
        return window
      },
      sortedAndFilteredContents () {
        let filteredContents = this.contents.filter((content) => {
          if (content.type === 'teaching-module') {
            return this.showTeachingModules
          }
          if (content.type === 'trend') {
            return this.showTrends
          }
          if (content.type === 'tool') {
            return this.showTools
          }
        })
        return filteredContents.sort(this.sortContents)
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
      }
    }
  }
</script>

<style scoped>

</style>