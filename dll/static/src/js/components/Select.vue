<template>
  <div class="form-group">
    <label :for="id">{{ label }}</label>
    <select :name="id" :id="id" class="form-control" v-model="inputValue">
      <option v-for="option in options" :value="option.value" :selected="option.value === defaultVal">{{ option.label }}</option>
    </select>
  </div>
</template>

<script>
  export default {
    name: 'Select',
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
      }
    },
    data () {
      return {
        inputValue: null
      }
    },
    created () {
      if (this.defaultVal) {
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