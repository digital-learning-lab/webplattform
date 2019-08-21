<template>
  <div class="form-group">
    <label :for="id">{{ label }}:<span v-if="required">*</span></label>
    <div class="d-flex align-items-baseline" v-for="link in links">
        <input type="text" class="form-control mr-3" :id="id" placeholder="Linktext" v-model="link.text">
        <input type="text" class="form-control mr-3" :id="id" placeholder="https://example.org" v-model="link.url">
        <button class="button button--teaching-module" @click="removeLink(link)" type="button">
          x
        </button>
    </div>
    <button class="button--neutral" @click="addLink" type="button">+</button>
  </div>
</template>

<script>
  export default {
    name: 'LinksInput',
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
      }
    },
    data () {
      return {
        links: []
      }
    },
    methods: {
      addLink () {
        this.links.push({text: '', url: ''})
      },
      removeLink (link) {
        this.links.splice(this.links.indexOf(link), 1)
      }
    },
    watch: {
      links (newValue) {
        this.$emit('update:links', newValue)
      }
    }
  }
</script>

<style scoped>

</style>