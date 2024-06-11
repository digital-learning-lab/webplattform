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
      v-model:review-value="reviewValue.feedback"
      label="Feedback"
      :review="false"
      :required="false"
      :rows="3"
      :help-text="getHelpText('feedback')"
    />
    <TextInput id="author" v-model:input-value="data.author" label="Autor_in" readonly required />
    <TextInput
      id="title"
      v-model:input-value="data.name"
      v-model:review-value="reviewValue.name"
      label="Titel des Tools"
      required
      character-counter
      :readonly="readonly"
      :review="review"
      :error="errorFields.includes('name')"
      :maximal-chars="140"
      :help-text="getHelpText('name')"
    />
    <div v-if="mode === 'edit' || mode === 'review'">
      <FileInput
        id="image"
        v-model:file-value="previewImage"
        v-model:review-value="reviewValue.previewImage"
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
        :readonly="readonly"
        :review="review"
        :error="errorFields.includes('teaser')"
        :rows="3"
        :help-text="getHelpText('teaser')"
      />
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
        label="Passende Tools"
        fetch-url="/api/tools"
        multiple
        prefetch
        :readonly="readonly"
        :review="review"
        :error="errorFields.includes('tools')"
        :help-text="getHelpText('tools')"
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
      <AppDropdown
        v-if="!dltFeatures"
        id="competences"
        v-model:dropdown-value="data.competences"
        v-model:review-value="reviewValue.competences"
        :readonly="readonly"
        :review="review"
        label="Kompetenzen in der digitalen Welt"
        :required="true"
        :error="errorFields.includes('competences')"
        fetch-url="/api/competences"
        :multiple="true"
        :prefetch="true"
        :help-text="getHelpText('competences')"
      />
      <AppDropdown
        v-if="!dltFeatures"
        id="tool-functions"
        v-model:dropdown-value="data.functions"
        v-model:review-value="reviewValue.functions"
        :readonly="readonly"
        :review="review"
        label="Tool-Funktionen"
        :required="true"
        :error="errorFields.includes('functions')"
        fetch-url="/api/toolFunctions"
        :multiple="true"
        :prefetch="true"
        :help-text="getHelpText('functions')"
      />
      <LinkInput
        id="url"
        v-model:link-value="data.url"
        v-model:review-value="reviewValue.url"
        :readonly="readonly"
        :review="review"
        :error="errorFields.includes('url')"
        label="Website"
        :type="'null'"
        :help-text="getHelpText('url')"
        :required="true"
      />
      <ListInput
        v-if="!dltFeatures"
        id="pro"
        v-model:list-value="data.pro"
        v-model:review-value="reviewValue.pro"
        :min="1"
        :readonly="readonly"
        :review="review"
        label="Vorteile"
        :error="errorFields.includes('pro')"
        :initial="data.pro"
        :help-text="getHelpText('pro')"
      />
      <ListInput
        v-if="!dltFeatures"
        id="contra"
        v-model:list-value="data.contra"
        v-model:review-value="reviewValue.contra"
        :min="1"
        :readonly="readonly"
        :review="review"
        label="Nachteile"
        :error="errorFields.includes('contra')"
        :initial="data.contra"
        :help-text="getHelpText('contra')"
      />
      <AppSelect
        id="data-privacy"
        v-model:input-value="data.privacy"
        v-model:review-value="reviewValue.privacy"
        :readonly="readonly"
        :review="review"
        label="Datenschutz"
        :options="dataPrivacyOptions"
        :error="errorFields.includes('privacy')"
        :default-val="data.privacy"
        :help-text="getHelpText('privacy')"
      />
      <TextArea
        id="usage"
        v-model:input-value="data.usage"
        v-model:review-value="reviewValue.usage"
        :readonly="readonly"
        :review="review"
        label="Nutzung"
        :error="errorFields.includes('usage')"
        :character-counter="true"
        :maximal-chars="300"
        :help-text="getHelpText('usage')"
      />
      <AppDropdown
        id="applications"
        v-model:dropdown-value="data.applications"
        v-model:review-value="reviewValue.applications"
        :readonly="readonly"
        :review="review"
        label="Anwendung"
        :error="errorFields.includes('applications')"
        fetch-url="/api/applications"
        :multiple="true"
        :prefetch="true"
        :help-text="getHelpText('applications')"
      />
      <LinksInput
        id="mediaLinks"
        v-model:links-value="data.mediaLinks"
        v-model:review-value="reviewValue.mediaLinks"
        :readonly="readonly"
        :review="review"
        :error="errorFields.includes('mediaLinks')"
        label="Links zu Audio- und Videomedien"
        :type="'video'"
        :help-text="getHelpText('contentlink')"
        :types="true"
      />
      <LinksInput
        id="literatureLinks"
        v-model:links-value="data.literatureLinks"
        v-model:review-value="reviewValue.literatureLinks"
        :readonly="readonly"
        :review="review"
        :error="errorFields.includes('literatureLinks')"
        label="Text-Anleitung"
        :help-text="getHelpText('contentlink')"
        :types="true"
      />
      <AppSelect
        id="requires_registration"
        v-model:input-value="data.requires_registration"
        v-model:review-value="reviewValue.requires_registration"
        :readonly="readonly"
        :review="review"
        label="Registrierung erforderlich"
        :options="registrationOptions"
        :error="errorFields.includes('requires_registration')"
        :default-val="data.requires_registration"
        :help-text="getHelpText('requires_registration')"
      />
      <AppSelect
        id="usk"
        v-model:input-value="data.usk"
        v-model:review-value="reviewValue.usk"
        :readonly="readonly"
        :review="review"
        label="Altersfreigabe"
        :options="uskOptions"
        :error="errorFields.includes('usk')"
        :default-val="data.usk"
        :help-text="getHelpText('usk')"
      />
      <AppSelect
        id="status"
        v-model:input-value="data.status"
        v-model:review-value="reviewValue.status"
        :readonly="readonly"
        :review="review"
        label="Status"
        :options="statusOptions"
        :error="errorFields.includes('status')"
        :default-val="data.status"
        :help-text="getHelpText('status')"
      />
      <TextArea
        id="additional-info"
        v-model:input-value="data.additional_info"
        v-model:review-value="reviewValue.additional_info"
        :readonly="readonly"
        :review="review"
        label="Anmerkungen"
        :error="errorFields.includes('additional_info')"
        :character-counter="true"
        :maximal-chars="700"
        :rows="10"
        :help-text="getHelpText('additional_info')"
      />
      <TextArea
        id="description"
        v-model:input-value="data.description"
        v-model:review-value="reviewValue.description"
        :readonly="readonly"
        :review="review"
        label="Detaillierte Beschreibung"
        :error="errorFields.includes('description')"
        :character-counter="true"
        :maximal-chars="500"
        :rows="10"
        :help-text="getHelpText('description')"
      />
      <AppDropdown
        id="operating_systems"
        v-model:dropdown-value="data.operating_systems"
        v-model:review-value="reviewValue.operating_systems"
        :readonly="readonly"
        :review="review"
        label="Betriebssystem"
        :error="errorFields.includes('operating_systems')"
        fetch-url="/api/operatingSystems"
        :multiple="true"
        :prefetch="true"
        :help-text="getHelpText('operating_systems')"
      />
      <AppDropdown
        id="subject"
        v-model:dropdown-value="data.subjects"
        v-model:review-value="reviewValue.subjects"
        :readonly="readonly"
        :review="review"
        :required="true"
        label="Unterrichtsfach"
        :error="errorFields.includes('subjects')"
        fetch-url="/api/subjects"
        :multiple="true"
        :prefetch="true"
        :help-text="getHelpText('subjects')"
      />
      <AppSelect
        id="with_costs"
        v-model:input-value="data.with_costs"
        v-model:review-value="reviewValue.with_costs"
        :readonly="readonly"
        :review="review"
        label="Kostenpflichtig"
        :options="with_costsOptions"
        :error="errorFields.includes('with_costs')"
        :default-val="data.with_costs"
        :help-text="getHelpText('with_costs')"
      />
      <AppDropdown
        v-if="dltFeatures"
        id="tool-potentials"
        v-model:dropdown-value="data.potentials"
        v-model:review-value="reviewValue.potentials"
        :readonly="readonly"
        :review="review"
        label="Potential Kategorien"
        :required="true"
        :error="errorFields.includes('potentials')"
        fetch-url="/api/potentials"
        :multiple="true"
        :prefetch="true"
        :help-text="getHelpText('potentials')"
      />
      <TextArea
        v-if="dltFeatures"
        id="disclaimer"
        v-model:input-value="data.disclaimer"
        v-model:review-value="reviewValue.disclaimer"
        :readonly="readonly"
        :review="review"
        label="Disclaimer"
        :error="errorFields.includes('disclaimer')"
        :rows="3"
        :help-text="getHelpText('disclaimer')"
      />
      <LinksInput
        id="video_tutorials"
        v-model:links-value="data.video_tutorials"
        v-model:review-value="reviewValue.video_tutorials"
        :readonly="readonly"
        :review="review"
        :error="errorFields.includes('video_tutorials')"
        label="Video Anleitungen"
        :type="'video'"
        :help-text="getHelpText('video_tutorials')"
        :types="false"
      />
      <DataProtectionInput
        v-if="dltFeatures"
        id="server_location"
        v-model:compliance-text="data.data_privacy_assessment.server_location_text"
        v-model:compliance="data.data_privacy_assessment.server_location"
        v-model:review-value="reviewValue.server_location"
        label="Serverstandort"
        :readonly="readonly"
        :review="review"
        :error="errorFields.includes('server_location')"
        :help-text="getHelpText('server_location')"
        icon="serverstandort"
      />
      <DataProtectionInput
        v-if="dltFeatures"
        id="provider"
        v-model:compliance-text="data.data_privacy_assessment.provider_text"
        v-model:compliance="data.data_privacy_assessment.provider"
        v-model:review-value="reviewValue.provider"
        label="Anbieter"
        :readonly="readonly"
        :review="review"
        :error="errorFields.includes('provider')"
        :help-text="getHelpText('provider')"
        icon="anbieter"
      />
      <DataProtectionInput
        v-if="dltFeatures"
        id="user_registration"
        v-model:compliance-text="data.data_privacy_assessment.user_registration_text"
        v-model:compliance="data.data_privacy_assessment.user_registration"
        v-model:review-value="reviewValue.user_registration"
        label="Benutzeranmeldung"
        :readonly="readonly"
        :review="review"
        :error="errorFields.includes('user_registration')"
        :help-text="getHelpText('user_registration')"
        icon="benutzeranmeldung"
      />
      <DataProtectionInput
        v-if="dltFeatures"
        id="data_privacy_terms"
        v-model:compliance-text="data.data_privacy_assessment.data_privacy_terms_text"
        v-model:compliance="data.data_privacy_assessment.data_privacy_terms"
        v-model:review-value="reviewValue.data_privacy_terms"
        label="Datenschutzerklärung"
        :readonly="readonly"
        :review="review"
        :error="errorFields.includes('data_privacy_terms')"
        :help-text="getHelpText('data_privacy_terms')"
        icon="datenschutzerklarung"
      />
      <DataProtectionInput
        v-if="dltFeatures"
        id="terms_and_conditions"
        v-model:compliance-text="data.data_privacy_assessment.terms_and_conditions_text"
        v-model:compliance="data.data_privacy_assessment.terms_and_conditions"
        v-model:review-value="reviewValue.terms_and_conditions"
        label="AGB"
        :readonly="readonly"
        :review="review"
        :error="errorFields.includes('terms_and_conditions')"
        :help-text="getHelpText('terms_and_conditions')"
        icon="agb"
      />
      <DataProtectionInput
        v-if="dltFeatures"
        id="security"
        v-model:compliance-text="data.data_privacy_assessment.security_text"
        v-model:compliance="data.data_privacy_assessment.security"
        v-model:review-value="reviewValue.security"
        label="Sicherheit"
        :readonly="readonly"
        :review="review"
        :error="errorFields.includes('security')"
        :help-text="getHelpText('security')"
        icon="sicherheit"
      />
      <TextArea
        v-if="dltFeatures"
        id="conclusion"
        v-model:input-value="data.data_privacy_assessment.conclusion"
        v-model:review-value="reviewValue.conclusion"
        :readonly="readonly"
        :review="review"
        label="Fazit"
        :required="false"
        :error="errorFields.includes('conclusion')"
        :rows="3"
        :help-text="getHelpText('conclusion')"
        :character-counter="true"
        :maximal-chars="700"
      />
    </div>
  </ContentSubmissionForm>
