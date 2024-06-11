<template>
  <div class="form-group mb-3">
    <label :for="props.id">{{ props.label }}:<span v-if="props.required">*</span></label>

    <div class="custom-file">
      <div class="d-flex">
        <input
          :id="props.id"
          type="file"
          class="custom-file-input"
          :disabled="props.readonly"
          :accept="props.accept"
          @change="processInput($event)"
        />
        <label class="custom-file-label" :class="{ 'form__field--error': props.error }" :for="props.id">
          <span v-if="fileName" v-text="fileName" />
          <span v-else v-text="props.fileLabel" />
        </label>
        <button
          v-if="props.helpText"
          v-tooltip="props.helpText"
          class="button--neutral button--smallSquare button--help ms-1"
          type="button"
          data-bs-toggle="tooltip"
          data-placement="top"
        />
      </div>
    </div>
    <small v-if="props.hintText" class="form-text text-muted" v-text="props.hintText" />
    <img v-if="imageUrl" :src="imageUrl" alt="Vorschaubild" class="img-thumbnail" />
    <ReviewInput
      :id="'id' + -props.review"
      v-model="reviewValue"
      :mode="props.review ? 'review' : 'edit'"
      :name="props.label"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue';

import ReviewInput from './ReviewInput.vue';

//  --------------------------------------------------------------------------------------------------------------------
//  models + props
//  --------------------------------------------------------------------------------------------------------------------
const fileValue = defineModel('fileValue', { type: File });
const reviewValue = defineModel('reviewValue', { default: '', type: String });

const props = defineProps({
  accept: {
    default: 'image/gif, image/jpeg, image/png',
    type: String
  },
  error: {
    default: false,
    type: Boolean
  },
  fileLabel: {
    required: true,
    type: String
  },
  helpText: {
    default: '',
    type: String
  },
  hintText: {
    default: null,
    type: String
  },
  id: {
    required: true,
    type: String
  },
  image: {
    default: () => {
      return {};
    },
    type: Object
  },
  label: {
    required: true,
    type: String
  },
  readonly: {
    default: false,
    type: Boolean
  },
  required: {
    default: false,
    type: Boolean
  },
  review: {
    default: false,
    type: Boolean
  }
});

//  --------------------------------------------------------------------------------------------------------------------
//  computed
//  --------------------------------------------------------------------------------------------------------------------
const imageUrl = computed(() => {
  if (fileValue.value) {
    return URL.createObjectURL(fileValue.value);
  }

  if (props.image) {
    return props.image.url;
  }

  return null;
});

const fileName = computed(() => {
  if (fileValue.value) {
    return fileValue.value.name;
  }

  if (props.image) {
    return props.image.name;
  }

  return '';
});

//  --------------------------------------------------------------------------------------------------------------------
//  component logic
//  --------------------------------------------------------------------------------------------------------------------
const processInput = (e) => {
  fileValue.value = e.target.files[0];
};
</script>

<style scoped></style>
