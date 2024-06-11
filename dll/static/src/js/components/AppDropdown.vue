<template>
  <div class="form-group mb-3">
    <label :for="props.id">{{ props.label }}:<span v-if="props.required">*</span></label>
    <div class="d-flex">
      <Multiselect
        ref="multiselect"
        v-model="dropdownValue"
        class="dll-dropdown"
        :class="{ 'form__field--error': props.error }"
        searchable
        object
        :mode="selectMode"
        :close-on-select="closeOnSelect"
        :min-chars="1"
        :delay="0"
        :options="
          async function (query) {
            return await fetchOptions(query);
          }
        "
        :disabled="props.disabled || props.readonly"
        :filter-results="false"
        :resolve-on-load="props.prefetch"
        @open="triggerOptionFetch()"
      />
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
import Multiselect from '@vueform/multiselect';
import { computed, ref } from 'vue';

import { useAxios } from '../composables/axios';
import ReviewInput from './ReviewInput.vue';

//  --------------------------------------------------------------------------------------------------------------------
//  models + props
//  --------------------------------------------------------------------------------------------------------------------
const dropdownValue = defineModel('dropdownValue', { default: () => {}, type: Object });
const reviewValue = defineModel('reviewValue', { default: '', type: String });

const props = defineProps({
  disabled: {
    default: false,
    type: Boolean
  },
  error: {
    default: false,
    type: Boolean
  },
  fetchUrl: {
    default: '',
    type: String
  },
  helpText: {
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
  multiple: {
    default: false,
    type: Boolean
  },
  params: {
    default: () => {},
    type: Object
  },
  prefetch: {
    default: false,
    type: Boolean
  },
  readonly: {
    default: false,
    required: false,
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
//  component variables
//  --------------------------------------------------------------------------------------------------------------------
const { axios } = useAxios();
const multiselect = ref();

//  --------------------------------------------------------------------------------------------------------------------
//  component logic
//  --------------------------------------------------------------------------------------------------------------------
const fetchOptions = (q) => {
  const options = axios
    .get(props.fetchUrl, {
      params: {
        q,
        ...props.params
      }
    })
    .then((res) => {
      let options = res.data.results.map((el) => {
        return {
          label: el.username || el.name,
          pk: el.pk || el.id,
          value: el.pk || el.value || el.id
        };
      });

      const compareObjects = (a, b) => {
        return a.pk === b.pk && a.label === b.label;
      };

      let uniqueSet = new Set(options.map(JSON.stringify));
      let uniqueArray = Array.from(uniqueSet).map(JSON.parse);

      let resultArray = uniqueArray.filter((item, index, self) => {
        return self.findIndex((obj) => compareObjects(obj, item)) === index;
      });

      return resultArray;
    })
    .catch((err) => {
      console.log(err);
    });

  return options;
};

const triggerOptionFetch = () => {
  if (multiselect.value) {
    multiselect.value.refreshOptions();
  }
};

//  --------------------------------------------------------------------------------------------------------------------
//  computed
//  --------------------------------------------------------------------------------------------------------------------
const selectMode = computed(() => {
  return props.multiple ? 'tags' : 'single';
});

const closeOnSelect = computed(() => {
  return props.multiple ? false : true;
});
</script>

<style lang="scss" scoped></style>
