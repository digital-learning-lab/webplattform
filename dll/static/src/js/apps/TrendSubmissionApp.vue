<template>
  <ContentSubmissionForm
    v-model:mode="mode"
    :data="data"
    :errors="errors"
    :loading="loading"
    :saved="saved"
    :can-delete="canDelete"
    @update="updateContent"
    @create="createContent"
    @preview="goToPreview"
    @delete-warning="showDeleteWarning"
    @delete="deleteContent"
    @submit="submitContent"
    @update-review="updateReview"
    @approve-review="approveContent"
    @decline-review="declineContent"
  >
    <div v-if="reviewValue.feedback && !review" class="form-group mb-3">
      <label>Feedback:</label> <br />
      {{ reviewValue.feedback }}
    </div>
    <TextArea
      v-if="review"
      id="feedback"
      v-model:input-value="reviewValue.feedback"
      label="Feedback"
      :review="false"
      :required="false"
      :rows="3"
      :help-text="getHelpText('feedback')"
    />
    <TextInput id="author" v-model:input-value="data.author" :readonly="true" label="Autor_in" :required="true" />
    <TextInput
      id="title"
      v-model:review-value="reviewValue.name"
      v-model:input-value="data.name"
      :readonly="readonly"
      :review="review"
      :error="errorFields.includes('name')"
      label="Titel des Trends"
      :required="true"
      :character-counter="true"
      :maximal-chars="140"
      :help-text="getHelpText('name')"
    />
    <div v-if="mode === 'edit' || mode === 'review'">
      <FileInput
        id="image"
        v-model:file-value="previewImage"
        v-model:review-value="reviewValue.previewImage"
        :readonly="readonly"
        :review="review"
        :required="true"
        label="Anzeigebild"
        file-label="Bild wählen"
        :error="errorFields.includes('image')"
        :image="data.image"
        :help-text="getHelpText('image')"
        :hint-text="imageHintText"
      />
      <TextArea
        id="teaser"
        v-model:review-value="reviewValue.teaser"
        v-model:input-value="data.teaser"
        label="Kurzzusammenfassung"
        :readonly="readonly"
        :review="review"
        :error="errorFields.includes('teaser')"
        :required="true"
        :rows="3"
        :help-text="getHelpText('teaser')"
      />
      <AppDropdown
        id="co_authors"
        v-model:review-value="reviewValue.co_authors"
        v-model:dropdown-value="data.co_authors"
        :readonly="readonly"
        :review="review"
        :error="errorFields.includes('co_authors')"
        label="Co-Autor_innen"
        fetch-url="/api/authors"
        :multiple="true"
        :help-text="getHelpText('co_authors')"
      />
      <PendingCoAuthors :pending-co-authors="data.pending_co_authors" />
      <AppDropdown
        id="teaching-modules"
        v-model:review-value="reviewValue.teaching_modules"
        v-model:dropdown-value="data.teaching_modules"
        :readonly="readonly"
        :review="review"
        :error="errorFields.includes('teaching_modules')"
        label="Passende Unterrichtsbausteine"
        fetch-url="/api/unterrichtsbausteine"
        :multiple="true"
        :help-text="getHelpText('teaching_modules')"
        :prefetch="true"
      />
      <AppDropdown
        id="tools"
        v-model:review-value="reviewValue.tools"
        v-model:dropdown-value="data.tools"
        :readonly="readonly"
        :review="review"
        :error="errorFields.includes('tools')"
        label="Passende Tools"
        fetch-url="/api/tools"
        :multiple="true"
        :help-text="getHelpText('tools')"
        :prefetch="true"
      />
      <AppDropdown
        id="trends"
        v-model:review-value="reviewValue.trends"
        v-model:dropdown-value="data.trends"
        :readonly="readonly"
        :review="review"
        :error="errorFields.includes('trends')"
        label="Passende Trends"
        fetch-url="/api/trends"
        :multiple="true"
        :help-text="getHelpText('trends')"
        :prefetch="true"
      />
      <AppDropdown
        id="competences"
        v-model:review-value="reviewValue.competences"
        v-model:dropdown-value="data.competences"
        :readonly="readonly"
        :review="review"
        :error="errorFields.includes('competences')"
        label="Kompetenzen in der digitalen Welt"
        :required="true"
        fetch-url="/api/competences"
        :multiple="true"
        :prefetch="true"
        :help-text="getHelpText('competences')"
      />

      <AppSelect
        id="category"
        v-model:review-value="reviewValue.category"
        v-model:input-value="data.category"
        :readonly="readonly"
        :review="review"
        :error="errorFields.includes('category')"
        label="Kategorie"
        :options="categoryOptions"
        :default-val="data.category"
        :help-text="getHelpText('category')"
      />
      <ListInput
        id="target-group"
        v-model:review-value="reviewValue.target_group"
        v-model:list-value="data.target_group"
        :min="1"
        :readonly="readonly"
        :review="review"
        :error="errorFields.includes('target_group')"
        label="Zielgruppe"
        :initial="data.target_group"
        :help-text="getHelpText('target_group')"
      />
      <AppSelect
        id="language"
        v-model:review-value="reviewValue.language"
        v-model:input-value="data.language"
        :readonly="readonly"
        :review="review"
        :error="errorFields.includes('language')"
        label="Sprache"
        :options="languageOptions"
        :default-val="data.language"
        :help-text="getHelpText('language')"
      />
      <ListInput
        id="publisher"
        v-model:review-value="reviewValue.publisher"
        v-model:list-value="data.publisher"
        :min="1"
        :readonly="readonly"
        :review="review"
        :error="errorFields.includes('publisher')"
        label="Herausgeber_in"
        :initial="data.publisher"
        :help-text="getHelpText('publisher')"
      />
      <ListInput
        id="goals"
        v-model:review-value="reviewValue.learning_goals"
        v-model:list-value="data.learning_goals"
        :min="1"
        :readonly="readonly"
        :review="review"
        :error="errorFields.includes('learning_goals')"
        label="Zielsetzung"
        :initial="data.learning_goals"
        :help-text="getHelpText('learning_goals')"
      />
      <TextArea
        id="central-contents"
        v-model:review-value="reviewValue.central_contents"
        v-model:input-value="data.central_contents"
        :readonly="readonly"
        :review="review"
        :error="errorFields.includes('central_contents')"
        label="Zentrale Inhalte"
        :character-counter="true"
        :maximal-chars="1300"
        :help-text="getHelpText('central_contents')"
      />
      <TextArea
        id="additional-info"
        v-model:review-value="reviewValue.additional_info"
        v-model:input-value="data.additional_info"
        :readonly="readonly"
        :review="review"
        :error="errorFields.includes('additional_info')"
        label="Hintergrundinformationen"
        :character-counter="true"
        :maximal-chars="1500"
        :rows="10"
        :help-text="getHelpText('additional_info')"
      />
      <AppSelect
        id="license"
        v-model:review-value="reviewValue.licence"
        v-model:input-value="data.licence"
        :readonly="readonly"
        :review="review"
        :error="errorFields.includes('licence')"
        label="Lizenz"
        :options="licenseOptions"
        :default-val="data.licence"
        :help-text="getHelpText('licence')"
      />
      <TextArea
        id="citation-info"
        v-model:review-value="reviewValue.citation_info"
        v-model:input-value="data.citation_info"
        :readonly="readonly"
        :review="review"
        :error="errorFields.includes('citation_info')"
        label="Zitierhinweis"
        :character-counter="true"
        :maximal-chars="200"
        :help-text="getHelpText('citation_info')"
      />

      <LinksInput
        id="websites"
        v-model:links-value="data.literatureLinks"
        v-model:review-value="reviewValue.literatureLinks"
        :readonly="readonly"
        :review="review"
        :error="errorFields.includes('literatureLinks')"
        label="Website"
        type="href"
        :help-text="getHelpText('contentlink')"
      />
      <LinksInput
        id="additionalLinks"
        v-model:links-value="data.mediaLinks"
        v-model:review-value="reviewValue.mediaLinks"
        :readonly="readonly"
        :review="review"
        :error="errorFields.includes('mediaLinks')"
        label="Weitere Links"
        type="href"
        :types="true"
        :help-text="getHelpText('contentlink')"
      />
    </div>
  </ContentSubmissionForm>
