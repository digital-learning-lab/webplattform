<template>
  <div class="form-group">
    <label :for="id">{{ label }}<span v-if="required">*</span></label>

    <div class="custom-file">
      <div class="d-flex">
        <input type="file" class="custom-file-input" :id="id" @change="processInput" :disabled="readonly" :accept="accept">
        <label class="custom-file-label" :for="id"><span v-if="fileName">{{ fileName }}</span><span v-else>{{ fileLabel }}</span></label>
        <button class="button--neutral button--smallSquare ml-1" data-toggle="tooltip" data-placement="top" :title="helpText" v-if="helpText" type="button">
          <span class="far fa-question-circle"></span>
        </button>
      </div>
    </div>
    <small v-if="hintText" class="form-text text-muted">{{ hintText }}</small>
    <img v-if="imageUrl" :src="imageUrl" alt="Vorschaubild" class="img-thumbnail">
    <app-review-input :mode="review ? 'review' : 'edit'" :id="'id'+-review" :name="label" :reviewValue.sync="ownReviewValue"></app-review-input>
  </div>
</template>

<script>
  import ReviewInput from './ReviewInput.vue'
  import { reviewMixin } from '../mixins/reviewMixin'

  export default {
    name: 'FileInput',
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
      fileLabel: {
        type: String,
        default: '',
        required: true
      },
      image: {
        type: Object,
        default: () => {
          return {}
        },
        required: false
      },
      accept: {
        type: String,
        default: 'image/gif, image/jpeg, image/png',
        required: false
      },
      helpText: {
        type: String,
        default: '',
        required: false
      },
      hintText: {
        type: String,
        default: null,
        required: false
      },
      readonly: {
        type: Boolean,
        default: false,
        required: false
      }
    },
    data () {
      return {
        inputValue: null,
        file: null
      }
    },
    methods: {
      processInput (e) {
        this.inputValue = e.target.files[0]
      }
    },
    computed: {
      imageUrl () {
        if (this.inputValue) {
          return URL.createObjectURL(this.inputValue)
        }
        if (this.image) {
          return this.image.url
        }
        return null
      },
      fileName () {
        if (this.inputValue) {
          return this.inputValue.name
        }
        if (this.image) {
          return this.image.name
        }
        return ''
      }
    },
    created () {
      if (this.image) {

      }
    },
    watch: {
      inputValue (newValue) {
        this.$emit('update:value', newValue)
      }
    }
  }
</script>

<style scoped>

</style>