<template>
  <form class="mb-4">
    <div v-if="mode === 'edit'">
      <button class="button button--primary" type="button" @click="updateContent">Speichern</button>
      <button class="button button--primary" type="button">Vorschau</button>
      <button class="button button--primary" type="button">Einreichen</button>
      <button class="button button--primary" type="button">Löschen</button>
    </div>
      <app-text-input id="author" :read-only="true" label="Autor_in" :value.sync="data.author" :required="true"></app-text-input>
      <app-text-input id="title" label="Titel des Unterrichtbausteins" :value.sync="data.name" :required="true" :character-counter="true" :maximal-chars="140"></app-text-input>
    <div v-if="mode === 'edit'">
      <app-file-input id="image" label="Anzeigebild" file-label="Bild wählen"></app-file-input>
      <app-select id="imageRights" label="Bildrechte" :options="imageOptions" default-val="n" :value.sync="data.imageRights"></app-select>
      <app-text-area id="teaser" label="Teaser" :required="true" :value.sync="data.teaser" :rows="3"></app-text-area>
      <app-text-area id="description" label="Detaillierte Beschreibung" :required="true" :value.sync="data.description" :character-counter="true" :maximal-chars="1800" :rows="10"></app-text-area>
      <app-dropdown id="co_authors" label="Co-Autor_innen" :value.sync="data.co_authors" fetch-url="/api/authors" :multiple="true"></app-dropdown>
      <app-dropdown id="schoolType" label="Schulform" :value.sync="data.school_types" fetch-url="/api/schoolTypes" :multiple="true" :prefetch="true"></app-dropdown>
      <app-dropdown id="state" label="Bundesland" :value.sync="data.state" fetch-url="/api/states" :prefetch="true"></app-dropdown>
      <app-dropdown id="teaching-modules" label="Passende Unterrichtsbausteine" :value.sync="data.related_content" fetch-url="/api/unterrichtsbausteine" :multiple="true"></app-dropdown>
      <app-dropdown id="tools" label="Verwendete Tools" :value.sync="data.related_content" fetch-url="/api/tools" :multiple="true"></app-dropdown>
      <app-dropdown id="trends" label="Passende Trends" :value.sync="data.related_content" fetch-url="/api/trends" :multiple="true"></app-dropdown>
      <app-dropdown id="competences" label="Kompetenzen in der digitalen Welt" :required="true" :value.sync="data.competences" fetch-url="/api/competences" :multiple="true" :prefetch="true"></app-dropdown>
      <app-dropdown id="subCompetences" label="Detaillierte Kompetenzbeschreibungen" :value.sync="data.sub_competences" :disabled="!data.competences.length" fetch-url="/api/sub-competences" :prefetch="true" :params="{competences: data.competences}" :multiple="true"></app-dropdown>
      <app-text-area id="estimatedTime" label="Zeitumfang der Durchführung" :value.sync="data.estimated_time" :character-counter="true" :maximal-chars="250" :rows="2"></app-text-area>
      <app-text-area id="goals" label="Ziele" :value.sync="data.goals" :character-counter="true" :maximal-chars="850"></app-text-area>
      <app-range-input id="classes" label="Jahrgangsstufe" label-from="Von" label-to="Bis" type="number" :from.sync="data.classFrom" :from.to="data.classTo" :min="1" :max="13"></app-range-input>
      <app-text-area id="additional-information" label="Informationen zum Unterrichtsgegenstand" :value.sync="data.subject_of_tuition" :character-counter="true" :maximal-chars="1800"></app-text-area>
