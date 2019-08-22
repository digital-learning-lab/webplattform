<template>
  <form class="mb-4">
    <div class="alert alert-primary" v-if="saved">
      Ihre Änderungen wurden gespeichert.
    </div>
    <div class="alert alert-danger" v-if="errors.length">
      <ul class="list-unstyled">
        <li v-for="error in errors">{{ error }}</li>
      </ul>
    </div>
    <div v-if="mode === 'edit'">
      <button class="button button--primary" type="button" @click="updateContent" :disabled="loading">Speichern</button>
      <button class="button button--primary" type="button" :disabled="loading">Vorschau</button>
      <button class="button button--primary" type="button" :disabled="loading">Einreichen</button>
      <button class="button button--primary" type="button" :disabled="loading">Löschen</button>
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
      <app-dropdown id="subject" label="Unterrichtsfach" :value.sync="data.subjects" fetch-url="/api/subjects" :multiple="true" :prefetch="true"></app-dropdown>
      <app-select id="state" label="Bundesland" :value.sync="data.state" :default-val="data.state" :options="germanStateOptions"></app-select>
      <app-dropdown id="teaching-modules" label="Passende Unterrichtsbausteine" :value.sync="data.teaching_modules" fetch-url="/api/unterrichtsbausteine" :multiple="true"></app-dropdown>
      <app-dropdown id="tools" label="Verwendete Tools" :value.sync="data.tools" fetch-url="/api/tools" :multiple="true"></app-dropdown>
      <app-dropdown id="trends" label="Passende Trends" :value.sync="data.trends" fetch-url="/api/trends" :multiple="true"></app-dropdown>
      <app-dropdown id="competences" label="Kompetenzen in der digitalen Welt" :required="true" :value.sync="data.competences" fetch-url="/api/competences" :multiple="true" :prefetch="true"></app-dropdown>
      <app-dropdown id="subCompetences" label="Detaillierte Kompetenzbeschreibungen" :value.sync="data.sub_competences" :disabled="!data.competences.length" fetch-url="/api/sub-competences" :prefetch="true" :params="{competences: data.competences}" :multiple="true"></app-dropdown>
      <app-list-input id="estimatedTime" label="Zeitumfang der Durchführung" :list.sync="data.estimated_time" :initial="data.estimated_time"></app-list-input>
      <app-list-input id="goals" label="Ziele" :list.sync="data.learning_goals" :initial="data.learning_goals"></app-list-input>
      <app-range-input id="classes" label="Jahrgangsstufe" label-from="Von" label-to="Bis" type="number" :range.sync="data.school_class" :min="1" :max="13"></app-range-input>
      <app-list-input id="subject-of-tuition" label="Informationen zum Unterrichtsgegenstand" :list.sync="data.subject_of_tuition" :initial="data.subject_of_tuition"></app-list-input>
