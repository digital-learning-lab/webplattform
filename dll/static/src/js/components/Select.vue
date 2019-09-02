<template>
  <div class="form-group">
    <label :for="id">{{ label }}</label>
    <div class="d-flex">
      <select :name="id" :id="id" class="form-control" :class="{'form__field--error': error}" v-model="inputValue" :disabled="readonly">
        <option v-for="option in options" :value="option.value" :selected="option.value === defaultVal">{{ option.label }}</option>
      </select>
      <button class="button--neutral button--smallSquare ml-1" data-toggle="tooltip" data-placement="top" :title="helpText" v-if="helpText" type="button">
        <span class="far fa-question-circle"></span>
      </button>
    </div>
    <app-review-input :mode="review ? 'review' : 'edit'" :id="'id'+-review" :name="label" :reviewValue.sync="ownReviewValue"></app-review-input>
  </div>
</template>

<script>
  import { reviewMixin } from '../mixins/reviewMixin'
  import ReviewInput from './ReviewInput.vue'

  export default {
    name: 'Select',
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
      options: {
        type: Array,
        default: [],
        required: true
      },
      defaultVal: {
        default: '',
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
      error: {
        type: Boolean,
        default: false,
        required: false
      }
    },
    data () {
      return {
        inputValue: null
      }
    },
    created () {
      if (this.defaultVal !== undefined) {
        this.inputValue = this.defaultVal
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