<template>
  <form class="mb-4">
    <div v-if="mode === 'create'">
      <app-text-input id="author" :read-only="true" label="Autor_in" :value.sync="data.author" :required="true"></app-text-input>
      <app-text-input id="title" label="Titel des Unterrichtsbausteins" :value.sync="data.title" :required="true" :character-counter="true" :maximal-chars="140"></app-text-input>
      <app-text-area id="teaser" label="Teaser" :required="true" :value.sync="data.teaser"></app-text-area>
      <app-text-area id="description" label="Detaillierte Beschreibung" :required="true" :value.sync="data.teaser" :character-counter="true" :maximal-chars="1800"></app-text-area>
      <app-dropdown id="coAuthors" label="Co-Autor_innen" :value.sync="data.coAuthors" fetch-url="/api/authors" :multiple="true"></app-dropdown>
      <app-dropdown id="schoolType" label="Schulform" :value.sync="data.schoolType" fetch-url="/api/schoolTypes" :multiple="true"></app-dropdown>
      <app-dropdown id="state" label="Bundesland" :value.sync="data.state" fetch-url="/api/states"></app-dropdown>
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
          teaser: '',
          description: '',
          coAuthors: [],
          schoolTypes: [],
          state: '',
          estimatedTime: ''
        },
        imageOptions: [
          {label: 'Ja', code: 'y'},
          {label: 'Nein', code: 'n'},
        ],
      }
    }
  }
</script>

<style scoped>

</style>