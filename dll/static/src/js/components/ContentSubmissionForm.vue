<template>
  <form id="submission-form" class="mb-4">
    <slot name="progress" />
    <div class="submission-form">
      <div v-if="props.data.submitted && modeValue !== 'review'" class="alert alert-success">
        Der Inhalt wurde eingereicht und wird nun von Mitarbeiter_innen geprüft.
      </div>
      <slot name="messagesTop">
        <div v-if="props.saved" class="alert alert-primary">Ihre Änderungen wurden gespeichert.</div>
        <div v-if="props.errors.length" class="alert alert-danger">
          <ul class="list-unstyled">
            <li v-for="(error, index) in props.errors" :key="index">
              {{ error }}
            </li>
          </ul>
        </div>
      </slot>
      <slot name="buttonsTop">
        <div v-if="modeValue === 'edit'">
          <button
            v-if="!props.data.submitted"
            class="button me-2 button--primary"
            type="button"
            :disabled="props.loading"
            @click="emitUpdate()"
          >
            Speichern
          </button>
          <button class="button me-2 button--preview" type="button" :disabled="props.loading" @click="emitPreview()">
            Vorschau
          </button>
          <button
            v-if="!props.data.submitted"
            class="button me-2 button--submit"
            type="button"
            :disabled="props.loading"
            @click="emitSubmit()"
          >
            Einreichen
          </button>
          <button
            v-if="props.canDelete"
            class="button me-2 button--danger"
            type="button"
            :disabled="props.loading"
            @click="emitDeleteWarning()"
          >
            Löschen
          </button>
        </div>
        <div v-if="modeValue === 'review'">
          <button class="button me-2 button--primary" type="button" :disabled="props.loading" @click="emitUpdateReview()">
            Speichern
          </button>
          <button class="button me-2 button--submit" type="button" :disabled="props.loading" @click="emitApproveReview()">
            Freigeben
          </button>
          <button class="button me-2 button--danger" type="button" :disabled="props.loading" @click="emitDeclineReview()">
            Ablehnen
          </button>
        </div>
      </slot>
      <slot v-if="modeValue === 'edit' || modeValue === 'create' || modeValue === 'review'" />
      <div v-if="modeValue === 'delete'">
        <h3>Wollen Sie den folgenden Inhalt wirklich löschen?</h3>
        <p>
          <b>{{ props.data.name }}</b>
        </p>

        <button type="button" class="button me-2 button--danger" @click="emitDelete()">Ja, Inhalt löschen</button>
        <button type="button" class="button me-2 button--primary" @click="modeValue = 'edit'">Nein, abbrechen.</button>
      </div>
      <div v-if="modeValue === 'review'">
        <button class="button me-2 button--primary" type="button" :disabled="props.loading" @click="emitUpdateReview()">
          Speichern
        </button>
        <button class="button me-2 button--submit" type="button" :disabled="props.loading" @click="emitApproveReview()">
          Freigeben
        </button>
        <button class="button me-2 button--danger" type="button" :disabled="props.loading" @click="emitDeclineReview()">
          Ablehnen
        </button>
      </div>
      <div v-if="props.saved" class="alert alert-primary">Ihre Änderungen wurden gespeichert.</div>
      <div v-if="props.errors.length" class="alert alert-danger">
        <ul class="list-unstyled">
          <li v-for="(error, index) in props.errors" :key="index">
            {{ error }}
          </li>
        </ul>
      </div>
      <slot name="extraButtons" />
      <div v-if="modeValue === 'edit'">
        <button
          v-if="!props.data.submitted"
          class="button me-2 button--primary"
          type="button"
          :disabled="props.loading"
          @click="submit"
        >
          Speichern
        </button>
        <button class="button me-2 button--preview" type="button" :disabled="props.loading" @click="emitPreview()">
          Vorschau
        </button>
        <button
          v-if="!props.data.submitted"
          class="button me-2 button--submit"
          type="button"
          :disabled="props.loading"
          @click="emitSubmit()"
        >
          Einreichen
        </button>
        <button
          v-if="props.canDelete"
          class="button me-2 button--danger"
          type="button"
          :disabled="props.loading"
          @click="emitDeleteWarning()"
        >
          Löschen
        </button>
      </div>
      <button v-if="modeValue === 'create'" class="button me-2 button--primary" type="button" @click="emitCreate()">
        Speichern
      </button>
    </div>
  </form>
</template>

<script setup>
//  --------------------------------------------------------------------------------------------------------------------
//  models + props
//  --------------------------------------------------------------------------------------------------------------------
const modeValue = defineModel('mode', { required: true, type: String });

const props = defineProps({
  canDelete: {
    required: true,
    type: Boolean
  },
  data: {
    default: () => {
      return {};
    },
    type: Object
  },
  errors: {
    required: true,
    type: Array
  },
  loading: {
    required: true,
    type: Boolean
  },
  saved: {
    required: true,
    type: Boolean
  }
});

//  --------------------------------------------------------------------------------------------------------------------
//  component logic
//  --------------------------------------------------------------------------------------------------------------------
const submit = () => {
  const submissionEvent = new Event('content-submission');
  window.dispatchEvent(submissionEvent);
  emitUpdate();
};

//  --------------------------------------------------------------------------------------------------------------------
//  emits
//  --------------------------------------------------------------------------------------------------------------------
const emits = defineEmits([
  'update',
  'preview',
  'submit',
  'create',
  'deleteWarning',
  'approveReview',
  'declineReview',
  'updateReview',
  'delete'
]);

const emitUpdate = () => {
  emits('update');
};

const emitPreview = () => {
  emits('preview');
};

const emitSubmit = () => {
  emits('submit');
};

const emitCreate = () => {
  emits('create');
};

const emitDeleteWarning = () => {
  emits('deleteWarning');
};

const emitApproveReview = () => {
  emits('approveReview');
};

const emitDeclineReview = () => {
  emits('declineReview');
};

const emitUpdateReview = () => {
  emits('updateReview');
};

const emitDelete = () => {
  emits('delete');
};
</script>

<style lang="scss" scoped>
.submission-form {
  max-width: 992px;
  margin-left: auto;
  margin-right: auto;
}
</style>
