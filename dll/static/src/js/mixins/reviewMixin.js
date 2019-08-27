
export const reviewMixin = {
  props: {
    review: {
      type: Boolean,
      default: false,
      required: false
    },
    reviewValue: {
      type: String,
      default: '',
      required: false
    }
  },
  data () {
    return {
      inputValue: '',
      ownReviewValue: ''
    }
  },
  created () {
    this.ownReviewValue = this.reviewValue
  },
  watch: {
    ownReviewValue (newValue) {
      this.$emit('update:reviewValue', newValue)
    }
  }
}