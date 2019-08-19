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
            <h4>Unterrichtsfach</h4>
            <ul class="list-unstyled">
              <li v-for="subject in getSubjects()">
                <input type="checkbox" :value="subject.value" name="subjects" :id="'subject-' + subject.value" v-model="subjects"><label
                :for="'subject-' + subject.value">{{ subject.name }}</label>
              </li>
            </ul>
          </div>
          <div>
            <h4>Bundesland</h4>
            <select class="list-unstyled" v-model="state">
              <option v-for="state in getStates()" :value="state.value">{{state.name}}</option>
            </select>
          </div>
          <div>
            <h4>Jahrgangsstufe von / bis:</h4>
            <input type="text" name="schoolClassFrom" v-model="schoolClassFrom"> - <input type="text" name="schoolClassTo" v-model="schoolClassTo">
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
    name: 'TeachingModulesFilterApp',
    mixins: [contentFilter],
    data () {
      return {
        dataUrl: '/api/unterrichtsbausteine',
        subjects: [],
        state: null,
        schoolClassFrom: null,
        schoolClassTo: null
      }
    },
    methods: {
      getSubjects ()  {
        return window.subjectFilter
      },
      getStates ()  {
        return window.statesFilter
      },
      getQueryParams () {
        return {
          subjects: this.subjects,
          state: this.state,
          schoolClassFrom: this.schoolClassFrom,
          schoolClassTo: this.schoolClassTo
        }
      }
    },
    watch: {
      subjects () {
        this.updateContents()
      },
      state () {
        this.updateContents()
      },
      schoolClassFrom () {
        this.debouncedUpdate()
      },
      schoolClassTo () {
        this.debouncedUpdate()
      }
    }
  }
</script>

<style scoped>

</style>