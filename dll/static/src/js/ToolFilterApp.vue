<template>
  <div class="row mt-5 mb-5">
    <div class="col col-12 col-lg-5 col-xl-4 mb-4">
      <div class="section-info">
        <form action="" id="filterForm" class="collapse d-lg-block">
          <h2>Filtern nach</h2>
          <h3 class="form-subhead">Schlagwortsuche</h3>
          <input type="text" v-model="q" name="searchTerm" class="form-control" @keydown="preventEnter">

          <div>
            <h3 class="form-subhead">Tool-Kategorien</h3>
            <ul class="list-unstyled">
              <li class="form-check" v-for="potential in getPotentials()">
                <input type="checkbox" class="form-check-input" :value="potential.value" name="potential" :id="'potential' + potential.value" v-model="potentials">
                <label class="form-check-label" :for="'potential' + potential.value">{{ potential.name }}</label>
              </li>
            </ul>
          </div>
          <div>
            <h3 class="form-subhead">Fächerbezug</h3>
            <select name="subjects" id="subjects" v-model="subjects" @change="updateContents" class="form-control">
              <option value="" selected>--------</option>
              <option v-for="subject in getSubjects()" :value="subject.value">{{ subject.name }}</option>
            </select>
          </div>
          <div>
            <h3 class="form-subhead">Datenschutz</h3>
            <select name="dataPrivacy" id="dataPrivacy" v-model="dataPrivacy" @change="updateContents" class="form-control">
              <option value="" selected>--------</option>
              <option v-for="privacy in getDataPrivacyOptions()" :value="privacy.value">{{ privacy.name }}</option>
            </select>
          </div>
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
            <h3 class="form-subhead">Kostenpflichtig</h3>
            <select name="withCosts" id="withCosts" v-model="withCosts" @change="updateContents" class="form-control">
              <option value="" selected>--------</option>
              <option value="0" selected>Nein</option>
              <option value="1" selected>Ja</option>
            </select>
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
          <p>Bitte versuchen Sie es mit anderen Suchbegriffen oder schauen Sie gern auf anderen Datenbanken für freie Unterrichtsmaterialien wie <a href="https://oerhoernchen.de/suche" target="_blank" rel="noopener noreferrer">OERhörchen</a>.</p>
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
        applications: [],
        subjects: [],
        toolFunctions: [],
        potentials: [],
        operatingSystems: [],
        dataPrivacy: null,
        withCosts: null
      }
    },
    methods: {
      getPotentials () {
        return window.potentialFilter
      },
      getDataPrivacyOptions () {
        return window.dataPrivacyFilter
      },
      getQueryParams () {
        return {
          dataPrivacy: this.dataPrivacy,
          applications: this.applications,
          operatingSystems: this.operatingSystems,
          toolFunctions: this.toolFunctions,
          withCosts: this.withCosts,
          potentials: this.potentials,
          subjects: this.subjects
        }
      },
      getToolFunctions () {
        return window.functionsFilter
      }
    },
    watch: {
      toolFunctions () {
        this.debouncedUpdate()
      },
      dataPrivacy () {
        this.debouncedUpdate()
      },
      applications () {
        this.debouncedUpdate()
      },
      operatingSystems () {
        this.debouncedUpdate()
      },
      subjects () {
        this.debouncedUpdate()
      },
      withCosts () {
        this.debouncedUpdate()
      },
      potentials () {
        this.debouncedUpdate()
      }
    }
  }
</script>

<style scoped>

</style>