<template>
  <app-content-submission-form :errors="errors" :mode="mode" :loading="loading" :saved="saved" @update="updateContent" @create="createContent" @delete-warning="showDeleteWarning" :data="data" @delete="deleteContent">
      <app-text-input id="author" :read-only="true" label="Autor_in" :value.sync="data.author" :required="true"></app-text-input>
      <app-text-input id="title" label="Titel des Trends" :value.sync="data.name" :required="true" :character-counter="true" :maximal-chars="140" :help-text="getHelpText('name')"></app-text-input>
    <div v-if="mode === 'edit'">
      <app-file-input id="image" label="Anzeigebild" file-label="Bild wählen" :value.sync="previewImage" :image="data.image" :help-text="getHelpText('image')"></app-file-input>
      <app-select id="imageRights" label="Bildrechte" :options="imageOptions" default-val="n" :value.sync="data.imageRights" :help-text="getHelpText('imageRights')"></app-select>
      <app-text-area id="teaser" label="Kurzzusammenfassung" :required="true" :value.sync="data.teaser" :rows="3" :help-text="getHelpText('teaser')"></app-text-area>
      <app-dropdown id="co_authors" label="Co-Autor_innen" :value.sync="data.co_authors" fetch-url="/api/authors" :multiple="true" :help-text="getHelpText('co_authors')"></app-dropdown>
      <app-dropdown id="teaching-modules" label="Passende Unterrichtsbausteine" :value.sync="data.teaching_modules" fetch-url="/api/unterrichtsbausteine" :multiple="true" :help-text="getHelpText('teaching_modules')"></app-dropdown>
      <app-dropdown id="tools" label="Verwendete Tools" :value.sync="data.tools" fetch-url="/api/tools" :multiple="true" :help-text="getHelpText('tools')"></app-dropdown>
      <app-dropdown id="trends" label="Passende Trends" :value.sync="data.trends" fetch-url="/api/trends" :multiple="true" :help-text="getHelpText('trends')"></app-dropdown>
      <app-dropdown id="competences" label="Kompetenzen in der digitalen Welt" :required="true" :value.sync="data.competences" fetch-url="/api/competences" :multiple="true" :prefetch="true" :help-text="getHelpText('competences')"></app-dropdown>

      <app-select id="category" label="Kategorie" :options="categoryOptions" :value.sync="data.category" :default-val="data.category" :help-text="getHelpText('category')"></app-select>
      <app-list-input id="target-group" label="Zielgruppe" :list.sync="data.target_group" :initial="data.target_group" :help-text="getHelpText('target_group')"></app-list-input>
      <app-select id="language" label="Sprache" :options="languageOptions" :value.sync="data.language" :default-val="data.language" :help-text="getHelpText('language')"></app-select>
      <app-list-input id="publisher" label="Herausgeber_in" :list.sync="data.publisher" :initial="data.publisher" :help-text="getHelpText('publisher')"></app-list-input>
      <app-list-input id="goals" label="Zielsetzung" :list.sync="data.learning_goals" :initial="data.learning_goals" :help-text="getHelpText('learning_goals')"></app-list-input>
      <app-text-area id="central-contents" label="Zentrale Inhalte" :value.sync="data.central_contents" :character-counter="true" :maximal-chars="1300" :help-text="getHelpText('central_contents')"></app-text-area>
      <app-text-area id="additional-info" label="Hintergrundinformationen" :required="true" :value.sync="data.additional_info" :character-counter="true" :maximal-chars="1500" :rows="10" :help-text="getHelpText('additional_info')"></app-text-area>
      <app-select id="license" label="Lizenz" :options="licenseOptions" :default-val="data.licence" :value.sync="data.licence" :help-text="getHelpText('licence')"></app-select>
      <app-text-area id="citation-info" label="Zitierhinweis" :value.sync="data.citation_info" :character-counter="true" :maximal-chars="200" :help-text="getHelpText('citation_info')"></app-text-area>

      <app-links-input id="websites" :links.sync="data.mediaLinks" label="Website" type="href" :help-text="getHelpText('contentlink>')"></app-links-input>
      <app-links-input id="additionalLinks" :links.sync="data.literatureLinks" label="Weitere Links" type="href" :help-text="getHelpText('contentlink>')"></app-links-input>

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
          {value: 'english', label: 'Englisch'},
          {value: 'french', label: 'Französisch'},
          {value: 'russian', label: 'Russisch'}
        ]
      }
    }
  }
</script>

<style scoped>

</style>