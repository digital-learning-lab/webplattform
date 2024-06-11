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
      <div v-for="(item, index) in internalList" :key="index" class="d-flex align-items-baseline mb-2">
        <input
          v-if="!props.textarea"
          :id="props.id"
          v-model="internalList[index]"
          type="text"
          class="form-control me-3 form__list-input"
          :placeholder="props.placeholder"
          :readonly="props.readonly"
        />
        <textarea
          v-else
          :id="props.id"
          v-model="internalList[index]"
          type="text"
          class="form-control me-3"
          :placeholder="props.placeholder"
          :readonly="props.readonly"
        />
        <button
          v-if="!props.readonly"
          class="button--danger button--smallSquare"
          type="button"
          @click="removeItem(item)"
        >
          <span class="fas fa-times" />
        </button>
      </div>
    </div>
    <div>
      <button v-if="!props.readonly" class="button--neutral button--smallSquare" type="button" @click="addItem()">
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
import { ref, watch } from 'vue';

import ReviewInput from './ReviewInput.vue';

//  --------------------------------------------------------------------------------------------------------------------
//  models + props
//  --------------------------------------------------------------------------------------------------------------------
const listValue = defineModel('listValue', { default: [], type: Array });
const reviewValue = defineModel('reviewValue', { default: '', type: String });

const props = defineProps({
  helpText: {
    default: '',
    type: String
  },
  id: {
    required: true,
    type: String
  },
  initial: {
    default: () => [],
    type: Array
  },
  label: {
    required: true,
    type: String
  },
  min: {
    default: 0,
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
  textarea: {
    default: false,
    type: Boolean
  }
});

const internalList = ref(props.initial);

//  --------------------------------------------------------------------------------------------------------------------
//  component logic
//  --------------------------------------------------------------------------------------------------------------------
const addItem = () => {
  internalList.value.push('');
};

const removeItem = (text) => {
  internalList.value.splice(internalList.value.indexOf(text), 1);
};

//  --------------------------------------------------------------------------------------------------------------------
//  watchers
//  --------------------------------------------------------------------------------------------------------------------
watch(
  internalList,
  (newListValue) => {
    const result = newListValue.filter((input) => input.length !== 0);
    listValue.value = result;
  },
  { deep: true }
);

//  --------------------------------------------------------------------------------------------------------------------
//  lifecycle
//  --------------------------------------------------------------------------------------------------------------------
if (!internalList.value.length) {
  listValue.value = [];
  for (let i = 0; i < props.min; i++) {
    addItem();
  }
}
</script>

<style scoped></style>
