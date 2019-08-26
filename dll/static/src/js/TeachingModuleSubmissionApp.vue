<template>
  <app-content-submission-form :errors="errors" :mode="mode" :loading="loading" :saved="saved" @update="updateContent" @create="createContent" @preview="goToPreview" @delete-warning="showDeleteWarning" :data="data" @delete="deleteContent">
      <app-text-input id="author" :read-only="true" label="Autor_in" :value.sync="data.author" :required="true"></app-text-input>
      <app-text-input id="title" label="Titel des Unterrichtbausteins" :value.sync="data.name" :required="true" :character-counter="true" :maximal-chars="140" :help-text="getHelpText('name')"></app-text-input>
    <div v-if="mode === 'edit'">
      <app-file-input id="image" label="Anzeigebild" file-label="Bild wählen" :value.sync="previewImage" :image="data.image" :help-text="getHelpText('image')"></app-file-input>
      <app-select id="imageRights" label="Bildrechte" :options="imageOptions" default-val="n" :value.sync="data.imageRights" :help-text="getHelpText('imageRights')"></app-select>
      <app-text-area id="teaser" label="Teaser" :required="true" :value.sync="data.teaser" :rows="3" :help-text="getHelpText('teaser')"></app-text-area>
      <app-text-area id="description" label="Detaillierte Beschreibung" :required="true" :value.sync="data.description" :character-counter="true" :maximal-chars="1800" :rows="10" :help-text="getHelpText('description')"></app-text-area>
      <app-dropdown id="co_authors" label="Co-Autor_innen" :value.sync="data.co_authors" fetch-url="/api/authors" :multiple="true" :help-text="getHelpText('co_authors')"></app-dropdown>
      <app-dropdown id="schoolType" label="Schulform" :value.sync="data.school_types" fetch-url="/api/schoolTypes" :multiple="true" :prefetch="true" :help-text="getHelpText('school_types')"></app-dropdown>
      <app-dropdown id="subject" label="Unterrichtsfach" :value.sync="data.subjects" fetch-url="/api/subjects" :multiple="true" :prefetch="true" :help-text="getHelpText('subjects')"></app-dropdown>
      <app-select id="state" label="Bundesland" :value.sync="data.state" :default-val="data.state" :options="germanStateOptions" :help-text="getHelpText('state')"></app-select>
      <app-dropdown id="teaching-modules" label="Passende Unterrichtsbausteine" :value.sync="data.teaching_modules" fetch-url="/api/unterrichtsbausteine" :multiple="true" :help-text="getHelpText('teaching_modules')"></app-dropdown>
      <app-dropdown id="tools" label="Verwendete Tools" :value.sync="data.tools" fetch-url="/api/tools" :multiple="true" :help-text="getHelpText('tools')"></app-dropdown>
      <app-dropdown id="trends" label="Passende Trends" :value.sync="data.trends" fetch-url="/api/trends" :multiple="true" :help-text="getHelpText('trends')"></app-dropdown>
      <app-dropdown id="competences" label="Kompetenzen in der digitalen Welt" :required="true" :value.sync="data.competences" fetch-url="/api/competences" :multiple="true" :prefetch="true" :help-text="getHelpText('competences')"></app-dropdown>
      <app-dropdown id="subCompetences" label="Detaillierte Kompetenzbeschreibungen" :value.sync="data.sub_competences" :disabled="!data.competences.length" fetch-url="/api/sub-competences" :prefetch="true" :params="{competences: data.competences}" :multiple="true" :help-text="getHelpText('sub_competences')"></app-dropdown>
      <app-list-input id="estimatedTime" label="Zeitumfang der Durchführung" :list.sync="data.estimated_time" :initial="data.estimated_time" :help-text="getHelpText('estimated_time')"></app-list-input>
      <app-list-input id="goals" label="Ziele" :list.sync="data.learning_goals" :initial="data.learning_goals" :help-text="getHelpText('learning_goals')"></app-list-input>
      <app-range-input id="classes" label="Jahrgangsstufe" label-from="Von" label-to="Bis" type="number" :range.sync="data.school_class" :min="1" :max="13" :help-text="getHelpText('school_class')"></app-range-input>
      <app-list-input id="subject-of-tuition" label="Informationen zum Unterrichtsgegenstand" :list.sync="data.subject_of_tuition" :initial="data.subject_of_tuition" :help-text="getHelpText('subject_of_tuition')"></app-list-input>
<!--      <app-text-area id="tags" label="Schlagworte" :value.sync="data.tags" :character-counter="true" :maximal-chars="250" :help-text="getHelpText('name')"></app-text-area>-->
      <app-list-input id="expertise" label="Fachkompetenzen" :list.sync="data.expertise" :initial="data.expertise" :help-text="getHelpText('expertise')"></app-list-input>
      <app-list-input id="equipment" label="Medienausstattung" :list.sync="data.equipment" :initial="data.equipment" :help-text="getHelpText('equipment')"></app-list-input>
      <app-text-area id="educationalPlanReference" label="Bildungsplanbezug" :value.sync="data.educational_plan_reference" :character-counter="true" :maximal-chars="1300" :help-text="getHelpText('educational_plan_reference')"></app-text-area>
      <app-text-area id="differentiatingAttributes" label="Möglichkeiten der Differenzierung/Individualisierung" :value.sync="data.differentiating_attribute" :character-counter="true" :maximal-chars="700" :help-text="getHelpText('differentiating_attribute')"></app-text-area>
      <app-text-area id="hints" label="Hinweise" :value.sync="data.additional_info" :character-counter="true" :maximal-chars="1000" :help-text="getHelpText('additional_info')"></app-text-area>
      <app-select id="license" label="Lizenz" :options="licenseOptions" :default-val="data.licence" :value.sync="data.licence" :help-text="getHelpText('licence')"></app-select>
      <app-links-input id="mediaLinks" :links.sync="data.mediaLinks" label="Links zu Audio- und Videomedien" :type="'video'" :help-text="getHelpText('contentlink>')"></app-links-input>
      <app-links-input id="literatureLinks" :links.sync="data.literatureLinks" label="Weiterführende Literatur und Links" :help-text="getHelpText('contentlink>')"></app-links-input>
    </div>
  </app-content-submission-form>
</template>

<script>
  import { submissionMixin } from './mixins/submissionMixin'
  import ContentSubmissionForm from './ContentSubmissionForm.vue'

  export default {
    name: 'TeachingModuleSubmissionApp',
    mixins: [submissionMixin],
    components: {
      'AppContentSubmissionForm': ContentSubmissionForm
    },
    data () {
      return {
        resourceType: 'TeachingModule',
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
          expertise: [],
          classFrom: null,
          classTo: null,
          subject_of_tuition: [],
          subjects: [],
          equipment: [],
          hints: '',
          related_content: [],
          mediaLinks: [],
          literatureLinks: [],
          license: null
        },
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
        ]
      }
    }
  }
</script>

<style scoped>

</style>