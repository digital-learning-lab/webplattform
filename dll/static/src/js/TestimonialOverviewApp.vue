<template>
  <div>
    <div class="row mb-4 text-center">
      <div class="col">
        <div>
          <label for="status">Status:</label>
        </div>
        <select name="status" id="status" v-model="status" @change="updateReviews">
          <option value="">Alle</option>
          <option value="0">Neu</option>
          <option value="4">Änderungen angefragt</option>
          <option value="2">Akzeptiert</option>
          <option value="3">Abgelehnt</option>
        </select>
      </div>
      <div class="col">
        <div>
          <label for="contentSearch">Suche:</label>
        </div>
        <input type="text" name="q" v-model="searchTerm" id="contentSearch" @input="debouncedUpdate">
      </div>
    </div>

    <div class="content-box" :class="'content-box--' + review.type" v-for="review in reviews">
      <div class="row">
        <div class="col-sm-3">
          <div class="content-box__type">{{ review.type_verbose }} ({{ review.status_display }})</div>
          <div class="content-box__title">{{ review.name }}</div>
          <div class="content-box__author">
            <span class="fas fa-user"></span> {{ review.author }}
          </div>
          <div class="content-box__date" v-if="review.submitted">
            <span>Einreichungsdatum: {{ review.submitted }}</span>
          </div>
        </div>
        <div class="col">
          <p class="font-weight-bold">Erfahrungsbericht</p>
          <p>
            {{ review.testimonial_comment }}
          </p>
        </div>
        <div class="col">
          <ul class="content-box__actions" v-if="review.status == 0 || review.status === 1">
            <li class="content-box__action">
              <a class="content-box__link content-box__link--action" @click="accept(review)">
                <span class="far fa-thumbs-up"></span>
              </a>
            </li>
            <li class="content-box__action">
              <a class="content-box__link content-box__link--action" @click="decline(review)">
                <span class="far fa-thumbs-down"></span>
              </a>
            </li>
            <li class="content-box__action">
              <a class="content-box__link content-box__link--action" @click="changeComment(review)">
                <span class="far fa-edit"></span>
              </a>
            </li>
          </ul>
          <div v-else-if="review.status === 4">
            <p class="font-weight-bold">Review Kommentar</p>
            <p>{{ review.comment }}</p>
          </div>
        </div>
      </div>
      <div class="row mt-3"  v-if="(review.status === 0 || review.status === 1) && review.change">
        <div class="col-12">
          <textarea name="review-comment" class="form-control" v-model="review.comment"></textarea>
          <div class="alert alert-danger mt-2" v-if="review.commentError" v-text="review.commentError"></div>
        </div>
        <div class="col-12 mt-2">
          <button class="btn btn-primary" @click="requestChange(review)">Änderungen anfragen</button>
        </div>
      </div>
    </div>
    <app-pagination :current-page="currentPage" :pagination="pagination" @prev="previousPage" @next="nextPage" @jump="jumpTo"></app-pagination>
    <div v-if="reviews.length === 0" class="text-center">
      Es stehen keine Erfahrungsberichte zur Verfügung.
    </div>
  </div>
</template>

<script>
  import Vue from 'vue'
  import vSelect from 'vue-select'
  import debounce from 'lodash/debounce'
  import axios from 'axios'
  import Pagination from './components/Pagination.vue'
  import { paginationMixin } from './mixins/paginationMixin'
  import { axiosMixin } from './mixins/axiosMixin'

  export default {
    name: 'OverviewApp',
    data () {
      return {
        reviews: [],
        type: null,
        searchTerm: null,
        status: null,
        retrieveUrl: null,
        invitationContents: [],
        reviewers: []
      }
    },
    components: {
      'AppPagination': Pagination,
      'v-select': vSelect,
    },
    mixins: [paginationMixin, axiosMixin],
    computed: {
      params () {
        return {
          type: this.type,
          q: this.searchTerm,
          status: this.status,
        }
      }
    },
    methods: {
      changeComment(review) {
        if (review.change === undefined) {
          Vue.set(review, 'change', true)
        } else {
          Vue.set(review, 'change', !review.change)
        }
      },
      updateReviews (page) {
        axios.get(this.retrieveUrl, {
          params: {
            ...this.params,
            page: Number.isInteger(page) ? page : 1,
          }
        })
        .then(res => {
          this.reviews = res.data.results
          this.updatePagination(res)
        })
        .catch(err => {
          console.log(err)
        })
        .catch(err => {
          console.log(err)
        })
      },
      sendChange(url, body) {
        body = body || {}
        axios.post(url, body, {
            headers: {
              'X-CSRFToken': window.dllData.csrfToken
            },
        }).then(res => {
          this.updateReviews()
        })
      },
      accept(review) {
        const url = `${this.retrieveUrl}${review.pk}/accept/`
        this.sendChange(url)
      },
      decline(review) {
        const url = `${this.retrieveUrl}${review.pk}/decline/`
        this.sendChange(url)
      },
      requestChange(review) {
        if (!review.comment) {
          Vue.set(review, 'commentError', 'Bitte gib einen Kommentar ein.')
          return
        }
        const url = `${this.retrieveUrl}${review.pk}/request_changes/`
        const body = {
          comment: review.comment
        }
        this.sendChange(url, body)
      },
    },
    created () {
      if (!window.dllData.retrieveUrl) {
        throw Error('Retrieve URL is not defined.')
      }
      this.retrieveUrl = window.dllData.retrieveUrl
      this.csrfToken = window.dllData.csrfToken
      this.updateReviews()
      this.debouncedUpdate = debounce(this.updateReviews, 500)
    }
  }
</script>

<style scoped>

</style>