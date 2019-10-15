<template>
  <div class="form-group">
    <label  :for="id" class="mb-2 w-100">{{ label }}:<span v-if="required">*</span></label>
    <button class="button--neutral button--smallSquare button--help ml-1 float-right" type="button" data-toggle="tooltip" data-placement="top" :title="helpText" v-if="helpText"></button>
    <div class="form__list-inputs">
      <div class="mb-2" v-for="link in internalLinks">
        <div class="d-flex align-items-baseline ">
          <input type="text" class="form-control mr-3" :id="id" :placeholder="namePlaceholder" v-model="link.name" :readonly="readonly">
          <input type="text" class="form-control mr-3" :class="{'form__field--error': !link.validUrl}" :id="id" :placeholder="linkPlaceholder" v-model="link.url" :readonly="readonly" @blur="checkLinkValid(link)">
          <select class="form-control mr-3" name="types" v-model="link.type" v-if="types">
            <option value="video">Video / Audio</option>
            <option value="href">Text</option>
          </select>
          <button class="button--danger button--smallSquare" @click="removeLink(link)" type="button" v-if="!readonly">
            <span class="fas fa-times"></span>
          </button>
        </div>
        <div class="alert alert-danger mt-1" v-if="!link.validUrl">
          Bitte geben Sie eine valide URL ein. Die URL muss mit http:// bzw. https:// beginnen.
        </div>
      </div>
    </div>
    <div v-if="!readonly">
      <button class="button--neutral button--smallSquare" @click="addLink" type="button">
        <span class="fas fa-plus"></span>
      </button>
    </div>
    <app-review-input :mode="review ? 'review' : 'edit'" :id="'id'+-review" :name="label" :reviewValue.sync="ownReviewValue"></app-review-input>
  </div>
</template>

<script>
  import ReviewInput from './ReviewInput.vue'
  import { reviewMixin } from '../mixins/reviewMixin'

  export default {
    name: 'LinksInput',
    components: {
      'AppReviewInput': ReviewInput
    },
    mixins: [reviewMixin],
    props: {
      id: {
        type: String,
        default: '',
        required: true
      },
      required: {
        type: Boolean,
        default: false,
        required: false
      },
      namePlaceholder: {
        type: String,
        default: 'Linktext',
        required: false
      },
      linkPlaceholder: {
        type: String,
        default: 'https://example.org',
        required: false
      },
      label: {
        type: String,
        default: '',
        required: true
      },
      type: {
        type: String,
        default: 'href',
        required: false
      },
      links: {
        type: Array,
        default: () => {
          return []
        },
        required: false
      },
      helpText: {
        type: String,
        default: '',
        required: false
      },
      readonly: {
        type: Boolean,
        default: false,
        required: false
      },
      types: {
        type: Boolean,
        default: false,
        required: false
      }
    },
    data () {
      return {
        internalLinks: []
      }
    },
    methods: {
      addLink () {
        this.internalLinks.push({name: '', url: '', type: this.type, validUrl: true})
      },
      removeLink (link) {
        this.internalLinks.splice(this.internalLinks.indexOf(link), 1)
      },
      isValidUrl (url) {
        // https://stackoverflow.com/questions/5717093/check-if-a-javascript-string-is-a-url
        var pattern = new RegExp('^(https?:\\/\\/)'+
          '((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.)+[a-z]{2,}|'+
          '((\\d{1,3}\\.){3}\\d{1,3}))'+
          '(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*'+
          '(\\?[;&a-z\\d%_.~+=-]*)?'+
          '(\\#[-a-z\\d_]*)?$','i');
        return !!pattern.test(url)
      },
      checkLinkValid (link) {
        link.validUrl = this.isValidUrl(link.url)
        this.$forceUpdate()
      }
    },
    created () {
      if (this.links) {
        this.internalLinks = this.links
        for (let i = 0; i < this.internalLinks.length; i++) {
          this.internalLinks[i].validUrl = true
        }
      }
    },
    watch: {
      internalLinks: {
        handler: function (newValue) {
          this.$emit('update:links', newValue)
        },
        deep: true
      },
      links (newValue) {
        if (newValue) {
          this.internalLinks = this.links
          for (let i = 0; i < this.internalLinks.length; i++) {
            this.internalLinks[i].validUrl = true
          }
        } else {
          this.internalLinks = []
        }
      }
    }
  }
</script>

<style scoped>
</style>