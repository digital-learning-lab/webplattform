<template>
  <div class="form-group">
    <label :for="id">{{ label }}:<span v-if="required">*</span></label>
    <div class="row">
      <div class="col d-flex align-items-baseline">
        <label class="mr-3" :for="id + 'from'">{{ labelFrom }}:</label>
        <input :type="type" class="form-control" :id="id + '-from'" v-model="inputFrom" :min="min" :max="max">
      </div>
      <div class="col d-flex align-items-baseline">
        <label class="mr-3" :for="id + 'to'">{{ labelTo }}:</label>
        <input :type="type" class="form-control" :id="id + '-to'" v-model="inputTo" :min="min" :max="max">
      </div>
    </div>
  </div>
</template>

<script>
  export default {
    name: 'RangeInput',
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
      value: {
        type: String,
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
      }
    },
    data () {
      return {
        inputFrom: null,
        inputTo: null
      }
    },
    watch: {
      inputFrom (newValue) {
        this.$emit('update:from', newValue)
      },
      inputTo (newValue) {
        this.$emit('update:to', newValue)
      }
    }
  }
</script>

<style scoped>

</style>