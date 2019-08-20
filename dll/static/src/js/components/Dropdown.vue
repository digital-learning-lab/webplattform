<template>
  <div class="form-group">
    <label :for="id">{{ label }}:<span v-if="required">*</span></label>
    <v-select v-model="inputValue" :options="options" @search="fetchOptions" :multiple="multiple"></v-select>
  </div>
</template>

<script>
  import vSelect from 'vue-select'
  import axios from 'axios'

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
      }
    },
    computed: {
      charactersLeft () {
        return this.maximalChars - this.value.length
      }
    },
    data () {
      return {
        inputValue: '',
        options: []
      }
    },
    created () {
      this.inputValue = this.value
    },
    methods: {
      fetchOptions (search, loading) {
        loading(true)
        axios.get(this.fetchUrl, {
          params: {
            q: search
          }
        }).then(res => {
          this.options = res.data.results.map((el) => {return {label: el.username, value: el.pk}})
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
      }
    }
  }
</script>

<style scoped>

</style>