</template>

<script setup>
import AppDropdown from '../components/AppDropdown.vue';
import AppSelect from '../components/AppSelect.vue';
import ContentSubmissionForm from '../components/ContentSubmissionForm.vue';
import DataProtectionInput from '../components/DataProtectionInput.vue';
import FileInput from '../components/FileInput.vue';
import LinkInput from '../components/LinkInput.vue';
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

data.value = {
  additional_info: '',
  author: '',
  co_authors: [],
  competences: [],
  contentlink_set: [],
  data_privacy_assessment: {},
  description: '',
  differentiating_attribute: '',
  disclaimer: '',
  educational_plan_reference: '',
  estimated_time: [],
  functions: [],
  image: null,
  imageRights: null,
  license: null,
  literatureLinks: [],
  mediaLinks: [],
  name: '',
  pending_co_authors: [],
  potentials: [],
  related_content: [],
  school_types: [],
  state: '',
  sub_competences: [],
  subjects: [],
  teaching_modules: [],
  teaser: '',
  tools: [],
  trends: [],
  video_tutorials: [],
  with_costs: false
};
resourceType.value = 'Tool';
requiredFields.value = [
  { field: 'name', title: 'Titel' },
  { field: 'teaser', title: 'Kurzzusammenfassung' },
  { field: 'image', title: 'Anzeigebild' },
  // {field: 'competences', title: 'Kompetenzen in der digitalen Welt'},
  { field: 'url', title: 'Website' }
];

