<template>
  <app-content-submission-form :errors="errors" :mode="mode" :loading="loading" :saved="saved" @update="updateContent" @create="createContent" @preview="goToPreview" @delete-warning="showDeleteWarning" :data="data" @delete="deleteContent" @submit="submitContent" @update-review="updateReview" @approve-review="approveContent" @decline-review="declineContent">
      <app-text-input id="author" :readonly="true" label="Autor_in" :value.sync="data.author" :required="true"></app-text-input>
      <app-text-input id="title" :readonly="readonly" :review="review" :review-value.sync="reviewValue.name" label="Titel des Trends" :value.sync="data.name" :required="true" :character-counter="true" :maximal-chars="140" :help-text="getHelpText('name')"></app-text-input>
    <div v-if="mode === 'edit' || mode === 'review'">
      <app-file-input id="image" :readonly="readonly" :review="review" :review-value.sync="reviewValue.image" label="Anzeigebild" file-label="Bild wählen" :value.sync="previewImage" :image="data.image" :help-text="getHelpText('image')" :hintText="imageHintText"></app-file-input>
      <app-text-area id="teaser" :readonly="readonly" :review="review" :review-value.sync="reviewValue.teaser" label="Kurzzusammenfassung" :required="true" :value.sync="data.teaser" :rows="3" :help-text="getHelpText('teaser')"></app-text-area>
      <app-dropdown id="co_authors" :readonly="readonly" :review="review" :review-value.sync="reviewValue.co_authors" label="Co-Autor_innen" :value.sync="data.co_authors" fetch-url="/api/authors" :multiple="true" :help-text="getHelpText('co_authors')"></app-dropdown>
      <app-pending-co-authors :pending_co_authors="data.pending_co_authors"></app-pending-co-authors>
      <app-dropdown id="teaching-modules" :readonly="readonly" :review="review" :review-value.sync="reviewValue.teaching_modules" label="Passende Unterrichtsbausteine" :value.sync="data.teaching_modules" fetch-url="/api/unterrichtsbausteine" :multiple="true" :help-text="getHelpText('teaching_modules')"></app-dropdown>
      <app-dropdown id="tools" :readonly="readonly" :review="review" :review-value.sync="reviewValue.tools" label="Verwendete Tools" :value.sync="data.tools" fetch-url="/api/tools" :multiple="true" :help-text="getHelpText('tools')"></app-dropdown>
      <app-dropdown id="trends" :readonly="readonly" :review="review" :review-value.sync="reviewValue.trends" label="Passende Trends" :value.sync="data.trends" fetch-url="/api/trends" :multiple="true" :help-text="getHelpText('trends')"></app-dropdown>
      <app-dropdown id="competences" :readonly="readonly" :review="review" :review-value.sync="reviewValue.competences" label="Kompetenzen in der digitalen Welt" :required="true" :value.sync="data.competences" fetch-url="/api/competences" :multiple="true" :prefetch="true" :help-text="getHelpText('competences')"></app-dropdown>

      <app-select id="category" :readonly="readonly" :review="review" :review-value.sync="reviewValue.category" label="Kategorie" :options="categoryOptions" :value.sync="data.category" :default-val="data.category" :help-text="getHelpText('category')"></app-select>
      <app-list-input id="target-group" :readonly="readonly" :review="review" :review-value.sync="reviewValue.target_group" label="Zielgruppe" :list.sync="data.target_group" :initial="data.target_group" :help-text="getHelpText('target_group')"></app-list-input>
      <app-select id="language" :readonly="readonly" :review="review" :review-value.sync="reviewValue.language" label="Sprache" :options="languageOptions" :value.sync="data.language" :default-val="data.language" :help-text="getHelpText('language')"></app-select>
      <app-list-input id="publisher" :readonly="readonly" :review="review" :review-value.sync="reviewValue.publisher" label="Herausgeber_in" :list.sync="data.publisher" :initial="data.publisher" :help-text="getHelpText('publisher')"></app-list-input>
      <app-list-input id="goals" :readonly="readonly" :review="review" :review-value.sync="reviewValue.learning_goals" label="Zielsetzung" :list.sync="data.learning_goals" :initial="data.learning_goals" :help-text="getHelpText('learning_goals')"></app-list-input>
      <app-text-area id="central-contents" :readonly="readonly" :review="review" :review-value.sync="reviewValue.central_contents" label="Zentrale Inhalte" :value.sync="data.central_contents" :character-counter="true" :maximal-chars="1300" :help-text="getHelpText('central_contents')"></app-text-area>
      <app-text-area id="additional-info" :readonly="readonly" :review="review" :review-value.sync="reviewValue.additional_info" label="Hintergrundinformationen" :value.sync="data.additional_info" :character-counter="true" :maximal-chars="1500" :rows="10" :help-text="getHelpText('additional_info')"></app-text-area>
      <app-select id="license" :readonly="readonly" :review="review" :review-value.sync="reviewValue.licence" label="Lizenz" :options="licenseOptions" :default-val="data.licence" :value.sync="data.licence" :help-text="getHelpText('licence')"></app-select>
      <app-text-area id="citation-info" :readonly="readonly" :review="review" :review-value.sync="reviewValue.citation_info" label="Zitierhinweis" :value.sync="data.citation_info" :character-counter="true" :maximal-chars="200" :help-text="getHelpText('citation_info')"></app-text-area>

      <app-links-input id="websites" :links.sync="data.mediaLinks" :readonly="readonly" :review="review" :review-value.sync="reviewValue.mediaLinks" label="Website" type="href" :help-text="getHelpText('contentlink')"></app-links-input>
      <app-links-input id="additionalLinks" :links.sync="data.literatureLinks" :readonly="readonly" :review="review" :review-value.sync="reviewValue.literatureLinks" label="Weitere Links" type="href" :help-text="getHelpText('contentlink')"></app-links-input>
      <app-links-input id="additionalLinks" :links.sync="data.literatureLinks" :readonly="readonly" :review="review" :review-value.sync="reviewValue.literatureLinks" label="Weitere Links" type="href" :help-text="getHelpText('contentlink')"></app-links-input>

    </div>
  </app-content-submission-form>
</template>

<script>
  import { submissionMixin } from './mixins/submissionMixin'
  import ContentSubmissionForm from './ContentSubmissionForm.vue'

  export default {
    name: 'TrendSubmissionApp',
    mixins: [submissionMixin],
    components: {
      'AppContentSubmissionForm': ContentSubmissionForm
    },
    data () {
      return {
        resourceType: 'Trend',
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
        requiredFields: [
        {field: 'name', title: 'Titel'},
        {field: 'teaser', title: 'Teaser'},
        {field: 'competences', title: 'Kompetenzen in der digitalen Welt'}
      ],
        categoryOptions: [
          {value: 0, label: 'Keine Angaben'},
          {value: 1, label: 'Forschung'},
          {value: 2, label: 'Portal'},
          {value: 3, label: 'Praxisbeispiel'},
          {value: 4, label: 'Veröffentlichung'}
        ],
        languageOptions: [
          {value: 'german', label: 'Deutsch'},
          {value: 'english', label: 'Englisch'}
        ]
      }
    }
  }
</script>

<style scoped>

</style>