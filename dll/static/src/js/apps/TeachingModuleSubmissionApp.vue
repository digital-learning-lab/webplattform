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
    <template v-if="mode === 'edit'" #progress>
      <FormProgress class="mt-5" :steps="steps" :active="stepIndex" @set-index="setIndex" />
    </template>

    <template #buttonsTop>
      <span />
    </template>
    <template #messagesTop>
      <span />
    </template>

    <h2 class="mt-5 mb-4">
      {{ currentStep.long }}
    </h2>

    <div v-if="reviewValue.feedback && !review" class="form-group mb-3">
      <label>Feedback:</label> <br />
      {{ reviewValue.feedback }}
    </div>
    <TextArea
      v-if="review"
      id="feedback"
      v-model:review-value="reviewValue.feedback"
      label="Feedback"
      :review="false"
      :required="false"
      :rows="3"
      :help-text="getHelpText('feedback')"
    />

    <div v-show="stepIndex === 0">
      <TextInput id="author" v-model:input-value="data.author" label="Autor_in" required readonly />
      <TextInput
        id="title"
        v-model:input-value="data.name"
        v-model:review-value="reviewValue.name"
        label="Titel des Unterrichtbausteins"
        required
        character-counter
        :readonly="readonly"
        :review="review"
        :error="errorFields.includes('name')"
        :maximal-chars="140"
        :help-text="getHelpText('name')"
      />
    </div>
    <div v-if="mode === 'edit' || mode === 'review'">
      <div v-show="stepIndex === 0">
        <AppDropdown
          id="co_authors"
          v-model:dropdown-value="data.co_authors"
          v-model:review-value="reviewValue.co_authors"
          label="Co-Autor_innen"
          fetch-url="/api/authors"
          multiple
          :readonly="readonly"
          :review="review"
          :error="errorFields.includes('co_authors')"
          :help-text="getHelpText('co_authors')"
        />
        <PendingCoAuthors :pending-co-authors="data.pending_co_authors" />
        <FileInput
          id="image"
          v-model:file-value="previewImage"
          v-model:review-value="reviewValue.image"
          label="Anzeigebild"
          file-label="Bild wählen"
          required
          :readonly="readonly"
          :review="review"
          :error="errorFields.includes('image')"
          :image="data.image"
          :help-text="getHelpText('image')"
          :hint-text="imageHintText"
        />
        <TextArea
          id="teaser"
          v-model:input-value="data.teaser"
          v-model:review-value="reviewValue.teaser"
          label="Kurzzusammenfassung"
          required
          character-counter
          :readonly="readonly"
          :review="review"
          :error="errorFields.includes('teaser')"
          :rows="3"
          :help-text="getHelpText('teaser')"
          :maximal-chars="140"
        />
        <TextArea
          id="description"
          v-model:input-value="data.description"
          v-model:review-value="reviewValue.description"
          label="Detaillierte Beschreibung"
          required
          character-counter
          :readonly="readonly"
          :review="review"
          :error="errorFields.includes('description')"
          :maximal-chars="1800"
          :rows="10"
          :help-text="getHelpText('description')"
        />
        <TextArea
          id="subject-of-tuition"
          v-model:input-value="data.subject_of_tuition"
          v-model:review-value="reviewValue.subject_of_tuition"
          label="Informationen zum Unterrichtsgegenstand"
          :readonly="readonly"
          :review="review"
          :error="errorFields.includes('subject_of_tuition')"
          :initial="data.subject_of_tuition"
          :help-text="getHelpText('subject_of_tuition')"
        />
        <AppSelect
          id="license"
          v-model:input-value="data.licence"
          v-model:review-value="reviewValue.licence"
          label="Lizenz"
          :readonly="readonly"
          :review="review"
          :options="licenseOptions"
          :default-val="data.licence"
          :error="errorFields.includes('licence')"
          :help-text="getHelpText('licence')"
        />
      </div>
      <div v-show="stepIndex === 1">
        <AppDropdown
          id="subject"
          v-model:dropdown-value="data.subjects"
          v-model:review-value="reviewValue.subjects"
          label="Unterrichtsfach"
          fetch-url="/api/subjects"
          required
          multiple
          prefetch
          :readonly="readonly"
          :review="review"
          :error="errorFields.includes('subjects')"
          :help-text="getHelpText('subjects')"
        />
        <AppDropdown
          id="schoolType"
          v-model:dropdown-value="data.school_types"
          v-model:review-value="reviewValue.school_types"
          label="Schulform"
          required
          multiple
          prefetch
          fetch-url="/api/schoolTypes"
          :readonly="readonly"
          :review="review"
          :error="errorFields.includes('school_types')"
          :help-text="getHelpText('school_types')"
        />

        <RangeInput
          id="classes"
          v-model:range-value="data.school_class"
          v-model:review-value="reviewValue.school_class"
          label="Jahrgangsstufe"
          label-from="Von"
          label-to="Bis"
          type="number"
          :readonly="readonly"
          :review="review"
          :error="errorFields.includes('school_class')"
          :min="1"
          :max="13"
          :help-text="getHelpText('school_class')"
        />
        <AppSelect
          id="state"
          v-model:input-value="data.state"
          v-model:review-value="reviewValue.state"
          label="Bundesland"
          :readonly="readonly"
          :review="review"
          :error="errorFields.includes('state')"
          :default-val="data.state"
          :options="germanStateOptions"
          :help-text="getHelpText('state')"
        />
        <TextInput
          id="estimatedTime"
          v-model:input-value="data.estimated_time"
          v-model:review-value="reviewValue.estimated_time"
          label="Zeitumfang der Durchführung"
          character-counter
          :readonly="readonly"
          :review="review"
          :error="errorFields.includes('estimated_time')"
          :initial="data.estimated_time"
          :help-text="getHelpText('estimated_time')"
          :maximal-chars="200"
        />
        <TextArea
          id="educationalPlanReference"
          v-model:input-value="data.educational_plan_reference"
          v-model:review-value="reviewValue.educational_plan_reference"
          label="Bildungsplanbezug"
          character-counter
          :readonly="readonly"
          :review="review"
          :error="errorFields.includes('educational_plan_reference')"
          :maximal-chars="1300"
          :help-text="getHelpText('educational_plan_reference')"
        />
      </div>
      <div v-show="stepIndex === 2">
        <ListInput
          id="goals"
          v-model:list-value="data.learning_goals"
          v-model:review-value="reviewValue.learning_goals"
          label="Ziele"
          textarea
          :min="1"
          :readonly="readonly"
          :review="review"
          :error="errorFields.includes('learning_goals')"
          :initial="data.learning_goals"
          :help-text="getHelpText('learning_goals')"
        />
        <ListInput
          id="expertise"
          v-model:list-value="data.expertise"
          v-model:review-value="reviewValue.expertise"
          label="Fachkompetenzen"
          :min="1"
          :readonly="readonly"
          :review="review"
          :error="errorFields.includes('expertise')"
          :initial="data.expertise"
          :help-text="getHelpText('expertise')"
        />
        <TextArea
          id="differentiatingAttributes"
          v-model:input-value="data.differentiating_attribute"
          v-model:review-value="reviewValue.differentiating_attribute"
          label="Möglichkeiten der Differenzierung/Individualisierung"
          character-counter
          :readonly="readonly"
          :review="review"
          :error="errorFields.includes('differentiating_attribute')"
          :maximal-chars="700"
          :help-text="getHelpText('differentiating_attribute')"
        />
        <AppDropdown
          id="competences"
          v-model:dropdown-value="data.competences"
          v-model:review-value="reviewValue.competences"
          label="Kompetenzen in der digitalen Welt"
          fetch-url="/api/competences"
          required
          multiple
          prefetch
          :readonly="readonly"
          :review="review"
          :error="errorFields.includes('competences')"
          :help-text="getHelpText('competences')"
        />
        <AppDropdown
          id="subCompetences"
          v-model:dropdown-value="data.sub_competences"
          v-model:review-value="reviewValue.sub_competences"
          label="Detaillierte Kompetenzbeschreibungen"
          fetch-url="/api/sub-competences"
          prefetch
          multiple
          :readonly="readonly"
          :review="review"
          :error="errorFields.includes('sub_competences')"
          :disabled="!data.competences.length"
          :params="{ competences: data.competences }"
          :help-text="getHelpText('sub_competences')"
        />
      </div>
      <div v-show="stepIndex === 3">
        <ListInput
          id="equipment"
          v-model:list-value="data.equipment"
          v-model:review-value="reviewValue.equipment"
          label="Medienausstattung"
          :min="1"
          :readonly="readonly"
          :review="review"
          :error="errorFields.includes('equipment')"
          :initial="data.equipment"
          :help-text="getHelpText('equipment')"
        />
        <TextArea
          id="hints"
          v-model:input-value="data.additional_info"
          v-model:review-value="reviewValue.additional_info"
          label="Hinweise"
          character-counter
          :readonly="readonly"
          :review="review"
          :error="errorFields.includes('additional_info')"
          :maximal-chars="1000"
          :help-text="getHelpText('additional_info')"
        />
        <LinksInput
          id="mediaLinks"
          v-model:links-value="data.mediaLinks"
          v-model:review-value="reviewValue.mediaLinks"
          label="Links zu Audio- und Videomedien"
          types
          :readonly="readonly"
          :review="review"
          :error="errorFields.includes('mediaLinks')"
          :type="'video'"
          :help-text="getHelpText('contentlink')"
        />

        <AppDropzone
          label="Dateiupload"
          :slug="data.slug"
          :files="data.content_files"
          :readonly="readonly"
          :help-text="getHelpText('contentfile')"
        />
      </div>
      <div v-show="stepIndex === 4">
        <LinksInput
          id="literatureLinks"
          v-model:links-value="data.literatureLinks"
          v-model:review-value="reviewValue.literatureLinks"
          label="Weiterführende Literatur und Links"
          types
          :readonly="readonly"
          :review="review"
          :error="errorFields.includes('literatureLinks')"
          :help-text="getHelpText('contentlink')"
        />
        <AppDropdown
          id="teaching-modules"
          v-model:dropdown-value="data.teaching_modules"
          v-model:review-value="reviewValue.teaching_modules"
          label="Passende Unterrichtsbausteine"
          fetch-url="/api/unterrichtsbausteine"
          multiple
          prefetch
          :readonly="readonly"
          :review="review"
          :error="errorFields.includes('teaching_modules')"
          :help-text="getHelpText('teaching_modules')"
        />
        <AppDropdown
          id="tools"
          v-model:dropdown-value="data.tools"
          v-model:review-value="reviewValue.tools"
          label="Verwendete Tools"
          fetch-url="/api/tools"
          multiple
          prefetch
          :readonly="readonly"
          :review="review"
          :error="errorFields.includes('tools')"
          :help-text="getHelpText('tools')"
        />
        <LinksInput
          id="additional_tools"
          v-model:links-value="data.additional_tools"
          v-model:review-value="reviewValue.additional_tools"
          label="Andere Tools"
          link-placeholder="Link zum Tool"
          name-placeholder="Name des Tools"
          :readonly="readonly"
          :review="review"
          :error="errorFields.includes('additional_tools')"
          :help-text="getHelpText('additional_tools')"
        />
        <AppDropdown
          id="trends"
          v-model:dropdown-value="data.trends"
          v-model:review-value="reviewValue.trends"
          label="Passende Trends"
          fetch-url="/api/trends"
          multiple
          prefetch
          :readonly="readonly"
          :review="review"
          :error="errorFields.includes('trends')"
          :help-text="getHelpText('trends')"
        />
      </div>
    </div>
    <template #extraButtons>
      <div v-if="mode === 'edit' || mode === 'review'" class="text-right">
        <button v-if="stepIndex > 0" class="button button--primary me-3" type="button" @click="setIndex(stepIndex - 1)">
          Vorheriger Schritt
        </button>
        <button
          v-if="stepIndex < steps.length - 1"
          class="button button--primary"
          type="button"
          @click="setIndex(stepIndex + 1)"
        >
          Nächster Schritt
        </button>
      </div>
    </template>
  </ContentSubmissionForm>