<!--      <app-text-area id="tags" label="Schlagworte" :value.sync="data.tags" :character-counter="true" :maximal-chars="250"></app-text-area>-->
<!--      <app-text-area id="expertise" label="Fachkompetenzen" :value.sync="data.expertise" :character-counter="true" :maximal-chars="1500"></app-text-area>-->
<!--      <app-text-area id="equipment" label="Medienausstattung" :value.sync="data.equipment" :character-counter="true" :maximal-chars="200" :rows="3"></app-text-area>-->
      <app-text-area id="educationalPlanReference" label="Bildungsplanbezug" :value.sync="data.educationalPlanReference" :character-counter="true" :maximal-chars="1300"></app-text-area>
      <app-text-area id="differentiatingAttributes" label="Möglichkeiten der Differenzierung/Individualisierung" :value.sync="data.differentiatingAttributes" :character-counter="true" :maximal-chars="700"></app-text-area>
      <app-text-area id="hints" label="Hinweise" :value.sync="data.additional_info" :character-counter="true" :maximal-chars="1000"></app-text-area>
      <app-select id="license" label="Lizenz" :options="licenseOptions" default-val="" :value.sync="data.license"></app-select>
      <app-links-input id="mediaLinks" :links.sync="data.mediaLinks" label="Links zu Audio- und Videomedien"></app-links-input>
      <app-links-input id="literatureLinks" :links.sync="data.literatureLinks" label="Weiterführende Literatur und Links"></app-links-input>
    </div>
    <button class="button button--primary" @click="createContent" type="button" v-if="mode === 'create'">Speichern</button>
  </form>
</template>

<script>
  import axios from 'axios'

  import TextInput from './components/TextInput.vue'
  import TextArea from './components/TextArea.vue'
  import Dropdown from './components/Dropdown.vue'
  import FileInput from './components/FileInput.vue'
  import Select from './components/Select.vue'
  import RangeInput from './components/RangeInput.vue'
  import LinksInput from './components/LinksInput.vue'

  export default {
    name: 'ContentSubmissionApp',
    components: {
      'AppDropdown': Dropdown,
      'AppFileInput': FileInput,
      'AppTextInput': TextInput,
      'AppTextArea': TextArea,
      'AppRangeInput': RangeInput,
      'AppLinksInput': LinksInput,
      'AppSelect': Select
    },
    data () {
      return {
        mode: 'create',
        data: {
          author: '',
          name: '',
          teaser: '',
          image: null,
          imageRights: null,
          description: '',
          co_authors: [],
          school_types: [],
          state: '',
          estimated_time: '',
          competences: [],
          sub_competences: '',
          goals: '',
          additional_info: '',
          expertise: [],
          classFrom: null,
          classTo: null,
          subject_of_tuition: '',
          equipment: [],
          educationalPlanReference: '',
          differentiatingAttributes: '',
          hints: '',
          license: null
        },
        imageOptions: [
          {label: 'Ja', value: 'y'},
          {label: 'Nein', value: 'n'},
        ],
        licenseOptions: [
          {value: null, label:'----------'},
          {value: 1, label:'CC0'},
          {value: 2, label:'CC BY'},
          {value: 5, label:'CC BY-NC'},
          {value: 7, label:'CC BY-NC-ND'},
          {value: 6, label:'CC BY-NC-SA'},
          {value: 4, label:'CC BY-ND'},
          {value: 3, label:'CC BY-SA'}
        ]
      }
    },
    methods: {
      getAxiosInstance () {
        const axiosInstance = axios.create({
          headers: {
            'X-CSRFToken': window.dllData.csrfToken
          }
        })
        return axiosInstance
      },
      createContent () {
        const axiosInstance = this.getAxiosInstance()
        axiosInstance.post('/api/inhalt-bearbeiten/', {
          ...this.data,
          resourcetype: 'TeachingModule'
        }).then(res => {
          this.mode = 'edit'
        }).catch(err => {
          console.log(err)
        })
      },
      updateContent () {
        const axiosInstance = this.getAxiosInstance()
        console.log(this.data)
        axiosInstance.put('/api/inhalt-bearbeiten/' + this.data.slug + '/', {
          ...this.data,
          resourcetype: 'TeachingModule'
        }).then(res => {
          this.mode = 'edit'
        }).catch(err => {
          console.log(err)
        })
      }
    },
    created () {
      this.mode = window.dllData.mode || 'create'
      this.data = window.dllData.module
      this.data.author = window.dllData.authorName
    }
  }
</script>

<style scoped>

</style>