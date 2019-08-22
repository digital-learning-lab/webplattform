<template>
  <div class="form-group">
    <label :for="id">{{ label }}:<span v-if="required">*</span></label>
    <div class="d-flex align-items-baseline" v-for="item in list">
      <input type="text" class="form-control mr-3" :id="id" :placeholder="placeholder" v-model="item.text" @input="emitUpdate">
      <button class="button button--teaching-module" @click="removeItem(item)" type="button">
        x
      </button>
    </div>
    <button class="button--neutral" @click="addItem" type="button">+</button>
  </div>
</template>

<script>
  export default {
    name: 'ListInput',
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
      placeholder: {
        type: String,
        default: '',
        required: false
      },
      initial: {
        type: Array,
        default: () => {
          return []
        },
        required: false
      }
    },
    data () {
      return {
        list: []
      }
    },
    created () {
      this.list = this.initial.map(x => { return {text: x}})
    },
    methods: {
      addItem () {
        this.list.push({text: ''})
      },
      removeItem (text) {
        this.list.splice(this.list.indexOf(text), 1)
      },
      emitUpdate () {
        const result = this.list.map(x => x.text)
        this.$emit('update:list', result)
      }
    },
    watch: {
      list (newValue) {
        const result = newValue.map(x => x.text)
        this.$emit('update:list', result)
      }
    }
  }
</script>

<style scoped>

</style>