const dltFeatures = window.dltFeatures;

const dataPrivacyOptions = [
  { label: 'Unbekannt', value: 0 },
  { label: 'Es werden keinerlei Daten erhoben', value: 1 },
  {
    label:
      'Personenbezogene Daten wie z.B. Logins werden geschützt auf dem Server abgelegt. Es greift die EU-Datenschutz-Grundverordnung.',
    value: 2
  },
  {
    label:
      'Personenbezogene Daten werden erhoben. Dritte haben Zugriff auf diese Daten. Es greift die EU-Datenschutz-Grundverordnung.',
    value: 3
  },
  {
    label: 'Personenbezogene Daten werden erhoben. Es greift NICHT die EU-Datenschutz-Grundverordnung.',
    value: 4
  }
];

const registrationOptions = [
  { label: 'Ja', value: true },
  { label: 'Nein', value: false }
];

const uskOptions = [
  { label: 'Ohne Altersbeschränkung', value: 'usk0' },
  { label: 'Ab 6 Jahren', value: 'usk6' },
  { label: 'Ab 12 Jahren', value: 'usk12' },
  { label: 'Ab 16 Jahren', value: 'usk16' },
  { label: 'Ab 18 Jahren', value: 'usk18' }
];
const statusOptions = [
  { label: 'Online', value: 'on' },
  { label: 'Offline', value: 'off' },
  { label: 'Online & Offline', value: 'onoff' }
];
const with_costsOptions = [
  { label: 'Ja', value: true },
  { label: 'Nein', value: false }
];
</script>

<style scoped></style>
