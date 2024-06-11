<template>
  <div class="form-group mb-3">
    <label :for="props.id" class="mb-2 w-100">{{ props.label }}:<span v-if="props.required">*</span></label>
    <button
      v-if="props.helpText"
      v-tooltip="props.helpText"
      class="button--neutral button--smallSquare button--help ms-1 float-end"
      type="button"
    />
    <div class="form__list-inputs">
      <div v-for="(link, index) in internalValue" :key="index" class="mb-2">
        <div class="d-flex align-items-baseline">
          <input
            :id="props.id"
            v-model="link.name"
            type="text"
            class="form-control me-3"
            :placeholder="props.namePlaceholder"
            :readonly="props.readonly"
          />
          <input
            :id="props.id"
            v-model="link.url"
            type="text"
            class="form-control me-3"
            :class="{ 'form__field--error': !link.validUrl }"
            :placeholder="props.linkPlaceholder"
            :readonly="props.readonly"
            @blur="checkLinkValid(link)"
          />
          <select v-if="props.types" v-model="link.type" class="form-control me-3" name="types">
            <option value="video">Video / Audio</option>
            <option value="href">Text</option>
          </select>
          <button
            v-if="!props.readonly"
            class="button--danger button--smallSquare"
            type="button"
            @click="removeLink(link)"
          >
            <span class="fas fa-times" />
          </button>
        </div>
        <div v-if="!link.validUrl" class="alert alert-danger mt-1">
          Bitte geben Sie eine valide URL ein. Die URL muss mit http:// bzw. https:// beginnen.
        </div>
      </div>
      <div v-if="readonlyAndEmpty">Keine Daten</div>
    </div>
    <div v-if="!props.readonly">
      <button class="button--neutral button--smallSquare" type="button" @click="addLink()">
        <span class="fas fa-plus" />
      </button>
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
const linksValue = defineModel('linksValue', {
  default: [],
  type: Array
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
  linkPlaceholder: {
    default: 'https://example.org',
    type: String
  },
  namePlaceholder: {
    default: 'Linktext',
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

const internalValue = ref(linksValue.value);

//  --------------------------------------------------------------------------------------------------------------------
//  computed
//  --------------------------------------------------------------------------------------------------------------------
const readonlyAndEmpty = computed(() => {
  return props.readonly && internalValue.value.length === 0;
});

//  --------------------------------------------------------------------------------------------------------------------
//  component logic
//  --------------------------------------------------------------------------------------------------------------------
const addLink = () => {
  internalValue.value.push({ name: '', type: props.type, url: '', validUrl: true });
};

const removeLink = (link) => {
  internalValue.value.splice(internalValue.value.indexOf(link), 1);
};

const isValidUrl = (url) => {
  // https://stackoverflow.com/questions/5717093/check-if-a-javascript-string-is-a-url
  var pattern = new RegExp(/^(ftp|http|https):\/\/[^ "]+$/, 'i');

  return !!pattern.test(url);
};

const checkLinkValid = (link) => {
  if (!props.readonly) {
    link.validUrl = isValidUrl(link.url);
  }
};

//  --------------------------------------------------------------------------------------------------------------------
//  watchers
//  --------------------------------------------------------------------------------------------------------------------
watch(
  () => props.error,
  () => {
    linksValue.value.forEach((link) => {
      checkLinkValid(link);
    });
  }
);

watch(
  internalValue,
  (newValue) => {
    linksValue.value = newValue;
  },
  { deep: true }
);

//  --------------------------------------------------------------------------------------------------------------------
//  lifecycle
//  --------------------------------------------------------------------------------------------------------------------
internalValue.value.forEach((link) => {
  link.validUrl = true;
});
</script>

<style scoped></style>
