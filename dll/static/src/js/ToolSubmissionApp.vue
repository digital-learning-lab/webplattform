<template>
  <app-content-submission-form :errors="errors" :mode="mode" :loading="loading" :saved="saved" @update="updateContent" @create="createContent" @delete-warning="showDeleteWarning" :data="data" @delete="deleteContent" @submit="submitContent">
      <app-text-input id="author" :readonly="true" label="Autor_in" :value.sync="data.author" :required="true"></app-text-input>
      <app-text-input id="title" :readonly="data.submitted" label="Titel des Tools" :value.sync="data.name" :required="true" :character-counter="true" :maximal-chars="140" :help-text="getHelpText('name')"></app-text-input>
    <div v-if="mode === 'edit'">
      <app-file-input id="image" :readonly="data.submitted" label="Anzeigebild" file-label="Bild wählen" :value.sync="previewImage" :image="data.image" :help-text="getHelpText('image')" :hintText="imageHintText"></app-file-input>
      <app-text-area id="teaser" :readonly="data.submitted" label="Kurzzusammenfassung" :required="true" :value.sync="data.teaser" :rows="3" :help-text="getHelpText('teaser')"></app-text-area>
      <app-dropdown id="co_authors" :readonly="data.submitted" label="Co-Autor_innen" :value.sync="data.co_authors" fetch-url="/api/authors" :multiple="true" :help-text="getHelpText('co_authors')"></app-dropdown>
      <app-dropdown id="teaching- :readonly=data.submittedmodules" label="Passende Unterrichtsbausteine" :value.sync="data.teaching_modules" fetch-url="/api/unterrichtsbausteine" :multiple="true" :help-text="getHelpText('teaching_modules')"></app-dropdown>
      <app-dropdown id="tools" :readonly="data.submitted" label="Verwendete Tools" :value.sync="data.tools" fetch-url="/api/tools" :multiple="true" :help-text="getHelpText('tools')"></app-dropdown>
      <app-dropdown id="trends" :readonly="data.submitted" label="Passende Trends" :value.sync="data.trends" fetch-url="/api/trends" :multiple="true" :help-text="getHelpText('trends')"></app-dropdown>
      <app-dropdown id="competences" :readonly="data.submitted" label="Kompetenzen in der digitalen Welt" :required="true" :value.sync="data.competences" fetch-url="/api/competences" :multiple="true" :prefetch="true" :help-text="getHelpText('competences')"></app-dropdown>
      <app-links-input id="websites" :readonly="data.submitted" :links.sync="data.websites" label="Website" :type="'null'" :help-text="getHelpText('websites')"></app-links-input>
      <app-list-input id="pro" :readonly="data.submitted" label="Vorteile" :list.sync="data.pro" :initial="data.pro" :help-text="getHelpText('pro')"></app-list-input>
      <app-list-input id="contra" :readonly="data.submitted" label="Nachteile" :list.sync="data.contra" :initial="data.contra" :help-text="getHelpText('contra')"></app-list-input>
      <app-select id="data- :readonly=data.submittedprivacy" label="Datenschutz" :options="dataPrivacyOptions" default-val="" :value.sync="data.privacy" :default-val="data.privacy" :help-text="getHelpText('privacy')"></app-select>
      <app-text-area id="usage" :readonly="data.submitted" label="Nutzung" :value.sync="data.usage" :character-counter="true" :maximal-chars="300" :help-text="getHelpText('usage')"></app-text-area>
      <app-dropdown id="applications" :readonly="data.submitted" label="Anwendung" :value.sync="data.applications" fetch-url="/api/applications" :multiple="true" :prefetch="true" :help-text="getHelpText('applications')"></app-dropdown>
      <app-links-input id="mediaLinks" :readonly="data.submitted" :links.sync="data.mediaLinks" label="Links zu Audio- und Videomedien" :type="'video'" :help-text="getHelpText('contentlink>')"></app-links-input>
      <app-links-input id="literatureLinks" :readonly="data.submitted" :links.sync="data.literatureLinks" label="Text-Anleitung" :help-text="getHelpText('contentlink>')"></app-links-input>
      <app-select id="requires_registration" :readonly="data.submitted" label="Registrierung erforderlich" :options="registrationOptions" :value.sync="data.requires_registration" :default-val="data.requires_registration" :help-text="getHelpText('requires_registration')"></app-select>
      <app-select id="usk" :readonly="data.submitted" label="Altersfreigabe" :options="uskOptions" :value.sync="data.usk" :default-val="data.usk" :help-text="getHelpText('usk')"></app-select>
      <app-select id="status" :readonly="data.submitted" label="Status" :options="statusOptions" :value.sync="data.status" :default-val="data.status" :help-text="getHelpText('status')"></app-select>
      <app-text-area id="additional- :readonly=data.submittedinfo" label="Anmerkungen" :required="true" :value.sync="data.additional_info" :character-counter="true" :maximal-chars="700" :rows="10" :help-text="getHelpText('additional_info')"></app-text-area>
      <app-text-area id="description" :readonly="data.submitted" label="Detaillierte Beschreibung" :required="true" :value.sync="data.description" :character-counter="true" :maximal-chars="500" :rows="10" :help-text="getHelpText('description')"></app-text-area>
      <app-dropdown id="operating_systems" :readonly="data.submitted" label="Betriebssystem" :value.sync="data.operating_systems" fetch-url="/api/operatingSystems" :multiple="true" :prefetch="true" :help-text="getHelpText('operating_systems')"></app-dropdown>
    </div>
  </app-content-submission-form>
</template>

<script>
  import { submissionMixin } from './mixins/submissionMixin'
  import ContentSubmissionForm from './ContentSubmissionForm.vue'

  export default {
    name: 'ToolSubmissionApp',
    mixins: [submissionMixin],
    components: {
      'AppContentSubmissionForm': ContentSubmissionForm
    },
    data () {
      return {
        resourceType: 'Tool',
        data: {
          author: '',
          name: '',
          contentlink_set: [],
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
          related_content: [],
          mediaLinks: [],
          literatureLinks: [],
          license: null
        },
        dataPrivacyOptions: [
          {value: 0, label: 'Unbekannt'},
          {value: 1, label: 'Es werden keinerlei Daten erhoben'},
          {value: 2, label: 'Personenbezogene Daten wie z.B. Logins werden geschützt auf dem Server abgelegt. Es greift die EU-Datenschutz-Grundverordnung.'},
          {value: 3, label: 'Personenbezogene Daten werden erhoben. Dritte haben Zugriff auf diese Daten. Es greift die EU-Datenschutz-Grundverordnung.'},
          {value: 4, label: 'Personenbezogene Daten werden erhoben. Es greift NICHT die EU-Datenschutz-Grundverordnung.'}
        ],
        registrationOptions: [
          {label: 'Ja', value: true},
          {label: 'Nein', value: false}
        ],
        uskOptions: [
          {value: 'usk0', label: 'Ohne Altersbeschränkung'},
          {value: 'usk6', label: 'Ab 6 Jahren'},
          {value: 'usk12', label: 'Ab 12 Jahren'},
          {value: 'usk16', label: 'Ab 16 Jahren'},
          {value: 'usk18', label: 'Ab 18 Jahren'}
        ],
        statusOptions: [
          {value: 'on', label: 'Online'},
          {value: 'off', label: 'Offline'},
          {value: 'onoff', label: 'Online & Offline'}
        ]
      }
    }
  }
</script>

<style scoped>

</style>