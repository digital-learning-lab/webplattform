<template>
  <div class="row mt-5 mb-5">
    <div class="col col-12 col-lg-5 col-xl-4 mb-4">
      <div class="section-info">
        <form action="" id="filterForm" class="collapse d-lg-block">
          <h2>Filtern nach</h2>

          <h3 class="form-subhead">Sortierung</h3>
          <select name="sortby" id="sortby-select" class="form-control" v-model="sortBy" @change="updateContents">
            <option value="latest">Neustes zuerst</option>
            <option value="-latest">Ältestes zuerst</option>
            <option value="az">A-Z</option>
            <option value="za">Z-A</option>
          </select>
          <h3 class="form-subhead">Schlagwortsuche</h3>
          <input type="text" v-model="searchTerm" name="searchTerm" class="form-control" @keydown="preventEnter">
          <app-competence-filter :competences.sync="competences"></app-competence-filter>
          <div>
            <h3 class="form-subhead">Sprachen</h3>
            <select name="language" id="language-dropdown" v-model="language" @change="updateContents" class="form-control">
                <option id="language-0" value="" name="language" selected>--------</option>
                <option id="language-1" value="german" name="language">Deutsch</option>
                <option id="language-2" value="english" name="language">Englisch</option>
            </select>
          </div>
          <div>
            <h3 class="form-subhead">Trendtyp:</h3>
            <ul class="list-unstyled">
              <li class="form-check">
                <input type="checkbox" value="1" name="trend-type" id="type-1" v-model="trendTypes" class="form-check-input">
                <label class="form-check-label" for="type-1">Forschung</label>
              </li>
              <li class="form-check">
                <input type="checkbox" value="2" name="trend-type" id="type-2" v-model="trendTypes" class="form-check-input">
                <label class="form-check-label" for="type-2">Portal</label>
              </li>
              <li class="form-check"><input type="checkbox" value="3" name="trend-type" id="type-3" v-model="trendTypes" class="form-check-input">
                <label class="form-check-label" for="type-3">Praxisbeispiel</label>
              </li>
              <li class="form-check">
                <input type="checkbox" value="4" name="trend-type" id="type-4" v-model="trendTypes" class="form-check-input">
                <label class="form-check-label" for="type-4">Veröffentlichung</label>
              </li>
            </ul>
          </div>
        </form>
        <div class="text-center">
          <button class="button button--primary d-lg-none" type="button" data-toggle="collapse" data-target="#filterForm" aria-expanded="false" aria-controls="filterForm">
            Filter ausklappen <span class="fas fa-chevron-circle-down"></span>
          </button>
        </div>
      </div>
    </div>
    <div class="col col-12 col-lg-7 col-xl-8">
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

  import { contentFilter } from './mixins/contentFilterMixin'

  export default {
    name: 'TrendsFilterApp',
    mixins: [contentFilter],
    data () {
      return {
        dataUrl: '/api/trends',
        language: null,
        trendTypes: []
      }
    },
    methods: {
      getQueryParams () {
        return {
          language: this.language,
          trendTypes: this.trendTypes
        }
      }
    },
    watch: {
      trendTypes () {
        this.debouncedUpdate()
      }
    }
  }
</script>

<style scoped>

</style>