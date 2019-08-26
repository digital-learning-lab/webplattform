<template>
  <div class="form-group">
    <label :for="id">{{ label }}:<span v-if="required">*</span></label>
    <div class="d-flex">
    <v-select v-model="inputValue" :options="options" @search="fetchOptions" :multiple="multiple" :disabled="disabled"></v-select>
      <button class="button--neutral button--smallSquare ml-1" data-toggle="tooltip" data-placement="top" :title="helpText" v-if="helpText" type="button">
        <span class="far fa-question-circle"></span>
      </button>
    </div>
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
      helpText: {
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
      }
    }
  }
</script>

<style scoped>
  .v-select {
    width: 100%;
  }
</style>