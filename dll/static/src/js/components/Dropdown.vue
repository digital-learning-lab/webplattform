<template>
  <div class="form-group">
    <label :for="id">{{ label }}:<span v-if="required">*</span></label>
    <div class="d-flex">
    <v-select v-model="inputValue" :options="calcOptions" :class="{'form__field--error': error}" @search="fetchOptions" :multiple="multiple" :disabled="disabled || readonly" :filterable="false"></v-select>
      <button class="button--neutral button--smallSquare button--help ml-1" type="button" data-toggle="tooltip" data-placement="top" :title="helpText" v-if="helpText"></button>
    </div>
    <app-review-input :mode="review ? 'review' : 'edit'" :id="'id'+-review" :name="label" :reviewValue.sync="ownReviewValue"></app-review-input>
  </div>
</template>

<script>
  import vSelect from 'vue-select'
  import axios from 'axios'
  import ReviewInput from './ReviewInput.vue'
  import { reviewMixin } from '../mixins/reviewMixin'

  export default {
    name: 'Dropdown',
    components: {
      'v-select': vSelect,
      'AppReviewInput': ReviewInput
    },
    mixins: [reviewMixin],
    props: {
      prefetch: {
        type: Boolean,
        default: false,
        required: false
      },
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
      multiple: {
        type: Boolean,
        default: false,
        required: false
      },
      fetchUrl:  {
        type: String,
        default: '',
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
        required: false
      },
      params: {
        type: Object,
        default: () => {
          return {}
        },
        required: false
      },
      disabled: {
        type: Boolean,
        default: false,
        required: false
      },
      error: {
        type: Boolean,
        default: false,
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
      }
    },
    computed: {
      charactersLeft () {
        return this.maximalChars - this.value.length
      },
      calcOptions () {
        return this.options.filter(option => !this.inputValue.some(item => item.label === option.label))
      }
    },
    data () {
      return {
        inputValue: '',
        options: []
      }
    },
    created () {
      if (this.value) {
        this.inputValue = this.value
      }
      if (this.prefetch) {
        this.fetchOptions('', function () {})
      }
    },
    methods: {
      fetchOptions (search, loading) {
        loading(true)
        axios.get(this.fetchUrl, {
          params: {
            q: search,
            ...this.params
          }
        }).then(res => {
          this.options = res.data.results.map((el) => {return {label: el.username || el.name, value: el.pk || el.value, pk: el.pk || el.id}})
          loading(false)
        }).catch(err => {
          loading(false)
          console.log(err)
        })
      }
    },
    watch: {
      inputValue (newValue) {
        this.$emit('update:value', newValue)
      },
      disabled (newValue) {
        if (!newValue && this.prefetch) {
          this.fetchOptions('', function () {})
        }
      },
      value (newValue) {
        this.inputValue = newValue
      },
      params (newValue) {
        this.fetchOptions('', function () {})
      }
    }
  }
</script>

<style scoped>
  .v-select {
    width: 100%;
  }
</style>