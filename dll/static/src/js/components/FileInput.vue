<template>
  <div class="form-group">
    <label :for="id">{{ label }}</label>

    <div class="custom-file">
      <input type="file" class="custom-file-input" :id="id" @change="processInput" :accept="accept">
      <label class="custom-file-label" :for="id"><span v-if="inputValue">{{ inputValue.name }}</span><span v-else>{{ fileLabel }}</span></label>
    </div>
    <img v-if="imageUrl" :src="imageUrl" alt="Vorschaubild" class="img-thumbnail">
  </div>
</template>

<script>
  export default {
    name: 'FileInput',
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
      fileLabel: {
        type: String,
        default: '',
        required: true
      },
      accept: {
        type: String,
        default: 'image/gif, image/jpeg, image/png',
        required: false
      }
    },
    data () {
      return {
        inputValue: null,
        file: null
      }
    },
    methods: {
      processInput (e) {
        this.inputValue = e.target.files[0]
      }
    },
    computed: {
      imageUrl () {
        if (this.inputValue) {
          return URL.createObjectURL(this.inputValue)
        }
        return null
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