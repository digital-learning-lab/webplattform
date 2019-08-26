
export const reviewMixin = {
  props: {
    review: {
      type: Boolean,
      default: false,
      required: false
    }
  },
  data () {
    return {
      reviewValue: ''
    }
  },
  watch: {
    reviewValue (newValue) {
      this.$emit('update:reviewValue', newValue)
    }
  }
}