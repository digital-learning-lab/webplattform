<template>
  <div class="row mt-5 mb-5">
    <div class="col col-12 col-lg-5 col-xl-4">
      <div class="section-info">
        <form action="">
          <h2>Filtern nach</h2>

          <h3 class="form-subhead">Sortierung</h3>
          <select name="sortby" id="sortby-select" v-model="sortBy" @change="updateContents" class="form-control">
            <option value="latest" selected>Neustes zuerst</option>
            <option value="-latest">Ältestes zuerst</option>
            <option value="az">A-Z</option>
            <option value="za">Z-A</option>
          </select>
          <h3 class="form-subhead">Schlagwortsuche</h3>
          <input type="text" v-model="searchTerm" name="searchTerm" class="form-control" @keydown="preventEnter">
          <app-competence-filter :competences.sync="competences"></app-competence-filter>
           <div>
            <h3 class="form-subhead">Anwendung:</h3>
            <ul class="list-unstyled">
                <li class="form-check">
                  <input type="checkbox" class="form-check-input" value="App" name="application" id="application-1" v-model="applications">
                  <label class="form-check-label" for="application-1">App</label>
                </li>
                <li class="form-check">
                  <input type="checkbox" class="form-check-input" value="Website" name="application" id="application-2" v-model="applications">
                  <label class="form-check-label" for="application-2">Website</label>
                </li>
                <li class="form-check">
                  <input type="checkbox" class="form-check-input" value="Programm" name="application" id="application-3" v-model="applications">
                  <label class="form-check-label" for="application-3">Programm</label>
                </li>
                <li class="form-check">
                  <input type="checkbox" class="form-check-input" value="Browser-Add-on" name="application" id="application-4" v-model="applications">
                  <label class="form-check-label" for="application-4">Browser-Add-on</label>
                </li>
            </ul>
          </div>
           <div>
            <h3 class="form-subhead">Betriebssystem:</h3>
            <ul class="list-unstyled">
              <li class="form-check">
                <input type="checkbox" class="form-check-input" value="1" name="os" id="os-1" v-model="operatingSystems">
                <label class="form-check-label" for="os-1">Android</label>
              </li>
                <li class="form-check">
                  <input type="checkbox" class="form-check-input" value="7" name="os" id="os-2" v-model="operatingSystems">
                  <label class="form-check-label" for="os-2">BlackBerry OS</label>
                </li>
                <li class="form-check">
                  <input type="checkbox" class="form-check-input" value="2" name="os" id="os-3" v-model="operatingSystems">
                  <label class="form-check-label" for="os-3">iOS</label>
                </li>
                <li class="form-check">
                  <input type="checkbox" class="form-check-input" value="5" name="os" id="os-4" v-model="operatingSystems">
                  <label class="form-check-label" for="os-4">Linux</label>
                </li>
                <li class="form-check">
                  <input type="checkbox" class="form-check-input" value="3" name="os" id="os-5" v-model="operatingSystems">
                  <label class="form-check-label" for="os-5">macOS</label>
                </li>
                <li class="form-check">
                  <input type="checkbox" class="form-check-input" value="4" name="os" id="os-6" v-model="operatingSystems">
                  <label class="form-check-label" for="os-6">Windows</label>
                </li>
                <li class="form-check">
                  <input type="checkbox" class="form-check-input" value="6" name="os" id="os-7" v-model="operatingSystems">
                  <label class="form-check-label" for="os-7">Windows Phone</label>
                </li>
            </ul>
          </div>

          <div>
            <h3 class="form-subhead">Status</h3>
            <select name="status" id="status-dropdown" v-model="status" @change="updateContents" class="form-control">
                <option id="status-0" value="" name="status" selected>--------</option>
                <option id="status-1" value="on" name="status">Online</option>
                <option id="status-2" value="off" name="status">Offline</option>
                <option id="status-3" value="onoff" name="status">Online & Offline</option>
            </select>
          </div>
        </form>
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
    name: 'ToolsFilterApp',
    mixins: [contentFilter],
    data () {
      return {
        dataUrl: '/api/tools',
        status: '',
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