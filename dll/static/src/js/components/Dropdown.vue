<template>
  <div class="form-group">
    <label :for="id">{{ label }}:<span v-if="required">*</span></label>
    <v-select v-model="inputValue" :options="options"></v-select>
    <small v-if="characterCounter" class="form-text text-muted float-right">{{ charactersLeft }} Zeichen verbleibend</small>
  </div>
</template>

<script>
  import vSelect from 'vue-select'

  export default {
    name: 'Dropdown',
    components: {
      'v-select': vSelect
    },
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
      readOnly: {
        type: Boolean,
        default: false,
        required: false
      },
      options: {
        type: Array,
        default: [],
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