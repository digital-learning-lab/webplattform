<template>
  <div class="row mt-5 mb-5">
    <div class="col col-3">
      <div class="section-info">
        <form action="">
          <h2>Filtern nach</h2>

          <h3>Sortierung</h3>
          <select name="sortby" id="sortby-select" v-model="sortBy" @change="updateContents">
            <option value="latest">Neustes zuerst</option>
            <option value="-latest">Ältestes zuerst</option>
            <option value="az">A-Z</option>
            <option value="za">Z-A</option>
          </select>
          <h3>Schlagwortsuche</h3>
          <input type="text" v-model="searchTerm" name="searchTerm">
          <app-competence-filter :competences.sync="competences"></app-competence-filter>
          <div>
            <h4>Sprachen</h4>
            <select name="language" id="language-dropdown" v-model="language" @change="updateContents">
                <option id="language-0" value="" name="language" selected>--------</option>
                <option id="language-1" value="german" name="language">Deutsch</option>
                <option id="language-2" value="english" name="language">Englisch</option>
                <option id="language-3" value="french" name="language">Französisch</option>
                <option id="language-4" value="russian" name="language">Russisch</option>
            </select>
          </div>
          <div>
            <h4>Trendtyp:</h4>
            <ul class="list-unstyled">
              <li>
                <input type="checkbox" value="1" name="trend-type" id="type-1" v-model="trendTypes"><label for="type-1">Forschung</label>
              </li>
              <li>
                <input type="checkbox" value="2" name="trend-type" id="type-2" v-model="trendTypes"><label for="type-2">Portal</label>
              </li>
              <li><input type="checkbox" value="3" name="trend-type" id="type-3" v-model="trendTypes"><label for="type-3">Praxisbeispiel</label>
              </li>
              <li>
                <input type="checkbox" value="4" name="trend-type" id="type-4" v-model="trendTypes"><label for="type-4">Veröffentlichung</label>
              </li>
            </ul>
          </div>
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
        <app-pagination :current-page="currentPage" :pagination="pagination" @prev="previousPage" @next="nextPage" @jump="jumpTo"></app-pagination>
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