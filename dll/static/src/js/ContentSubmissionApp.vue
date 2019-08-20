<template>
  <form class="mb-4">
    <div v-if="mode === 'create'">
      <app-text-input id="author" :read-only="true" label="Autor_in" :value.sync="data.author" :required="true"></app-text-input>
      <app-text-input id="title" label="Titel des Unterrichtsbausteins" :value.sync="data.title" :required="true" :character-counter="true" :maximal-chars="140"></app-text-input>
      <app-dropdown id="imageRights" label="Bildrechte" :value.sync="data.imageRights" :required="true"></app-dropdown>
      <app-text-area id="teaser" label="Teaser" :required="true" :value.sync="data.teaser"></app-text-area>
      <app-text-area id="description" label="Detaillierte Beschreibung" :required="true" :value.sync="data.teaser" :character-counter="true" :maximal-chars="1800"></app-text-area>
      <app-text-area id="estimatedTime" label="Zeitumfang der Durchführung" :value.sync="data.estimatedTime" :character-counter="true" :maximal-chars="250"></app-text-area>
    </div>
  </form>
</template>

<script>

  import TextInput from './components/TextInput.vue'
  import TextArea from './components/TextArea.vue'
  import Dropdown from './components/Dropdown.vue'

  export default {
    name: 'ContentSubmissionApp',
    components: {
      'AppDropdown': Dropdown,
      'AppTextInput': TextInput,
      'AppTextArea': TextArea
    },
    data () {
      return {
        mode: 'create',
        data: {
          author: 'Robert Stein',
          title: '',
          teaser: ''
        }
      }
    }
  }
</script>

<style scoped>

</style>