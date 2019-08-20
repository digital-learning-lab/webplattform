<template>
  <form class="mb-4">
    <div v-if="mode === 'create'">
      <app-text-input id="author" :read-only="true" label="Autor_in" :value.sync="data.author" :required="true"></app-text-input>
      <app-text-input id="title" label="Titel des Unterrichtsbausteins" :value.sync="data.title" :required="true" :character-counter="true" :maximal-chars="140"></app-text-input>
      <app-file-input id="image" label="Anzeigebild" file-label="Bild wählen"></app-file-input>
      <app-select id="imageRights" label="Bildrechte" :options="imageOptions" default-val="n" :value.sync="data.imageRights"></app-select>
      <app-text-area id="teaser" label="Teaser" :required="true" :value.sync="data.teaser" :rows="3"></app-text-area>
      <app-text-area id="description" label="Detaillierte Beschreibung" :required="true" :value.sync="data.teaser" :character-counter="true" :maximal-chars="1800" :rows="10"></app-text-area>
      <app-dropdown id="coAuthors" label="Co-Autor_innen" :value.sync="data.coAuthors" fetch-url="/api/authors" :multiple="true"></app-dropdown>
      <app-dropdown id="schoolType" label="Schulform" :value.sync="data.schoolType" fetch-url="/api/schoolTypes" :multiple="true" :prefetch="true"></app-dropdown>
      <app-dropdown id="state" label="Bundesland" :value.sync="data.state" fetch-url="/api/states" :prefetch="true"></app-dropdown>
      <app-dropdown id="teaching-modules" label="Passende Unterrichtsbausteine" :value.sync="data.teachingModules" fetch-url="/api/unterrichtsbausteine" :multiple="true"></app-dropdown>
      <app-dropdown id="tools" label="Verwendete Tools" :value.sync="data.tools" fetch-url="/api/tools" :multiple="true"></app-dropdown>
      <app-dropdown id="trends" label="Passende Trends" :value.sync="data.trends" fetch-url="/api/trends" :multiple="true"></app-dropdown>
      <app-dropdown id="competences" label="Kompetenzen in der digitalemn Welt" :required="true" :value.sync="data.competences" fetch-url="/api/competences" :multiple="true" :prefetch="true"></app-dropdown>
      <app-dropdown id="subCompetences" label="Detaillierte Kompetenzbeschreibungen" :value.sync="data.subCompetences" :disabled="!data.competences.length" fetch-url="/api/sub-competences" :prefetch="true" :params="{competences: data.competences}" :multiple="true"></app-dropdown>
      <app-text-area id="estimatedTime" label="Zeitumfang der Durchführung" :value.sync="data.estimatedTime" :character-counter="true" :maximal-chars="250" :rows="2"></app-text-area>
      <app-text-area id="goals" label="Ziele" :value.sync="data.goals" :character-counter="true" :maximal-chars="850"></app-text-area>
      <app-text-area id="additional-information" label="Informationen zum Unterrichtsgegenstand" :value.sync="data.additionalInformation" :character-counter="true" :maximal-chars="1800"></app-text-area>
<!--      <app-text-area id="tags" label="Schlagworte" :value.sync="data.tags" :character-counter="true" :maximal-chars="250"></app-text-area>-->
      <app-text-area id="expertise" label="Fachkompetenzen" :value.sync="data.expertise" :character-counter="true" :maximal-chars="1500"></app-text-area>
      <app-text-area id="equipment" label="Medienausstattung" :value.sync="data.equipment" :character-counter="true" :maximal-chars="200" :rows="3"></app-text-area>
      <app-text-area id="educationalPlanReference" label="Bildungsplanbezug" :value.sync="data.educationalPlanReference" :character-counter="true" :maximal-chars="1300"></app-text-area>
      <app-text-area id="differentiatingAttributes" label="Möglichkeiten der Differenzierung/Individualisierung" :value.sync="data.differentiatingAttributes" :character-counter="true" :maximal-chars="700"></app-text-area>
      <app-text-area id="hints" label="Hinweise" :value.sync="data.hints" :character-counter="true" :maximal-chars="1000"></app-text-area>
    </div>
  </form>
</template>

<script>

  import TextInput from './components/TextInput.vue'
  import TextArea from './components/TextArea.vue'
  import Dropdown from './components/Dropdown.vue'
  import FileInput from './components/FileInput.vue'
  import Select from './components/Select.vue'

  export default {
    name: 'ContentSubmissionApp',
    components: {
      'AppDropdown': Dropdown,
      'AppFileInput': FileInput,
      'AppTextInput': TextInput,
      'AppTextArea': TextArea,
      'AppSelect': Select
    },
    data () {
      return {
        mode: 'create',
        data: {
          author: 'Robert Stein',
          title: '',
          teaser: '',
          image: null,
          imageRights: null,
          description: '',
          coAuthors: [],
          schoolTypes: [],
          state: '',
          estimatedTime: '',
          competences: '',
          subCompetences: '',
          goals: '',
          additionalInformation: '',
          expertise: '',
          equipment: '',
          educationalPlanReference: '',
          differentiatingAttributes: '',
          hints: '',
        },
        imageOptions: [
          {label: 'Ja', value: 'y'},
          {label: 'Nein', value: 'n'},
        ],
      }
    }
  }
</script>

<style scoped>

</style>