</template>

<script setup>
import { computed, ref } from 'vue';

import AppDropdown from '../components/AppDropdown.vue';
import AppDropzone from '../components/AppDropzone.vue';
import AppSelect from '../components/AppSelect.vue';
import ContentSubmissionForm from '../components/ContentSubmissionForm.vue';
import FileInput from '../components/FileInput.vue';
import FormProgress from '../components/FormProgress.vue';
import LinksInput from '../components/LinksInput.vue';
import ListInput from '../components/ListInput.vue';
import PendingCoAuthors from '../components/PendingCoAuthors.vue';
import RangeInput from '../components/RangeInput.vue';
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

const steps = ref([
  {
    long: 'Allgemeine Informationen zum Unterrichtsbaustein',
    short: 'Allgemeine Informationen'
  },
  {
    long: 'Allgemeine Informationen zum schulischen Kontext des Unterrichtsbausteins',
    short: 'Informationen zum schulischen Kontext'
  },
  {
    long: 'Zielsetzungen des Unterrichtsbausteins',
    short: 'Zielsetzungen'
  },
  {
    long: 'Voraussetzungen zum Einsatz des Unterrichtsbausteins im Unterricht',
    short: 'Voraussetzungen zum Einsatz'
  },
  {
    long: 'Weiterführende Informationen zum Unterrichtsbaustein',
    short: 'Weiterführende Informationen'
  }
]);
const stepIndex = ref(0);
const germanStateOptions = ref([
  { label: 'Nordrhein-Westfalen', value: 'nordrhein-westfalen' },
  { label: 'Niedersachsen', value: 'niedersachsen' },
  { label: 'Bayern', value: 'bayern' },
  { label: 'Rheinland-Pfalz', value: 'rheinland-pfalz' },
  { label: 'Hessen', value: 'hessen' },
  { label: 'Saarland', value: 'saarland' },
  { label: 'Berlin', value: 'berlin' },
  { label: 'Brandenburg', value: 'brandenburg' },
  { label: 'Schleswig-Holstein', value: 'schleswig-holstein' },
  { label: 'Mecklenburg-Vorpommern', value: 'mecklenburg-vorpommern' },
  { label: 'Thüringen', value: 'thueringen' },
  { label: 'Sachsen', value: 'sachsen' },
  { label: 'Sachsen-Anhalt', value: 'sachsen-anhalt' },
  { label: 'Bremen', value: 'bremen' },
  { label: 'Baden-Württemberg', value: 'baden-wuerttemberg' },
  { label: 'Hamburg', value: 'hamburg' }
]);

