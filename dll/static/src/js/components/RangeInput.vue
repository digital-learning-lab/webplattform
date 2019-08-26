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
    watch: {
      from (newValue) {
        this.$emit('update:range', {'lower': parseInt(this.from), 'upper': parseInt(this.to)})
      },
      to (newValue) {
        this.$emit('update:range', {'lower': parseInt(this.from), 'upper': parseInt(this.to)})
      }
    }
  }
</script>

<style scoped>

</style>