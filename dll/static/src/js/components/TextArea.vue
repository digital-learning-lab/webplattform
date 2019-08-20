<template>
  <div class="form-group">
    <label :for="id">{{ label }}:<span v-if="required">*</span></label>
    <textarea :type="type" class="form-control" :id="id" :placeholder="placeholder" v-model="inputValue" :readonly="readOnly"></textarea>
    <small v-if="characterCounter" class="form-text text-muted">{{ charactersLeft }} Zeichen verbleibend</small>
  </div>
</template>

<script>
  export default {
    name: 'TextInput',
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
        default: 0,
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