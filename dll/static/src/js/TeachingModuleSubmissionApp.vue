<template>
  <app-content-submission-form :errors="errors" :mode="mode" :loading="loading" :saved="saved" @update="updateContent" @create="createContent" @preview="goToPreview" @delete-warning="showDeleteWarning" :data="data" @delete="deleteContent" @submit="submitContent" @update-review="updateReview" @approve-review="approveContent" @decline-review="declineContent" :can-delete="canDelete">
      <div class="form-group" v-if="reviewValue.feedback && !review">
        <label>Feedback:</label> <br>
        {{ reviewValue.feedback }}
      </div>
      <app-text-area id="feedback" v-if="review" :review="false" label="Feedback" :required="false" :value.sync="reviewValue.feedback" :rows="3" :help-text="getHelpText('feedback')"></app-text-area>
      <app-text-input id="author" :readonly="true" label="Autor_in" :value.sync="data.author" :required="true"></app-text-input>
      <app-text-input id="title" :readonly="readonly" :review="review" label="Titel des Unterrichtbausteins" :value.sync="data.name" :review-value.sync="reviewValue.name" :error="errorFields.includes('name')" :required="true" :character-counter="true" :maximal-chars="140" :help-text="getHelpText('name')"></app-text-input>
    <div v-if="mode === 'edit' || mode === 'review'">
      <app-file-input id="image" :readonly="readonly" :review="review" :required="true" label="Anzeigebild" file-label="Bild wählen" :value.sync="previewImage" :review-value.sync="reviewValue.image" :error="errorFields.includes('image')" :image="data.image" :help-text="getHelpText('image')" :hintText="imageHintText"></app-file-input>
      <app-text-area id="teaser" :readonly="readonly" :review="review" label="Kurzzusammenfassung" :required="true" :value.sync="data.teaser" :review-value.sync="reviewValue.teaser" :error="errorFields.includes('teaser')" :rows="3" :help-text="getHelpText('teaser')" :character-counter="true" :maximal-chars="140"></app-text-area>
      <app-text-area id="description" :readonly="readonly" :review="review" label="Detaillierte Beschreibung" :required="true" :value.sync="data.description" :review-value.sync="reviewValue.description" :error="errorFields.includes('description')" :character-counter="true" :maximal-chars="1800" :rows="10" :help-text="getHelpText('description')"></app-text-area>
      <app-dropdown id="co_authors" :readonly="readonly" :review="review" label="Co-Autor_innen" :value.sync="data.co_authors" :review-value.sync="reviewValue.co_authors" :error="errorFields.includes('co_authors')" fetch-url="/api/authors" :multiple="true" :help-text="getHelpText('co_authors')"></app-dropdown>
      <app-pending-co-authors :pending_co_authors="data.pending_co_authors"></app-pending-co-authors>
      <app-dropdown id="schoolType" :readonly="readonly" :review="review" :required="true" label="Schulform" :value.sync="data.school_types" :review-value.sync="reviewValue.school_types" :error="errorFields.includes('school_types')" fetch-url="/api/schoolTypes" :multiple="true" :prefetch="true" :help-text="getHelpText('school_types')"></app-dropdown>
      <app-dropdown id="subject" :readonly="readonly" :review="review" :required="true" label="Unterrichtsfach" :value.sync="data.subjects" :review-value.sync="reviewValue.subjects" :error="errorFields.includes('subjects')" fetch-url="/api/subjects" :multiple="true" :prefetch="true" :help-text="getHelpText('subjects')"></app-dropdown>
      <app-select id="state" :readonly="readonly" :review="review" label="Bundesland" :value.sync="data.state" :review-value.sync="reviewValue.state" :error="errorFields.includes('state')" :default-val="data.state" :options="germanStateOptions" :help-text="getHelpText('state')"></app-select>
      <app-dropdown id="teaching-modules" :readonly="readonly" :review="review" label="Passende Unterrichtsbausteine" :value.sync="data.teaching_modules" :review-value.sync="reviewValue.teaching_modules" :error="errorFields.includes('teaching_modules')" fetch-url="/api/unterrichtsbausteine" :multiple="true" :help-text="getHelpText('teaching_modules')" :prefetch="true"></app-dropdown>
      <app-dropdown id="tools" :readonly="readonly" :review="review" label="Verwendete Tools" :value.sync="data.tools" :review-value.sync="reviewValue.tools" :error="errorFields.includes('tools')" fetch-url="/api/tools" :multiple="true" :help-text="getHelpText('tools')" :prefetch="true"></app-dropdown>
      <app-links-input id="additional_tools" :readonly="readonly" :review="review" :links.sync="data.additional_tools" :review-value.sync="reviewValue.additional_tools" :error="errorFields.includes('additional_tools')" label="Andere Tools" :help-text="getHelpText('additional_tools')" link-placeholder="Link zum Tool" name-placeholder="Name des Tools"></app-links-input>
      <app-dropdown id="trends" :readonly="readonly" :review="review" label="Passende Trends" :value.sync="data.trends" :review-value.sync="reviewValue.trends" :error="errorFields.includes('trends')" fetch-url="/api/trends" :multiple="true" :help-text="getHelpText('trends')" :prefetch="true"></app-dropdown>
      <app-dropdown id="competences" :readonly="readonly" :review="review" label="Kompetenzen in der digitalen Welt" :required="true" :value.sync="data.competences" :review-value.sync="reviewValue.competences" :error="errorFields.includes('competences')" fetch-url="/api/competences" :multiple="true" :prefetch="true" :help-text="getHelpText('competences')"></app-dropdown>
      <app-dropdown id="subCompetences" :readonly="readonly" :review="review" label="Detaillierte Kompetenzbeschreibungen" :value.sync="data.sub_competences" :review-value.sync="reviewValue.sub_competences" :error="errorFields.includes('sub_competences')" :disabled="!data.competences.length" fetch-url="/api/sub-competences" :prefetch="true" :params="{competences: data.competences}" :multiple="true" :help-text="getHelpText('sub_competences')"></app-dropdown>
      <app-text-input id="estimatedTime" :readonly="readonly" :review="review" label="Zeitumfang der Durchführung" :value.sync="data.estimated_time" :review-value.sync="reviewValue.estimated_time" :error="errorFields.includes('estimated_time')" :initial="data.estimated_time" :help-text="getHelpText('estimated_time')" :character-counter="true" :maximal-chars="200"></app-text-input>
      <app-list-input id="goals" :min="1" :readonly="readonly" :review="review" label="Ziele" :list.sync="data.learning_goals" :review-value.sync="reviewValue.learning_goals" :error="errorFields.includes('learning_goals')" :initial="data.learning_goals" :help-text="getHelpText('learning_goals')" :textarea="true"></app-list-input>
      <app-range-input id="classes" :readonly="readonly" :review="review" label="Jahrgangsstufe" label-from="Von" label-to="Bis" type="number" :range.sync="data.school_class" :review-value.sync="reviewValue.school_class" :error="errorFields.includes('school_class')" :min="1" :max="13" :help-text="getHelpText('school_class')"></app-range-input>
      <app-text-area id="subject-of-tuition" :readonly="readonly" :review="review" label="Informationen zum Unterrichtsgegenstand" :value.sync="data.subject_of_tuition" :review-value.sync="reviewValue.subject_of_tuition" :error="errorFields.includes('subject_of_tuition')" :initial="data.subject_of_tuition" :help-text="getHelpText('subject_of_tuition')"></app-text-area>
      <app-list-input id="expertise" :min="1" :readonly="readonly" :review="review" label="Fachkompetenzen" :list.sync="data.expertise" :review-value.sync="reviewValue.expertise" :error="errorFields.includes('expertise')" :initial="data.expertise" :help-text="getHelpText('expertise')"></app-list-input>
      <app-list-input id="equipment" :min="1" :readonly="readonly" :review="review" label="Medienausstattung" :list.sync="data.equipment" :review-value.sync="reviewValue.equipment" :error="errorFields.includes('equipment')" :initial="data.equipment" :help-text="getHelpText('equipment')"></app-list-input>
      <app-text-area id="educationalPlanReference" :readonly="readonly" :review="review" label="Bildungsplanbezug" :value.sync="data.educational_plan_reference" :review-value.sync="reviewValue.educational_plan_reference" :error="errorFields.includes('educational_plan_reference')" :character-counter="true" :maximal-chars="1300" :help-text="getHelpText('educational_plan_reference')"></app-text-area>
      <app-text-area id="differentiatingAttributes" :readonly="readonly" :review="review" label="Möglichkeiten der Differenzierung/Individualisierung" :value.sync="data.differentiating_attribute" :review-value.sync="reviewValue.differentiating_attribute" :error="errorFields.includes('differentiating_attribute')" :character-counter="true" :maximal-chars="700" :help-text="getHelpText('differentiating_attribute')"></app-text-area>
      <app-text-area id="hints" :readonly="readonly" :review="review" label="Hinweise" :value.sync="data.additional_info" :review-value.sync="reviewValue.additional_info" :error="errorFields.includes('additional_info')" :character-counter="true" :maximal-chars="1000" :help-text="getHelpText('additional_info')"></app-text-area>
      <app-select id="license" :readonly="readonly" :review="review" label="Lizenz" :options="licenseOptions" :default-val="data.licence" :value.sync="data.licence" :review-value.sync="reviewValue.licence" :error="errorFields.includes('licence')" :help-text="getHelpText('licence')"></app-select>
      <app-links-input id="mediaLinks" :readonly="readonly" :review="review" :links.sync="data.mediaLinks" :review-value.sync="reviewValue.mediaLinks" :error="errorFields.includes('mediaLinks')" label="Links zu Audio- und Videomedien" :type="'video'" :help-text="getHelpText('contentlink')" :types="true"></app-links-input>
      <app-links-input id="literatureLinks" :readonly="readonly" :review="review" :links.sync="data.literatureLinks" :review-value.sync="reviewValue.literatureLinks" :error="errorFields.includes('literatureLinks')" label="Weiterführende Literatur und Links" :help-text="getHelpText('contentlink')" :types="true"></app-links-input>
      <app-dropzone :slug="data.slug" label="Dateiupload" :files="data.content_files" :help-text="getHelpText('contentfile')"></app-dropzone>
    </div>
  </app-content-submission-form>
</template>

<script>
  import { submissionMixin } from './mixins/submissionMixin'
  import ContentSubmissionForm from './ContentSubmissionForm.vue'
  import Dropzone from './components/Dropzone.vue'

  export default {
    name: 'TeachingModuleSubmissionApp',
    mixins: [submissionMixin],
    components: {
      'AppContentSubmissionForm': ContentSubmissionForm,
      'AppDropzone': Dropzone
    },
    data () {
      return {
        resourceType: 'TeachingModule',
        requiredFields: [
          {field: 'name', title: 'Titel'},
          {field: 'teaser', title: 'Kurzzusammenfassung'},
          {field: 'image', title: 'Anzeigebild'},
          {field: 'competences', title: 'Kompetenzen in der digitalen Welt'},
          {field: 'description', title: 'Detaillierte Beschreibung'},
          {field: 'school_types', title: 'Schulform'},
          {field: 'subjects', title: 'Unterrichtsfach'}
        ],
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
          estimated_time: '',
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
          subject_of_tuition: '',
          subjects: [],
          equipment: [],
          additional_tools: [],
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