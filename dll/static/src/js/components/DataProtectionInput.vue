<template>
  <div class="form-group mb-3">
    <label :for="props.id" class="mb-2 w-100">
      <span v-if="props.icon" class="icon--dlt me-3" :class="iconClass" /> {{ props.label }}:<span v-if="props.required"
        >*</span
      >
    </label>
    <button
      v-if="props.helpText"
      v-tooltip="props.helpText"
      class="button--neutral button--smallSquare button--help ms-1 float-end"
      type="button"
    />
    <div class="form__links-input">
      <div class="d-flex align-items-baseline">
        <select v-model="compliance" class="form-control me-3" name="types" @change="updateText($event)">
          <option value="compliant">Erfüllt</option>
          <option value="not_compliant">Nicht erfüllt</option>
          <option value="unknown">Unbekannt</option>
        </select>
        <input
          :id="props.id"
          v-model="complianceText"
          type="text"
          class="form-control me-3"
          :class="{ 'form__field--error': props.error }"
          placeholder="Anmerkungen"
          :readonly="props.readonly"
        />
      </div>
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
import { computed, ref } from 'vue';

import ReviewInput from './ReviewInput.vue';

//  --------------------------------------------------------------------------------------------------------------------
//  models + props
//  --------------------------------------------------------------------------------------------------------------------
const complianceText = defineModel('complianceText', { default: '', type: String });
const compliance = defineModel('compliance', { default: 'unknown', type: String });
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
  icon: {
    default: '',
    type: String
  },
  id: {
    default: '',
    required: true,
    type: String
  },
  label: {
    default: '',
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

const defaultTextCompliant = ref('');
const defaultTextNotCompliant = ref('');
const defaultTextUnknown = ref('');

//  --------------------------------------------------------------------------------------------------------------------
//  computed
//  --------------------------------------------------------------------------------------------------------------------
const iconClass = computed(() => {
  if (props.icon) {
    const icon = props.icon ? 'icon-' + props.icon : '';
    if (compliance.value === 'compliant') {
      return icon + '--green';
    } else if (compliance.value === 'not_compliant') {
      return icon + '--red';
    } else {
      return icon + '--grey';
    }
  }
  return '';
});

//  --------------------------------------------------------------------------------------------------------------------
//  component logic
//  --------------------------------------------------------------------------------------------------------------------
const isDefaultText = (s) => {
  return (
    s === defaultTextCompliant.value ||
    s === defaultTextNotCompliant.value ||
    s === defaultTextUnknown.value ||
    s === ''
  );
};

const updateText = (event) => {
  if (event.target.value === 'compliant') {
    if (isDefaultText(complianceText.value)) {
      complianceText.value = defaultTextCompliant.value;
    }
  } else if (event.target.value === 'not_compliant') {
    if (isDefaultText(complianceText.value)) {
      complianceText.value = defaultTextNotCompliant.value;
    }
  } else {
    if (isDefaultText(complianceText.value)) {
      complianceText.value = defaultTextUnknown.value;
    }
  }
};

//  --------------------------------------------------------------------------------------------------------------------
//  lifecycle
//  --------------------------------------------------------------------------------------------------------------------
defaultTextCompliant.value = window.compliance[props.id].compliant;
defaultTextNotCompliant.value = window.compliance[props.id].not_compliant;
defaultTextUnknown.value = window.compliance[props.id].unknown;
</script>

<style scoped></style>
