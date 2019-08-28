<template>
  <div>
    <div class="mb-5" v-if="mode === 'review'">
      <button class="button--neutral button--smallSquare mt-3" @click="show = true" type="button" v-if="!show">
        <span class="fas fa-plus"></span>
      </button>
      <div class="form-group mt-4" v-if="inputValue || show">
        <div class="d-flex">
          <input type="text" class="form-control mr-2" :id="id" v-model="inputValue" :placeholder="'Kommentar zum Feld \'' + name + '\''">
          <button class="button--danger button--smallSquare" @click="remove" type="button">
            <span class="fas fa-times"></span>
          </button>
        </div>
      </div>
    </div>
    <div class="form-comment mb-5" v-if="mode === 'edit' && reviewValue">
      Anmerkung: <br>
      {{reviewValue}}
    </div>
  </div>
</template>

<script>
  export default {
    name: 'ReviewInput',
    props: {
      id: {
        type: String,
        default: '',
        required: true
      },
      name: {
        type: String,
        default: '',
        required: true
      },
      value: {
        type: String,
        default: '',
        required: false
      },
      reviewValue: {
        type: String,
        default: '',
        required: false
      },
      mode: {
        type: String,
        default: '',
        required: false
      }
    },
    data () {
      return {
        show: false,
        inputValue: ''
      }
    },
    methods: {
      remove () {
        this.inputValue = ''
        this.show = false
      }
    },
    created () {
      this.inputValue = this.reviewValue
    },
    watch: {
      inputValue (newValue) {
        this.$emit('update:reviewValue', newValue)
      }
    }
  }
</script>

<style scoped>

</style>