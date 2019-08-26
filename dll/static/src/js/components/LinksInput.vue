<template>
  <div class="form-group">
    <div class="d-flex">
      <label  :for="id" class="mb-2 w-100">{{ label }}:<span v-if="required">*</span></label>
      <button class="button--neutral button--smallSquare ml-1" data-toggle="tooltip" data-placement="top" :title="helpText" v-if="helpText" type="button">
        <span class="far fa-question-circle"></span>
      </button>
    </div>
    <div class="d-flex align-items-baseline mb-2" v-for="link in internalLinks">
        <input type="text" class="form-control mr-3" :id="id" placeholder="Linktext" v-model="link.name" :readonly="readonly">
        <input type="text" class="form-control mr-3" :id="id" placeholder="https://example.org" v-model="link.url" :readonly="readonly">
        <button class="button--danger button--smallSquare" @click="removeLink(link)" type="button" v-if="!readonly">
          <span class="fas fa-times"></span>
        </button>
    </div>
    <div v-if="!readonly">
      <button class="button--neutral button--smallSquare" @click="addLink" type="button">
        <span class="fas fa-plus"></span>
      </button>
    </div>
    <app-review-input v-if="review" :id="'id'+-review" :name="label" :reviewValue.sync="reviewValue"></app-review-input>
  </div>
</template>

<script>
  import ReviewInput from './ReviewInput.vue'
  import { reviewMixin } from '../mixins/reviewMixin'

  export default {
    name: 'LinksInput',
    components: {
      'AppReviewInput': ReviewInput
    },
    mixins: [reviewMixin],
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
      },
      helpText: {
        type: String,
        default: '',
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