</template>

<script setup>
import { ref } from 'vue';

import AppDropdown from '../components/AppDropdown.vue';
import AppSelect from '../components/AppSelect.vue';
import ContentSubmissionForm from '../components/ContentSubmissionForm.vue';
import FileInput from '../components/FileInput.vue';
import LinksInput from '../components/LinksInput.vue';
import ListInput from '../components/ListInput.vue';
import PendingCoAuthors from '../components/PendingCoAuthors.vue';
import TextArea from '../components/TextArea.vue';
import TextInput from '../components/TextInput.vue';
import { useSubmission } from '../composables/submission';

const {
  approveContent,
  canDelete,
  createContent,
  data,
  declineContent,
  deleteContent,
  errorFields,
  errors,
  getHelpText,
  goToPreview,
  imageHintText,
  licenseOptions,
  loading,
  mode,
  previewImage,
  readonly,
  requiredFields,
  resourceType,
  review,
  reviewValue,
  saved,
  showDeleteWarning,
  submitContent,
  updateContent,
  updateReview
} = useSubmission();

const categoryOptions = ref([
  { label: 'Keine Angaben', value: 0 },
  { label: 'Forschung', value: 1 },
  { label: 'Portal', value: 2 },
  { label: 'Praxisbeispiel', value: 3 },
  { label: 'Veröffentlichung', value: 4 }
]);

const languageOptions = ref([
  { label: 'Deutsch', value: 'german' },
  { label: 'Englisch', value: 'english' }
]);

data.value = {
  additional_info: '',
  author: '',
  co_authors: [],
  competences: [],
  contentlink_set: [],
  description: '',
  differentiating_attribute: '',
  educational_plan_reference: '',
  estimated_time: [],
  image: null,
  imageRights: null,
  license: null,
  literatureLinks: [],
  mediaLinks: [],
  name: '',
  pending_co_authors: [],
  related_content: [],
  school_types: [],
  state: '',
  sub_competences: [],
  teaching_modules: [],
  teaser: '',
  tools: [],
  trends: []
};

resourceType.value = 'Trend';
requiredFields.value = [
  { field: 'name', title: 'Titel' },
  { field: 'teaser', title: 'Kurzzusammenfassung' },
  { field: 'image', title: 'Anzeigebild' },
  { field: 'competences', title: 'Kompetenzen in der digitalen Welt' }
];
</script>

<style scoped></style>
