<template>
  <app-content-submission-form :errors="errors" :mode="mode" :loading="loading" :saved="saved" @update="updateContent" @create="createContent" @preview="goToPreview" @delete-warning="showDeleteWarning" :data="data" @delete="deleteContent" @submit="submitContent" @update-review="updateReview" @approve-review="approveContent" @decline-review="declineContent" :can-delete="canDelete">
      <div class="form-group" v-if="reviewValue.feedback && !review">
        <label>Feedback:</label> <br>
        {{ reviewValue.feedback }}
      </div>
      <app-text-area id="feedback" v-if="review" :review="false" label="Feedback" :required="false" :value.sync="reviewValue.feedback" :rows="3" :help-text="getHelpText('feedback')"></app-text-area>
      <app-text-input id="author" :readonly="true" label="Autor_in" :value.sync="data.author" :required="true"></app-text-input>
      <app-text-input id="title" :readonly="readonly" :review="review" label="Titel des Tools" :value.sync="data.name" :review-value.sync="reviewValue.name" :error="errorFields.includes('name')" :required="true" :character-counter="true" :maximal-chars="140" :help-text="getHelpText('name')"></app-text-input>
    <div v-if="mode === 'edit' || mode === 'review'">
      <app-file-input id="image" :readonly="readonly" :review="review" :required="true" label="Anzeigebild" file-label="Bild wählen" :value.sync="previewImage" :review-value.sync="reviewValue.previewImage" :error="errorFields.includes('image')" :image="data.image" :help-text="getHelpText('image')" :hintText="imageHintText"></app-file-input>
      <app-text-area id="teaser" :readonly="readonly" :review="review" label="Kurzzusammenfassung" :required="true" :value.sync="data.teaser" :review-value.sync="reviewValue.teaser" :error="errorFields.includes('teaser')" :rows="3" :help-text="getHelpText('teaser')"></app-text-area>
      <app-dropdown id="co_authors" :readonly="readonly" :review="review" label="Co-Autor_innen" :value.sync="data.co_authors" :review-value.sync="reviewValue.co_authors" :error="errorFields.includes('co_authors')" fetch-url="/api/authors" :multiple="true" :help-text="getHelpText('co_authors')"></app-dropdown>
      <app-pending-co-authors :pending_co_authors="data.pending_co_authors"></app-pending-co-authors>
      <app-dropdown id="teaching-modules" :readonly="readonly" :review=review label="Passende Unterrichtsbausteine" :value.sync="data.teaching_modules" :review-value.sync="reviewValue.teaching_modules" :error="errorFields.includes('teaching_modules')" fetch-url="/api/unterrichtsbausteine" :multiple="true" :help-text="getHelpText('teaching_modules')" :prefetch="true"></app-dropdown>
      <app-dropdown id="tools" :readonly="readonly" :review="review" label="Passende Tools" :value.sync="data.tools" :review-value.sync="reviewValue.tools" :error="errorFields.includes('tools')" fetch-url="/api/tools" :multiple="true" :help-text="getHelpText('tools')" :prefetch="true"></app-dropdown>
      <app-dropdown id="trends" :readonly="readonly" :review="review" label="Passende Trends" :value.sync="data.trends" :review-value.sync="reviewValue.trends" :error="errorFields.includes('trends')" fetch-url="/api/trends" :multiple="true" :help-text="getHelpText('trends')" :prefetch="true"></app-dropdown>
      <!-- <app-dropdown id="competences" :readonly="readonly" :review="review" label="Kompetenzen in der digitalen Welt" :required="true" :value.sync="data.competences" :review-value.sync="reviewValue.competences" :error="errorFields.includes('competences')" fetch-url="/api/competences" :multiple="true" :prefetch="true" :help-text="getHelpText('competences')"></app-dropdown> -->
      <app-dropdown id="tool-functions" :readonly="readonly" :review="review" label="Tool-Funktionen" :required="true" :value.sync="data.functions" :review-value.sync="reviewValue.functions" :error="errorFields.includes('functions')" fetch-url="/api/toolFunctions" :multiple="true" :prefetch="true" :help-text="getHelpText('functions')"></app-dropdown>
      <app-link-input id="url" :readonly="readonly" :review="review" :link.sync="data.url" :review-value.sync="reviewValue.url" :error="errorFields.includes('url')" label="Website" :type="'null'" :help-text="getHelpText('url')" :required="true"></app-link-input>
      <app-list-input :min="1" id="pro" :readonly="readonly" :review="review" label="Vorteile" :list.sync="data.pro" :review-value.sync="reviewValue.pro" :error="errorFields.includes('pro')" :initial="data.pro" :help-text="getHelpText('pro')"></app-list-input>
      <app-list-input :min="1" id="contra" :readonly="readonly" :review="review" label="Nachteile" :list.sync="data.contra" :review-value.sync="reviewValue.contra" :error="errorFields.includes('contra')" :initial="data.contra" :help-text="getHelpText('contra')"></app-list-input>
      <app-select id="data-privacy" :readonly=readonly  :review="review" label="Datenschutz" :options="dataPrivacyOptions" default-val="" :value.sync="data.privacy" :review-value.sync="reviewValue.privacy" :error="errorFields.includes('privacy')" :default-val="data.privacy" :help-text="getHelpText('privacy')"></app-select>
      <app-text-area id="usage" :readonly="readonly" :review="review" label="Nutzung" :value.sync="data.usage" :review-value.sync="reviewValue.usage" :error="errorFields.includes('usage')" :character-counter="true" :maximal-chars="300" :help-text="getHelpText('usage')"></app-text-area>
      <app-dropdown id="applications" :readonly="readonly" :review="review" label="Anwendung" :value.sync="data.applications" :review-value.sync="reviewValue.applications" :error="errorFields.includes('applications')" fetch-url="/api/applications" :multiple="true" :prefetch="true" :help-text="getHelpText('applications')"></app-dropdown>
      <app-links-input id="mediaLinks" :readonly="readonly" :review="review" :links.sync="data.mediaLinks" :review-value.sync="reviewValue.mediaLinks" :error="errorFields.includes('mediaLinks')" label="Links zu Audio- und Videomedien" :type="'video'" :help-text="getHelpText('contentlink')" :types="true"></app-links-input>
      <app-links-input id="literatureLinks" :readonly="readonly" :review="review" :links.sync="data.literatureLinks" :review-value.sync="reviewValue.literatureLinks" :error="errorFields.includes('literatureLinks')" label="Text-Anleitung" :help-text="getHelpText('contentlink')" :types="true"></app-links-input>
      <app-select id="requires_registration" :readonly="readonly" :review="review" label="Registrierung erforderlich" :options="registrationOptions" :value.sync="data.requires_registration" :review-value.sync="reviewValue.requires_registration" :error="errorFields.includes('requires_registration')" :default-val="data.requires_registration" :help-text="getHelpText('requires_registration')"></app-select>
      <app-select id="usk" :readonly="readonly" :review="review" label="Altersfreigabe" :options="uskOptions" :value.sync="data.usk" :review-value.sync="reviewValue.usk" :error="errorFields.includes('usk')" :default-val="data.usk" :help-text="getHelpText('usk')"></app-select>
      <app-select id="status" :readonly="readonly" :review="review" label="Status" :options="statusOptions" :value.sync="data.status" :review-value.sync="reviewValue.status" :error="errorFields.includes('status')" :default-val="data.status" :help-text="getHelpText('status')"></app-select>
      <app-text-area id="additional-info" :readonly="readonly" :review="review" label="Anmerkungen" :value.sync="data.additional_info" :review-value.sync="reviewValue.additional_info" :error="errorFields.includes('additional_info')" :character-counter="true" :maximal-chars="700" :rows="10" :help-text="getHelpText('additional_info')"></app-text-area>
      <app-text-area id="description" :readonly="readonly" :review="review" label="Detaillierte Beschreibung" :value.sync="data.description" :review-value.sync="reviewValue.description" :error="errorFields.includes('description')" :character-counter="true" :maximal-chars="500" :rows="10" :help-text="getHelpText('description')"></app-text-area>
      <app-dropdown id="operating_systems" :readonly="readonly" :review="review" label="Betriebssystem" :value.sync="data.operating_systems" :review-value.sync="reviewValue.operating_systems" :error="errorFields.includes('operating_systems')" fetch-url="/api/operatingSystems" :multiple="true" :prefetch="true" :help-text="getHelpText('operating_systems')"></app-dropdown>
      <app-dropdown id="subject" :readonly="readonly" :review="review" :required="true" label="Unterrichtsfach" :value.sync="data.subjects" :review-value.sync="reviewValue.subjects" :error="errorFields.includes('subjects')" fetch-url="/api/subjects" :multiple="true" :prefetch="true" :help-text="getHelpText('subjects')"></app-dropdown>
      <app-select id="with_costs" :readonly="readonly" :review="review" label="Kostenpflichtig" :options="with_costsOptions" :value.sync="data.with_costs" :review-value.sync="reviewValue.with_costs" :error="errorFields.includes('with_costs')" :default-val="data.with_costs" :help-text="getHelpText('with_costs')"></app-select>
      <app-dropdown id="tool-potentials" :readonly="readonly" :review="review" label="Potential Kategorien" :required="true" :value.sync="data.potentials" :review-value.sync="reviewValue.potentials" :error="errorFields.includes('potentials')" fetch-url="/api/potentials" :multiple="true" :prefetch="true" :help-text="getHelpText('potentials')"></app-dropdown>
      <app-text-area id="disclaimer" :readonly="readonly" :review="review" label="Kurzzusammenfassung" :required="true" :value.sync="data.disclaimer" :review-value.sync="reviewValue.disclaimer" :error="errorFields.includes('disclaimer')" :rows="3" :help-text="getHelpText('disclaimer')"></app-text-area>
      <app-links-input id="video_tutorials" :readonly="readonly" :review="review" :links.sync="data.video_tutorials" :review-value.sync="reviewValue.video_tutorials" :error="errorFields.includes('video_tutorials')" label="Video Anleitungen" :type="'video'" :help-text="getHelpText('video_tutorials')" :types="false"></app-links-input>
      <app-data-protection-input id="server_location" label="Serverstandort" :readonly="readonly" :review="review" :links.sync="data.server_location" :review-value.sync="reviewValue.server_location" :error="errorFields.includes('server_location')" :help-text="getHelpText('server_location')" icon="serverstandort"></app-data-protection-input>
      <app-data-protection-input id="provider" label="Anbieter" :readonly="readonly" :review="review" :links.sync="data.provider" :review-value.sync="reviewValue.provider" :error="errorFields.includes('provider')" :help-text="getHelpText('provider')" icon="anbieter"></app-data-protection-input>
      <app-data-protection-input id="user_registration" label="Benutzeranmeldung" :readonly="readonly" :review="review" :links.sync="data.user_registration" :review-value.sync="reviewValue.user_registration" :error="errorFields.includes('user_registration')" :help-text="getHelpText('user_registration')" icon="benutzeranmeldung"></app-data-protection-input>
      <app-data-protection-input id="data_privacy_terms" label="Datenschutzerklärung" :readonly="readonly" :review="review" :links.sync="data.data_privacy_terms" :review-value.sync="reviewValue.data_privacy_terms" :error="errorFields.includes('data_privacy_terms')" :help-text="getHelpText('data_privacy_terms')" icon="datenschutzerklarung"></app-data-protection-input>
      <app-data-protection-input id="terms_and_conditions" label="AGB" :readonly="readonly" :review="review" :links.sync="data.terms_and_conditions" :review-value.sync="reviewValue.terms_and_conditions" :error="errorFields.includes('terms_and_conditions')" :help-text="getHelpText('terms_and_conditions')" icon="agb"></app-data-protection-input>
      <app-data-protection-input id="security" label="Sicherheit" :readonly="readonly" :review="review" :links.sync="data.security" :review-value.sync="reviewValue.security" :error="errorFields.includes('security')" :help-text="getHelpText('security')" icon="sicherheit"></app-data-protection-input>
      <app-text-area id="conclusion" :readonly="readonly" :review="review" label="Fazit" :required="true" :value.sync="data.conclusion" :review-value.sync="reviewValue.conclusion" :error="errorFields.includes('conclusion')" :rows="3" :help-text="getHelpText('conclusion')" :character-counter="true" :maximal-chars="700"></app-text-area>
    </div>
  </app-content-submission-form>
