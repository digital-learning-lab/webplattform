<template>
  <div class="row mt-5 mb-5">
    <div class="col col-3">
      <div class="section-info">
        <form action="">
          <h2>Filtern nach</h2>

          <h3>Sortierung</h3>
          <select name="sortby" id="sortby-select" v-model="sortBy" @change="updateContents">
            <option value="az">A-Z</option>
            <option value="za">Z-A</option>
          </select>
          <h3>Schlagwortsuche</h3>
          <input type="text" v-model="searchTerm" name="searchTerm">
          <h3>Auswahl</h3>
          <ul class="list-unstyled">
            <li>
              <input type="checkbox" id="teaching-modules-checkbox" @change="updateContents" v-model="showTeachingModules">
              <label for="teaching-modules-checkbox">Unterrichtsbausteine</label>
            </li>
            <li>
              <input type="checkbox" id="tools-checkbox" @change="updateContents" v-model="showTools">
              <label for="tools-checkbox">Tools</label>
            </li>
            <li>
              <input type="checkbox" id="trends-checkbox" @change="updateContents" v-model="showTrends">
              <label for="trends-checkbox">Trends</label>
            </li>
          </ul>
        </form>
      </div>
    </div>
    <div class="col col-9">
      <h1 v-html="window.competenceName"></h1>
      <p class="mb-5" v-html="window.competenceText"></p>
      <div class="row">
        <div class="col col-12 col-md-6 mb-4" v-for="content in contents">
          <app-content-teaser :content="content"></app-content-teaser>
        </div>
      </div>
        <div class="pagination">
          <button class="pagination__previous" @click="previousPage" :disabled="pagination.prev === null">
            <span><</span>
          </button>
          <button class="pagination__number" v-for="page in pages" @click="jumpTo(page)">{{ page }}</button>
          <button class="pagination__next" @click="nextPage" :disabled="pagination.next === null">
            <span>></span>
          </button>
        </div>
      </div>
  </div>
</template>

<script>
  import { debounce } from 'lodash'
  import axios from 'axios'
  import ContentTeaser from './components/ContentTeaser.vue'

  export default {
    name: 'CompetenceFilterApp',
    components: {
      'AppContentTeaser': ContentTeaser
    },
    data () {
      return {
        contents: [],
        competence: {
          name: 'Kommunizieren & Kooperieren',
          description: 'Um im digitalen Raum adäquat KOMMUNIZIEREN & KOOPERIEREN zu können, braucht es entsprechende Kompetenzen, digitale Werkzeuge zur angemessenen und effektiven Kommunikation einsetzen und in digitalen Umgebungen zielgerichtet kooperieren zu können. Dabei geht es vor allem darum, entsprechend der jeweiligen Situation und ausgerichtet an den Kommunikations- bzw. Kooperationspartnern die passenden Werkzeuge auszuwählen und entsprechende Umgangsregeln einzuhalten.'
        },
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
      updateContents (page) {

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