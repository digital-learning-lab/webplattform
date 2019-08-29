<template>
  <div>
    <div class="row mb-4 text-center">
      <div class="col">
        <div>
          <label for="type">Elemente:</label>
        </div>
        <select name="type" id="type" v-model="type" @change="updateContents">
          <option value="">Alle</option>
          <option value="trend">Trend</option>
          <option value="tool">Tool</option>
          <option value="teaching-module">Unterrichtsbaustein</option>    
        </select>
      </div>
      <div class="col" v-if="mode === 'overview'">
        <div>
          <label for="status">Status:</label>
        </div>
        <select name="status" id="status" v-model="status" @change="updateContents">
          <option value="">Alle</option>
          <option value="draft">Entwurf</option>
          <option value="submitted">Eingereicht</option>
          <option value="approved">Freigegeben</option>
          <option value="declined">Abgelehnt</option>
        </select>
      </div>
      <div class="col">
        <div>
          <label for="contentSearch">Suche:</label>
        </div>
        <input type="text" name="q" v-model="searchTerm" id="contentSearch" @input="debouncedUpdate">
      </div>
    </div>

    <div class="content-box" :class="'content-box--' + content.type" v-for="content in contents">
      <div class="row">
        <div class="col">
          <div class="content-box__type">{{ content.type_verbose }} ({{ content.status }})</div>
          <div class="content-box__title">{{ content.name }}</div>
          <div class="content-box__author">
            <span class="fas fa-user"></span> {{ content.author }}
          </div>
        </div>
        <div class="col" v-if="content.co_authors.length">
          <div class="content-box__coauthors">
            <span class="fas fa-users align-top"></span>
            <ul class="list-unstyled d-inline-block ml-1">
              <li v-for="author in content.co_authors">{{ author }}</li>
            </ul>
          </div>
        </div>
        <div class="col">
          <ul class="content-box__actions">
            <li class="content-box__action">
              <a class="content-box__link content-box__link--preview" :href="content.preview_url">
                <span class="far fa-eye"></span>
              </a>
            </li>
            <li class="content-box__action" v-if="mode === 'overview'">
              <a class="content-box__link content-box__link--action" :href="content.edit_url">
                <span class="far fa-edit"></span>
              </a>
            </li>
            <li class="content-box__action" v-if="mode === 'review'">
              <a class="content-box__link content-box__link--action" :href="content.review_url">
                <span class="far fa-edit"></span>
              </a>
            </li>
          </ul>
        </div>
      </div>
    </div>
    <app-pagination :current-page="currentPage" :pagination="pagination" @prev="previousPage" @next="nextPage" @jump="jumpTo"></app-pagination>
    <div v-if="contents.length === 0" class="text-center">
      Es stehen keine Inhalte zur Verfügung.
    </div>
  </div>
</template>

<script>
  import { debounce } from 'lodash'
  import axios from 'axios'
  import Pagination from './components/Pagination.vue'

  export default {
    name: 'OverviewApp',
    data () {
      return {
        contents: [],
        type: null,
        searchTerm: null,
        status: null,
        retrieveUrl: null,
        mode: null
      }
    },
    components: {
      'AppPagination': Pagination
    },
    computed: {
      params () {
        return {
          type: this.type,
          q: this.searchTerm,
          status: this.status
        }
      }
    },
    methods: {
      updateContents () {
        axios.get(this.retrieveUrl, {
          params: {
            ...this.params
          }
        })
        .then(res => {
          this.contents = res.data.results
        })
        .catch(err => {
          console.log(err)
        })
      }
    },
    created () {
      if (!window.dllData.retrieveUrl) {
        throw Error('Retrieve URL is not defined.')
      }
      this.retrieveUrl = window.dllData.retrieveUrl
      this.mode = window.dllData.mode || 'overview'
      this.updateContents()
      this.debouncedUpdate = debounce(this.updateContents, 500)
    }
  }
</script>

<style scoped>

</style>