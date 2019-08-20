<template>
  <form class="mb-4">
    <div v-if="mode === 'create'">
      <app-text-input id="author" :read-only="true" label="Autor_in" :value.sync="data.author" :required="true"></app-text-input>
      {{ data.title }}
      <app-text-input id="title" label="Titel des Unterrichtsbausteins" :value.sync="data.title" :required="true"></app-text-input>
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
        data: {
          author: 'Robert Stein',
          title: ''
        }
      }
    }
  }
</script>

<style scoped>

</style>