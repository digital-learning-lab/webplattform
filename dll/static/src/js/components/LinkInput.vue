<template>
  <div class="form-group">
      <label  :for="id" class="mb-2 w-100">{{ label }}:<span v-if="required">*</span></label>
      <button class="button--neutral button--smallSquare button--help ml-1 float-right" type="button" data-toggle="tooltip" data-placement="top" :title="helpText" v-if="helpText"></button>
    <div class="form__links-input">
      <div class="d-flex align-items-baseline ">
        <input type="text" class="form-control mr-3" :class="{'form__field--error': error}" :id="id" placeholder="Linktext" v-model="internalLink.name" :readonly="readonly">
        <input type="text" class="form-control mr-3" :class="{'form__field--error': !internalLink.validUrl || error}" :id="id" placeholder="https://example.org" v-model="internalLink.url" :readonly="readonly" @blur="checkLinkValid(internalLink)">
        <select class="form-control mr-3" name="types" v-model="internalLink.type" v-if="types">
          <option value="video">Video / Audio</option>
          <option value="href">Text</option>
        </select>
      </div>
    </div>
    <div class="alert alert-danger mt-1" v-if="!internalLink.validUrl">
      Bitte geben Sie eine valide URL ein. Die URL muss mit http:// bzw. https:// beginnen.
    </div>
    <div class="alert alert-danger mt-1" v-if="incomplete">
      Bitte geben Sie sowohl eine Bezeichnung (z.B. Webseite X) und eine URL an.
    </div>
    <app-review-input :mode="review ? 'review' : 'edit'" :id="'id'+-review" :name="label" :reviewValue.sync="ownReviewValue"></app-review-input>
  </div>
</template>

<script>
  import ReviewInput from './ReviewInput.vue'
  import { reviewMixin } from '../mixins/reviewMixin'
  export default {
    name: 'LinkInput',
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
      error: {
        type: Boolean,
        default: false,
        required: false
      },
      link: {
        type: Object,
        default: () => {
          return {url: '', name: '',  validUrl: true}
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
        internalLink: [],
        incomplete: false
      }
    },
    methods: {
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
        this.incomplete  = !link.url || !link.name
        this.$forceUpdate()
      }
    },
    created () {
      if (this.link) {
        this.internalLink = this.link
        this.internalLink.validUrl = true
      } else {
        this.internalLink = {url: '', name: '',  validUrl: true}
      }
    },
    watch: {
      internalLink: {
        handler: function (newValue) {
           console.log(newValue)
          this.$emit('update:link', newValue)
        },
        deep: true
      }
    }
  }
</script>

<style scoped>

</style>