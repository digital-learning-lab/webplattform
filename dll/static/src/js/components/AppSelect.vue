<template>
  <div class="form-group mb-3">
    <label :for="props.id" v-text="props.label" />
    <div class="d-flex">
      <select
        :id="props.id"
        v-model="selectValue"
        :name="props.id"
        class="form-control"
        :class="{ 'form__field--error': props.error }"
        :disabled="props.readonly"
      >
        <option
          v-for="(option, index) in props.options"
          :key="index"
          :value="option.value"
          :selected="option.value == defaultVal"
        >
          {{ option.label }}
        </option>
      </select>
      <button
        v-if="props.helpText"
        v-tooltip="props.helpText"
        class="button--neutral button--smallSquare button--help ms-1"
        type="button"
      />
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
import ReviewInput from './ReviewInput.vue';

//  --------------------------------------------------------------------------------------------------------------------
//  models + props
//  --------------------------------------------------------------------------------------------------------------------
const selectValue = defineModel('inputValue', { default: '', type: [String, Number, Boolean] });
const reviewValue = defineModel('reviewValue', { default: '', type: String });

const props = defineProps({
  defaultVal: {
    default: '',
    type: [String, Number, Boolean]
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
  options: {
    required: true,
    type: Array
  },
  readonly: {
    default: false,
    type: Boolean
  },
  review: {
    default: false,
    type: Boolean
  }
});

//  --------------------------------------------------------------------------------------------------------------------
//  lifecycle
//  --------------------------------------------------------------------------------------------------------------------
selectValue.value = props.defaultVal;
</script>

<style scoped></style>
