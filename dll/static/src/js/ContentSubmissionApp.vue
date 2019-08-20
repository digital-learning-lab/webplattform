<template>
  <form class="mb-4">
    <div v-if="mode === 'create'">
      <app-text-input id="author" :read-only="true" label="Autor_in" :value.sync="author"></app-text-input>
    </div>
  </form>
</template>

<script>

  import TextInput from './components/TextInput.vue'

  export default {
    name: 'ContentSubmissionApp',
    components: {
      'AppTextInput': TextInput
    },
    data () {
      return {
        mode: 'create',
        author: 'Robert Stein'
      }
    }
  }
</script>

<style scoped>

</style>