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
          <app-competence-filter :competences.sync="competences"></app-competence-filter>
           <div>
            <h4>Anwendung:</h4>
            <ul class="list-unstyled">
                <li><input type="checkbox" value="App" name="application" id="application-1" v-model="applications"><label for="application-1">App</label></li>
                <li><input type="checkbox" value="Website" name="application" id="application-2" v-model="applications"><label for="application-2">Website</label></li>
                <li><input type="checkbox" value="Programm" name="application" id="application-3" v-model="applications"><label for="application-3">Programm</label></li>
                <li><input type="checkbox" value="Browser-Add-on" name="application" id="application-4" v-model="applications"><label for="application-4">Browser-Add-on</label></li>
            </ul>
          </div>
           <div>
            <h4>Betriebssystem:</h4>
            <ul class="list-unstyled">
              <li>
                <input type="checkbox" value="1" name="os" id="os-1" v-model="operatingSystems"><label for="os-1">Android</label>
              </li>
                <li><input type="checkbox" value="7" name="os" id="os-2" v-model="operatingSystems"><label for="os-2">BlackBerry OS</label></li>
                <li><input type="checkbox" value="2" name="os" id="os-3" v-model="operatingSystems"><label for="os-3">iOS</label></li>
                <li><input type="checkbox" value="5" name="os" id="os-4" v-model="operatingSystems"><label for="os-4">Linux</label></li>
                <li><input type="checkbox" value="3" name="os" id="os-5" v-model="operatingSystems"><label for="os-5">macOS</label></li>
                <li><input type="checkbox" value="4" name="os" id="os-6" v-model="operatingSystems"><label for="os-6">Windows</label></li>
                <li><input type="checkbox" value="6" name="os" id="os-7" v-model="operatingSystems"><label for="os-7">Windows Phone</label></li>
            </ul>
          </div>

          <div>
            <h4>Status</h4>
            <select name="status" id="status-dropdown" v-model="status" @change="updateContents">
                <option id="status-0" value="" name="status" selected>--------</option>
                <option id="status-1" value="on" name="status">Online</option>
                <option id="status-2" value="off" name="status">Offline</option>
                <option id="status-3" value="onoff" name="status">Online & Offline</option>
            </select>
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
  import { contentFilter } from './mixins/contentFilterMixin'

  export default {
    name: 'ToolsFilterApp',
    mixins: [contentFilter],
    data () {
      return {
        dataUrl: '/api/tools',
        status: null,
        applications: [],
        operatingSystems: []
      }
    },
    methods: {
      getQueryParams () {
        return {
          status: this.status,
          applications: this.applications,
          operatingSystems: this.operatingSystems
        }
      }
    },
    watch: {
      applications () {
        this.debouncedUpdate()
      },
      operatingSystems () {
        this.debouncedUpdate()
      }
    }
  }
</script>

<style scoped>

</style>