</template>

<script>
  import { submissionMixin } from './mixins/submissionMixin'
  import ContentSubmissionForm from './ContentSubmissionForm.vue'
  import DataProtectionInput from './components/DataProtectionInput.vue'

  export default {
    name: 'ToolSubmissionApp',
    mixins: [submissionMixin],
    components: {
      'AppContentSubmissionForm': ContentSubmissionForm,
      'AppDataProtectionInput': DataProtectionInput,
    },
    data () {
      return {
        resourceType: 'Tool',
        requiredFields: [
          {field: 'name', title: 'Titel'},
          {field: 'teaser', title: 'Kurzzusammenfassung'},
          {field: 'image', title: 'Anzeigebild'},
          // {field: 'competences', title: 'Kompetenzen in der digitalen Welt'},
          {field: 'url', title: 'Website'},
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
          estimated_time: [],
          competences: [],
          functions: [],
          educational_plan_reference: '',
          differentiating_attribute: '',
          sub_competences: [],
          subjects: [],
          tools: [],
          trends: [],
          teaching_modules: [],
          additional_info: '',
          related_content: [],
          mediaLinks: [],
          video_tutorials: [],
          literatureLinks: [],
          license: null,
          with_costs: false,
          potentials: [],
          disclaimer: '',
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
        ],
        with_costsOptions: [
          {value: true, label: 'Ja'},
          {value: false, label: 'Nein'}
        ]
      }
    },
    methods: {}
  }
</script>

<style scoped>

</style>