<template>
  <div class="form-group">
    <label :for="id">Email address</label>
    <input type="email" class="form-control" :id="id" :placeholder="placeholder">
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
      placeholder:{
        type: String,
        default: '',
        required: false
      },
      characterCounter: {
        type: Boolean,
        default: false,
        required: false
      }
    },
    computed: {
      charactersLeft () {
        return 1
      }
    }
  }
</script>

<style scoped>

</style>