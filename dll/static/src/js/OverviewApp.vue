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
      <div class="col">
        <div>
          <label for="status">Status:</label>
        </div>
        <select name="status" id="status" v-model="status" @change="updateContents">
          <option value="">Alle</option>
          <option value="draft">Entwurf</option>
          <option value="submitted">Eingereicht</option>
          <option value="approved">Freigegeben</option>
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
        <div class="col" v-if="content.co_authors">
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
              <a :href="content.preview_url">
                <span class="far fa-eye"></span>
              </a>
            </li>
            <li class="content-box__action">
              <a :href="content.edit_url">
                <span class="far fa-edit"></span>
              </a>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import { debounce } from 'lodash'
  import axios from 'axios'

  export default {
    name: 'OverviewApp',
    data () {
      return {
        contents: [],
        type: null,
        searchTerm: null,
        status: null
      }
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
        axios.get('/api/meine-inhalte', {
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
      this.updateContents()
      this.debouncedUpdate = debounce(this.updateContents, 500)
    }
  }
</script>

<style scoped>

</style>