<!--      <app-text-area id="tags" label="Schlagworte" :value.sync="data.tags" :character-counter="true" :maximal-chars="250"></app-text-area>-->
      <app-list-input id="expertise" label="Fachkompetenzen" :list.sync="data.expertise" :initial="data.expertise"></app-list-input>
      <app-list-input id="equipment" label="Medienausstattung" :list.sync="data.equipment" :initial="data.equipment"></app-list-input>
      <app-text-area id="educationalPlanReference" label="Bildungsplanbezug" :value.sync="data.educational_plan_reference" :character-counter="true" :maximal-chars="1300"></app-text-area>
      <app-text-area id="differentiatingAttributes" label="Möglichkeiten der Differenzierung/Individualisierung" :value.sync="data.differentiating_attribute" :character-counter="true" :maximal-chars="700"></app-text-area>
      <app-text-area id="hints" label="Hinweise" :value.sync="data.additional_info" :character-counter="true" :maximal-chars="1000"></app-text-area>
      <app-select id="license" label="Lizenz" :options="licenseOptions" :default-val="data.licence" :value.sync="data.licence"></app-select>
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
  import ListInput from './components/ListInput.vue'

  export default {
    name: 'ContentSubmissionApp',
    components: {
      'AppDropdown': Dropdown,
      'AppFileInput': FileInput,
      'AppTextInput': TextInput,
      'AppTextArea': TextArea,
      'AppRangeInput': RangeInput,
      'AppLinksInput': LinksInput,
      'AppListInput': ListInput,
      'AppSelect': Select
    },
    data () {
      return {
        mode: 'create',
        errors: [],
        loading: false,
        saved: false,
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
          estimated_time: [],
          competences: [],
          educational_plan_reference: '',
          differentiating_attribute: '',
          sub_competences: [],
          tools: [],
          trends: [],
          teaching_modules: [],
          additional_info: '',
          expertise: [],
          classFrom: null,
          classTo: null,
          subject_of_tuition: [],
          subjects: [],
          equipment: [],
          hints: '',
          related_content: [],
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
        ],
        germanStateOptions: [
          {value: 'nordrhein-westfalen', label: 'Nordrhein-Westfalen'},
          {value: 'niedersachsen', label: 'Niedersachsen'},
          {value: 'bayern', label: 'Bayern'},
          {value: 'rheinland-pfalz', label: 'Rheinland-Pfalz'},
          {value: 'hessen', label: 'Hessen'},
          {value: 'saarland', label: 'Saarland'},
          {value: 'berlin', label: 'Berlin'},
          {value: 'brandenburg', label: 'Brandenburg'},
          {value: 'schleswig-holstein', label: 'Schleswig-Holstein'},
          {value: 'mecklenburg-vorpommern', label: 'Mecklenburg-Vorpommern'},
          {value: 'thueringen', label: 'Thüringen'},
          {value: 'sachsen', label: 'Sachsen'},
          {value: 'sachsen-anhalt', label: 'Sachsen-Anhalt'},
          {value: 'bremen', label: 'Bremen'},
          {value: 'baden-wuerttemberg', label: 'Baden-Württemberg'},
          {value: 'hamburg', label: 'Hamburg'},
        ],
        requiredFields: [
          {field: 'name', title: 'Titel'},
          {field: 'teaser', title: 'Teaser'},
          {field: 'description', title: 'Detaillierte Beschreibung'},
          {field: 'competences', title: 'Kompetenzen in der digitalen Welt'}
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
        this.errors = []
        const axiosInstance = this.getAxiosInstance()
        this.loading = true
        axiosInstance.post('/api/inhalt-bearbeiten/', {
          ...this.data,
          resourcetype: 'TeachingModule'
        }).then(res => {
          this.loading = false
          this.mode = 'edit'
          this.data = res.data
          this.data.author = window.dllData.authorName
        }).catch(err => {
          this.loading = false
          if (err.response.status === 400) {
            for (let field in err.response.data) {
              for (let i = 0; i < err.response.data[field].length; i++) {
                this.errors.push(err.response.data[field][i])
              }
            }
          }
        })
      },
      updateContent () {
        this.validate()
        if (this.errors.length) {
          return
        }
        this.data.related_content = this.data.tools.concat(this.data.trends.concat(this.data.teaching_modules))
        const axiosInstance = this.getAxiosInstance()
        this.loading = true
        axiosInstance.put('/api/inhalt-bearbeiten/' + this.data.slug + '/', {
          ...this.data,
          resourcetype: 'TeachingModule'
        }).then(res => {
          this.loading = false
          this.saved = true
          this.mode = 'edit'
          setTimeout(() => {
            this.saved = false
          }, 5000)
        }).catch(err => {
          this.loading = false
          if (err.response.status === 400) {
            for (let i = 0; i < err.response.data.length; i++) {
              this.errors.push(err.response.data[i])
            }
          }
        })
      },
      validate () {
        this.errors = []
        for (let i = 0; i < this.requiredFields.length; i++) {
          if (!this.data[this.requiredFields[i].field]) {
            this.errors.push('Bitte füllen Sie das Pflichtfeld \'' + this.requiredFields[i].title + '\' aus.')
          }
        }
      }
    },
    created () {
      if (window.dllData) {
        this.mode = window.dllData.mode || 'create'
        if (this.mode === 'edit') {
          this.data = window.dllData.module
        }
        this.data.author = window.dllData.authorName
      }
    }
  }
</script>

<style scoped>

</style>