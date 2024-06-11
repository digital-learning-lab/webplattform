<template>
  <div class="form-group mb-3">
    <label :for="props.id">{{ props.label }}:<span v-if="props.required">*</span></label>
    <div class="d-flex">
      <textarea
        :id="props.id"
        v-model="textAreaValue"
        class="form-control"
        :class="{ 'form__field--error': props.error }"
        :placeholder="props.placeholder"
        :readonly="props.readonly"
        :maxlength="props.maximalChars"
        :rows="props.rows"
      />
      <button
        v-if="props.helpText"
        v-tooltip="props.helpText"
        class="button--neutral button--smallSquare button--help ms-1"
        type="button"
      />
    </div>
    <small v-if="props.characterCounter" class="form-text text-muted float-end">
      {{ charactersLeft }} Zeichen verbleibend
    </small>
    <div class="clearfix" />
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
const textAreaValue = defineModel('inputValue', { default: '', type: String });
const reviewValue = defineModel('reviewValue', { default: '', type: String });

const props = defineProps({
  characterCounter: {
    default: false,
    type: Boolean
  },
  error: {
    default: false,
    type: Boolean
  },
  helpText: {
    default: '',
    type: String
  },
  id: {
    required: true,
    type: String
  },
  label: {
    required: true,
    type: String
  },
  maximalChars: {
    default: null,
    type: Number
  },
  placeholder: {
    default: '',
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
  },
  rows: {
    default: 10,
    type: Number
  }
});

//  --------------------------------------------------------------------------------------------------------------------
//  computed
//  --------------------------------------------------------------------------------------------------------------------
const charactersLeft = computed(() => {
  return textAreaValue.value ? props.maximalChars - textAreaValue.value.length : props.maximalChars;
});
</script>

<style scoped></style>
