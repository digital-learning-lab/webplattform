<template>
  <div class="form-group mb-3">
    <label :for="props.id" class="mb-2 w-100">{{ props.label }}:<span v-if="props.required">*</span></label>
    <button
      v-if="props.helpText"
      class="button--neutral button--smallSquare button--help ms-1 float-end"
      type="button"
      data-bs-toggle="tooltip"
      data-placement="top"
      :title="props.helpText"
    />
    <div class="form__links-input">
      <div class="d-flex align-items-baseline">
        <input
          :id="props.id"
          v-model="internalValue.url_name"
          type="text"
          class="form-control me-3"
          :class="{ 'form__field--error': props.error }"
          placeholder="Linktext"
          :readonly="props.readonly"
          @blur="checkLinkValid(internalValue)"
        />
        <input
          :id="props.id"
          v-model="internalValue.url"
          type="text"
          class="form-control me-3"
          :class="{ 'form__field--error': !internalValue.validUrl || props.error }"
          placeholder="https://example.org"
          :readonly="props.readonly"
          @blur="checkLinkValid(internalValue)"
        />
        <select v-if="props.types" v-model="internalValue.type" class="form-control me-3" name="types">
          <option value="video">Video / Audio</option>
          <option value="href">Text</option>
        </select>
      </div>
    </div>
    <div v-if="!internalValue.validUrl" class="alert alert-danger mt-1">
      Bitte geben Sie eine valide URL ein. Die URL muss mit http:// bzw. https:// beginnen.
    </div>
    <div v-if="incomplete" class="alert alert-danger mt-1">
      Bitte geben Sie sowohl eine Bezeichnung (z.B. Webseite X) und eine URL an.
    </div>
    <ReviewInput
      :id="'id' + -props.review"
      v-model="reviewValue"
      :mode="props.review ? 'review' : 'edit'"
      :name="props.label"
    />
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue';

import ReviewInput from './ReviewInput.vue';

//  --------------------------------------------------------------------------------------------------------------------
//  models + props
//  --------------------------------------------------------------------------------------------------------------------
const linkValue = defineModel('linkValue', {
  default: () => {},
  type: Object
});
const reviewValue = defineModel('reviewValue', { default: '', type: String });

const props = defineProps({
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
  type: {
    default: 'href',
    type: String
  },
  types: {
    default: false,
    type: Boolean
  }
});

const incomplete = ref(false);
const internalValue = ref(linkValue.value);

//  --------------------------------------------------------------------------------------------------------------------
//  component logic
//  --------------------------------------------------------------------------------------------------------------------
const checkLinkValid = (link) => {
  if (!props.readonly) {
    link.validUrl = isValidUrl(link.url);
    incomplete.value = !link.url || !link.url_name;
  }
};

const isValidUrl = (url) => {
  var pattern = new RegExp(/^(ftp|http|https):\/\/[^ "]+$/, 'i');
  return !!pattern.test(url);
};

//  --------------------------------------------------------------------------------------------------------------------
//  watchers
//  --------------------------------------------------------------------------------------------------------------------
watch(
  internalValue,
  (newValue) => {
    linkValue.value = newValue;
  },
  { deep: true }
);

//  --------------------------------------------------------------------------------------------------------------------
//  lifecycle
//  --------------------------------------------------------------------------------------------------------------------
if (!internalValue.value) {
  internalValue.value = { url: '', url_name: '', validUrl: true };
}

if (linkValue.value) {
  internalValue.value = linkValue.value;
  internalValue.value.validUrl = true;
}
</script>

<style scoped></style>
