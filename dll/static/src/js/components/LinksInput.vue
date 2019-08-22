<template>
  <div class="form-group">
    <label :for="id" class="mb-2">{{ label }}:<span v-if="required">*</span></label>
    <div class="d-flex align-items-baseline mb-2" v-for="link in internalLinks">
        <input type="text" class="form-control mr-3" :id="id" placeholder="Linktext" v-model="link.name">
        <input type="text" class="form-control mr-3" :id="id" placeholder="https://example.org" v-model="link.url">
        <button class="button--danger button--smallSquare" @click="removeLink(link)" type="button">
          <span class="fas fa-times"></span>
        </button>
    </div>
    <div>
      <button class="button--neutral button--smallSquare" @click="addLink" type="button">
        <span class="fas fa-plus"></span>
      </button>
    </div>
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
      },
      type: {
        type: String,
        default: 'href',
        required: false
      },
      links: {
        type: Array,
        default: () => {
          return []
        },
        required: false
      }
    },
    data () {
      return {
        internalLinks: []
      }
    },
    methods: {
      addLink () {
        this.internalLinks.push({name: '', url: '', type: this.type})
      },
      removeLink (link) {
        this.internalLinks.splice(this.internalLinks.indexOf(link), 1)
      }
    },
    created () {
      if (this.links) {
        this.internalLinks = this.links
      }
    },
    watch: {
      internalLinks (newValue) {
        this.$emit('update:links', newValue)
      }
    }
  }
</script>

<style scoped>
</style>