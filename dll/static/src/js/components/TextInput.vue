<template>
  <div class="form-group">
    <label :for="id">{{ label }}:<span v-if="required">*</span></label>
    <div class="d-flex">
    <input :type="type" class="form-control" :id="id" :placeholder="placeholder" v-model="inputValue" :readonly="readonly" :maxlength="maximalChars">
      <button class="button--neutral button--smallSquare ml-1" data-toggle="tooltip" data-placement="top" :title="helpText" v-if="helpText" type="button">
        <span class="far fa-question-circle"></span>
      </button>
    </div>
    <small v-if="characterCounter" class="form-text text-muted float-right">{{ charactersLeft }} Zeichen verbleibend</small>

    <app-review-input :mode="review ? 'review' : 'edit'" :id="'id'+-review" :name="label" :reviewValue.sync="ownReviewValue"></app-review-input>
  </div>
</template>

<script>
  import ReviewInput from './ReviewInput.vue'
  import { reviewMixin } from '../mixins/reviewMixin'

  export default {
    name: 'TextInput',
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
      type: {
        type: String,
        default: 'text',
        required: false
      },
      readonly: {
        type: Boolean,
        default: false,
        required: false
      },
      placeholder:{
        type: String,
        default: '',
        required: false
      },
      characterCounter: {
        type: Boolean,
        default: false,
        required: false
      },
      maximalChars: {
        type: Number,
        default: null,
        required: false
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
      value: {
        type: String,
        default: '',
        required: false
      },
      helpText: {
        type: String,
        default: '',
        required: false
      }
    },
    computed: {
      charactersLeft () {
        return this.maximalChars - this.value.length
      }
    },
    data () {
      return {
        inputValue: ''
      }
    },
    created () {
      this.inputValue = this.value
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