data.value = {
  additional_info: '',
  additional_tools: [],
  author: '',
  classFrom: null,
  classTo: null,
  co_authors: [],
  competences: [],
  contentlink_set: [],
  description: '',
  differentiating_attribute: '',
  educational_plan_reference: '',
  equipment: [],
  estimated_time: '',
  expertise: [],
  hints: '',
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
  subject_of_tuition: '',
  subjects: [],
  teaching_modules: [],
  teaser: '',
  tools: [],
  trends: []
};
resourceType.value = 'TeachingModule';
requiredFields.value = [
  { field: 'name', title: 'Titel' },
  { field: 'teaser', title: 'Kurzzusammenfassung' },
  { field: 'image', title: 'Anzeigebild' },
  { field: 'competences', title: 'Kompetenzen in der digitalen Welt' },
  { field: 'description', title: 'Detaillierte Beschreibung' },
  { field: 'school_types', title: 'Schulform' },
  { field: 'subjects', title: 'Unterrichtsfach' }
];

//  --------------------------------------------------------------------------------------------------------------------
//  computed
//  --------------------------------------------------------------------------------------------------------------------
const currentStep = computed(() => {
  return steps.value[stepIndex.value];
});

//  --------------------------------------------------------------------------------------------------------------------
//  component logic
//  --------------------------------------------------------------------------------------------------------------------
const setIndex = (index) => {
  if (mode.value === 'edit') {
    updateContent();
  }

  if (mode.value === 'review') {
    updateReview();
  }

  stepIndex.value = index;
  let ele = document.getElementById('submission-form');
  if (window.scrollY > ele.offsetTop) {
    window.scrollTo(0, ele.offsetTop);
  }
};
</script>

<style scoped></style>
