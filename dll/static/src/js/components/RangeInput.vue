<template>
  <div class="form-group mb-3">
    <label :for="props.id">{{ props.label }}:<span v-if="props.required">*</span></label>
    <div class="row">
      <div class="col d-flex align-items-baseline">
        <label class="me-3" :for="props.id + 'from'">{{ props.labelFrom }}:</label>
        <input
          :id="props.id + '-from'"
          v-model="from"
          :type="props.type"
          class="form-control"
          :min="props.min"
          :max="props.max"
          :readonly="readonly"
          @blur="validateFrom($event)"
        />
      </div>
      <div class="col d-flex align-items-baseline">
        <label class="me-3" :for="props.id + 'to'">{{ props.labelTo }}:</label>
        <input
          :id="props.id + '-to'"
          v-model="to"
          :type="props.type"
          class="form-control"
          :min="props.min"
          :max="props.max"
          :readonly="props.readonly"
          @blur="validateTo($event)"
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
import { ref, watch } from 'vue';

import ReviewInput from './ReviewInput.vue';

//  --------------------------------------------------------------------------------------------------------------------
//  models + props
//  --------------------------------------------------------------------------------------------------------------------
const rangeValue = defineModel('rangeValue', { type: Object });
const reviewValue = defineModel('reviewValue', { default: '', type: String });

const props = defineProps({
  id: {
    required: true,
    type: String
  },
  label: {
    required: true,
    type: String
  },
  labelFrom: {
    required: true,
    type: String
  },
  labelTo: {
    required: true,
    type: String
  },
  max: {
    default: null,
    type: Number
  },
  min: {
    default: null,
    type: Number
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
    default: 'text',
    type: String
  }
});

//  --------------------------------------------------------------------------------------------------------------------
//  component variables
//  --------------------------------------------------------------------------------------------------------------------
const from = ref(null);
const to = ref(null);

//  --------------------------------------------------------------------------------------------------------------------
//  component logic
//  --------------------------------------------------------------------------------------------------------------------
const checkValues = () => {
  if (to.value && from.value && parseInt(from.value) >= parseInt(to.value)) {
    if (parseInt(to.value) === 1) {
      to.value = 2;
    }
    from.value = to.value - 1;
  }
};

const validateTo = (e) => {
  let newValue = e.target.value;
  if (newValue || newValue === 0) {
    if (newValue < props.min) {
      to.value = props.min;
    }
    if (newValue > props.max) {
      to.value = props.max;
    }
    checkValues();
  }
};

const validateFrom = (e) => {
  let newValue = e.target.value;
  if (newValue || newValue === 0) {
    if (newValue < props.min) {
      from.value = props.min;
    }
    if (newValue > props.max) {
      from.value = props.max;
    }
    checkValues();
  }
};

const updateRangeValue = () => {
  rangeValue.value = {
    lower: parseInt(from.value),
    upper: parseInt(to.value)
  };
};

//  --------------------------------------------------------------------------------------------------------------------
//  watchers
//  --------------------------------------------------------------------------------------------------------------------
watch([from, to], () => {
  updateRangeValue();
});

//  --------------------------------------------------------------------------------------------------------------------
//  lifecycle
//  --------------------------------------------------------------------------------------------------------------------
if (rangeValue.value) {
  from.value = rangeValue.value['lower'];
  to.value = rangeValue.value['upper'];
}
</script>

<style scoped></style>
