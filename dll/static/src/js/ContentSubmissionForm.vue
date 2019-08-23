<template>
  <form class="mb-4">
    <div class="alert alert-primary" v-if="saved">
      Ihre Änderungen wurden gespeichert.
    </div>
    <div class="alert alert-danger" v-if="errors.length">
      <ul class="list-unstyled">
        <li v-for="error in errors">{{ error }}</li>
      </ul>
    </div>
    <div v-if="mode === 'edit'">
      <button class="button button--primary" type="button" @click="$emit('update')" :disabled="loading">Speichern</button>
      <button class="button button--primary" type="button" :disabled="loading">Vorschau</button>
      <button class="button button--primary" type="button" :disabled="loading">Einreichen</button>
      <button class="button button--primary" type="button" :disabled="loading">Löschen</button>
    </div>
    <slot></slot>
    <button class="button button--primary" @click="$emit('create')" type="button" v-if="mode === 'create'">Speichern</button>
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
      loading: {
        type: Boolean,
        default: false,
        required: true
      }
    }
  }
</script>

<style scoped>

</style>