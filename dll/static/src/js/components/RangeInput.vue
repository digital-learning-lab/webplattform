<template>
  <div class="form-group">
    <label :for="id">{{ label }}:<span v-if="required">*</span></label>
    <div class="row">
      <div class="col d-flex align-items-baseline">
        <label class="mr-3" :for="id + 'from'">{{ labelFrom }}:</label>
        <input :type="type" class="form-control" :id="id + '-from'" v-model="from" :min="min" :max="max" :readonly="readonly">
      </div>
      <div class="col d-flex align-items-baseline">
        <label class="mr-3" :for="id + 'to'">{{ labelTo }}:</label>
        <input :type="type" class="form-control" :id="id + '-to'" v-model="to" :min="min" :max="max" :readonly="readonly">
      </div>
    </div>
    <app-review-input :mode="review ? 'review' : 'edit'" :id="'id'+-review" :name="label" :reviewValue.sync="ownReviewValue"></app-review-input>
  </div>
</template>

<script>
  import ReviewInput from './ReviewInput.vue'
  import { reviewMixin } from '../mixins/reviewMixin'

  export default {
    name: 'RangeInput',
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
      labelFrom: {
        type: String,
        default: '',
        required: true
      },
      labelTo: {
        type: String,
        default: '',
        required: true
      },
      range: {
        default: '',
        required: false
      },
      min: {
        type: Number,
        default: null,
        required: false
      },
      max: {
        type: Number,
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
        from: null,
        to: null
      }
    },
    created () {
      if (this.range) {
        this.from = this.range['lower']
        this.to = this.range['upper']
      }
    },
    methods: {
      checkValues () {
        if (this.to && this.from && parseInt(this.from) >= parseInt(this.to)) {
          if (parseInt(this.to) === 1) {
            this.to = 2
          }
          this.from = this.to - 1
        }
      }
    },
    watch: {
      from (newValue) {
        if (newValue || newValue === 0) {
          if (newValue < this.min) {
            this.from = this.min
          }
          if (newValue > this.max) {
            this.from = this.max
          }
          this.checkValues()
        }
        this.$emit('update:range', {'lower': parseInt(this.from), 'upper': parseInt(this.to)})
      },
      to (newValue) {
        if (newValue || newValue === 0) {
          if (newValue < this.min) {
            this.to = this.min
          }
          if (newValue > this.max) {
            this.to = this.max
          }
          this.checkValues()
        }
        this.$emit('update:range', {'lower': parseInt(this.from), 'upper': parseInt(this.to)})
      }
    }
  }
</script>

<style scoped>

</style>