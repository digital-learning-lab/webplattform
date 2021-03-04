<template>
  <form class="mb-4" id="submission-form">
    <slot name="progress"></slot>
    <div class="submission-form">
    <div class="alert alert-success" v-if="data.submitted && mode !== 'review'">
      Der Inhalt wurde eingereicht und wird nun von Mitarbeiter_innen geprüft.
    </div>
    <slot name="messages-top">
      <div class="alert alert-primary" v-if="saved">
        Ihre Änderungen wurden gespeichert.
      </div>
      <div class="alert alert-danger" v-if="errors.length">
        <ul class="list-unstyled">
          <li v-for="error in errors">{{ error }}</li>
        </ul>
      </div>
    </slot>
    <slot name="buttons-top">
      <div v-if="mode === 'edit'">
        <button class="button button--primary" type="button" @click="$emit('update')" :disabled="loading" v-if="!data.submitted">Speichern</button>
        <button class="button button--preview" type="button" :disabled="loading" @click="$emit('preview')">Vorschau</button>
        <button class="button button--submit" type="button" :disabled="loading" @click="$emit('submit')" v-if="!data.submitted">Einreichen</button>
        <button class="button button--danger" type="button" :disabled="loading" @click="$emit('delete-warning')" v-if="canDelete">Löschen</button>
      </div>
      <div v-if="mode === 'review'">
        <button class="button button--primary" type="button" @click="$emit('update-review')" :disabled="loading">Speichern</button>
        <button class="button button--submit" type="button" :disabled="loading" @click="$emit('approve-review')">Freigeben</button>
        <button class="button button--danger" type="button" :disabled="loading" @click="$emit('decline-review')">Ablehnen</button>
      </div>
    </slot>
    <slot v-if="mode === 'edit' || mode === 'create' || mode === 'review'"></slot>
    <div v-if="mode === 'delete'">
      <h3>Wollen Sie den folgenden Inhalt wirklich löschen?</h3>
      <p><b>{{ data.name }}</b></p>

      <button type="button" class="button button--danger" @click="$emit('delete')">Ja, Inhalt löschen</button>
      <button type="button" class="button button--primary" @click="mode = 'edit'">Nein, abbrechen.</button>
    </div>
    <div v-if="mode === 'review'">
      <button class="button button--primary" type="button" @click="$emit('update-review')" :disabled="loading">Speichern</button>
      <button class="button button--submit" type="button" :disabled="loading" @click="$emit('approve-review')">Freigeben</button>
      <button class="button button--danger" type="button" :disabled="loading" @click="$emit('decline-review')">Ablehnen</button>
    </div>
    <div class="alert alert-primary" v-if="saved">
      Ihre Änderungen wurden gespeichert.
    </div>
    <div class="alert alert-danger" v-if="errors.length">
      <ul class="list-unstyled">
        <li v-for="error in errors">{{ error }}</li>
      </ul>
    </div>
    <slot name="extra-buttons"></slot>
    <div v-if="mode === 'edit'">
      <button class="button button--primary" type="button" @click="submit" :disabled="loading" v-if="!data.submitted">Speichern</button>
      <button class="button button--preview" type="button" :disabled="loading" @click="$emit('preview')">Vorschau</button>
      <button class="button button--submit" type="button" :disabled="loading" @click="$emit('submit')" v-if="!data.submitted">Einreichen</button>
      <button class="button button--danger" type="button" :disabled="loading" @click="$emit('delete-warning')" v-if="canDelete">Löschen</button>
    </div>
    <button class="button button--primary" @click="$emit('create')" type="button" v-if="mode === 'create'">Speichern</button>
    </div>
  </form>
</template>

<script>
  export default {
    name: 'ContentSubmissionForm',
    props: {
      saved: {
        type: Boolean,
        default: false,
        required: true
      },
      errors: {
        type: Array,
        default: () => {
          return []
        },
        required: true
      },
      mode: {
        type: String,
        default: 'create',
        required: true
      },
      canDelete: {
        type: Boolean,
        default: false,
        required: true
      },
      loading: {
        type: Boolean,
        default: false,
        required: true
      },
      data: {
        type: Object,
        default: () => {
          return {}
        },
        required: false
      }
    },
    methods: {
      submit () {
        const submissionEvent = new Event('content-submission')
        window.dispatchEvent(submissionEvent)
        this.$emit('update')
      }
    }
  }
</script>

<style scoped>
  .submission-form {
    max-width: 992px;
    margin-left: auto;
    margin-right: auto;
  }
</style>